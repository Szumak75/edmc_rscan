# -*- coding: UTF-8 -*-
"""
  Author:  Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
  Created: 19.12.2023

  Purpose: main class
"""

from inspect import currentframe
from queue import Queue
from threading import Thread
from typing import Optional

from jsktoolbox.raisetool import Raise

from rscan_libs.data import RscanData
from rscan_libs.base_logs import BLogClient, BLogProcessor
from rscan_libs.system import LogProcessor, LogClient
from rscan_libs.dialogs import EdrsDialog


class EDRS(BLogProcessor, BLogClient):
    """edrs_object main class."""

    def __init__(self):
        """Initialize main class."""
        # data
        self.data = RscanData()

        self.data.pluginname = "EDRS"
        self.data.version = "1.0.0"

        # logging subsystem
        self.qlog = Queue()
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
    def dialog(self) -> Optional[EdrsDialog]:
        """Give me data access."""
        if "dialog" not in self._data:
            self._data["dialog"] = None
        return self._data["dialog"]

    @dialog.setter
    def dialog(self, value: EdrsDialog):
        if isinstance(value, EdrsDialog):
            self._data["dialog"] = value
        else:
            raise Raise.error(
                f"EdrsDialog type expected, '{type(value)} received.'",
                TypeError,
                self._c_name,
                currentframe(),
            )

    @property
    def data(self) -> Optional[RscanData]:
        """Give me data access."""
        if "rscan" not in self._data:
            self._data["rscan"] = None
        return self._data["rscan"]

    @data.setter
    def data(self, value: RscanData) -> None:
        if isinstance(value, RscanData):
            self._data["rscan"] = value
        else:
            raise Raise.error(
                f"RscanData type expected, '{type(value)} received.'",
                TypeError,
                self._c_name,
                currentframe(),
            )

    def th_logger(self) -> None:
        """Def th_logger - thread logs processor."""
        self.logger.info = "Starting logger worker"
        if "rscan" not in self._data:
            return
        while not self.data.shutting_down:
            while True:
                log = self.qlog.get(True)
                if log is None:
                    break
                self.log_processor.send(log)


# #[EOF]#######################################################################
