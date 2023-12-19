# -*- coding: UTF-8 -*-
"""
  Author:  Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
  Created: 19.12.2023

  Purpose: EDRS dialogs classes.
"""

import time
import tkinter as tk
from inspect import currentframe
from queue import Queue
from threading import Thread
from tkinter import ttk
from typing import List, Optional
from types import FrameType

from jsktoolbox.raisetool import Raise


from rscan_libs.cartesianmath import Euclid
from rscan_libs.data import RscanData
from rscan_libs.base_logs import BLogClient
from rscan_libs.stars import StarsSystem
from rscan_libs.system import Clip, LogClient
from rscan_libs.th import ThSystemSearch
from rscan_libs.tools import Numbers
from rscan_libs.dialogs_tools import CreateToolTip
from rscan_libs.dialogs_helper import DialogKeys


class EdrsScanDialog(tk.Toplevel, BLogClient):
    """Create new  window."""

    _w = None
    widgetName = None
    master = None
    tk = None
    _name = None
    children = None

    def __init__(
        self,
        log_queue: Queue,
        data: RscanData,
        euclid_alg: Euclid,
        master=None,
    ) -> None:
        """Initialize dataset."""
        super().__init__(master=master)

        # tools
        self._data[DialogKeys.TOOLS] = {DialogKeys.CLIP: None, DialogKeys.MATH: None}
        self._data[DialogKeys.TOOLS][DialogKeys.CLIP] = Clip()

        # witgets declaration
        self._data[DialogKeys.WIDGETS] = {}
        self._data[DialogKeys.WIDGETS][DialogKeys.STATUS] = None
        self._data[DialogKeys.WIDGETS][DialogKeys.FDATA] = None
        self._data[DialogKeys.WIDGETS][DialogKeys.SYSTEM] = None
        self._data[DialogKeys.WIDGETS][DialogKeys.RADIUS] = None
        self._data[DialogKeys.WIDGETS][DialogKeys.SBUTTON] = None
        self._data[DialogKeys.WIDGETS][DialogKeys.SPANEL] = None

        # init log subsystem
        if isinstance(log_queue, Queue):
            self.logger = LogClient(log_queue)
        else:
            raise Raise.error(
                f"Queue type expected, '{type(log_queue)}' received.",
                TypeError,
                self._c_name,
                currentframe(),
            )

        if isinstance(data, RscanData):
            self._data[DialogKeys.RDATA] = data
            self.debug(currentframe(), f"{self._data[DialogKeys.RDATA]}")
        else:
            raise Raise.error(
                f"RscanData type expected, '{type(data)}' received",
                TypeError,
                self._c_name,
                currentframe(),
            )

        # Euclid's algorithm for calculating the length of vectors
        if isinstance(euclid_alg, Euclid):
            self._data[DialogKeys.TOOLS][DialogKeys.MATH] = euclid_alg
        else:
            raise Raise.error(
                f"Euclid type expected, '{type(euclid_alg)}' received",
                TypeError,
                self._c_name,
                currentframe(),
            )

        self.debug(currentframe(), "Initialize dataset")

        # list of found systems: [[system, frame, label with name],...]
        self._data[DialogKeys.STARS] = []

        if self._data[DialogKeys.RDATA].starsystem.name is not None:
            self._data[DialogKeys.START] = self._data[DialogKeys.RDATA].starsystem

        # starting worker th
        self._data[DialogKeys.QTH] = Queue()
        self._data[DialogKeys.RTH] = Thread(
            target=self.th_worker,
            name=f"{self._data[DialogKeys.RDATA].pluginname} worker",
        )
        self._data[DialogKeys.RTH].daemon = True
        self._data[DialogKeys.RTH].start()

        # fonts configure
        self._data[DialogKeys.FONTS] = {
            "bold": tk.font.Font(
                family="Helvetica",
                size=10,
                weight=tk.font.BOLD,
                overstrike=0,
            ),
            "normal": tk.font.Font(family="Helvetica", size=10, overstrike=0),
            "strike": tk.font.Font(family="Helvetica", size=10, overstrike=1),
        }

        # create window
        self.__frame_build()

        self.debug(currentframe(), "Constructor work done.")

    def __frame_build(self) -> None:
        """Create window."""
        self.title(self._data[DialogKeys.RDATA].pluginname)
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
        system_name = tk.Entry(command_frame, textvariable="")
        system_name.grid(row=0, column=1, sticky=tk.EW)
        if self._data[DialogKeys.RDATA].starsystem.name is not None:
            system_name.delete(0, tk.END)
            system_name.insert(0, self._data[DialogKeys.RDATA].starsystem.name)
        self._data[DialogKeys.WIDGETS][DialogKeys.SYSTEM] = system_name
        tk.Label(command_frame, text="Radius:").grid(row=0, column=2, sticky=tk.E)
        radius = tk.Entry(command_frame, textvariable=tk.StringVar(value="50"), width=5)
        radius.grid(row=0, column=3, sticky=tk.W)
        self._data[DialogKeys.WIDGETS][DialogKeys.RADIUS] = radius
        bgenerator = tk.Button(command_frame, text="Search", command=self.__generator)
        bgenerator.grid(row=0, column=4, sticky=tk.E)
        CreateToolTip(bgenerator, "Locate visited systems that have not been explored.")
        self._data[DialogKeys.WIDGETS][DialogKeys.SBUTTON] = bgenerator

        # create data panel
        data_frame = tk.LabelFrame(self, text=" Flight route ")
        data_frame.grid(row=r_data_idx, padx=5, pady=5, sticky=tk.NSEW)
        self._data[DialogKeys.WIDGETS][DialogKeys.FDATA] = data_frame

        # create scrolled panel
        spanel = VerticalScrolledFrame(data_frame)
        spanel.pack(ipadx=1, ipady=1, fill=tk.BOTH, expand=tk.TRUE)
        self._data[DialogKeys.WIDGETS][DialogKeys.SPANEL] = spanel

        # create status panel
        status_frame = tk.LabelFrame(self, text="")
        status_frame.grid(row=r_stat_idx, padx=5, pady=5, sticky=tk.EW)
        status_string = tk.StringVar()
        status = tk.Label(status_frame, textvariable=status_string)
        status.pack(side=tk.LEFT)
        self._data[DialogKeys.WIDGETS][DialogKeys.STATUS] = status_string

        # init flags
        self._data[DialogKeys.CLOSED] = False

        # closing event
        self.protocol("WM_DELETE_WINDOW", self.__on_closing)

    def __on_closing(self) -> None:
        """Run on closing event."""
        self.debug(currentframe(), "Window is closing now.")
        self._data[DialogKeys.CLOSED] = True
        self._data[DialogKeys.QTH].put(None)
        self.destroy()

    def __to_clipboard(self, clip_text: str) -> None:
        """Copy txt to clipboard."""
        # USE: command=lambda: self.__to_clipboard('txt')
        self.debug(currentframe(), f"string: '{clip_text}'")
        if self._data[DialogKeys.TOOLS][DialogKeys.CLIP].is_tool:
            self._data[DialogKeys.TOOLS][DialogKeys.CLIP].copy(clip_text)
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
        system = self._data[DialogKeys.WIDGETS][DialogKeys.SYSTEM].get()
        radius = self._data[DialogKeys.WIDGETS][DialogKeys.RADIUS].get()
        self.debug(currentframe(), f"system: {system}, type:{type(system)}")
        self.debug(currentframe(), f"radius: {radius}, type:{type(radius)}")

        if not system or not radius:
            msg = ""
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
        obj = ThSystemSearch(
            self,
            self.logger.queue,
            self._data[DialogKeys.RDATA],
            self._data[DialogKeys.TOOLS][DialogKeys.MATH],
        )
        obj.radius = radius
        # initializing start system for search engine
        if DialogKeys.START not in self._data or self._data[DialogKeys.START] is None:
            self._data[DialogKeys.START] = StarsSystem(name=system)
        if self._data[DialogKeys.START].name != system:
            self._data[DialogKeys.START].name = None
            self._data[DialogKeys.START].name = system
        obj.start_system = self._data[DialogKeys.START]

        # put it into queue
        self._data[DialogKeys.QTH].put(obj)

    def __disable_button(self, flag: bool) -> None:
        """Disable generator button on working time."""
        if self._data[DialogKeys.WIDGETS][DialogKeys.SBUTTON] is None:
            return
        if isinstance(flag, bool):
            if flag:
                self._data[DialogKeys.WIDGETS][DialogKeys.SBUTTON].config(
                    state=tk.DISABLED
                )
            else:
                self._data[DialogKeys.WIDGETS][DialogKeys.SBUTTON].config(
                    state=tk.ACTIVE
                )

    def th_worker(self) -> None:
        """Run thread for getting data and computing results."""
        pname = self._data[DialogKeys.RDATA].pluginname
        cname = self._c_name
        self.logger.info = f"{pname}->{cname}: Starting worker..."
        while not self._data[DialogKeys.RDATA].shutting_down:
            item = self._data[DialogKeys.QTH].get(True)
            if item is None:
                break
            self.__disable_button(True)
            self.logger.info = (
                f"{pname}->{cname}: Get new search work for "
                f"{item.start_system.name} with radius: {item.radius}ly"
            )
            tstart = time.time()
            # start processing request
            item.start()
            item.join()
            # getting results
            tstop = time.time()
            self.logger.info = (
                f"{pname}->{cname}: Work is done in: {int(tstop-tstart)}s"
            )
            self.__process_work_output(item.get_result)
            self.__disable_button(False)
        self.logger.info = f"{pname}->{cname}: worker finished."

    def __process_work_output(self, systems: Optional[List]) -> None:
        """Build frame with found systems."""
        # destroy previous data
        for item in self._data[DialogKeys.STARS]:
            item[1].pack_forget()
            item[1].destroy()
        self._data[DialogKeys.STARS] = []
        # generate new list
        count = 0
        for system in systems:
            count += 1
            self.__build_row_frame(count, system)

    def __build_row_frame(self, count: int, item: StarsSystem) -> None:
        """Construct and return Frame row for search dialog."""
        list_object = []
        # StarsSystem [0]
        list_object.append(item)

        # create frame [1]
        # frame = tk.Frame(self._data[DialogKeys.WIDGETS]['fdata'])
        frame = tk.Frame(self._data[DialogKeys.WIDGETS][DialogKeys.SPANEL].interior)
        frame.pack(fill=tk.X)
        list_object.append(frame)

        # create count label
        tk.Label(
            frame, text=f" {count}: ", font=self._data[DialogKeys.FONTS]["normal"]
        ).pack(side=tk.LEFT)

        # create name label [2]
        lname = tk.Label(frame, text=f"{item.name}")
        lname.pack(side=tk.LEFT)
        lname["font"] = self._data[DialogKeys.FONTS]["normal"]
        list_object.append(lname)

        # create range label
        distance = "??"
        jump = 50
        if "distance" in item.data:
            distance = f"{item.data['distance']:.2f}"
        ljump = tk.Label(
            frame, text=f"[{distance:} ly]", font=self._data[DialogKeys.FONTS]["normal"]
        )
        ljump.pack(side=tk.LEFT)
        if self._data[DialogKeys.RDATA].jumprange:
            jump = self._data[DialogKeys.RDATA].jumprange - 4
        if "distance" in item.data and item.data["distance"] > jump:
            ljump["font"] = self._data[DialogKeys.FONTS]["bold"]
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
            font=self._data[DialogKeys.FONTS]["normal"],
        )
        btn.pack(side=tk.RIGHT)
        CreateToolTip(btn, "Copy to clipboard")

        # finish
        self._data[DialogKeys.STARS].append(list_object)

    def dialog_update(self) -> None:
        """Update current position in system list."""
        if self._data[DialogKeys.RDATA].shutting_down:
            self._data[DialogKeys.QTH].put(None)

        # update located system
        for item in self._data[DialogKeys.STARS]:
            if item[0].name == self._data[DialogKeys.RDATA].starsystem.name:
                item[2]["font"] = self._data[DialogKeys.FONTS]["strike"]

    def debug(self, currentframe: FrameType, message: str = "") -> None:
        """Build debug message."""
        pname = f"{self._data[DialogKeys.RDATA].pluginname}"
        cname = f"{self._c_name}"
        mname = f"{currentframe.f_code.co_name}"
        if message != "":
            message = f": {message}"
        self.logger.debug = f"{pname}->{cname}.{mname}{message}"

    @property
    def is_closed(self) -> bool:
        """Check, if window is closed."""
        return self._data[DialogKeys.CLOSED]

    @property
    def status(self):
        """Return status object."""
        if self._data[DialogKeys.WIDGETS][DialogKeys.STATUS] is None:
            return tk.StringVar()
        return self._data[DialogKeys.WIDGETS][DialogKeys.STATUS]

    @status.setter
    def status(self, message: str) -> None:
        """Set status message."""
        if self._data[DialogKeys.WIDGETS][DialogKeys.STATUS] is not None:
            if message:
                self._data[DialogKeys.WIDGETS][DialogKeys.STATUS].set(f"{message}")
            else:
                self._data[DialogKeys.WIDGETS][DialogKeys.STATUS].set("")


