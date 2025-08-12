# logger_config.py
import logging

from colorama import init, Fore, Style

init(autoreset=True)


class AddWorkerFilter(logging.Filter):
    """Гарантированно добавляет поле `worker` в каждый LogRecord."""

    def filter(self, record):
        if not hasattr(record, 'worker'):
            # по умолчанию помечаем главный процесс
            record.worker = -1
        return True


class ColorFormatter(logging.Formatter):
    LEVEL_COLORS = {
        logging.DEBUG: Fore.CYAN,
        logging.INFO: Fore.LIGHTGREEN_EX,
        logging.WARNING: Fore.YELLOW,
        logging.ERROR: Fore.RED,
        logging.CRITICAL: Fore.MAGENTA,
    }

    def format(self, record):
        color = self.LEVEL_COLORS.get(record.levelno, "")
        message = super().format(record)
        return f"{color}{message}{Style.RESET_ALL}"


def setup_logger(name: str = None) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        handler = logging.StreamHandler()

        # Добавляем фильтр, чтобы везде было поле worker
        handler.addFilter(AddWorkerFilter())

        fmt = (
            "[%(asctime)s][PID=%(process)d][worker-%(worker)d] "
            "%(levelname)s — %(message)s"
        )
        formatter = ColorFormatter(fmt, datefmt="%Y-%m-%d %H:%M:%S")
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    # Настройка стороннего логгера
    external_logger = logging.getLogger("evergreenlib.parsers.exceldata")
    external_logger.setLevel(logging.INFO)
    external_logger.handlers = logger.handlers
    external_logger.propagate = False

    return logger
