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

from rscan.jsktoolbox.raisetool import Raise
from rscan.jsktoolbox.basetool.threads import ThBaseObject
from rscan.jsktoolbox.attribtool import ReadOnlyClass
from rscan.jsktoolbox.edmctool.base import BLogClient
from rscan.jsktoolbox.edmctool.stars import StarsSystem
from rscan.jsktoolbox.edmctool.logs import LogClient
from rscan.jsktoolbox.edmctool.edsm import Url
from rscan.jsktoolbox.edmctool.edsm_keys import EdsmKeys
from rscan.jsktoolbox.edmctool.data import RscanData
from rscan.jsktoolbox.edmctool.math import (
    AlgGeneric,
    AlgGenetic,
    Euclid,
    AlgGenetic2,
    AlgTsp,
    AlgAStar,
    AlgSimulatedAnnealing,
)


class _Keys(object, metaclass=ReadOnlyClass):
    """Keys for system search class."""

    R_DATA: str = "__rscan_data__"
    MATH: str = "__ss_math__"
    PARENT: str = "__ss_parent__"
    START_SYSTEM: str = "__ss_start_system__"
    RADIUS: str = "__ss_radius__"
    FOUND: str = "__ss_found__"


class ThSystemSearch(Thread, ThBaseObject, BLogClient):
    """Thread system search engine."""

    def __init__(
        self,
        parent,
        log_queue: Union[Queue, SimpleQueue],
        data: RscanData,
        euclid_alg: Euclid,
    ) -> None:
        """Create object instance of class."""
        Thread.__init__(self, name=self._c_name)
        self._stop_event = Event()

        # init log subsystem
        self.logger = LogClient(log_queue)

        self._set_data(key=_Keys.R_DATA, value=data, set_default_type=RscanData)
        self.debug(currentframe(), f"{self._get_data(key=_Keys.R_DATA)}")

        # Euclid's algorithm for calculating the length of vectors
        self._set_data(
            key=_Keys.MATH,
            value=euclid_alg,
            set_default_type=Euclid,
        )

        # initialize private variables
        self._set_data(
            key=_Keys.PARENT,
            value=parent,
        )
        self._set_data(
            key=_Keys.START_SYSTEM,
            set_default_type=Optional[StarsSystem],
            value=None,
        )
        self._set_data(
            key=_Keys.RADIUS,
            set_default_type=int,
            value=10,
        )
        self._set_data(key=_Keys.FOUND, set_default_type=List, value=[])

    @property
    def __data(self) -> RscanData:
        """Return data object."""
        return self._get_data(key=_Keys.R_DATA)  # type: ignore

    @property
    def __found(self) -> List[StarsSystem]:
        return self._get_data(key=_Keys.FOUND)  # type: ignore

    @property
    def __math(self) -> Euclid:
        """Return math object."""
        return self._get_data(key=_Keys.MATH)  # type: ignore

    @property
    def __parent(self):
        return self._get_data(key=_Keys.PARENT)

    def run(self) -> None:
        """Run the work."""
        p_name: str = self.__data.plugin_name
        c_name: str = self._c_name
        self.logger.info = f"{p_name}->{c_name}: Starting new work..."
        # build radius query
        query_url: Optional[str] = self.__build_radius_query()
        # self.debug(
        #     currentframe(),
        #     f"query_url: {query_url}",
        # )
        if query_url is None:
            return
        # create query object
        url = Url()
        # querying starts database
        systems = url.url_query(query_url)
        if self.logger:
            self.logger.debug = f"Systems from JSON: {systems}"
        if not systems or not isinstance(systems, List):
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
            d_sum += item.data[EdsmKeys.DISTANCE]
            self.__found.append(item)
        # work done
        self.status(
            f"{len(systems_out)} systems found, calculations done. Final distance: {d_sum:.2f} ly"
        )
        self.logger.info = f"{p_name}->{c_name}: Done."

    def debug(self, currentframe: Optional[FrameType], message: str = "") -> None:
        """Build debug message."""
        p_name: str = f"{self.__data.plugin_name}"
        c_name: str = f"{self._c_name}"
        m_name: str = f"{currentframe.f_code.co_name}" if currentframe else ""
        if message != "":
            message = f": {message}"
        self.logger.debug = f"{p_name}->{c_name}.{m_name}{message}"
        # currentframe()

    def status(self, message: Any) -> None:
        """Write message to status bar."""
        self.__parent.status = f"{message}"  # type: ignore

    @property
    def stopped(self) -> bool:
        """Get stop event flag."""
        if self._stop_event:
            return self._stop_event.isSet()
        return False

    def stop(self) -> None:
        """Set stop event."""
        if not self.stopped:
            self.debug(currentframe(), "Stopping event is set now.")
            if self._stop_event:
                self._stop_event.set()

    @property
    def get_result(self) -> List[StarsSystem]:
        """Get list of StarsSystem objects."""
        return self.__found

    @property
    def start_system(self) -> StarsSystem:
        """Return start system for search radius."""
        return self._get_data(key=_Keys.START_SYSTEM)  # type: ignore

    @start_system.setter
    def start_system(self, value: StarsSystem) -> None:
        """Set start system for search radius."""
        self._set_data(key=_Keys.START_SYSTEM, value=value)

    @property
    def radius(self) -> int:
        """Give me radius value for system search from start_system position."""
        return self._get_data(key=_Keys.RADIUS)  # type: ignore

    @radius.setter
    def radius(self, value: Union[int, float, str]) -> None:
        try:
            self._set_data(key=_Keys.RADIUS, value=int(value))
        except Exception as ex:
            self.debug(currentframe(), f"Unexpected exception: {ex}")
        if self.radius is None:
            self.logger.warning = "Invalid radius value, set default: 10 ly."
            self._set_data(key=_Keys.RADIUS, value=10)
        elif self.radius > 100:
            self.logger.warning = "Radius too high, set max value: 100 ly."
            self._set_data(key=_Keys.RADIUS, value=100)
        elif self.radius < 5:
            self.logger.warning = "Radius too low, set min value: 5 ly."
            self._set_data(key=_Keys.RADIUS, value=5)
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
                self._c_name,
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
            if (
                EdsmKeys.BODY_COUNT in item
                and item[EdsmKeys.BODY_COUNT] is None
                or EdsmKeys.BODIES in item
                and item[EdsmKeys.BODIES] is None
                or EdsmKeys.BODY_COUNT in item
                and EdsmKeys.BODIES in item
                and item[EdsmKeys.BODY_COUNT] != item[EdsmKeys.BODIES]
                # or EdsmKeys.COORDS_LOCKED in item
                # and item[EdsmKeys.COORDS_LOCKED] == False
            ):
                count += 1
                system = StarsSystem()
                system.update_from_edsm(item)
                system.data[EdsmKeys.BODIES] = None
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
            alg = AlgGeneric(
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
        elif len(systems) > 2:
            alg = AlgSimulatedAnnealing(
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
