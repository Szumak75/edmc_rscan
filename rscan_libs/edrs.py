# -*- coding: UTF-8 -*-
"""
  edrs.py
  Author : Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
  Created: 14.01.2024, 13:31:32
  
  Purpose: EDRS main class module.
"""


from rscan_libs.base_log import BLogClient, BLogProcessor
from rscan_libs.data import RscanData
from rscan_libs.dialogs import EdrsDialog
from rscan_libs.system import LogClient, LogProcessor


from jsktoolbox.attribtool import NoDynamicAttributes
from jsktoolbox.raisetool import Raise


import inspect
from queue import SimpleQueue
from threading import Thread


class EDRS(BLogProcessor, BLogClient, NoDynamicAttributes):
    """edrs_object main class."""

    __data: RscanData = None  # type: ignore
    __dialog: EdrsDialog = None  # type: ignore

    def __init__(self) -> None:
        """Initialize main class."""
        # data
        self.data = RscanData()

        self.data.pluginname = "EDRS"
        self.data.version = "0.2.15"

        # logging subsystem
        self.qlog = SimpleQueue()
        self.log_processor = LogProcessor(self.data.pluginname)
        self.logger = LogClient(self.qlog)

        # logging thread
        self.thlog = Thread(
            target=self.th_logger, name=f"{self.data.pluginname} log worker"
        )
        self.thlog.daemon = True
        self.thlog.start()

        self.logger.debug = f"{self.data.pluginname} object creation complete."

    @property
    def dialog(self) -> EdrsDialog:
        """Give me data access."""
        return self.__dialog

    @dialog.setter
    def dialog(self, value) -> None:
        if isinstance(value, EdrsDialog):
            self.__dialog = value
        else:
            raise Raise.error(
                f"EdrsDialog type expected, '{type(value)} received.'",
                TypeError,
                self.__class__.__name__,
                inspect.currentframe(),
            )

    @property
    def data(self) -> RscanData:
        """Give me data access."""
        return self.__data

    @data.setter
    def data(self, value) -> None:
        if isinstance(value, RscanData):
            self.__data = value
        else:
            raise Raise.error(
                f"RscanData type expected, '{type(value)} received.'",
                TypeError,
                self.__class__.__name__,
                inspect.currentframe(),
            )

    def th_logger(self) -> None:
        """Def th_logger - thread logs processor."""
        self.logger.info = "Starting logger worker"
        while not self.data.shutting_down:
            while True:
                log = self.qlog.get(True)
                if log is None:
                    break
                self.log_processor.send(log)


# #[EOF]#######################################################################
