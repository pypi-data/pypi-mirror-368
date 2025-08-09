from logger_protocol import SilentLogger


def test_silent_logger_methods_do_nothing(caplog):
    logger = SilentLogger()

    assert logger.debug("msg") is None
    assert logger.info("msg", 123) is None
    assert logger.warning("msg", key="value") is None
    assert logger.error() is None
    assert logger.critical(1, 2, 3) is None

    assert caplog.records == []
