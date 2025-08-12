from datetime import datetime, tzinfo, timezone
from decimal import Decimal
import json
from queue import Queue
import sys
import time
from typing import Dict, List, Union
import httpx
from tenacity import (
    retry,
    stop_after_attempt,
    stop_after_delay,
    wait_random,
)
import asyncio
from transpara.tlogging import (
    logd_async,
    get_logger,
    set_log_level,
    TRANSPARA_DEBUG_LEVEL,
)
import pendulum
from datetime import datetime
from transpara.internal.settings import OutputTstoreSettings


#{"name":"system","tags":{"host":"server01"},"fields":{"cpu_usage":23.5,"mem_total":2048,"mem_used":1024,"disk_total":500000,"disk_used":250000},"timestamp":1627334400}
#pyinstaller --onefile output_tstore.py --copy-metadata opentelemetry-sdk --additional-hooks-dir extra-hooks


set_log_level(TRANSPARA_DEBUG_LEVEL)
logger = get_logger(__name__)


class OutputTStore:

    #TODO implement max buffer size
    def __init__(self, config: OutputTstoreSettings):
        self.config = config
        self.client = httpx.AsyncClient()
        self.q: Queue = Queue()
        self.start_time = time.time()
        self.buffer_batches : List[Dict] = []
        self.max_buffer_size = 1_000_000
        
    def _add_to_buffer(self, items: List[Dict]):
        # Extend the buffer with new items
        self.buffer_batches.extend(items)
        # Ensure the buffer size does not exceed the max size
        if len(self.buffer_batches) > self.max_buffer_size:
            # Calculate how many items need to be removed
            excess_items = len(self.buffer_batches) - self.max_buffer_size
            # Remove the oldest items to maintain the buffer size
            self.buffer_batches = self.buffer_batches[excess_items:]


    async def _get_localized_timestamp(
        self, date: Union[str, datetime, int, float], pytz: tzinfo
    ) -> str:

        if isinstance(date, (int, float)):
            if date >= 1e16:  
                date /= 1e9
            elif date >= 1e14:  
                date /= 1e6
            elif date >= 1e11:  
                date /= 1e3
            date = datetime.fromtimestamp(date, tz=timezone.utc)
        if isinstance(date, str):
            return pendulum.parse(date, tz=pytz).isoformat()
        if date.tzinfo is None:
            return pytz.localize(date).isoformat()
        else:
            return date.astimezone(pytz).isoformat()

    async def enqueue_data(self, metric, value, timestamp, labels, pytz: tzinfo):
        """
        pytz is a pytz.timezone object that will be used to localize the timestamp
        """
        data = {
            "metric": metric,
            "value": value,
            "timestamp": await self._get_localized_timestamp(timestamp, pytz),
            "labels": labels,
        }
        self.q.put(data)

        if self.config.LOG_ENQUEUING:
            logger.tdebug(f"Enqueued data: {data}")

    async def _get_batches_from_queue(self, batch_size=200) -> List[Dict]:

        rows = []

        while not self.q.empty():
            rows.append(self.q.get())

        #get all the rows from the queue and put them in a list
        #each row looks like: {"metric": "metric_name", "value": 123, "timestamp": "2023-08-11T05:45:00-06:00", "labels": "label1=value1,label2=value2"}

        batches = []
        #each batch will be a valid tstore payload

        current_batch = 0
        items_in_batch = 0
        batches.append({})

        for item in rows:

            if items_in_batch >= batch_size:
                current_batch += 1
                items_in_batch = 0
                batches.append({})
            
            batch: Dict = batches[current_batch]

            lookup = item["metric"] + "|" + item["labels"]

            if lookup not in batch:
                batch[lookup] = []

            batch[lookup].append({"v": item["value"], "ts": item["timestamp"]})
            items_in_batch += 1

        return batches

    
    
    @logd_async()
    @retry(
    stop=(stop_after_delay(5) | stop_after_attempt(2)),
    wait=wait_random(min=2, max=4),
    reraise=True)
    async def _send_data(self, batches: List[Dict]):
        url = self.config.get_write_endpoint()
        for batch in batches:
            if not batch:
                continue
            json_data = json.dumps(batch, cls=DecimalEncoder)
            response = await self.client.post(url, content=json_data)
            self.last_send_time = time.time()
            response.raise_for_status()

    @logd_async(verbose_exc=True)
    async def _try_send_data(self):
        try:
            batches = await self._get_batches_from_queue(self.config.OUTPUT_BATCH_SIZE)
            await self._send_data(batches)
        except httpx.HTTPStatusError as http_err:
            logger.terror(f"HTTP status error occurred: {http_err}")
        except httpx.ConnectError as conn_err:
            self._add_to_buffer(batches)
            logger.terror(f"Connection error occurred: {conn_err}, buffering batches")
        except httpx.TimeoutException as timeout_err:
            self._add_to_buffer(batches)
            logger.terror(f"Timeout error occurred: {timeout_err}, buffering batches")
        except httpx.RequestError as req_err:
            self._add_to_buffer(batches)
            logger.terror(f"Request error occurred: {req_err}, buffering batches")
        except BaseException as e:
            logger.terror(f"Error sending data: {e}")
        
        if not self.buffer_batches:
            return
        
        logger.tdebug(f"Sending {len(self.buffer_batches)} buffered batches")

        try:
            await self._send_data(self.buffer_batches)
            self.buffer_batches.clear()
        except BaseException as e:
            logger.terror(f"Error sending buffered batches: {e}, trying again later")
        
    async def send_data_loop(self):

        while True:

            if self.q.qsize() >= self.config.TSTORE_FLUSH_SIZE:
                logger.tdebug(f"Sending data due to size limit, config.max_size = {self.config.TSTORE_FLUSH_SIZE}, current_queue_size = {self.q.qsize()}")
                await self._try_send_data()
                self.start_time = time.time()
            elif (time.time() - self.start_time) >= self.config.TSTORE_FLUSH_INTERVAL_SECONDS and self.q.qsize() > 0:
                logger.tdebug(f"Sending data due to time limit, config.interval_seconds = {self.config.TSTORE_FLUSH_INTERVAL_SECONDS}, current_queue_size = {self.q.qsize()}")
                await self._try_send_data()
                self.start_time = time.time() 

            await asyncio.sleep(0.1)

class DecimalEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, Decimal):
                return float(obj) 
            return super().default(obj)

def sanitize_string(string:str) -> str:
    
    if not isinstance(string, str):
        string = str(string)
    
    """
    tStore does not support commas, because we use it as a label separator
    """
    return string.replace(',','_')
    
def add_labels(key, value, curr_labels):
    if curr_labels == "":
        return f"{key}={value}"
    else:
        return f"{curr_labels},{key}={value}"

async def process_line(rawLine, output_tstore:OutputTStore):

    labels: str = ""

    # this should not be required, 
    # but we seem to be getting malformed data from time to time
    try:
        line = json.loads(rawLine)
    except Exception as ex:
        logger.tdebug("TEXT-I-Invalid data received - {}\n\t({})".format(rawLine,ex))
        return
    
    # pick apart the line, convert to json and construct the labels, etc.
    ts = line['timestamp']
    tags:Dict = line['tags']
    fields:Dict = line['fields']

    metric:str = sanitize_string(line['name'])
    telegraf_metric_name = metric

    if output_tstore.config.METRIC_NAME:
        metric = output_tstore.config.METRIC_NAME
    elif output_tstore.config.USE_HOST_AS_METRIC_NAME and "host" in tags:
        metric = sanitize_string(tags["host"])
        del tags["host"]
    elif output_tstore.config.USE_HOST_AS_METRIC_NAME and "host" not in tags:
        logger.tdebug("Host tag not found, using default measurement name")

    # everybody treats tags as Labels
    for tag, value in tags.items():
        labels = add_labels(sanitize_string(tag), sanitize_string(value), labels)
        
    #we create a sample for EACH field
    #if not output_tstore.config.TREAT_FIELDS_AS_LABELS:
    for field, value in fields.items():

        current_labels = labels

        if output_tstore.config.USE_HOST_AS_METRIC_NAME or output_tstore.config.METRIC_NAME:

            metric_name = metric

            if sanitize_string(field) == "value":
                current_labels = add_labels("metric", telegraf_metric_name, current_labels)
            else:
                current_labels = add_labels("metric", f"{telegraf_metric_name}_{sanitize_string(field)}", current_labels)


        else:

            if sanitize_string(field) == "value":
                metric_name = metric
            else:
                metric_name = f"{metric}_{sanitize_string(field)}"

        await output_tstore.enqueue_data(metric_name, value, ts, current_labels, output_tstore.config.get_tz())

    # #We treat the fields as additional labels
    # Chat with michael on15 may 24, just treat it as a lookup if it has a value and a timestamp.
    # else:
    #     for field, value in fields.items():
    #         current_labels = add_labels(sanitize_string(field), sanitize_string(value), labels)
    #         await output_tstore.enqueue_data(measurement, value, ts, current_labels, output_tstore.config.get_tz())

    

async def read_stdin_async(output_tstore):
    loop = asyncio.get_event_loop()

    while True:
        # Read a line from stdin using run_in_executor
        line = await loop.run_in_executor(None, sys.stdin.readline)
        if not line:
            sys.exit(0)
            # If stdin is closed, exit loop

        await process_line(line.strip(), output_tstore)

async def run_all():
    config = OutputTstoreSettings()
    output_tstore = OutputTStore(config)
    set_log_level(TRANSPARA_DEBUG_LEVEL)
    await asyncio.gather(
            read_stdin_async(output_tstore),
            output_tstore.send_data_loop(),
    )


# def get_metrics():
#     metrics = {
#         "name": "system",
#         "tags": {
#             "host": "server01"
#         },
#         "fields": {
#             "cpu_usage": 23.5,
#             "mem_total": 2048,
#             "mem_used": 1024,
#             "disk_total": 500000,
#             "disk_used": 250000
#         },
#         "timestamp": int(time.time())
#     }
#     return metrics


# def test_line():
#     output_tstore = OutputTStore(BaseConfig())
#     asyncio.run(process_line(json.dumps(get_metrics()), output_tstore))
#     assert output_tstore.q.qsize() == 5


if __name__ == "__main__":
    #test_line()
    if sys.platform == 'win32':
        from dotenv import load_dotenv
        #import os
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy()) 
        load_dotenv()
        #script_dir = os.path.dirname(os.path.abspath(__file__))
        #os.chdir(script_dir)
        #print(f"Current working directory: {os.getcwd()}")

    asyncio.run(run_all())


