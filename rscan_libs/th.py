# -*- coding: UTF-8 -*-
"""
  Author:  Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
  Created: 19.12.2023

  Purpose: system search class.
"""

from inspect import currentframe
from queue import Queue, SimpleQueue
from threading import Event, Thread
from typing import Any, Dict, List, Optional, Union
from types import FrameType

from jsktoolbox.raisetool import Raise

from rscan_libs.cartesianmath import Euclid
from rscan_libs.data import RscanData
from rscan_libs.base_log import BLogClient
from rscan_libs.stars import StarsSystem
from rscan_libs.system import LogClient
from rscan_libs.tools import AlgGenetic, AlgTsp, Url


class ThSystemSearch(Thread, BLogClient):
    """Thread system search engine."""

    __slots__: List[str] = [
        "__parent",
        "__data",
        "__math",
        "__stop_event",
        "__start_system",
        "__radius",
        "__found",
    ]

    def __init__(
        self,
        parent,
        log_queue: Union[Queue, SimpleQueue],
        data: RscanData,
        euclid_alg: Euclid,
    ) -> None:
        """Create object instance of class."""
        Thread.__init__(self, name=self.__class__.__name__)
        self.__stop_event = Event()
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
        self.__data: RscanData = data
        self.debug(currentframe(), f"{self.__data}")

        # Euclid's algorithm for calculating the length of vectors
        if not isinstance(euclid_alg, Euclid):
            raise Raise.error(
                f"Euclid type expected, '{type(euclid_alg)}' received",
                TypeError,
                self.__class__.__name__,
                currentframe(),
            )
        self.__math: Euclid = euclid_alg

        # initialize private variables
        self.__parent = parent
        self.__start_system: StarsSystem = None  # type: ignore
        self.__radius: int = None  # type: ignore
        self.__found: List[StarsSystem] = []

    def run(self) -> None:
        """Run the work."""
        p_name: str = self.__data.plugin_name
        c_name: str = self.__class__.__name__
        self.logger.info = f"{p_name}->{c_name}: Starting new work..."
        # build radius query
        query_url: Optional[str] = self.__build_radius_query()
        if query_url is None:
            return
        # create query object
        url = Url()
        # querying starts database
        systems: List[Dict[str, Any]] = url.url_query(query_url)
        if self.logger:
            self.logger.debug = f"Systems from JSON: {systems}"
        if not systems:
            return
        # filtering system
        r_systems: Optional[List[StarsSystem]] = self.__build_radius_systems_list(
            systems
        )
        # self.debug(
        #     currentframe(),
        #     f"Search result: {systems}"
        # )
        if not r_systems:
            self.status("0 systems found.")
            return
        # traceroute optimization
        self.status(
            f"{len(systems)} systems found, flight route calculations in progress..."
        )
        systems_out: List[StarsSystem] = self.__flight_route_systems(r_systems)
        self.debug(currentframe(), f"Search result: {systems_out}")
        # put it into result list
        d_sum: float = 0.0
        for item in systems_out:
            d_sum += item.data["distance"]
            self.__found.append(item)
        # work done
        self.status(
            f"{len(systems_out)} systems found, calculations done. Final distance: {d_sum:.2f} ly"
        )
        self.logger.info = f"{p_name}->{c_name}: Done."

    def debug(self, currentframe: Optional[FrameType], message: str = "") -> None:
        """Build debug message."""
        p_name: str = f"{self.__data.plugin_name}"
        c_name: str = f"{self.__class__.__name__}"
        m_name: str = f"{currentframe.f_code.co_name}" if currentframe else ""
        if message != "":
            message = f": {message}"
        self.logger.debug = f"{p_name}->{c_name}.{m_name}{message}"
        # currentframe()

    def status(self, message: Any) -> None:
        """Write message to status bar."""
        self.__parent.status = f"{message}"

    @property
    def stopped(self) -> bool:
        """Get stop event flag."""
        return self.__stop_event.isSet()

    def stop(self) -> None:
        """Set stop event."""
        if not self.stopped:
            self.debug(currentframe(), "Stopping event is set now.")
            self.__stop_event.set()

    @property
    def get_result(self) -> List:
        """Get list of StarsSystem objects."""
        return self.__found

    @property
    def start_system(self) -> StarsSystem:
        """Give me start system for search radius."""
        return self.__start_system

    @start_system.setter
    def start_system(self, value: StarsSystem) -> None:
        if not isinstance(value, StarsSystem):
            raise Raise.error(
                f"StarsSystem type expected, '{type(value)}' received.",
                TypeError,
                self.__class__.__name__,
                currentframe(),
            )
        self.__start_system = value

    @property
    def radius(self) -> Optional[int]:
        """Give me radius value for system search from start_system position."""
        return self.__radius

    @radius.setter
    def radius(self, value: Union[int, float]) -> None:
        try:
            self.__radius = int(value)
        except Exception as ex:
            self.debug(currentframe(), f"Unexpected exception: {ex}")
        if self.radius is None:
            self.logger.warning = "Invalid radius value, set default: 50 ly."
            self.__radius = 50
        elif self.radius > 100:
            self.logger.warning = "Radius too high, set max value: 100 ly."
            self.__radius = 100
        elif self.radius < 5:
            self.logger.warning = "Radius too low, set min value: 5 ly."
            self.__radius = 5
        else:
            self.logger.info = f"Radius is set to: {self.radius} ly."

    def __progress(self, cur: int, systems_count: int) -> None:
        """Set progress status in parent."""
        if systems_count == 0:
            self.status("Found 0 systems")
            return
        self.status(
            f"{systems_count} systems found, analysis progress: {int( cur * 100 / systems_count )} %"
        )

    def __build_radius_query(self) -> Optional[str]:
        """Create URL query for systems data."""
        url = Url()

        # checking needed variables
        if self.start_system is None or self.radius is None:
            raise Raise.error(
                "Needed variables not initialized properly.",
                TypeError,
                self.__class__.__name__,
                currentframe(),
            )

        # updating data for start system, if needed
        if self.start_system.pos_x is None:
            out = url.system_query(self.start_system)
            self.debug(currentframe(), f"Start System data: {out}")
            if out:
                self.start_system.update_from_edsm(out)

        return url.radius_url(self.start_system, self.radius)

    def __build_radius_systems_list(
        self, systems: List[Dict[str, Any]]
    ) -> Optional[List[StarsSystem]]:
        """Build filtered systems list from EDSM API output."""
        out: List[StarsSystem] = []
        systems_count: int = len(systems)
        cur_count = 0
        count = 0
        for item in systems:
            cur_count += 1
            self.__progress(cur_count, systems_count)
            if "bodyCount" in item and item["bodyCount"] is None:
                count += 1
                system = StarsSystem()
                system.update_from_edsm(item)
                system.data["bodies"] = None
                self.debug(
                    currentframe(),
                    f"EDSM system nr:{count} {system}",
                )
                out.append(system)

        if self.logger:
            self.logger.info = f"Found {count} systems"
        return out

    def __flight_route_systems(self, systems: List[StarsSystem]) -> List[StarsSystem]:
        """Try to find the optimal order of flight."""
        jump = 50
        out: List[StarsSystem] = []
        if self.__data.jump_range is not None:
            jump: int = int(self.__data.jump_range) - 4
        if len(systems) > 10:
            alg = AlgGenetic(
                self.start_system,
                systems,
                jump,
                self.logger.queue,
                self.__math,
                self.__data.plugin_name,
            )
            alg.run()
            for item in alg.get_final:
                out.append(item)
        elif len(systems) > 1:
            alg = AlgTsp(
                self.start_system,
                systems,
                jump,
                self.logger.queue,
                self.__math,
                self.__data.plugin_name,
            )
            alg.run()
            for item in alg.get_final:
                out.append(item)
        if out:
            return out
        return systems


# #[EOF]#######################################################################
