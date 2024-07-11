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
from typing import List, Optional, Union, Dict, Any
from types import FrameType


from jsktoolbox.attribtool import NoDynamicAttributes
from jsktoolbox.raisetool import Raise
from jsktoolbox.attribtool import ReadOnlyClass
from jsktoolbox.tktool.widgets import CreateToolTip, VerticalScrolledTkFrame

from rscan_libs.cartesianmath import Euclid
from rscan_libs.data import RscanData
from rscan_libs.base_log import BLogClient
from rscan_libs.stars import StarsSystem
from rscan_libs.system import Clip, LogClient
from rscan_libs.th import ThSystemSearch
from rscan_libs.tools import Numbers
from rscan_libs.gfx import Pics


class __FontFamily(object, metaclass=ReadOnlyClass):

    helvetica: str = "Helvetica"


class EdrsScanDialog(tk.Toplevel, BLogClient):
    """Create new  window."""

    class __Keys(object, metaclass=ReadOnlyClass):
        """Private keys."""

        BOLD: str = "bold"  # tk key
        CLIP: str = "_clip_"
        F_DATA: str = "_f_data_"
        FONT: str = "font"  # tk key
        MATH: str = "_math_"
        NORMAL: str = "normal"  # tk key
        RADIUS: str = "_radius_"
        S_BUTTON: str = "_s_button_"
        S_PANEL: str = "_s_panel_"
        STATUS: str = "_status_"
        STRIKE: str = "strike"  # tk key
        SYSTEM: str = "_system_"

    __closed = False
    # RScanData
    __data: RscanData = None  # type: ignore
    # start system name
    __start: StarsSystem = None  # type: ignore
    # stars list
    __stars: List[Any] = None  # type: ignore
    # widgets container
    __widgets: Dict[str, Any] = None  # type: ignore
    # th worker
    __rscan_th: Thread = None  # type: ignore
    __rscan_qth: SimpleQueue = None  # type: ignore
    __fonts: Dict[str, Any] = None  # type: ignore
    __tools: Dict[str, Any] = None  # type: ignore

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
        self.__tools = {
            EdrsScanDialog.__Keys.CLIP: None,
            EdrsScanDialog.__Keys.MATH: None,
        }

        self.__tools[EdrsScanDialog.__Keys.CLIP] = Clip()

        # widgets declaration
        self.__widgets = {}
        self.__widgets[EdrsScanDialog.__Keys.STATUS] = None  #: Optional[tk.StringVar]
        self.__widgets[EdrsScanDialog.__Keys.F_DATA] = None  #: Optional[tk.LabelFrame]
        self.__widgets[EdrsScanDialog.__Keys.SYSTEM] = None  #: Optional[tk.Entry]
        self.__widgets[EdrsScanDialog.__Keys.RADIUS] = None  #: Optional[tk.Entry]
        self.__widgets[EdrsScanDialog.__Keys.S_BUTTON] = None  #: Optional[tk.Button]
        self.__widgets[EdrsScanDialog.__Keys.S_PANEL] = (
            None  #: Optional[VerticalScrolledFrame]
        )

        # init log subsystem
        if not isinstance(log_queue, (Queue, SimpleQueue)):
            raise Raise.error(
                f"Queue or SimpleQueue type expected, '{type(log_queue)}' received.",
                TypeError,
                self.__class__.__name__,
                currentframe(),
            )
        self.logger = LogClient(log_queue)

        if not isinstance(data, RscanData):
            raise Raise.error(
                f"RscanData type expected, '{type(data)}' received",
                TypeError,
                self.__class__.__name__,
                currentframe(),
            )
        self.__data = data
        self.debug(currentframe(), f"{self.__data}")

        # Euclid's algorithm for calculating the length of vectors
        if not isinstance(euclid_alg, Euclid):
            raise Raise.error(
                f"Euclid type expected, '{type(euclid_alg)}' received",
                TypeError,
                self.__class__.__name__,
                currentframe(),
            )
        self.__tools[EdrsScanDialog.__Keys.MATH] = euclid_alg

        self.debug(currentframe(), "Initialize dataset")

        # list of found systems: [[system, frame, label with name],...]
        self.__stars = []

        if self.__data.star_system.name is not None:
            self.__start = self.__data.star_system

        # starting worker th
        self.__rscan_qth = SimpleQueue()
        self.__rscan_th = Thread(
            target=self.th_worker, name=f"{self.__data.plugin_name} worker"
        )
        self.__rscan_th.daemon = True
        self.__rscan_th.start()

        # fonts configure
        self.__fonts = {
            EdrsScanDialog.__Keys.BOLD: font.Font(
                family=__FontFamily.helvetica,
                size=10,
                weight=font.BOLD,
                overstrike=False,
            ),
            EdrsScanDialog.__Keys.NORMAL: font.Font(
                family=__FontFamily.helvetica, size=10, overstrike=False
            ),
            EdrsScanDialog.__Keys.STRIKE: font.Font(
                family=__FontFamily.helvetica, size=10, overstrike=True
            ),
        }

        # create window
        self.__frame_build()

        self.debug(currentframe(), "Constructor work done.")

    def __frame_build(self) -> None:
        """Create window."""
        self.title(self.__data.plugin_name)
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
        if self.__data.star_system.name is not None:
            system_name.delete(0, tk.END)
            system_name.insert(0, self.__data.star_system.name)
        self.__widgets[EdrsScanDialog.__Keys.SYSTEM] = system_name
        tk.Label(command_frame, text="Radius:").grid(row=0, column=2, sticky=tk.E)
        radius = tk.Entry(command_frame, textvariable=tk.StringVar(value="50"), width=5)
        radius.bind("<Return>", self.__generator)
        radius.grid(row=0, column=3, sticky=tk.W)
        self.__widgets[EdrsScanDialog.__Keys.RADIUS] = radius
        b_generator_img = tk.PhotoImage(data=Pics.SEARCH_16)
        b_generator = tk.Button(
            command_frame, image=b_generator_img, command=self.__generator
        )
        b_generator.image = b_generator_img  # type: ignore
        b_generator.grid(row=0, column=4, ipadx=2, sticky=tk.E)
        CreateToolTip(
            b_generator, "Locate visited systems that have not been explored."
        )
        self.__widgets[EdrsScanDialog.__Keys.S_BUTTON] = b_generator

        # create data panel
        data_frame = tk.LabelFrame(self, text=" Flight route ")
        data_frame.grid(
            row=r_data_idx, column=0, columnspan=2, padx=5, pady=5, sticky=tk.NSEW
        )
        self.__widgets[EdrsScanDialog.__Keys.F_DATA] = data_frame

        # create scrolled panel
        s_panel = VerticalScrolledTkFrame(
            data_frame,
            borderwidth=2,
            relief=tk.FLAT,
            background="light gray",
        )
        s_panel.pack(ipadx=1, ipady=1, fill=tk.BOTH, expand=tk.TRUE)
        self.__widgets[EdrsScanDialog.__Keys.S_PANEL] = s_panel

        # create status panel
        status_frame = tk.Frame(self)
        status_frame.grid(row=r_stat_idx, column=0, sticky=tk.EW)

        status_label_frame = tk.LabelFrame(status_frame, text="")
        status_label_frame.pack(side=tk.LEFT, fill=tk.X, expand=tk.TRUE, padx=5, pady=5)
        status_string = tk.StringVar()
        status = tk.Label(status_label_frame, textvariable=status_string)
        status.pack(side=tk.LEFT)
        self.__widgets[EdrsScanDialog.__Keys.STATUS] = status_string

        # size grip
        sizegrip = ttk.Sizegrip(self)
        sizegrip.grid(row=r_stat_idx, column=1, padx=1, pady=1, sticky=tk.SE)

        # closing event
        self.protocol("WM_DELETE_WINDOW", self.__on_closing)

    def __on_closing(self) -> None:
        """Run on closing event."""
        self.debug(currentframe(), "Window is closing now.")
        self.__closed = True
        self.__rscan_qth.put(None)
        self.destroy()

    def __to_clipboard(self, clip_text: str) -> None:
        """Copy txt to clipboard."""
        # USE: command=lambda: self.__to_clipboard('txt')
        self.debug(currentframe(), f"string: '{clip_text}'")
        if self.__tools[EdrsScanDialog.__Keys.CLIP].is_tool:
            self.__tools[EdrsScanDialog.__Keys.CLIP].copy(clip_text)
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
        system = self.__widgets[EdrsScanDialog.__Keys.SYSTEM].get()
        radius = self.__widgets[EdrsScanDialog.__Keys.RADIUS].get()
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
            self.__data,
            self.__tools[EdrsScanDialog.__Keys.MATH],
        )
        obj.radius = radius
        # initializing start system for search engine
        if self.__start is None:
            self.__start = StarsSystem(name=system)
        if self.__start.name != system:
            self.__start.name = None
            self.__start.name = system
        obj.start_system = self.__start

        # put it into queue
        if obj:
            self.__rscan_qth.put(obj)

    def __disable_button(self, flag: bool) -> None:
        """Disable generator button on working time."""
        if self.__widgets[EdrsScanDialog.__Keys.S_BUTTON] is None:
            return
        if isinstance(flag, bool):
            if flag:
                self.__widgets[EdrsScanDialog.__Keys.S_BUTTON].config(state=tk.DISABLED)
            else:
                self.__widgets[EdrsScanDialog.__Keys.S_BUTTON].config(state=tk.ACTIVE)

    def th_worker(self) -> None:
        """Run thread for getting data and computing results."""
        p_name: str = self.__data.plugin_name
        c_name: str = self.__class__.__name__
        if self.logger:
            self.logger.info = f"{p_name}->{c_name}: Starting worker..."
        while not self.__data.shutting_down:
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
        for item in self.__stars:
            item[1].pack_forget()
            item[1].destroy()
        self.__stars = []
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
            self.__widgets[EdrsScanDialog.__Keys.S_PANEL].interior,
            relief=tk.GROOVE,
            borderwidth=1,
        )
        frame.pack(fill=tk.X, expand=tk.TRUE)
        list_object.append(frame)

        # create count label
        tk.Label(
            frame, text=f" {count}: ", font=self.__fonts[EdrsScanDialog.__Keys.NORMAL]
        ).pack(side=tk.LEFT)

        # create name label [2]
        lname = tk.Label(frame, text=f"{item.name}")
        lname.pack(side=tk.LEFT)
        lname["font"] = self.__fonts[EdrsScanDialog.__Keys.NORMAL]
        list_object.append(lname)

        # create range label
        distance: str = "??"
        jump = 50
        if "distance" in item.data:
            distance = f"{item.data['distance']:.2f}"
        label_jump = tk.Label(
            frame,
            text=f"[{distance:} ly]",
            font=self.__fonts[EdrsScanDialog.__Keys.NORMAL],
        )
        label_jump.pack(side=tk.LEFT)
        if self.__data.jump_range:
            jump: float = self.__data.jump_range - 4
        if "distance" in item.data and item.data["distance"] > jump:
            label_jump["font"] = self.__fonts[EdrsScanDialog.__Keys.BOLD]
            label_jump["fg"] = "red"
            CreateToolTip(
                label_jump,
                "Warning. The calculated distance exceeded the ship's maximum single jump distance.",
            )
        # permission
        if "requirepermit" in item.data and item.data["requirepermit"]:
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
            font=self.__fonts[EdrsScanDialog.__Keys.NORMAL],
        )
        btn.image = btn_img  # type: ignore
        btn.pack(side=tk.RIGHT)
        CreateToolTip(btn, "Copy to clipboard")

        # finish
        self.__stars.append(list_object)

    def dialog_update(self) -> None:
        """Update current position in system list."""
        if self.__data.shutting_down:
            self.__rscan_qth.put(None)

        # update located system
        for item in self.__stars:
            if item[0].name == self.__data.star_system.name:
                item[2][EdrsScanDialog.__Keys.FONT] = self.__fonts[
                    EdrsScanDialog.__Keys.STRIKE
                ]

    def debug(self, currentframe: Optional[FrameType], message: str = "") -> None:
        """Build debug message."""
        p_name: str = f"{self.__data.plugin_name}"
        c_name: str = f"{self.__class__.__name__}"
        m_name: str = f"{currentframe.f_code.co_name}" if currentframe else ""
        if message != "":
            message = f": {message}"
        if self.logger:
            self.logger.debug = f"{p_name}->{c_name}.{m_name}{message}"

    @property
    def is_closed(self) -> bool:
        """Check, if window is closed."""
        return self.__closed

    @property
    def status(self) -> Optional[tk.StringVar]:
        """Return status object."""
        return self.__widgets[EdrsScanDialog.__Keys.STATUS]

    @status.setter
    def status(self, message) -> None:
        """Set status message."""
        if self.__widgets[EdrsScanDialog.__Keys.STATUS] is not None:
            if message:
                self.__widgets[EdrsScanDialog.__Keys.STATUS].set(f"{message}")
            else:
                self.__widgets[EdrsScanDialog.__Keys.STATUS].set("")


