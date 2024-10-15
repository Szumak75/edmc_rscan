# -*- coding: UTF-8 -*-
"""
  edrs.py
  Author : Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
  Created: 14.01.2024, 13:31:32
  
  Purpose: EDRS main class module.
"""

from queue import SimpleQueue
from threading import Thread


from rscan.jsktoolbox.attribtool import ReadOnlyClass
from rscan.jsktoolbox.edmctool.base import BLogClient, BLogProcessor
from rscan.jsktoolbox.edmctool.logs import LogClient, LogProcessor
from rscan.jsktoolbox.edmctool.data import RscanData
from rscan.dialogs import EdrsDialog


class _Keys(object, metaclass=ReadOnlyClass):
    """Keys for EDRS class."""

    R_DATA: str = "__r_data__"
    R_DIALOG: str = "__r_dialog__"


class EDRS(BLogProcessor, BLogClient):
    """edrs_object main class."""

    def __init__(self) -> None:
        """Initialize main class."""
        # data
        self._set_data(key=_Keys.R_DATA, value=RscanData(), set_default_type=RscanData)

        self.data.plugin_name = "EDRS"
        self.data.version = "0.2.19"

        # logging subsystem
        self.qlog = SimpleQueue()
        self.log_processor = LogProcessor(self.data.plugin_name)
        self.logger = LogClient(self.qlog)

        # logging thread
        self.th_log = Thread(
            target=self.th_logger, name=f"{self.data.plugin_name} log worker"
        )
        self.th_log.daemon = True
        self.th_log.start()

        self.logger.debug = f"{self.data.plugin_name} object creation complete."

    @property
    def dialog(self) -> EdrsDialog:
        """Return dialog access."""
        return self._get_data(key=_Keys.R_DIALOG, default_value=None)  # type: ignore

    @dialog.setter
    def dialog(self, value: EdrsDialog) -> None:
        """Set dialog access."""
        self._set_data(key=_Keys.R_DIALOG, value=value, set_default_type=EdrsDialog)

    @property
    def data(self) -> RscanData:
        """Give me data access."""
        return self._get_data(
            key=_Keys.R_DATA,
        )  # type: ignore

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
