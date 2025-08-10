import logging

from pytest import LogCaptureFixture, fixture, mark

from ..src.logs import MyLogger

LOGGER_NAME = 'TestLogger'

@fixture(autouse= True)
def setCaplogLvl(caplog: LogCaptureFixture) -> None:
    caplog.set_level(logging.DEBUG)
    caplog.clear()

@fixture()
def my_logger() -> MyLogger:
    return MyLogger(LOGGER_NAME, logging.DEBUG)


class TestLogs:
    @mark.parametrize('msg', [
        'Debug test message',
    ])
    def test_debug(
        self,
        msg: str,
        caplog: LogCaptureFixture,
        my_logger: MyLogger
    ) -> None:
        my_logger.debug(msg)
        record: logging.LogRecord = caplog.records[0]
        assert record.message == msg
        assert record.levelno == logging.DEBUG
        assert record.name == LOGGER_NAME

    @mark.parametrize('msg', [
        'Info test message',
    ])
    def test_info(
        self,
        msg: str,
        caplog: LogCaptureFixture,
        my_logger: MyLogger
    ) -> None:
        my_logger.info(msg)
        record: logging.LogRecord = caplog.records[0]
        assert record.message == msg
        assert record.levelno == logging.INFO
        assert record.name == LOGGER_NAME

    @mark.parametrize('msg', [
        'Warning test message',
    ])
    def test_warning(
        self,
        msg: str,
        caplog: LogCaptureFixture,
        my_logger: MyLogger
    ) -> None:
        my_logger.warning(msg)
        record: logging.LogRecord = caplog.records[0]
        assert record.message == msg
        assert record.levelno == logging.WARNING
        assert record.name == LOGGER_NAME

    @mark.parametrize('msg', [
        'Error test message',
    ])
    def test_error(
        self,
        msg: str,
        caplog: LogCaptureFixture,
        my_logger: MyLogger
    ) -> None:
        my_logger.error(msg)
        record: logging.LogRecord = caplog.records[0]
        assert record.message == msg
        assert record.levelno == logging.ERROR
        assert record.name == LOGGER_NAME

    @mark.parametrize('msg', [
        'Critical test message',
    ])
    def test_critical(
        self,
        msg: str,
        caplog: LogCaptureFixture,
        my_logger: MyLogger
    ) -> None:
        my_logger.critical(msg)
        record: logging.LogRecord = caplog.records[0]
        assert record.message == msg
        assert record.levelno == logging.CRITICAL
        assert record.name == LOGGER_NAME

    @mark.parametrize('lvl, nMessages', [
        (logging.DEBUG, 5),
        (logging.INFO, 4),
        (logging.WARNING, 3),
        (logging.ERROR, 2),
        (logging.CRITICAL, 1),
    ])
    def test_set_logging_level(
        self,
        lvl: int,
        nMessages: int, 
        caplog: LogCaptureFixture,
        my_logger: MyLogger
    ) -> None:
        my_logger.set_logging_level(lvl)
        my_logger.debug('Debug test message')
        my_logger.info('Info test message')
        my_logger.warning('Warning test message')
        my_logger.error('Error test message')
        my_logger.critical('Critical test message')
        assert len(caplog.records) == nMessages
