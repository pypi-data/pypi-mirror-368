# transpara-py-sdk
installation 


pip3 install transpara-py-sdk==0.19.0

https://github.com/transpara/transpara-py-sdk/blob/main/tests/tests.py

If you are upgrading from a version prior to 0.14.0 there will be breaking changes:
The breaking changes can be fixed by replacing the following:   

    transpara_logging with tlogging
    transpara.middlewares with transpara.tlogging
    log_middleware with logd


Import tracing & use trace decorator

    from transpara.tracing import traced, traced_async
    from transpara import tracing

    if settings.EXPORT_TRACES:
    tracing.init(
        trace_host=settings.OTEL_EXPORTER_HOST, 
        trace_port=settings.OTEL_EXPORTER_PORT,
        export_traces=settings.EXPORT_TRACES, 
        export_arguments=settings.EXPORT_TRACE_ARGS,
        service_name=f"tcore-api-{settings.TCORE_ID}", 
        fastapi_app=app #can be none if this is not a fastapi app
    )

    @router.get("/startup-information")
    @traced_async()
    async def startup_information(mg:MGOperations = Depends(get_mg)):
        method....body....
        
Import logger & use logger:

    from transpara.tlogging import get_logger, GREY, BLUE, RESET_COLOR, logd, logd_async
    from transpara import tlogging

    tlogging.set_log_level(tlogging.TRANSPARA_DEBUG_LEVEL)
    logger = get_logger(__name__)

    logger.terror("t err")
    logger.tdebug("tdebugging something")
    logger.info("regular info")

    tlogging.set_default_format(f"{GREY}%(message)s")
    logger.info("regular info grey format")

    tlogging.set_default_format(f"{BLUE}%(message)s")
    logger.info("regular info blue format")

    tlogging.set_default_format(f"{RESET_COLOR}%(message)s")
    logger.info("reset")

Import logging decorators 
    from transpara.tlogging import logd, logd_async, elapsed, elapsed_async

    @logd(suppress_exc=True)
    def raise_suppressed():
        raise Exception("I was suppressed")

    @logd(suppress_exc=True, suppressed_return_value=0)
    def raise_suppressed_def():
        raise Exception("I was suppressed")

    @logd()
    def testone():
        raise Exception()

    @elapsed()
    def testone():
        raise Exception()
