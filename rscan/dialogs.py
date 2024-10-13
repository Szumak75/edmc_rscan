# -*- coding: UTF-8 -*-
"""
  Author:  Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
  Created: 19.12.2023

  Purpose: EDRS dialogs classes.
"""

from inspect import currentframe
import time
import tkinter as tk
from tkinter import font
from queue import Queue, SimpleQueue
from threading import Thread
from tkinter import ttk
from typing import List, Optional, Union
from types import FrameType


from rscan.jsktoolbox.raisetool import Raise
from rscan.jsktoolbox.attribtool import ReadOnlyClass
from rscan.jsktoolbox.basetool.data import BData
from rscan.jsktoolbox.tktool.widgets import CreateToolTip, VerticalScrolledTkFrame
from rscan.jsktoolbox.tktool.base import TkBase

from rscan.jsktoolbox.edmctool.math import Euclid
from rscan.jsktoolbox.edmctool.data import RscanData

from rscan.jsktoolbox.edmctool.base import BLogClient
from rscan.jsktoolbox.edmctool.logs import LogClient
from rscan.jsktoolbox.edmctool.stars import StarsSystem

from rscan.jsktoolbox.edmctool.edsm_keys import EdsmKeys
from rscan.jsktoolbox.tktool.tools import ClipBoard

from rscan.th import ThSystemSearch
from rscan.tools import Numbers
from rscan.gfx import Pics


class _FontKeys(object, metaclass=ReadOnlyClass):
    """Font keys for Tkinter."""

    FONT: str = "font"  # tk key
    FONT_BOLD: str = "bold"  # tk key
    FONT_NORMAL: str = "normal"  # tk key
    FONT_STRIKE: str = "strike"  # tk key


class _FontFamily(object, metaclass=ReadOnlyClass):
    """Font families for Tkinter."""

    HELVETICA: str = "Helvetica"


class _Keys(object, metaclass=ReadOnlyClass):
    """Internal Keys container class."""

    CLIP: str = "_clip_"
    EUCLID: str = "euclid"
    F_DATA: str = "_f_data_"
    MATH: str = "_math_"
    RADIUS: str = "_radius_"
    S_BUTTON: str = "_s_button_"
    S_PANEL: str = "_s_panel_"
    STATUS: str = "_status_"
    SYSTEM: str = "_system_"
    BUTTON: str = "_button_"
    PARENT: str = "__parent__"
    WINDOWS: str = "__windows__"

    CLOSED: str = "__closed__"
    DATA: str = "__rscan_data__"
    START: str = "__start__"
    STARS: str = "__stars__"
    RSCAN_TH: str = "__rscan_th__"
    RSCAN_QTH: str = "__rscan_qth__"

    WIDGETS_KEY: str = "__widgets__"
    FONT_KEY: str = "__font__"
    TOOLS_KEY: str = "__tools__"


