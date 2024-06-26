# -*- coding: UTF-8 -*-
"""
  Author:  Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
  Created: 19.12.2023

  Purpose: plugin entry point.
"""


import logging
import tkinter as tk
from tkinter import ttk
from typing import Any, Dict, Optional

from jsktoolbox.tktool.widgets import CreateToolTip

from config import config

from rscan_libs.dialogs import EdrsDialog
from rscan_libs.edrs import EDRS
from rscan_libs.system import LogLevels


edrs_object = EDRS()


def plugin_start3(plugin_dir: str) -> str:
    """Load plugin into EDMC.

    plugin_dir:     plugin directory
    return:         local name of the plugin
    """
    edrs_object.logger.debug = f"{edrs_object.data.plugin_name}->plugin_start3 start..."
    # loglevel set from config
    loglevel: Optional[int] = LogLevels().get(config.get_str("loglevel"))
    edrs_object.log_processor.loglevel = (
        loglevel if loglevel is not None else logging.DEBUG
    )
    edrs_object.logger.debug = f"{edrs_object.data.plugin_name}->plugin_start3 done."
    return f"{edrs_object.data.plugin_name}"


def plugin_stop() -> None:
    """Stop plugin if EDMC is closing."""
    edrs_object.logger.debug = f"{edrs_object.data.plugin_name}->plugin_stop: start..."
    edrs_object.data.shutting_down = True
    edrs_object.logger.debug = (
        f"{edrs_object.data.plugin_name}->plugin_stop: shut down flag is set"
    )
    # something to do
    if edrs_object.dialog is not None:
        edrs_object.dialog.dialog_update()
    # shut down logger at last
    edrs_object.logger.debug = (
        f"{edrs_object.data.plugin_name}->plugin_stop: terminating the logger"
    )
    edrs_object.qlog.put(None)
    edrs_object.th_log.join()
    edrs_object.th_log = None  # type: ignore


def plugin_app(parent: tk.Frame) -> ttk.Button:
    """Create a pair of TK widgets for the EDMarketConnector main window.

    parent:     The root EDMarketConnector window
    """
    edrs_object.logger.debug = f"{edrs_object.data.plugin_name}->plugin_app: start..."
    if edrs_object.dialog is None:
        edrs_object.dialog = EdrsDialog(parent, edrs_object.qlog, edrs_object.data)
    button: ttk.Button = edrs_object.dialog.button()
    CreateToolTip(
        button,
        [
            f"{edrs_object.data.plugin_name} v{edrs_object.data.version}",
            "",
            "Search the edsm database for partially",
            "uncovered systems within a given radius",
            "that require a full scan.",
        ],
    )
    edrs_object.logger.debug = f"{edrs_object.data.plugin_name}->plugin_app: done."
    return button


def prefs_changed(cmdr: str, is_beta: bool) -> None:
    """Save settings.

    cmdr:       The current commander
    is_beta:    If the game is currently a beta version
    """
    edrs_object.logger.debug = (
        f"{edrs_object.data.plugin_name}->prefs_changed: start..."
    )
    # set loglevel after config update
    loglevel: Optional[int] = LogLevels().get(config.get_str("loglevel"))
    edrs_object.log_processor.loglevel = (
        loglevel if loglevel is not None else logging.DEBUG
    )
    edrs_object.logger.debug = f"{edrs_object.data.plugin_name}->prefs_changed: done."


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
    edrs_object.logger.debug = (
        f"{edrs_object.data.plugin_name}->journal_entry: start..."
    )
    edrs_object.logger.debug = (
        f"{edrs_object.data.plugin_name}->journal_entry: cmdr:{cmdr}, system:{system}"
    )
    edrs_object.data.cmdr = cmdr
    # new
    edrs_object.data.star_system.name = system
    if entry["event"] in ("FSDJump", "Loadout", "Docked", "CarrierJump"):
        # new
        edrs_object.data.star_system.name = entry.get(
            "StarsSystem", edrs_object.data.star_system.name
        )
        edrs_object.data.star_system.address = entry.get(
            "SystemAddress", edrs_object.data.star_system.address
        )
        edrs_object.data.star_system.star_pos = entry.get(
            "StarPos", edrs_object.data.star_system.star_pos
        )
        edrs_object.data.star_system.star_class = entry.get(
            "StarClass", edrs_object.data.star_system.star_class
        )
        edrs_object.data.jump_range = entry.get(
            "MaxJumpRange", edrs_object.data.jump_range
        )
        edrs_object.logger.debug = f"{edrs_object.data}"
        if edrs_object.dialog is not None:
            edrs_object.dialog.dialog_update()
    elif entry["event"] == "FSDTarget":
        edrs_object.data.jump_system.name = entry.get(
            "StarsSystem", edrs_object.data.jump_system.name
        )
        edrs_object.data.jump_system.address = entry.get(
            "SystemAddress", edrs_object.data.jump_system.address
        )
        edrs_object.data.jump_system.star_class = entry.get(
            "StarClass", edrs_object.data.jump_system.star_class
        )
    edrs_object.logger.debug = f"{edrs_object.data.plugin_name}->journal_entry: done."


# #[EOF]#######################################################################