class EdrsDialog(BLogClient):
    """Create config dialog for plugin."""

    def __init__(
        self,
        parent: tk.Frame,
        log_queue: Queue,
        data: RscanData,
    ) -> None:
        """Initialize datasets."""
        # init log subsystem
        if isinstance(log_queue, Queue):
            self.logger = LogClient(log_queue)
        else:
            raise Raise.error(
                f"Queue type expected, '{type(log_queue)}' received.",
                TypeError,
                self._c_name,
                currentframe(),
            )

        if isinstance(data, RscanData):
            self._data[DialogKeys.RDATA] = data
            self.debug(currentframe(), f"{self._data[DialogKeys.RDATA]}")
        else:
            raise Raise.error(
                f"RscanData type expected, '{type(data)}' received",
                TypeError,
                self._c_name,
                currentframe(),
            )

        if isinstance(parent, tk.Frame):
            self._data[DialogKeys.PARENT] = parent
        else:
            raise Raise.error(
                f"tk.Frame type expected, '{type(parent)}' received",
                TypeError,
                self._c_name,
                currentframe(),
            )

        self._data[DialogKeys.WINDOWS] = []

        # tools
        self._data[DialogKeys.TOOLS] = {}
        self._data[DialogKeys.TOOLS][DialogKeys.EUCLID] = Euclid(log_queue, data)
        self._data[DialogKeys.TOOLS][DialogKeys.EUCLID].benchmark()

    def button(self):
        """Give me the button for main application frame."""
        if DialogKeys.BUTTON not in self._data or self._data[DialogKeys.BUTTON] is None:
            self._data[DialogKeys.BUTTON] = ttk.Button(
                self._data[DialogKeys.PARENT],
                text="Scanner",
                command=self.__bt_callback,
                default=tk.ACTIVE,
                # state=tk.DISABLED
            )
            self._data[DialogKeys.BUTTON].grid(sticky=tk.NSEW)
        return self._data[DialogKeys.BUTTON]

    def dialog_update(self) -> None:
        """Do update for windows."""
        self.debug(
            currentframe(),
            f"Update init, found {len(self._data[DialogKeys.WINDOWS])} windows",
        )
        for window in self._data[DialogKeys.WINDOWS]:
            if not window.is_closed:
                window.dialog_update()

    def __bt_callback(self) -> None:
        """Run main button callback."""
        self.debug(currentframe(), "click!")
        # purge closed window from list
        for window in self._data[DialogKeys.WINDOWS]:
            if window.is_closed:
                self._data[DialogKeys.WINDOWS].remove(window)
        # create new window
        esd = EdrsScanDialog(
            self.logger.queue,
            self._data[DialogKeys.RDATA],
            self._data[DialogKeys.TOOLS][DialogKeys.EUCLID],
        )
        if self._data[DialogKeys.RDATA].starsystem.name is not None:
            esd.title(
                f"{self._data[DialogKeys.RDATA].pluginname}: {self._data[DialogKeys.RDATA].starsystem.name}"
            )

        self._data[DialogKeys.WINDOWS].append(esd)
        self.debug(
            currentframe(),
            f"numbers of windows: {len(self._data[DialogKeys.WINDOWS])}",
        )

    def debug(self, currentframe: FrameType, message: str = "") -> None:
        """Build debug message."""
        pname = f"{self._data[DialogKeys.RDATA].pluginname}"
        cname = f"{self._c_name}"
        mname = f"{currentframe.f_code.co_name}"
        if message != "":
            message = f": {message}"
        self.logger.debug = f"{pname}->{cname}.{mname}{message}"


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
        interior_id = canvas.create_window(0, 0, window=interior, anchor=tk.NW)

        # Track changes to the canvas and frame width and sync them,
        # also updating the scrollbar.
        def _configure_interior(event) -> None:
            # Update the scrollbars to match the size of the inner frame.
            size = (interior.winfo_reqwidth(), interior.winfo_reqheight())
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
