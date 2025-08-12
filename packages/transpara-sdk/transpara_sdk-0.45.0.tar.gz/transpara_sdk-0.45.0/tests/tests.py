from transpara import tlogging
from transpara.tlogging import get_logger, GREY, BLUE, RESET_COLOR, logd, logd_async


#region setup
@logd(suppress_exc=True)
def raise_suppressed():
    raise Exception("I was suppressed")

@logd(suppress_exc=True, suppressed_return_value=0)
def raise_suppressed_def():
    raise Exception("I was suppressed")
#endregion

#region tests
def test_logger():
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

def test_suppress():
    assert raise_suppressed() == "Exception: I was suppressed"

def test_suppress_default():
    assert raise_suppressed_def() == 0
#endregion



