# -*- coding: UTF-8 -*-
"""
  Author:  Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
  Created: 19.12.2023

  Purpose: ToolTip
"""

import tkinter as tk
from typing import List, Tuple, Union, Optional, Dict, Any

from jsktoolbox.attribtool import NoDynamicAttributes


class CreateToolTip(NoDynamicAttributes):
    """Create a tooltip for a given widget."""

    __data: Dict[str, Any] = None  # type: ignore

    def __init__(
        self,
        widget,
        text: Union[str, List, Tuple] = "widget info",
        wait_time: int = 500,
        wrap_length: int = 300,
    ) -> None:
        """Create class object."""
        self.__data = {
            "waittime": wait_time,  # miliseconds
            "wraplength": wrap_length,  # pixels
            "widget": widget,  # parent widget
            "id": None,
            "tw": None,
        }
        # set message
        self.text = text
        self.__data["widget"].bind("<Enter>", self.enter)
        self.__data["widget"].bind("<Leave>", self.leave)
        self.__data["widget"].bind("<ButtonPress>", self.leave)

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
        self.__data["id"] = self.__data["widget"].after(
            self.__data["waittime"], self.showtip
        )

    def unschedule(self) -> None:
        """Unschedule method."""
        __id = self.__data["id"]
        self.__data["id"] = None
        if __id:
            self.__data["widget"].after_cancel(__id)

    def showtip(self, event: Optional[tk.Event] = None) -> None:
        """Show tooltip."""
        __x = 0
        __y = 0
        __x, __y, __cx, __cy = self.__data["widget"].bbox("insert")
        __x += self.__data["widget"].winfo_rootx() + 25
        __y += self.__data["widget"].winfo_rooty() + 20
        # creates a toplevel window
        self.__data["tw"] = tk.Toplevel(self.__data["widget"])
        # Leaves only the label and removes the app window
        self.__data["tw"].wm_overrideredirect(True)
        self.__data["tw"].wm_geometry(f"+{__x}+{__y}")
        label = tk.Label(
            self.__data["tw"],
            text=self.text,
            justify="left",
            background="#ffffff",
            relief="solid",
            borderwidth=1,
            wraplength=self.__data["wraplength"],
        )
        label.pack(ipadx=1)

    def hidetip(self) -> None:
        """Hide tooltip."""
        __tw = self.__data["tw"]
        self.__data["tw"] = None
        if __tw:
            __tw.destroy()

    @property
    def text(self) -> str:
        """Return text message."""
        if "text" not in self.__data:
            self.__data["text"] = ""
        if isinstance(self.__data["text"], (List, Tuple)):
            tmp: str = ""
            for msg in self.__data["text"]:
                tmp += msg if not tmp else f"\n{msg}"
            return tmp
        return self.__data["text"]

    @text.setter
    def text(self, value: Union[str, List, Tuple]) -> None:
        """Set text message object."""
        self.__data["text"] = value


# #[EOF]#######################################################################
