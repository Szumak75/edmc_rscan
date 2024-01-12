# -*- coding: UTF-8 -*-
"""
  Author:  Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
  Created: 19.12.2023

  Purpose: plugin entry point.
"""


import inspect
import tkinter as tk
from queue import SimpleQueue
from threading import Thread
from typing import Any, Dict, Optional, Tuple
from attribtool.ndattrib import NoDynamicAttributes
from raisetool.formatter import Raise

from config import config
from rscan_libs.data import RscanData
from rscan_libs.dialogs import EdrsDialog
from rscan_libs.mlog import MLogClient, MLogProcessor
from rscan_libs.system import LogClient, LogLevels, LogProcessor


class EDRS(MLogProcessor, MLogClient, NoDynamicAttributes):
    """edrs_object main class."""

    __data = None
    __dialog = None

    def __init__(self):
        """Initialize main class."""
        # data
        self.data = RscanData()

        self.data.pluginname = "EDRS"
        self.data.version = "0.1.2"

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
    def dialog(self):
        """Give me data access."""
        return self.__dialog

    @dialog.setter
    def dialog(self, value):
        if isinstance(value, EdrsDialog):
            self.__dialog = value
        else:
            raise Raise.type_error(
                self.__class__.__name__,
                inspect.currentframe(),
                f"EdrsDialog type expected, '{type(value)} received.'",
            )

    @property
    def data(self):
        """Give me data access."""
        return self.__data

    @data.setter
    def data(self, value):
        if isinstance(value, RscanData):
            self.__data = value
        else:
            raise Raise.type_error(
                self.__class__.__name__,
                inspect.currentframe(),
                f"RscanData type expected, '{type(value)} received.'",
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


edrs_object = EDRS()


def plugin_start3(plugin_dir: str) -> str:
    """Load plugin into EDMC.

    plugin_dir:     plugin directory
    return:         local name of the plugin
    """
    edrs_object.logger.debug = f"{edrs_object.data.pluginname}->plugin_start3 start..."
    # loglevel set from config
    edrs_object.log_processor.loglevel = LogLevels().get(config.get_str("loglevel"))
    edrs_object.logger.debug = f"{edrs_object.data.pluginname}->plugin_start3 done."
    return f"{edrs_object.data.pluginname}"


def plugin_stop() -> None:
    """Stop plugin if EDMC is closing."""
    edrs_object.logger.debug = f"{edrs_object.data.pluginname}->plugin_stop: start..."
    edrs_object.data.shutting_down = True
    edrs_object.logger.debug = (
        f"{edrs_object.data.pluginname}->plugin_stop: shut down flag is set"
    )
    # something to do
    if edrs_object.dialog is not None:
        edrs_object.dialog.dialog_update()
    # shut down logger at last
    edrs_object.logger.debug = (
        f"{edrs_object.data.pluginname}->plugin_stop: terminating the logger"
    )
    edrs_object.qlog.put(None)
    edrs_object.thlog.join()
    edrs_object.thlog = None


def plugin_app(parent: tk.Frame) -> Tuple[tk.Label, tk.Label]:
    """Create a pair of TK widgets for the EDMarketConnector main window.

    parent:     The root EDMarketConnector window
    """
    edrs_object.logger.debug = f"{edrs_object.data.pluginname}->plugin_app: start..."
    # add button to main frame
    label = tk.Label(
        parent,
        text=f"{edrs_object.data.pluginname} v{edrs_object.data.version}:",
    )
    if edrs_object.dialog is None:
        edrs_object.dialog = EdrsDialog(parent, edrs_object.qlog, edrs_object.data)
    button = edrs_object.dialog.button()
    edrs_object.logger.debug = f"{edrs_object.data.pluginname}->plugin_app: done."
    return label, button


def prefs_changed(cmdr: str, is_beta: bool) -> None:
    """Save settings.

    cmdr:       The current commander
    is_beta:    If the game is currently a beta version
    """
    edrs_object.logger.debug = f"{edrs_object.data.pluginname}->prefs_changed: start..."
    # set loglevel after config update
    edrs_object.log_processor.loglevel = LogLevels().get(config.get_str("loglevel"))
    edrs_object.logger.debug = f"{edrs_object.data.pluginname}->prefs_changed: done."


def journal_entry(
    cmdr: str,
    is_beta: bool,
    system: str,
    station: str,
    entry: Dict[str, Any],
    state: Dict[str, Any],
) -> Optional[str]:
    """Get new entry in the game's journal.

    cmdr:       Current commander name
    is_beta:    Is the game currently in beta
    system:     Current system, if known
    station:    Current station, if any
    entry:      The journal event
    state:      More info about the commander, their ship, and their cargo
    """
    edrs_object.logger.debug = f"{edrs_object.data.pluginname}->journal_entry: start..."
    edrs_object.logger.debug = (
        f"{edrs_object.data.pluginname}->journal_entry: cmdr:{cmdr}, system:{system}"
    )
    edrs_object.data.cmdr = cmdr
    # new
    edrs_object.data.starsystem.name = system
    if entry["event"] in ("FSDJump", "Loadout", "Docked", "CarrierJump"):
        # new
        edrs_object.data.starsystem.name = entry.get(
            "StarsSystem", edrs_object.data.starsystem.name
        )
        edrs_object.data.starsystem.address = entry.get(
            "SystemAddress", edrs_object.data.starsystem.address
        )
        edrs_object.data.starsystem.star_pos = entry.get(
            "StarPos", edrs_object.data.starsystem.star_pos
        )
        edrs_object.data.starsystem.star_class = entry.get(
            "StarClass", edrs_object.data.starsystem.star_class
        )
        edrs_object.data.jumprange = entry.get(
            "MaxJumpRange", edrs_object.data.jumprange
        )
        edrs_object.logger.debug = f"{edrs_object.data}"
        if edrs_object.dialog is not None:
            edrs_object.dialog.dialog_update()
    elif entry["event"] == "FSDTarget":
        edrs_object.data.jumpsystem.name = entry.get(
            "StarsSystem", edrs_object.data.jumpsystem.name
        )
        edrs_object.data.jumpsystem.address = entry.get(
            "SystemAddress", edrs_object.data.jumpsystem.address
        )
        edrs_object.data.jumpsystem.star_class = entry.get(
            "StarClass", edrs_object.data.jumpsystem.star_class
        )
    edrs_object.logger.debug = f"{edrs_object.data.pluginname}->journal_entry: done."


# #[EOF]#######################################################################