class _BEdrsDialog(BData):
    """Base class for EDMC dialogs."""

    @property
    def _button(self) -> ttk.Button:
        return self._get_data(key=_Keys.BUTTON, default_value=None)  # type: ignore

    @_button.setter
    def _button(self, value: ttk.Button) -> None:
        self._set_data(key=_Keys.BUTTON, value=value, set_default_type=ttk.Button)

    @property
    def _parent(self) -> tk.Frame:
        return self._get_data(key=_Keys.PARENT, default_value=None)  # type: ignore

    @_parent.setter
    def _parent(self, value: tk.Frame) -> None:
        self._set_data(key=_Keys.PARENT, value=value, set_default_type=tk.Frame)

    @property
    def _r_data(self) -> RscanData:
        return self._get_data(key=_Keys.DATA)  # type: ignore

    @_r_data.setter
    def _r_data(self, value: RscanData) -> None:
        self._set_data(key=_Keys.DATA, value=value, set_default_type=RscanData)

    @property
    def _fonts(self) -> BData:
        if self._get_data(key=_Keys.FONT_KEY, default_value=None) is None:  # type: ignore
            self._set_data(key=_Keys.FONT_KEY, value=BData(), set_default_type=BData)
        return self._get_data(key=_Keys.FONT_KEY)  # type: ignore

    @property
    def _tools(self) -> BData:
        if self._get_data(key=_Keys.TOOLS_KEY, default_value=None) is None:  # type: ignore
            self._set_data(key=_Keys.TOOLS_KEY, value=BData(), set_default_type=BData)
        return self._get_data(key=_Keys.TOOLS_KEY)  # type: ignore

    @property
    def _widgets(self) -> BData:
        if self._get_data(key=_Keys.WIDGETS_KEY, default_value=None) is None:  # type: ignore
            self._set_data(key=_Keys.WIDGETS_KEY, value=BData(), set_default_type=BData)
        return self._get_data(key=_Keys.WIDGETS_KEY)  # type: ignore

    @property
    def _windows(self) -> List["EdrsScanDialog"]:
        return self._get_data(key=_Keys.WINDOWS, default_value=None)  # type: ignore

    @_windows.setter
    def _windows(self, value: List) -> None:
        self._set_data(key=_Keys.WINDOWS, value=value, set_default_type=List)

    @property
    def _stars(self) -> List:
        return self._get_data(key=_Keys.STARS, default_value=None)  # type: ignore

    @_stars.setter
    def _stars(self, value: List) -> None:
        self._set_data(key=_Keys.STARS, value=value, set_default_type=List)

    @property
    def _start(self) -> StarsSystem:
        return self._get_data(key=_Keys.START, default_value=None)  # type: ignore

    @_start.setter
    def _start(self, value: StarsSystem) -> None:
        self._set_data(key=_Keys.START, value=value, set_default_type=StarsSystem)


