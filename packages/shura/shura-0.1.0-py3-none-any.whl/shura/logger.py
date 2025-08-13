import logging
import sys
from colorama import Fore, Style, init as colorama_init

colorama_init(autoreset=True)

class ShuraFormatter(logging.Formatter):
    COLORS = {
        'DEBUG': Fore.CYAN,
        'INFO': Fore.GREEN,
        'WARNING': Fore.YELLOW,
        'ERROR': Fore.RED,
        'CRITICAL': Fore.MAGENTA,
    }

    def format(self, record):
        color = self.COLORS.get(record.levelname, "")
        reset = Style.RESET_ALL
        fmt = f"{color}[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s{reset}"
        formatter = logging.Formatter(fmt, datefmt="%Y-%m-%d %H:%M:%S")
        return formatter.format(record)

def get_logger(name="shura", level=logging.DEBUG, to_file=False, filename="shura.log"):
    logger = logging.getLogger(name)
    logger.setLevel(level)

    if not logger.handlers:
        # Console handler with colors
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setFormatter(ShuraFormatter())
        logger.addHandler(stream_handler)

        # Optional file dumping
        if to_file:
            file_handler = logging.FileHandler(filename)
            file_handler.setFormatter(logging.Formatter(
                "[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S"
            ))
            logger.addHandler(file_handler)

    return logger
