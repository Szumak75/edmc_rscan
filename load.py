# -*- coding: UTF-8 -*-
"""
  Author:  Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
  Created: 19.12.2023

  Purpose: plugin entry point.
"""


import logging
import tkinter as tk
from tkinter import ttk
from typing import Any, Dict, Optional, Tuple

from config import config
from theme import theme

from rscan_libs.dialogs import EdrsDialog
from rscan_libs.edrs import EDRS
from rscan_libs.system import LogLevels


edrs_object = EDRS()


def plugin_start3(plugin_dir: str) -> str:
    """Load plugin into EDMC.

    plugin_dir:     plugin directory
    return:         local name of the plugin
    """
    edrs_object.logger.debug = f"{edrs_object.data.pluginname}->plugin_start3 start..."
    # loglevel set from config
    loglevel: Optional[int] = LogLevels().get(config.get_str("loglevel"))
    edrs_object.log_processor.loglevel = (
        loglevel if loglevel is not None else logging.DEBUG
    )
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
    edrs_object.thlog = None  # type: ignore


def plugin_app(parent: tk.Frame) -> Tuple[tk.Label, ttk.Button]:
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
    button: ttk.Button = edrs_object.dialog.button()
    edrs_object.logger.debug = f"{edrs_object.data.pluginname}->plugin_app: done."
    return label, button


def prefs_changed(cmdr: str, is_beta: bool) -> None:
    """Save settings.

    cmdr:       The current commander
    is_beta:    If the game is currently a beta version
    """
    edrs_object.logger.debug = f"{edrs_object.data.pluginname}->prefs_changed: start..."
    # set loglevel after config update
    loglevel: Optional[int] = LogLevels().get(config.get_str("loglevel"))
    edrs_object.log_processor.loglevel = (
        loglevel if loglevel is not None else logging.DEBUG
    )
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
