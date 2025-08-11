import logging, json
from collections.abc import Iterable
from colorama import Fore, Back, Style

class ColorfulFormatter(logging.Formatter):

    format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    FORMATS = {
        logging.DEBUG: Style.RESET_ALL + Style.DIM + "%(asctime)s - %(name)s - " + Style.RESET_ALL + Fore.BLUE + Back.WHITE + " %(levelname)s " + Style.RESET_ALL + Fore.CYAN + " - %(message)s",
        logging.INFO: Style.RESET_ALL + Style.DIM + "%(asctime)s - %(name)s - " + Style.RESET_ALL + Fore.YELLOW + Back.BLUE + Style.BRIGHT + " %(levelname)s " + Style.RESET_ALL + Fore.GREEN + " - %(message)s",
        logging.WARNING: Style.RESET_ALL + Style.DIM + "%(asctime)s - %(name)s - " + Style.RESET_ALL + Fore.BLUE + Back.YELLOW + " %(levelname)s " + Style.RESET_ALL + Fore.YELLOW + " - %(message)s",
        logging.ERROR: Style.RESET_ALL + Style.DIM + "%(asctime)s - %(name)s - " + Style.RESET_ALL + Fore.WHITE + Back.RED + Style.BRIGHT + " %(levelname)s " + Style.RESET_ALL + Fore.RED + Style.BRIGHT + " - %(message)s",
        logging.CRITICAL: Style.RESET_ALL + Style.DIM + "%(asctime)s - %(name)s - " + Style.RESET_ALL + Fore.WHITE + Back.RED + Style.BRIGHT + " %(levelname)s " + Style.RESET_ALL + Fore.RED + Style.BRIGHT + " - %(message)s",
    }

    def format(self, record):
        if isinstance(record.msg, Iterable) and not isinstance(record.msg, str):
            record.msg = json.dumps(record.msg, indent=4, ensure_ascii=False)
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)