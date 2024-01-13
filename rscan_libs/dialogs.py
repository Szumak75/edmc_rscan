# -*- coding: UTF-8 -*-
"""
  Author:  Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
  Created: 19.12.2023

  Purpose: EDRS dialogs classes.
"""

import inspect
import time
import tkinter as tk
from tkinter import font
from queue import Queue, SimpleQueue
from threading import Thread
from tkinter import ttk
from typing import List, Optional, Union, Tuple, Dict, Any
from types import FrameType
from jsktoolbox.attribtool import NoDynamicAttributes
from jsktoolbox.raisetool import Raise

from rscan_libs.cartesianmath import Euclid
from rscan_libs.data import RscanData
from rscan_libs.mlog import MLogClient
from rscan_libs.stars import StarsSystem
from rscan_libs.system import Clip, LogClient
from rscan_libs.th import ThSystemSearch
from rscan_libs.tools import Numbers
from rscan_libs.dialogs_tools import CreateToolTip


class EdrsScanDialog(tk.Toplevel, MLogClient):
    """Create new  window."""

    __closed = False
    # RScanData
    __data: RscanData = None  # type: ignore
    # start system name
    __start: StarsSystem = None  # type: ignore
    # stars list
    __stars: List[Any] = None  # type: ignore
    # wighets container
    __widgets: Dict[str, Any] = None  # type: ignore
    # th worker
    __rscan_th: Thread = None  # type: ignore
    __rscan_qth: SimpleQueue = None  # type: ignore
    __fonts: Dict[str, Any] = None  # type: ignore
    __tools: Dict[str, Any] = None  # type: ignore

    def __init__(
        self,
        log_queue: Queue or SimpleQueue,
        data: RscanData,
        euclid_alg: Euclid,
        master=None,
    ) -> None:
        """Initialize dataset."""
        super().__init__(master=master)

        # tools
        self.__tools = {"clip": None, "math": None}

        self.__tools["clip"] = Clip()

        # witgets declaration
        self.__widgets = {}
        self.__widgets["status"] = None  #: Optional[tk.StringVar]
        self.__widgets["fdata"] = None  #: Optional[tk.LabelFrame]
        self.__widgets["system"] = None  #: Optional[tk.Entry]
        self.__widgets["radius"] = None  #: Optional[tk.Entry]
        self.__widgets["sbutton"] = None  #: Optional[tk.Button]
        self.__widgets["spanel"] = None  #: Optional[VerticalScrolledFrame]

        # init log subsystem
        if isinstance(log_queue, (Queue, SimpleQueue)):
            self.logger = LogClient(log_queue)
        else:
            raise Raise.error(
                f"Queue or SimpleQueue type expected, '{type(log_queue)}' received.",
                TypeError,
                self.__class__.__name__,
                inspect.currentframe(),
            )

        if isinstance(data, RscanData):
            self.__data = data
            self.debug(inspect.currentframe(), f"{self.__data}")
        else:
            raise Raise.error(
                f"RscanData type expected, '{type(data)}' received",
                TypeError,
                self.__class__.__name__,
                inspect.currentframe(),
            )

        # Euclid's algorithm for calculating the length of vectors
        if isinstance(euclid_alg, Euclid):
            self.__tools["math"] = euclid_alg
        else:
            raise Raise.error(
                f"Euclid type expected, '{type(euclid_alg)}' received",
                TypeError,
                self.__class__.__name__,
                inspect.currentframe(),
            )

        self.debug(inspect.currentframe(), "Initialize dataset")

        # list of found systems: [[system, frame, label with name],...]
        self.__stars = []

        if self.__data.starsystem.name is not None:
            self.__start = self.__data.starsystem

        # starting worker th
        self.__rscan_qth = SimpleQueue()
        self.__rscan_th = Thread(
            target=self.th_worker, name=f"{self.__data.pluginname} worker"
        )
        self.__rscan_th.daemon = True
        self.__rscan_th.start()

        # fonts configure
        self.__fonts = {
            "bold": font.Font(
                family="Helvetica",
                size=10,
                weight=font.BOLD,
                overstrike=False,
            ),
            "normal": font.Font(family="Helvetica", size=10, overstrike=False),
            "strike": font.Font(family="Helvetica", size=10, overstrike=True),
        }

        # create window
        self.__frame_build()

        self.debug(inspect.currentframe(), "Constructor work done.")

    # def __del__(self):
    #     """Destroy datasets on close."""
    #     self.debug(
    #         inspect.currentframe(),
    #         f"Delete window: {self.title()}"
    #     )
    #
    def __frame_build(self) -> None:
        """Create window."""
        self.title(self.__data.pluginname)
        self.geometry("600x400")
        # grid configure
        self.columnconfigure(0, weight=1)
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
        label.grid(row=r_label_idx)

        # create command panel
        command_frame = tk.LabelFrame(self, text=" Generator ")
        command_frame.grid(
            row=r_comm_idx, padx=5, pady=5, ipadx=2, ipady=2, sticky=tk.EW
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
        if self.__data.starsystem.name is not None:
            system_name.delete(0, tk.END)
            system_name.insert(0, self.__data.starsystem.name)
        self.__widgets["system"] = system_name
        tk.Label(command_frame, text="Radius:").grid(row=0, column=2, sticky=tk.E)
        radius = tk.Entry(command_frame, textvariable=tk.StringVar(value="50"), width=5)
        radius.grid(row=0, column=3, sticky=tk.W)
        self.__widgets["radius"] = radius
        bgenerator = tk.Button(command_frame, text="Search", command=self.__generator)
        bgenerator.grid(row=0, column=4, sticky=tk.E)
        CreateToolTip(bgenerator, "Locate visited systems that have not been explored.")
        self.__widgets["sbutton"] = bgenerator

        # create data panel
        data_frame = tk.LabelFrame(self, text=" Flight route ")
        data_frame.grid(row=r_data_idx, padx=5, pady=5, sticky=tk.NSEW)
        self.__widgets["fdata"] = data_frame

        # create scrolled panel
        spanel = VerticalScrolledFrame(data_frame)
        spanel.pack(ipadx=1, ipady=1, fill=tk.BOTH, expand=tk.TRUE)
        self.__widgets["spanel"] = spanel

        # create status panel
        status_frame = tk.LabelFrame(self, text="")
        status_frame.grid(row=r_stat_idx, padx=5, pady=5, sticky=tk.EW)
        status_string = tk.StringVar()
        status = tk.Label(status_frame, textvariable=status_string)
        status.pack(side=tk.LEFT)
        self.__widgets["status"] = status_string

        # closing event
        self.protocol("WM_DELETE_WINDOW", self.__on_closing)

    def __on_closing(self) -> None:
        """Run on closing event."""
        self.debug(inspect.currentframe(), "Window is closing now.")
        self.__closed = True
        self.__rscan_qth.put(None)
        self.destroy()

    def __to_clipboard(self, clip_text: str) -> None:
        """Copy txt to clipboard."""
        # USE: command=lambda: self.__to_clipboard('txt')
        self.debug(inspect.currentframe(), f"string: '{clip_text}'")
        if self.__tools["clip"].is_tool:
            self.__tools["clip"].copy(clip_text)
        else:
            clip = tk.Tk()
            clip.withdraw()
            clip.clipboard_clear()
            clip.clipboard_append(clip_text)
            clip.update()
            clip.destroy()

    def __generator(self) -> None:
        """Command button callback."""
        # get variables
        system = self.__widgets["system"].get()
        radius = self.__widgets["radius"].get()
        self.debug(inspect.currentframe(), f"system: {system}, type:{type(system)}")
        self.debug(inspect.currentframe(), f"radius: {radius}, type:{type(radius)}")

        if not system or not radius:
            msg: str = ""
            if not system:
                msg = "System"
            if not radius and msg:
                msg = f"{msg} and radius"
            elif not radius:
                msg = "Radius"
            msg = f"{msg} must be set for processing request."
            self.status = msg
            return

        if radius and not Numbers().is_float(radius):
            msg = "Radius must be set as decimal expression."
            self.status = msg
            return

        # build thread object for worker
        obj = ThSystemSearch(self, self.logger.queue, self.__data, self.__tools["math"])
        obj.radius = radius
        # initializing start system for search engine
        if self.__start is None:
            self.__start = StarsSystem(name=system)
        if self.__start.name != system:
            self.__start.name = None
            self.__start.name = system
        obj.start_system = self.__start

        # put it into queue
        self.__rscan_qth.put(obj)

    def __disable_button(self, flag: bool) -> None:
        """Disable generator button on working time."""
        if self.__widgets["sbutton"] is None:
            return
        if isinstance(flag, bool):
            if flag:
                self.__widgets["sbutton"].config(state=tk.DISABLED)
            else:
                self.__widgets["sbutton"].config(state=tk.ACTIVE)

    def th_worker(self) -> None:
        """Run thread for getting data and computing results."""
        pname: str = self.__data.pluginname
        cname: str = self.__class__.__name__
        if self.logger:
            self.logger.info = f"{pname}->{cname}: Starting worker..."
        while not self.__data.shutting_down:
            item: ThSystemSearch = self.__rscan_qth.get(True)
            if item is None:
                break
            self.__disable_button(True)
            if self.logger:
                self.logger.info = (
                    f"{pname}->{cname}: Get new search work for "
                    f"{item.start_system.name} with radius: {item.radius}ly"
                )
            tstart: float = time.time()
            # start processing request
            item.start()
            item.join()
            # getting results
            tstop: float = time.time()
            if self.logger:
                self.logger.info = (
                    f"{pname}->{cname}: Work is done in: {int(tstop-tstart)}s"
                )
            self.__process_work_output(item.get_result)
            self.__disable_button(False)
        if self.logger:
            self.logger.info = f"{pname}->{cname}: worker finished."

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
        # frame = tk.Frame(self.__widgets['fdata'])
        frame = tk.Frame(self.__widgets["spanel"].interior)
        frame.pack(fill=tk.X)
        list_object.append(frame)

        # create count label
        tk.Label(frame, text=f" {count}: ", font=self.__fonts["normal"]).pack(
            side=tk.LEFT
        )

        # create name label [2]
        lname = tk.Label(frame, text=f"{item.name}")
        lname.pack(side=tk.LEFT)
        lname["font"] = self.__fonts["normal"]
        list_object.append(lname)

        # create range label
        distance: str = "??"
        jump = 50
        if "distance" in item.data:
            distance = f"{item.data['distance']:.2f}"
        ljump = tk.Label(frame, text=f"[{distance:} ly]", font=self.__fonts["normal"])
        ljump.pack(side=tk.LEFT)
        if self.__data.jumprange:
            jump: float = self.__data.jumprange - 4
        if "distance" in item.data and item.data["distance"] > jump:
            ljump["font"] = self.__fonts["bold"]
            ljump["fg"] = "red"
            CreateToolTip(
                ljump,
                "Warning. The calculated distance exceeded the ship's maximum single jump distance.",
            )
        # permission
        # self.debug(inspect.currentframe(), message=f'{item}')
        if "requirepermit" in item.data and item.data["requirepermit"]:
            lpermit = tk.Label(frame, text=f"P")
            lpermit.pack(side=tk.LEFT)
            CreateToolTip(
                lpermit,
                "Warning. Required permissions to enter this system.",
            )
        # create clipboard button
        btn = tk.Button(
            frame,
            text="C",
            command=lambda: self.__to_clipboard(item.name),
            font=self.__fonts["normal"],
        )
        btn.pack(side=tk.RIGHT)
        CreateToolTip(btn, "Copy to clipboard")

        # finish
        self.__stars.append(list_object)

    def dialog_update(self):
        """Update current position in system list."""
        if self.__data.shutting_down:
            self.__rscan_qth.put(None)

        # update located system
        for item in self.__stars:
            if item[0].name == self.__data.starsystem.name:
                item[2]["font"] = self.__fonts["strike"]

    def debug(self, currentframe, message="") -> None:
        """Build debug message."""
        pname = f"{self.__data.pluginname}"
        cname = f"{self.__class__.__name__}"
        mname = f"{currentframe.f_code.co_name}"
        if message != "":
            message = f": {message}"
        if self.logger:
            self.logger.debug = f"{pname}->{cname}.{mname}{message}"

    @property
    def is_closed(self) -> bool:
        """Check, if window is closed."""
        return self.__closed

    @property
    def status(self) -> Optional[tk.StringVar]:
        """Return status object."""
        return self.__widgets["status"]

    @status.setter
    def status(self, message) -> None:
        """Set status message."""
        if self.__widgets["status"] is not None:
            if message:
                self.__widgets["status"].set(f"{message}")
            else:
                self.__widgets["status"].set("")


class EdrsDialog(MLogClient, NoDynamicAttributes):
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
        log_queue: Queue or SimpleQueue,
        data: RscanData,
    ) -> None:
        """Initialize datasets."""
        # init log subsystem
        if isinstance(log_queue, (Queue, SimpleQueue)):
            self.logger = LogClient(log_queue)
        else:
            raise Raise.error(
                f"Queue or SimpleQueue type expected, '{type(log_queue)}' received.",
                TypeError,
                self.__class__.__name__,
                inspect.currentframe(),
            )

        if isinstance(data, RscanData):
            self.__data = data
            self.debug(inspect.currentframe(), f"{self.__data}")
        else:
            raise Raise.error(
                f"RscanData type expected, '{type(data)}' received",
                TypeError,
                self.__class__.__name__,
                inspect.currentframe(),
            )

        if isinstance(parent, tk.Frame):
            self.__parent = parent
        else:
            raise Raise.error(
                f"tk.Frame type expected, '{type(parent)}' received",
                TypeError,
                self.__class__.__name__,
                inspect.currentframe(),
            )

        self.__windows = []

        # tools
        self.__tools = {}
        self.__tools["euclid"] = Euclid(log_queue, data)
        self.__tools["euclid"].benchmark()

    # def __del__(self):
    #     """Destroy datasets on close."""
    #     for window in self.__windows:
    #         window.close()
    #         del window

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
            inspect.currentframe(),
            f"Update init, found {len(self.__windows)} windows",
        )
        for window in self.__windows:
            if not window.is_closed:
                window.dialog_update()

    def __bt_callback(self) -> None:
        """Run main button callback."""
        self.debug(inspect.currentframe(), "click!")
        # purge closed window from list
        for window in self.__windows:
            if window.is_closed:
                self.__windows.remove(window)
        # create new window
        esd = EdrsScanDialog(self.logger.queue, self.__data, self.__tools["euclid"])
        if self.__data.starsystem.name is not None:
            esd.title(f"{self.__data.pluginname}: {self.__data.starsystem.name}")

        self.__windows.append(esd)
        self.debug(
            inspect.currentframe(),
            f"numbers of windows: {len(self.__windows)}",
        )

    def debug(self, currentframe: Optional[FrameType], message: str = "") -> None:
        """Build debug message."""
        pname = f"{self.__data.pluginname}"
        cname = f"{self.__class__.__name__}"
        mname = f"{currentframe.f_code.co_name}"
        if message != "":
            message = f": {message}"
        if self.logger:
            self.logger.debug = f"{pname}->{cname}.{mname}{message}"


