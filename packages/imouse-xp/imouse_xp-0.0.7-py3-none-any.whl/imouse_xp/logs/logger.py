import logging
import os
from typing import Optional

import colorlog
import inspect
import threading
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler


_log_level = logging.DEBUG
_is_debug = True
_log_show_file_and_line = False
_log_show_thread_id = False

class Logger:
    _instance = None
    def __new__(cls, name, log_dir=None):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.logger = logging.getLogger(name)
            cls._instance.logger.setLevel(_log_level)
            console_formatter = colorlog.ColoredFormatter(
                '%(log_color)s%(asctime)s.%(msecs)03d[%(levelname)-7s] %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S',
                log_colors={
                    'DEBUG': 'cyan',
                    'INFO': 'green',
                    'WARNING': 'yellow',
                    'ERROR': 'red',
                    'CRITICAL': 'bold_red',
                }
            )
            file_formatter = logging.Formatter(
                '%(asctime)s.%(msecs)03d[%(levelname)-7s] %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(console_formatter)
            cls._instance.logger.addHandler(console_handler)
            if log_dir:
                if not os.path.exists(log_dir):
                    os.makedirs(log_dir)
                log_file = os.path.join(log_dir, name + '.log')
                file_handler = RotatingFileHandler(log_file, maxBytes=10 * 1024 * 1024, backupCount=30)
                file_handler.setFormatter(file_formatter)
                cls._instance.logger.addHandler(file_handler)

                timed_file_handler = TimedRotatingFileHandler(log_file, when='midnight', interval=1, backupCount=30)
                timed_file_handler.setFormatter(file_formatter)
                cls._instance.logger.addHandler(timed_file_handler)

        return cls._instance

    def log(self, level, message):
        frame = inspect.stack()[2]
        # filename = os.path.basename(inspect.getframeinfo(frame[0]).filename)
        filename = inspect.getframeinfo(frame[0]).filename
        lineno = inspect.getframeinfo(frame[0]).lineno
        thread_id = threading.get_ident()
        log_message = "[{}]".format(thread_id) if _log_show_thread_id else ""
        log_message += " [{:<10}:line {:>3}]".format(filename, lineno) if _log_show_file_and_line else ""
        log_message += " {}".format(message)
        if level == "INFO":
            self.logger.info(log_message)
        elif level == "WARNING":
            self.logger.warning(log_message)
        elif level == "ERROR":
            self.logger.error(log_message)
        elif level == "DEBUG":
            self.logger.debug(log_message)
        elif level == "CRITICAL":
            self.logger.critical(log_message)

    def info(self, message):
        self.log("INFO", message)

    def warning(self, message):
        self.log("WARNING", message)

    def error(self, message):
        self.log("ERROR", message)

    def debug(self, message):
        self.log("DEBUG", message)

    def critical(self, message):
        self.log("CRITICAL", message)


def set_log(is_debug:bool=None,log_level:int = None,log_show_file_and_line:bool = None,log_show_thread_id:bool = None):
    global _log_level,_is_debug,_log_show_file_and_line,_log_show_thread_id
    if is_debug is not None:
        _is_debug = is_debug
    if log_level is not None:
        _log_level = log_level
    if log_show_file_and_line is not None:
        _log_show_file_and_line = log_show_file_and_line
    if log_show_thread_id is not None:
        _log_show_thread_id = log_show_thread_id


log: Optional[Logger] = None
def _initialize_logger():
    global log
    log = Logger('imouse_xp', 'logs')

def debug(msg):
    if not _is_debug:
        return
    if log is None:
        _initialize_logger()
    log.debug(f'iMouse调试输出->>>{msg}')


def error(msg):
    if not _is_debug:
        return
    if log is None:
        _initialize_logger()
    log.error(f'iMouse异常输出->>>{msg}')