class EdrsScanDialog(tk.Toplevel, TkBase, BLogClient, _BEdrsDialog):
    """Create new  window."""

    def __init__(
        self,
        log_queue: Union[Queue, SimpleQueue],
        data: RscanData,
        euclid_alg: Euclid,
        master=None,
    ) -> None:
        """Initialize dataset."""
        super().__init__(master=master)

        # tools
        self._tools._set_data(
            key=_Keys.CLIP, value=ClipBoard(), set_default_type=ClipBoard
        )
        # Euclid's algorithm for calculating the length of vectors
        self._tools._set_data(
            key=_Keys.MATH,
            value=euclid_alg,
            set_default_type=Euclid,
        )

        # widgets declaration
        self._widgets._set_data(
            key=_Keys.STATUS, value=None, set_default_type=Optional[tk.StringVar]
        )
        self._widgets._set_data(
            key=_Keys.F_DATA, value=None, set_default_type=Optional[tk.LabelFrame]
        )
        self._widgets._set_data(
            key=_Keys.SYSTEM, value=None, set_default_type=Optional[tk.Entry]
        )
        self._widgets._set_data(
            key=_Keys.RADIUS, value=None, set_default_type=Optional[tk.Entry]
        )
        self._widgets._set_data(
            key=_Keys.S_BUTTON, value=None, set_default_type=Optional[tk.Button]
        )
        self._widgets._set_data(
            key=_Keys.S_PANEL,
            value=None,
            set_default_type=Optional[VerticalScrolledTkFrame],
        )

        # init log subsystem
        self.logger = LogClient(log_queue)

        self._r_data = data
        self.debug(currentframe(), f"{self._r_data}")

        self.debug(currentframe(), "Initialize dataset")

        # list of found systems: [[system, frame, label with name],...]
        self._stars = []

        if self._r_data.stars_system.name is not None:
            self._start = self._r_data.stars_system

        # starting worker th
        self._set_data(
            key=_Keys.RSCAN_QTH,
            value=SimpleQueue(),
            set_default_type=Union[Queue, SimpleQueue],
        )
        self._set_data(
            key=_Keys.RSCAN_TH,
            value=Thread(
                target=self.th_worker,
                name=f"{self._r_data.plugin_name} worker",
                daemon=True,
            ),
            set_default_type=Thread,
        )
        self.__rscan_th.start()

        # fonts configure
        self._fonts._set_data(
            key=_FontKeys.FONT_BOLD,
            value=font.Font(
                family=_FontFamily.HELVETICA,
                size=10,
                weight=font.BOLD,
                overstrike=False,
            ),
            set_default_type=font.Font,
        )
        self._fonts._set_data(
            key=_FontKeys.FONT_NORMAL,
            value=font.Font(
                family=_FontFamily.HELVETICA,
                size=10,
                overstrike=False,
            ),
            set_default_type=font.Font,
        )
        self._fonts._set_data(
            key=_FontKeys.FONT_STRIKE,
            value=font.Font(
                family=_FontFamily.HELVETICA,
                size=10,
                overstrike=True,
            ),
            set_default_type=font.Font,
        )

        # closed flag
        self._set_data(key=_Keys.CLOSED, value=False, set_default_type=bool)

        # create window
        self.__frame_build()

        self.debug(currentframe(), "Constructor work done.")

    @property
    def __clip(self) -> ClipBoard:
        return self._tools._get_data(key=_Keys.CLIP)  # type: ignore

    @property
    def __rscan_th(self) -> Thread:
        return self._get_data(key=_Keys.RSCAN_TH)  # type: ignore

    @property
    def __rscan_qth(self) -> Union[Queue, SimpleQueue]:
        return self._get_data(key=_Keys.RSCAN_QTH)  # type: ignore

    def __frame_build(self) -> None:
        """Create window."""
        self.title(self._r_data.plugin_name)
        self.geometry("600x400")
        self.minsize(width=300, height=400)
        # grid configure
        self.columnconfigure(0, weight=100)
        self.columnconfigure(1, weight=1)
        # label row
        r_label_idx = 0
        self.rowconfigure(r_label_idx, weight=1)
        # command row
        r_comm_idx = r_label_idx + 1
        self.rowconfigure(r_comm_idx, weight=1)
        # data row
        r_data_idx = r_comm_idx + 1
        self.rowconfigure(r_data_idx, weight=100)
        # status row
        r_stat_idx = r_data_idx + 1
        self.rowconfigure(r_stat_idx, weight=1)

        # create label
        label = tk.Label(self, text="EDSM Red Scanner Flight Router")
        label.grid(row=r_label_idx, column=0, columnspan=2)

        # create command panel
        command_frame = tk.LabelFrame(self, text=" Generator ")
        command_frame.grid(
            row=r_comm_idx,
            column=0,
            columnspan=2,
            padx=5,
            pady=5,
            ipadx=5,
            ipady=5,
            sticky=tk.EW,
        )
        command_frame.columnconfigure(0, weight=1)
        command_frame.columnconfigure(1, weight=100)
        command_frame.columnconfigure(2, weight=1)
        command_frame.columnconfigure(3, weight=1)
        command_frame.columnconfigure(4, weight=1)
        command_frame.rowconfigure(0, weight=1)
        tk.Label(command_frame, text="Start system:").grid(row=0, column=0, sticky=tk.E)
        system_name = tk.Entry(command_frame, textvariable=tk.StringVar(value=""))
        system_name.grid(row=0, column=1, sticky=tk.EW)
        system_name.bind("<Return>", self.__generator)
        if self._r_data.stars_system.name is not None:
            system_name.delete(0, tk.END)
            system_name.insert(0, self._r_data.stars_system.name)
        self._widgets._set_data(key=_Keys.SYSTEM, value=system_name)
        tk.Label(command_frame, text="Radius:").grid(row=0, column=2, sticky=tk.E)
        radius = tk.Entry(command_frame, textvariable=tk.StringVar(value="10"), width=5)
        radius.bind("<Return>", self.__generator)
        radius.grid(row=0, column=3, sticky=tk.W)
        self._widgets._set_data(key=_Keys.RADIUS, value=radius)
        b_generator_img = tk.PhotoImage(data=Pics.SEARCH_16)
        b_generator = tk.Button(
            command_frame, image=b_generator_img, command=self.__generator
        )
        b_generator.image = b_generator_img  # type: ignore
        b_generator.grid(row=0, column=4, ipadx=2, sticky=tk.E)
        CreateToolTip(
            b_generator, "Locate visited systems that have not been explored."
        )
        self._widgets._set_data(key=_Keys.S_BUTTON, value=b_generator)

        # create data panel
        data_frame = tk.LabelFrame(self, text=" Flight route ")
        data_frame.grid(
            row=r_data_idx, column=0, columnspan=2, padx=5, pady=5, sticky=tk.NSEW
        )
        self._widgets._set_data(key=_Keys.F_DATA, value=data_frame)

        # create scrolled panel
        s_panel = VerticalScrolledTkFrame(
            data_frame,
            borderwidth=2,
            relief=tk.FLAT,
            background="light gray",
        )
        s_panel.pack(ipadx=1, ipady=1, fill=tk.BOTH, expand=tk.TRUE)
        self._widgets._set_data(key=_Keys.S_PANEL, value=s_panel)

        # create status panel
        status_frame = tk.Frame(self)
        status_frame.grid(row=r_stat_idx, column=0, sticky=tk.EW)

        status_label_frame = tk.LabelFrame(status_frame, text="")
        status_label_frame.pack(side=tk.LEFT, fill=tk.X, expand=tk.TRUE, padx=5, pady=5)
        status_string = tk.StringVar()
        status = tk.Label(status_label_frame, textvariable=status_string)
        status.pack(side=tk.LEFT)
        self._widgets._set_data(key=_Keys.STATUS, value=status_string)

        # size grip
        sizegrip = ttk.Sizegrip(self)
        sizegrip.grid(row=r_stat_idx, column=1, padx=1, pady=1, sticky=tk.SE)

        # closing event
        self.protocol("WM_DELETE_WINDOW", self.__on_closing)

    def __on_closing(self) -> None:
        """Run on closing event."""
        self.debug(currentframe(), "Window is closing now.")
        self._set_data(
            key=_Keys.CLOSED,
            value=True,
        )
        self.__rscan_qth.put(None)
        self.destroy()

    def __to_clipboard(self, clip_text: str) -> None:
        """Copy txt to clipboard."""
        # USE: command=lambda: self.__to_clipboard('txt')
        self.debug(currentframe(), f"string: '{clip_text}'")
        if self.__clip.is_tool:
            self.__clip.copy(clip_text)
        else:
            clip = tk.Tk()
            clip.withdraw()
            clip.clipboard_clear()
            clip.clipboard_append(clip_text)
            clip.update()
            clip.destroy()

    def __generator(self, event: Optional[tk.Event] = None) -> None:
        """Command button callback."""
        # get variables
        system = self._widgets._get_data(key=_Keys.SYSTEM).get()  # type: ignore
        radius = self._widgets._get_data(key=_Keys.RADIUS).get()  # type: ignore
        self.debug(currentframe(), f"system: {system}, type:{type(system)}")
        self.debug(currentframe(), f"radius: {radius}, type:{type(radius)}")

        if not system or not radius:
            msg: str = ""
            if not system:
                msg = "system"
            if not radius and msg:
                msg = f"{msg} and radius"
            elif not radius:
                msg = "radius"
            msg = f"{msg} must be set for processing request."
            self.status = msg
            return

        if radius and not Numbers().is_float(radius):
            msg = "Radius must be set as decimal expression."
            self.status = msg
            return

        # build thread object for worker
        obj = ThSystemSearch(
            self,
            self.logger.queue,
            self._r_data,
            self._tools._get_data(key=_Keys.MATH),  # type: ignore
        )
        obj.radius = radius
        # initializing start system for search engine
        if self._start is None:
            self._start = StarsSystem(name=system)
        if self._start.name != system:
            self._start.name = None
            self._start.name = system
        obj.start_system = self._start

        # put it into queue
        if obj:
            self.__rscan_qth.put(obj)

    def __disable_button(self, flag: bool) -> None:
        """Disable generator button on working time."""
        if self._widgets._get_data(key=_Keys.S_BUTTON) is None:
            return
        if isinstance(flag, bool):
            if flag:
                self._widgets._get_data(key=_Keys.S_BUTTON).config(state=tk.DISABLED)  # type: ignore
            else:
                self._widgets._get_data(key=_Keys.S_BUTTON).config(state=tk.ACTIVE)  # type: ignore

    def th_worker(self) -> None:
        """Run thread for getting data and computing results."""
        p_name: str = self._r_data.plugin_name
        c_name: str = self._c_name
        if self.logger:
            self.logger.info = f"{p_name}->{c_name}: Starting worker..."
        while not self._r_data.shutting_down:
            item: ThSystemSearch = self.__rscan_qth.get(True)
            if item is None:
                break
            self.__disable_button(True)
            if self.logger:
                self.logger.info = (
                    f"{p_name}->{c_name}: Get new search work for "
                    f"{item.start_system.name} with radius: {item.radius}ly"
                )
            time_start: float = time.time()
            # start processing request
            item.start()
            item.join()
            # getting results
            time_stop: float = time.time()
            if self.logger:
                self.logger.info = (
                    f"{p_name}->{c_name}: Work is done in: {int(time_stop-time_start)}s"
                )
            self.__process_work_output(item.get_result)
            self.__disable_button(False)
        if self.logger:
            self.logger.info = f"{p_name}->{c_name}: worker finished."

    def __process_work_output(self, systems: Optional[List[StarsSystem]]) -> None:
        """Build frame with found systems."""
        # destroy previous data
        for item in self._stars:
            item[1].pack_forget()
            item[1].destroy()
        self._stars = []
        # generate new list
        count = 0

        if systems:
            for system in systems:
                count += 1
                self.__build_row_frame(count, system)

    def __build_row_frame(self, count: int, item: StarsSystem) -> None:
        """Construct and return Frame row for search dialog."""
        list_object = []
        # StarsSystem [0]
        list_object.append(item)

        # create frame [1]
        frame = tk.Frame(
            self._widgets._get_data(key=_Keys.S_PANEL).interior,  # type: ignore
            relief=tk.GROOVE,
            borderwidth=1,
        )
        frame.pack(fill=tk.X, expand=tk.TRUE)
        list_object.append(frame)

        # create count label
        tk.Label(
            frame, text=f" {count}: ", font=self._fonts._get_data(key=_FontKeys.FONT_NORMAL)  # type: ignore
        ).pack(side=tk.LEFT)

        # create name label [2]
        lname = tk.Label(frame, text=f"{item.name}")
        lname.pack(side=tk.LEFT)
        lname["font"] = self._fonts._get_data(key=_FontKeys.FONT_NORMAL)  # type: ignore
        list_object.append(lname)

        # create range label
        distance: str = "??"
        jump = 50
        if EdsmKeys.DISTANCE in item.data:
            distance = f"{item.data[EdsmKeys.DISTANCE]:.2f}"
        label_jump = tk.Label(
            frame,
            text=f"[{distance:} ly]",
            font=self._fonts._get_data(key=_FontKeys.FONT_NORMAL),  # type: ignore
        )
        label_jump.pack(side=tk.LEFT)
        if self._r_data.jump_range:
            jump: float = self._r_data.jump_range - 4
        if EdsmKeys.DISTANCE in item.data and item.data[EdsmKeys.DISTANCE] > jump:
            label_jump["font"] = self._fonts._get_data(key=_FontKeys.FONT_BOLD)  # type: ignore
            label_jump["fg"] = "red"
            CreateToolTip(
                label_jump,
                "Warning. The calculated distance exceeded the ship's maximum single jump distance.",
            )
        # permission
        if EdsmKeys.REQUIRE_PERMIT in item.data and item.data[EdsmKeys.REQUIRE_PERMIT]:
            label_permit_img = tk.PhotoImage(data=Pics.PERMIT_16)
            label_permit = tk.Label(frame, image=label_permit_img)
            label_permit.image = label_permit_img  # type: ignore
            label_permit.pack(side=tk.LEFT)
            CreateToolTip(
                label_permit,
                "Warning. Required permissions to enter this system.",
            )
        # create clipboard button
        btn_img = tk.PhotoImage(data=Pics.CLIPBOARD_16)
        btn = tk.Button(
            frame,
            # text="C",
            image=btn_img,
            command=lambda: self.__to_clipboard(f"{item.name}"),
            font=self._fonts._get_data(key=_FontKeys.FONT_NORMAL),  # type: ignore
        )
        btn.image = btn_img  # type: ignore
        btn.pack(side=tk.RIGHT)
        CreateToolTip(btn, "Copy to clipboard")

        # finish
        self._stars.append(list_object)

    def dialog_update(self) -> None:
        """Update current position in system list."""
        if self._r_data.shutting_down:
            self.__rscan_qth.put(None)

        # update located system
        for item in self._stars:
            if item[0].name == self._r_data.stars_system.name:
                item[2][_FontKeys.FONT] = self._fonts._get_data(key=_FontKeys.FONT_STRIKE)  # type: ignore

    def debug(self, currentframe: Optional[FrameType], message: str = "") -> None:
        """Build debug message."""
        p_name: str = f"{self._r_data.plugin_name}"
        c_name: str = f"{self._c_name}"
        m_name: str = f"{currentframe.f_code.co_name}" if currentframe else ""
        if message != "":
            message = f": {message}"
        if self.logger:
            self.logger.debug = f"{p_name}->{c_name}.{m_name}{message}"

    @property
    def is_closed(self) -> bool:
        """Check, if window is closed."""
        return self._get_data(key=_Keys.CLOSED)  # type: ignore

    @property
    def status(self) -> Optional[tk.StringVar]:
        """Return status object."""
        return self._widgets._get_data(key=_Keys.STATUS)

    @status.setter
    def status(self, message) -> None:
        """Set status message."""
        if self._widgets._get_data(key=_Keys.STATUS) is not None:
            if message:
                self._widgets._get_data(key=_Keys.STATUS).set(f"{message}")  # type: ignore
            else:
                self._widgets._get_data(key=_Keys.STATUS).set("")  # type: ignore


