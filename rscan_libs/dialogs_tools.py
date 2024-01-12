# -*- coding: UTF-8 -*-
"""
  Author:  Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
  Created: 19.12.2023

  Purpose: ToolTip
"""

import tkinter as tk
from typing import List, Tuple, Union, Optional

from jsktoolbox.libs.base_data import BData

from rscan_libs.dialogs_helper import DialogKeys


class CreateToolTip(BData):
    """Create a tooltip for a given widget."""

    def __init__(
        self,
        widget,
        tooltip_text: Union[str, List, Tuple] = "widget info",
        wait_time: int = 500,
        wrap_length: int = 300,
    ) -> None:
        """Create class object."""
        self._data[DialogKeys.WAITTIME] = wait_time  # miliseconds
        self._data[DialogKeys.WRAPLENGTH] = wrap_length  # pixels
        self._data[DialogKeys.WIDGET] = widget  # parent widget
        self._data[DialogKeys.ID] = None
        self._data[DialogKeys.TW] = None
        self._data[DialogKeys.TT_TEXT] = ""

        # set message
        self._data[DialogKeys.WIDGET].bind("<Enter>", self.enter)
        self._data[DialogKeys.WIDGET].bind("<Leave>", self.leave)
        self._data[DialogKeys.WIDGET].bind("<ButtonPress>", self.leave)
        self.tooltip = tooltip_text

    @property
    def tooltip(self) -> str:
        """Return text message."""
        if DialogKeys.TT_TEXT not in self._data:
            self._data[DialogKeys.TT_TEXT] = ""
        if isinstance(self._data[DialogKeys.TT_TEXT], (List, Tuple)):
            tmp: str = ""
            for msg in self._data[DialogKeys.TT_TEXT]:
                tmp += msg if not tmp else f"\n{msg}"
            return tmp
        return self._data[DialogKeys.TT_TEXT]

    @tooltip.setter
    def tooltip(self, value: Union[str, List, Tuple]) -> None:
        """Set text message object."""
        self._data[DialogKeys.TT_TEXT] = value

    def enter(self, event: Optional[tk.Event] = None) -> None:
        """Call on <Enter> event."""
        self.schedule()

    def leave(self, event: Optional[tk.Event] = None) -> None:
        """Call on <Leave> event."""
        self.unschedule()
        self.hidetip()

    def schedule(self) -> None:
        """Schedule method."""
        self.unschedule()
        self._data[DialogKeys.ID] = self._data[DialogKeys.WIDGET].after(
            self._data[DialogKeys.WAITTIME], self.showtip
        )

    def unschedule(self) -> None:
        """Unschedule method."""
        __id = self._data[DialogKeys.ID]
        self._data[DialogKeys.ID] = None
        if __id:
            self._data[DialogKeys.WIDGET].after_cancel(__id)

    def showtip(self, event: Optional[tk.Event] = None) -> None:
        """Show tooltip."""
        __x = 0
        __y = 0
        __x, __y, __cx, __cy = self._data[DialogKeys.WIDGET].bbox("insert")
        __x += self._data[DialogKeys.WIDGET].winfo_rootx() + 25
        __y += self._data[DialogKeys.WIDGET].winfo_rooty() + 20
        # creates a toplevel window
        self._data[DialogKeys.TW] = tk.Toplevel(self._data[DialogKeys.WIDGET])
        # Leaves only the label and removes the app window
        self._data[DialogKeys.TW].wm_overrideredirect(True)
        self._data[DialogKeys.TW].wm_geometry(f"+{__x}+{__y}")
        label = tk.Label(
            self._data[DialogKeys.TW],
            text=self.tooltip,
            justify="left",
            background="#ffffff",
            relief="solid",
            borderwidth=1,
            wraplength=self._data[DialogKeys.WRAPLENGTH],
        )
        label.pack(ipadx=1)

    def hidetip(self) -> None:
        """Hide tooltip."""
        __tw = self._data[DialogKeys.TW]
        self._data[DialogKeys.TW] = None
        if __tw:
            __tw.destroy()


# #[EOF]#######################################################################
