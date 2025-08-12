from pydantic import BaseModel
from pydantic_settings import SettingsConfigDict, BaseSettings
from typing import Any, Optional, Union, get_args
from transpara import tlogging
from transpara.tlogging import TRANSPARA_DEBUG_LEVEL
from os import getenv
import requests
import pytz
from datetime import datetime
from transpara.internal.utils import urljoin
#Setting verbose logging, once we get settings from tSystem we can set the actual value
tlogging.set_log_level(TRANSPARA_DEBUG_LEVEL)
logger = tlogging.get_logger(__name__)

class BaseRequiredSettings(BaseSettings):
    TSYSTEM_HOST: str = "tsystem_api"
    ALLOW_OFFLINE: bool = True
    IMAGE_TAG: str =  "0.0.0"
    VERSION: str = "0.0.6"
    COMPONENT_ID: str = "049f6ed7-e754-4315-bdc6-bf5ed6e4d437"
    TSYSTEM_COMPONENT_TYPE: str = "tgraphs"
    model_config = SettingsConfigDict(case_sensitive=True)

required_settings = BaseRequiredSettings()

class BaseTSystemSettings(BaseModel):    

    LOG_LEVEL: Optional[Union[str,int]] = TRANSPARA_DEBUG_LEVEL
    LOG_GLOBAL_VERBOSE: Optional[bool] = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.load_settings()


    def __env_to_bool(self, v: Any) -> bool:    
        if isinstance(v, bool):
            return v
        if isinstance(v, str):
            return v.lower() in ("yes", "true", "t", "1")
        return bool(v)

    def __env_to_int(self, v: Any) -> bool:    
        try:
            return int(v)
        except:
            return v
        
    def __env_to_float(self, v: Any) -> bool:
        try:
            return float(v)
        except:
            return v

    def load_settings(self):
        try:
            timeout = float(getenv("TSYSTEM_SETTINGS_TIMEOUT", 1))
            response = requests.get(f"http://{required_settings.TSYSTEM_HOST}/{required_settings.TSYSTEM_COMPONENT_TYPE}/{required_settings.COMPONENT_ID}", timeout=timeout)
            response.raise_for_status()
            settings: dict = response.json()["settings"]
            for key, value in settings.items():
                if hasattr(self, key): 
                    setattr(self, key, value)
        except:
        
            logger.terror(f"Failed to get settings from tSystem")

            if not required_settings.ALLOW_OFFLINE:
                logger.terror("Can't get settings from tSystem, and it is not allowed to run offline")
                raise
        
            logger.tdebug("Running offline, using settings from env")
            self.load_from_env()

    def load_from_env(self):
        for key, field in self.model_fields.items():
            try:
                value = getenv(key)
                
                types = get_args(field.annotation) or [field.annotation]

                if value is None:
                    continue
                
                if bool in types:
                    setattr(self, key, self.__env_to_bool(value))
                elif int in types:
                    setattr(self, key, self.__env_to_int(value))
                elif float in types:
                    setattr(self, key, self.__env_to_float(value))
                else:
                    setattr(self, key, value)
            except:
                logger.warning(f"Failed to load {key} from env and tSystem, falling back to {field.default}")

class OutputTstoreSettings(BaseTSystemSettings, BaseRequiredSettings):
    TSTORE_API_URL: Optional[str]
    TSTORE_FLUSH_SIZE: int = 50
    OUTPUT_BATCH_SIZE: int = 5
    TSTORE_FLUSH_INTERVAL_SECONDS: Optional[int] = 10
    SOURCE_TZ: str
    LOG_ENQUEUING: bool = False

    #USED on the telegraf mode
    USE_HOST_AS_METRIC_NAME: Optional[bool] = False
    METRIC_NAME: Optional[str] = None

    def get_tz(self) -> pytz.timezone:
        return pytz.timezone(self.SOURCE_TZ)

    def get_write_endpoint(self) -> str:
        return urljoin(self.TSTORE_API_URL, 'api/v1/write/write-data?overwrite_data=true')

class BaseExtractorSettings(OutputTstoreSettings):

    EXTRACTOR_PREFIX: Optional[str]
    CYCLE_SECONDS: Optional[int] = 30
    LOOKBACK_SECONDS: Optional[int] = 1800
    RECOVERY_LOOKBACK_SECONDS: Optional[int] = 0
    MAX_RANGE_PER_REQUEST_SECONDS: Optional[int] = 86400
    BACKFILL_START_TIME: str = "2021-01-01T00:00:00Z"
    BACKFILL_END_TIME: Optional[str] = None
    BACKFILL: bool = False
    #TREAT_FIELDS_AS_LABELS: bool = False

    def get_backfill_start_date(self) -> datetime:
        date = datetime.fromisoformat(self.BACKFILL_START_TIME)
        tz = self.get_tz()
        date = tz.localize(date)
        return date 
    
    def get_backfill_end_date(self) -> Optional[datetime]:
        if not self.BACKFILL_END_TIME:
            return None
        date = datetime.fromisoformat(self.BACKFILL_END_TIME)
        tz = self.get_tz()
        date = tz.localize(date)
        return date

base_tsystem_settings = BaseTSystemSettings()

tlogging.set_log_level(base_tsystem_settings.LOG_LEVEL)
tlogging.set_global_verbose(base_tsystem_settings.LOG_GLOBAL_VERBOSE)