class EdrsDialog(BLogClient, _BEdrsDialog):
    """Create config dialog for plugin."""

    def __init__(
        self,
        parent: tk.Frame,
        log_queue: Union[Queue, SimpleQueue],
        data: RscanData,
    ) -> None:
        """Initialize datasets."""
        # init log subsystem
        self.logger = LogClient(log_queue)

        self._r_data = data
        self.debug(currentframe(), f"{self._r_data}")

        if not isinstance(parent, tk.Frame):
            raise Raise.error(
                f"tk.Frame type expected, '{type(parent)}' received",
                TypeError,
                self._c_name,
                currentframe(),
            )
        self._parent = parent

        self._windows = []

        # tools
        self._tools._set_data(
            key=_Keys.EUCLID, value=Euclid(log_queue, data), set_default_type=Euclid
        )
        self._tools._get_data(key=_Keys.EUCLID).benchmark()  # type: ignore

    def button(self) -> ttk.Button:
        """Give me the button for main application frame."""
        if self._button is None:
            self._button = ttk.Button(
                self._parent,
                text="Scanner",
                command=self.__bt_callback,
                default=tk.ACTIVE,
                # state=tk.DISABLED
            )
            self._button.grid(sticky=tk.NSEW)
        return self._button

    def dialog_update(self) -> None:
        """Do update for windows."""
        self.debug(
            currentframe(),
            f"Update init, found {len(self._windows)} windows",
        )
        for window in self._windows:
            if not window.is_closed:
                window.dialog_update()

    def __bt_callback(self) -> None:
        """Run main button callback."""
        self.debug(currentframe(), "click!")
        # purge closed window from list
        for window in self._windows:
            if window.is_closed:
                self._windows.remove(window)
        # create new window
        esd = EdrsScanDialog(self.logger.queue, self._r_data, self._tools._get_data(key=_Keys.EUCLID))  # type: ignore
        if self._r_data.stars_system.name is not None:
            esd.title(f"{self._r_data.plugin_name}: {self._r_data.stars_system.name}")

        self._windows.append(esd)
        self.debug(
            currentframe(),
            f"numbers of windows: {len(self._windows)}",
        )

    def debug(self, currentframe: Optional[FrameType], message: str = "") -> None:
        """Build debug message."""
        p_name: str = f"{self._r_data.plugin_name}"
        c_name: str = f"{self._c_name}"
        m_name: str = f"{currentframe.f_code.co_name}" if currentframe else ""
        if message != "":
            message = f": {message}"
        if self.logger:
            self.logger.debug = f"{p_name}->{c_name}.{m_name}{message}"


# #[EOF]#######################################################################
