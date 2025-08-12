import ast
from contextlib import nullcontext
import functools
from typing import Any, Callable, Optional

import jsonpickle
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace import NonRecordingSpan, SpanContext, TraceFlags

__TRACE_ID_HEADER_NAME = "x-trace-id"
__SPAN_ID_HEADER_NAME = "x-span-id"
__EXPORT_ARGUMENTS = False
__EXPORT_TRACES = False

def start_span(span_name:str, trace_id_req, span_id_req):
    
    def create_context(trace_id_req, span_id_req):
        ctx = None
        if trace_id_req and span_id_req:
            try:
                """convert back to number from hex"""
                trace_id_req = ast.literal_eval("0x" + trace_id_req)
                span_id_req = ast.literal_eval("0x" + span_id_req)
                span_context = SpanContext(trace_id=trace_id_req, span_id = span_id_req, is_remote=True, trace_flags=TraceFlags(0x01))
                ctx = trace.set_span_in_context(NonRecordingSpan(span_context))
            except: pass
        return ctx

    ctx = create_context(trace_id_req, span_id_req)
    span = trace.get_tracer(__name__).start_as_current_span(str(span_name), context=ctx)
    return span

def get_span_from_ctx(trace_ctx, name):

    if not __EXPORT_TRACES:
        return nullcontext()

    return start_span(name, trace_ctx.get(__TRACE_ID_HEADER_NAME, None), trace_ctx.get(__SPAN_ID_HEADER_NAME, None))

def __configure_fastapi(tracer_provider, fastapi_app=None):
    if not fastapi_app:
        return

    @fastapi_app.middleware("http")
    async def add_trace_id_header(request, call_next):
        #request:Request
        if not __EXPORT_TRACES:
            """At this point the middleware does nothing"""
            return await call_next(request)

        trace_id_req = request.headers.get(__TRACE_ID_HEADER_NAME, None)
        span_id_req = request.headers.get(__SPAN_ID_HEADER_NAME, None)
        span = start_span(request.url, trace_id_req, span_id_req)
        with span:
            trace_id = trace.get_current_span().get_span_context().trace_id
            response = await call_next(request)
            response.headers[__TRACE_ID_HEADER_NAME] = format(trace_id, 'x')
            response.headers[__SPAN_ID_HEADER_NAME] = format(trace.get_current_span().get_span_context().span_id, 'x')
            return response

def get_current_trace_id():
    ctx = get_context()
    if ctx and __TRACE_ID_HEADER_NAME in ctx:
        trace_id = ctx[__TRACE_ID_HEADER_NAME]
        if trace_id and trace_id != "0":
            return trace_id
    return None

def get_context():
    result = {}
    ctx = trace.get_current_span().get_span_context()
    result[__TRACE_ID_HEADER_NAME] = format(ctx.trace_id, 'x')
    result[__SPAN_ID_HEADER_NAME] = format(ctx.span_id, 'x') 
    return result

def set_export_traces(export_traces:bool):
    global __EXPORT_TRACES
    __EXPORT_TRACES = export_traces

def set_export_arguments(export_arguments:bool):
    global __EXPORT_ARGUMENTS
    __EXPORT_ARGUMENTS = export_arguments


def init(
    trace_host="tstore_tscale", 
    trace_port="9202", 
    export_traces:bool=False, 
    export_arguments:bool=False, 
    service_name:str="Not Set", 
    fastapi_app:Optional[Any]=None
):
    """
    Example instantiation
    if settings.EXPORT_TRACES:
        trace_helper.init(
            trace_host=settings.OTEL_EXPORTER_HOST, 
            trace_port=settings.OTEL_EXPORTER_PORT,
            export_traces=settings.EXPORT_TRACES, 
            export_arguments=settings.EXPORT_TRACE_ARGS,
            service_name=f"tcore-api-{settings.TCORE_ID}", 
            fastapi_app=app
        )
    """
    set_export_traces(export_traces)
    set_export_arguments(export_arguments)
    tracer_provider = TracerProvider(resource=Resource.create({"service.name": service_name}))
    trace.set_tracer_provider(tracer_provider)
    processor = BatchSpanProcessor(OTLPSpanExporter(f"http://{trace_host}:{trace_port}"))
    trace.get_tracer_provider().add_span_processor(processor)
    __configure_fastapi(tracer_provider, fastapi_app)


#decorators
def traced(name: str=None, include_args:bool=False) -> Callable:

    def decorator(func: Callable):

        @functools.wraps(func)
        def wraps(*args, **kwargs):

            if not __EXPORT_TRACES:
                """At this point the decorator does nothing"""
                return func(*args, **kwargs)

            span_name = func.__name__ if not name else name
            span = trace.get_tracer(func.__module__).start_as_current_span(span_name)

            with span:
                include_arguments = include_args or __EXPORT_ARGUMENTS
                if include_arguments: 
                    attributes = {}
                    for idx, arg in enumerate(args):
                        try: 
                            attributes[f"arg {idx}"] = jsonpickle.encode(arg) 
                        except: pass
                    
                    for key, value in kwargs.items():
                        try: 
                            attributes[jsonpickle.encode(key)] = jsonpickle.encode(value)
                        except: pass

                    trace.get_current_span().add_event("Function Parameters", attributes=attributes)
                return func(*args, **kwargs)

        return wraps

    return decorator

def traced_async(name: str=None, include_args:bool=False) -> Callable:

    def decorator(func: Callable):

        @functools.wraps(func)
        async def wraps(*args, **kwargs):

            if not __EXPORT_TRACES:
                """At this point the decorator does nothing"""
                return await func(*args, **kwargs)

            span_name = func.__name__ if  not name else name
            span = trace.get_tracer(func.__module__).start_as_current_span(span_name)       

            with span:
                include_arguments = include_args or __EXPORT_ARGUMENTS
                if include_arguments: 
                    attributes = {}
                    for idx, arg in enumerate(args):
                        try: 
                            attributes[f"arg {idx}"] = jsonpickle.encode(arg) 
                        except: pass
                    
                    for key, value in kwargs.items():
                        try: 
                            attributes[jsonpickle.encode(key)] = jsonpickle.encode(value)
                        except: pass

                    trace.get_current_span().add_event("Function Parameters", attributes=attributes)
                return await func(*args, **kwargs)

        return wraps

    return decorator