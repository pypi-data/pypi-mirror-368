"""
File with custom logger class for your small console app
"""

import logging
from datetime import datetime
from typing import TextIO


class BotLogger:
    """
    Custom logger class for telegram bot / Locust test and С+ web doc, and now for C+ dependencies manager.
    """

    __log_file: TextIO  # file for logs
    __logger: logging.Logger  # private instance of composite logger
    __is_file_write: bool  # is need write to file
    __is_logging: bool  # do you need logging or not
    __log_file_name: str  # name of the log file

    def __init__(self, name: str = 'simple_logger', is_file_write: bool = False, is_on: bool = True):
        self.__logger = logging.getLogger(name)
        self.__is_logging = is_on
        if is_file_write:
            self.__is_file_write = True
            self.__get_log_file()
        else:
            self.__is_file_write = False

    def log(self, msg: str, level: int = 1, stacklevel: int = 1):
        """
        Method for writing logs
        :param msg: message to be written
        :param level: level of logging, 1 by default
        :param stacklevel: level of the stack
        :return: None
        """
        try:
            if self.__is_logging:
                formated_msg = f"{(datetime.now())}: '{msg}'."
                if self.__is_file_write:
                    self.__log_file.write(formated_msg)
                    self.__logger.log(msg=formated_msg, stacklevel=stacklevel, level=level)
                    print(formated_msg)
                else:
                    self.__logger.log(msg=formated_msg, stacklevel=stacklevel, level=level)
                    print(formated_msg)
            else:
                pass  # simple pass instruction for pass if you do not want logging in your small console app
        except Exception as e:
            print(f"Error occurred while writing log file - {e}")

    def __get_log_file(self):
        """
        Creates log file for bot actions
        :return: None
        """
        try:
            self.__log_file = open(self.__log_file_name)
        except Exception as e:
            print(f"{(datetime.now())}: Exception occurred in logger - {e}.")
            self.__log_file.close()

    def __close_log_file(self):
        """
        Closes log file
        :return: None
        """
        try:
            self.__log_file.close()
        except Exception as e:
            print(f"{(datetime.now())}: Error in closing log file - {e}.")

    def is_file_write(self):
        """
        Method for is writing info
        :return: bool value
        """
        return self.__is_file_write

    def get_log_file(self):
        """
        Method for getting log file descriptor
        :return:
        """
        return self.__log_file

    def set_log_file_name(self, log_file_name: str):
        """
        Setter method for logger file name
        :return: None
        """
        self.__log_file_name = log_file_name