# -*- coding: UTF-8 -*-
"""
  Author:  Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
  Created: 18.12.2023

  Purpose: base classes for logs subsystem.
"""

from inspect import currentframe
from typing import Optional
from queue import Queue

from jsktoolbox.attribtool import ReadOnlyClass
from jsktoolbox.raisetool import Raise
from jsktoolbox.libs.base_data import BData


class _Keys(object, metaclass=ReadOnlyClass):
    """Keys container class.

    For internal use only.
    """

    LOGGER = "__logger_client__"
    LPENGINE = "__engine__"
    LQUEUE = "__logger_queue__"
    THLOGGER = "__th_logger__"


class BLogProcessor(BData):
    """BLogProcessor base class.

    Container for logger processor methods.
    """

    @property
    def thlog(self) -> Optional[object]:
        """Give me thread logger handler."""
        if _Keys.THLOGGER not in self._data:
            self._data[_Keys.THLOGGER] = None
        return self._data[_Keys.THLOGGER]

    @thlog.setter
    def thlog(self, value: object) -> None:
        self._data[_Keys.THLOGGER] = value

    @property
    def qlog(self) -> Optional[Queue]:
        """Give me access to queue handler."""
        if _Keys.LQUEUE not in self._data:
            self._data[_Keys.LQUEUE] = None
        return self._data[_Keys.LQUEUE]

    @qlog.setter
    def qlog(self, value: Queue) -> None:
        """Setter for logging queue."""
        if not isinstance(value, Queue):
            raise Raise.error(
                f"Expected Queue type, received: '{type(value)}'",
                TypeError,
                self._c_name,
                currentframe(),
            )
        self._data[_Keys.LQUEUE] = value

    @property
    def log_processor(self) -> Optional[object]:
        """Give me handler for log processor."""
        if _Keys.LPENGINE not in self._data:
            self._data[_Keys.LPENGINE] = None
        return self._data[_Keys.LPENGINE]

    @log_processor.setter
    def log_processor(self, value: object) -> None:
        """Setter for log processor instance."""
        self._data[_Keys.LPENGINE] = value


class BLogClient(BData):
    """BLogClass base class.

    Container for logger methods.
    """

    @property
    def logger(self) -> Optional[object]:
        """Give me logger handler."""
        if _Keys.LOGGER not in self._data:
            self._data[_Keys.LOGGER] = None
        return self._data[_Keys.LOGGER]

    @logger.setter
    def logger(self, arg: object) -> None:
        """Set logger instance."""
        self._data[_Keys.LOGGER] = arg


# #[EOF]#######################################################################