class ToolTip:
    """Simple ToolTip class."""

    def __init__(self, widget: tk.Toplevel, text: str = None) -> None:
        """Create class object."""

        def on_enter(event: tk.Event) -> None:
            """Call freom <Enter> event.

            parameters:
                event [tk.Event]
            """
            self.tooltip = tk.Toplevel()
            self.tooltip.overrideredirect(True)
            self.tooltip.geometry(f"+{event.x_root+15}+{event.y_root+10}")

            self.label = tk.Label(self.tooltip, text=self.text)
            self.label.pack()

        def on_leave(event: tk.Event) -> None:
            """Call from <Leave> event.

            parameters:
                event [tk.Event]
            """
            self.tooltip.destroy()

        self.widget = widget
        self.text = text

        self.widget.bind("<Enter>", on_enter)
        self.widget.bind("<Leave>", on_leave)


class VerticalScrolledFrame(tk.Frame):
    """A pure Tkinter scrollable frame that actually works!
    * Use the 'interior' attribute to place widgets inside the scrollable frame.
    * Construct and pack/place/grid normally.
    * This frame only allows vertical scrolling.
    """

    def __init__(self, parent, *args, **kw) -> None:
        tk.Frame.__init__(self, parent, *args, **kw)

        # Create a canvas object and a vertical scrollbar for scrolling it.
        # vscrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL)
        vscrollbar = tk.Scrollbar(self, orient=tk.VERTICAL)
        vscrollbar.pack(fill=tk.Y, side=tk.RIGHT, expand=tk.FALSE)
        canvas = tk.Canvas(
            self, bd=0, highlightthickness=0, yscrollcommand=vscrollbar.set
        )
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.TRUE)
        vscrollbar.config(command=canvas.yview)

        # Reset the view
        canvas.xview_moveto(0)
        canvas.yview_moveto(0)

        # Create a frame inside the canvas which will be scrolled with it.
        # self.interior = interior = ttk.Frame(canvas)
        self.interior = interior = tk.Frame(canvas)
        interior_id: int = canvas.create_window(0, 0, window=interior, anchor=tk.NW)

        # Track changes to the canvas and frame width and sync them,
        # also updating the scrollbar.
        def _configure_interior(event) -> None:
            # Update the scrollbars to match the size of the inner frame.
            size: tuple[int, int] = (
                interior.winfo_reqwidth(),
                interior.winfo_reqheight(),
            )
            canvas.config(scrollregion="0 0 %s %s" % size)
            if interior.winfo_reqwidth() != canvas.winfo_width():
                # Update the canvas's width to fit the inner frame.
                canvas.config(width=interior.winfo_reqwidth())

        interior.bind("<Configure>", _configure_interior)

        def _configure_canvas(event) -> None:
            if interior.winfo_reqwidth() != canvas.winfo_width():
                # Update the inner frame's width to fill the canvas.
                canvas.itemconfigure(interior_id, width=canvas.winfo_width())

        canvas.bind("<Configure>", _configure_canvas)


# #[EOF]#######################################################################
