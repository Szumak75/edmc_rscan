# -*- coding: UTF-8 -*-
"""
Created on 04 jan 2023.

@author: szumak@virthost.pl
"""

from queue import SimpleQueue, Queue
from typing import Union, Any
from jsktoolbox.attribtool import NoDynamicAttributes

from rscan_libs.system import LogClient, LogProcessor


class MLogProcessor(NoDynamicAttributes):
    """MLogProcessor metaclass.

    Container for logger processor methods.
    """

    __logger_queue: Union[Queue, SimpleQueue] = None  # type: ignore
    __log_processor_engine = None
    __thread_logger = None

    @property
    def thlog(self):
        """Give me thread logger handler."""
        return self.__thread_logger

    @thlog.setter
    def thlog(self, value):
        self.__thread_logger = value

    @property
    def qlog(self) -> Union[Queue, SimpleQueue]:  
        """Give me access to queue handler."""
        return self.__logger_queue

    @qlog.setter
    def qlog(self, value):
        """Setter for logging queue."""
        self.__logger_queue = value

    @property
    def log_processor(self):
        """Give me handler for log processor."""
        return self.__log_processor_engine

    @log_processor.setter
    def log_processor(self, value):
        """Setter for log processor instance."""
        self.__log_processor_engine = value


class MLogClient:
    """MLogClass metaclass.

    Container for logger methods.
    """

    __logger: LogClient = None  # type: ignore

    @property
    def logger(self) -> LogClient:
        """Give me logger handler."""
        return self.__logger

    @logger.setter
    def logger(self, arg) -> None:
        """Set logger instance."""
        self.__logger = arg