class EdrsDialog(BLogClient, NoDynamicAttributes):
    """Create config dialog for plugin."""

    # RscanData
    __data: RscanData = None  # type: ignore
    # tk.Frame
    __parent: tk.Frame = None  # type: ignore
    # ttk.Button
    __button: ttk.Button = None  # type: ignore
    # list
    __windows: List[EdrsScanDialog] = None  # type: ignore
    # Tools
    __tools: Dict[str, Any] = None  # type: ignore

    def __init__(
        self,
        parent: tk.Frame,
        log_queue: Union[Queue, SimpleQueue],
        data: RscanData,
    ) -> None:
        """Initialize datasets."""
        # init log subsystem
        if not isinstance(log_queue, (Queue, SimpleQueue)):
            raise Raise.error(
                f"Queue or SimpleQueue type expected, '{type(log_queue)}' received.",
                TypeError,
                self.__class__.__name__,
                currentframe(),
            )
        self.logger = LogClient(log_queue)

        if not isinstance(data, RscanData):
            raise Raise.error(
                f"RscanData type expected, '{type(data)}' received",
                TypeError,
                self.__class__.__name__,
                currentframe(),
            )
        self.__data = data
        self.debug(currentframe(), f"{self.__data}")

        if not isinstance(parent, tk.Frame):
            raise Raise.error(
                f"tk.Frame type expected, '{type(parent)}' received",
                TypeError,
                self.__class__.__name__,
                currentframe(),
            )
        self.__parent = parent

        self.__windows = []

        # tools
        self.__tools = {}
        self.__tools["euclid"] = Euclid(log_queue, data)
        self.__tools["euclid"].benchmark()

    def button(self) -> ttk.Button:
        """Give me the button for main application frame."""
        if self.__button is None:
            self.__button = ttk.Button(
                self.__parent,
                text="Scanner",
                command=self.__bt_callback,
                default=tk.ACTIVE,
                # state=tk.DISABLED
            )
            self.__button.grid(sticky=tk.NSEW)
        return self.__button

    def dialog_update(self) -> None:
        """Do update for windows."""
        self.debug(
            currentframe(),
            f"Update init, found {len(self.__windows)} windows",
        )
        for window in self.__windows:
            if not window.is_closed:
                window.dialog_update()

    def __bt_callback(self) -> None:
        """Run main button callback."""
        self.debug(currentframe(), "click!")
        # purge closed window from list
        for window in self.__windows:
            if window.is_closed:
                self.__windows.remove(window)
        # create new window
        esd = EdrsScanDialog(self.logger.queue, self.__data, self.__tools["euclid"])
        if self.__data.star_system.name is not None:
            esd.title(f"{self.__data.plugin_name}: {self.__data.star_system.name}")

        self.__windows.append(esd)
        self.debug(
            currentframe(),
            f"numbers of windows: {len(self.__windows)}",
        )

    def debug(self, currentframe: Optional[FrameType], message: str = "") -> None:
        """Build debug message."""
        p_name: str = f"{self.__data.plugin_name}"
        c_name: str = f"{self.__class__.__name__}"
        m_name: str = f"{currentframe.f_code.co_name}" if currentframe else ""
        if message != "":
            message = f": {message}"
        if self.logger:
            self.logger.debug = f"{p_name}->{c_name}.{m_name}{message}"


# #[EOF]#######################################################################
