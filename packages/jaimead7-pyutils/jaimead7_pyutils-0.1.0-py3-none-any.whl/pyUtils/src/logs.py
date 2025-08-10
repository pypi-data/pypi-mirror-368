import logging

class Styles:
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    DEBUG = '\033[0m'
    INFO = '\033[94m'
    WARNING = '\033[93m'
    ERROR = '\033[91m'
    CRITICAL = '\033[101m'
    SUCCEED = '\033[92m'
    PURPLE = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'


class _MyFormatter(logging.Formatter):
    CUSTOM_STYLE_NAME = 'custom_style'

    def format(self, record) -> str:
        if hasattr(record, self.CUSTOM_STYLE_NAME):
            custom_style: str = getattr(record, self.CUSTOM_STYLE_NAME)
        else:
            custom_style: str = Styles.ENDC
        arrow: str = '-' * (30 - len(record.levelname + f"[{record.name}]")) + '>'
        log_fmt: str = f'{custom_style}{record.levelname}[{record.name}] {arrow} %(asctime)s:{Styles.ENDC} {record.msg}'
        formatter = logging.Formatter(log_fmt, datefmt='%d/%m/%Y %H:%M:%S')
        return formatter.format(record)


class MyLogger():
    def __init__(
        self,
        logger_name: str,
        logging_level: int = logging.DEBUG
    ) -> None:
        if logger_name not in logging.Logger.manager.loggerDict.keys():
            self._logger: logging.Logger = logging.getLogger(logger_name)
            self.set_logging_level(logging_level)
            _stream_handler: logging.StreamHandler  = logging.StreamHandler()
            _stream_handler.setFormatter(_MyFormatter())
            self._logger.addHandler(_stream_handler)
        else:
            self._logger: logging.Logger = logging.getLogger(logger_name)
            self.set_logging_level(logging_level)

    def set_logging_level(self, lvl: int = logging.DEBUG) -> None:
        self._logger.setLevel(lvl)

    def debug(self, msg: str, style: str = Styles.DEBUG) -> None:
        self._logger.debug(
            f'{msg}',
            extra= {_MyFormatter.CUSTOM_STYLE_NAME: style}
        )

    def info(self, msg: str, style: str = Styles.INFO) -> None:
        self._logger.info(
            f'{msg}',
            extra= {_MyFormatter.CUSTOM_STYLE_NAME: style}
        )

    def warning(self, msg: str, style: str = Styles.WARNING) -> None:
        self._logger.warning(
            f'{msg}',
            extra= {_MyFormatter.CUSTOM_STYLE_NAME: style}
        )

    def error(self, msg: str, style: str = Styles.ERROR) -> None:
        self._logger.error(
            f'{msg}',
            extra= {_MyFormatter.CUSTOM_STYLE_NAME: style}
        )

    def critical(self, msg: str, style: str = Styles.CRITICAL) -> None:
        self._logger.critical(
            f'{msg}',
            extra= {_MyFormatter.CUSTOM_STYLE_NAME: style}
        )

    @staticmethod
    def get_lvl_int(lvl_str: str) -> int:
        lvls: dict[str, int] = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR,
            'CRITICA': logging.CRITICAL,
        }
        try:
            return lvls[lvl_str.upper()]
        except KeyError:
            return logging.DEBUG
