# -*- coding: UTF-8 -*-
"""
  Author:  Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
  Created: 19.12.2023

  Purpose: system search class.
"""

import inspect
import json
from queue import Queue, SimpleQueue
from threading import Event, Thread
from typing import Any, Dict, List, Optional, Union
from types import FrameType

from rscan_libs.cartesianmath import Euclid
from rscan_libs.data import RscanData
from rscan_libs.mlog import MLogClient
from raisetool.formatter import Raise
from rscan_libs.stars import StarsSystem
from rscan_libs.system import LogClient
from rscan_libs.tools import AlgGenetic, AlgGeneticGPT, AlgTsp, Numbers, Url


class ThSystemSearch(Thread, MLogClient):
    """Thread system search engine."""

    __slots__ = [
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
    ):
        """Create object instance of class."""
        Thread.__init__(self, name=self.__class__.__name__)
        self.__stop_event = Event()
        # init log subsystem
        if isinstance(log_queue, (Queue, SimpleQueue)):
            self.logger = LogClient(log_queue)
        else:
            raise Raise.type_error(
                self.__class__.__name__,
                inspect.currentframe(),
                f"Queue or SimpleQueue type expected, '{type(log_queue)}' received.",
            )

        if isinstance(data, RscanData):
            self.__data = data
            self.debug(inspect.currentframe(), f"{self.__data}")
        else:
            raise Raise.type_error(
                self.__class__.__name__,
                inspect.currentframe(),
                f"RscanData type expected, '{type(data)}' received",
            )

        # Euclid's algorithm for calculating the length of vectors
        if isinstance(euclid_alg, Euclid):
            self.__math = euclid_alg
        else:
            raise Raise.type_error(
                self.__class__.__name__,
                inspect.currentframe(),
                f"Euclid type expected, '{type(euclid_alg)}' received",
            )

        # initialize private variables
        self.__parent = parent
        self.__start_system = None
        self.__radius = None
        self.__found = []

    def run(self):
        """Run the work."""
        pname = self.__data.pluginname
        cname = self.__class__.__name__
        self.logger.info = f"{pname}->{cname}: Starting new work..."
        # build radius query
        qurl = self.__build_radius_query()
        # create query object
        url = Url()
        # quering starts database
        systems = url.url_query(qurl)
        if systems is None:
            return
        # filtering system
        systems = self.__buils_radius_systems_list(systems)
        # self.debug(
        #     inspect.currentframe(),
        #     f"Search result: {systems}"
        # )
        if not systems:
            self.status("0 systems found.")
            return
        # tracerouting optimization
        self.status(
            f"{len(systems)} systems found, flight route calculations in progress..."
        )
        systems_out = self.__flightroute_systems(systems)
        self.debug(inspect.currentframe(), f"Search result: {systems_out}")
        # put it into result list
        dsum: float = 0.0
        for item in systems_out:
            dsum += item.data["distance"]
            self.__found.append(item)
        # work done
        self.status(
            f"{len(systems_out)} systems found, calculations done. Final distance: {dsum:.2f} ly"
        )
        self.logger.info = f"{pname}->{cname}: Done."

    def debug(self, currentframe: FrameType, message: str = ""):
        """Build debug message."""
        pname = f"{self.__data.pluginname}"
        cname = f"{self.__class__.__name__}"
        mname = f"{currentframe.f_code.co_name}"
        if message != "":
            message = f": {message}"
        self.logger.debug = f"{pname}->{cname}.{mname}{message}"
        inspect.currentframe()

    def status(self, message: Any):
        """Write message to status bar."""
        self.__parent.status = f"{message}"

    @property
    def stopped(self) -> bool:
        """Get stop event flag."""
        return self.__stop_event.isSet()

    def stop(self):
        """Set stop event."""
        if not self.stopped:
            self.debug(inspect.currentframe(), "Stopping event is set now.")
            self.__stop_event.set()

    @property
    def get_result(self) -> List:
        """Get list of StarsSystem objects."""
        return self.__found

    @property
    def start_system(self) -> Optional[StarsSystem]:
        """Give me start system for search radius."""
        return self.__start_system

    @start_system.setter
    def start_system(self, value: StarsSystem):
        if not isinstance(value, StarsSystem):
            raise Raise.type_error(
                self.__class__.__name__,
                inspect.currentframe(),
                f"StarsSystem type expected, '{type(value)}' received.",
            )
        self.__start_system = value

    @property
    def radius(self) -> Optional[int]:
        """Give me radius value for system search from start_system position."""
        return self.__radius

    @radius.setter
    def radius(self, value: Union[int, float]):
        try:
            self.__radius = int(value)
        except Exception as ex:
            self.debug(inspect.currentframe(), f"Unexpected exception: {ex}")
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

    def __progress(self, cur: int, systems_count: int):
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
            raise Raise.value_error(
                self.__class__.__name__,
                inspect.currentframe(),
                "Needed variables not initialized properly.",
            )

        # updating data for start system, if needed
        if self.start_system.pos_x is None:
            out = url.system_query(self.start_system)
            self.debug(inspect.currentframe(), f"Start System data: {out}")
            self.start_system.update_from_edsm(out)

        return url.radius_url(self.start_system, self.radius)

    def __buils_radius_systems_list(self, systems: list) -> Optional[List]:
        """Build filtered systems list from EDSM API output."""
        out = []
        out_body = []
        systems_count = len(systems)
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
                # self.debug(
                #     inspect.currentframe(),
                #     f"{item}"
                # )
                self.debug(
                    inspect.currentframe(),
                    f"EDSM system nr:{count} {system}",
                )
                out.append(system)
            # else:
            #     self.logger.debug = f"OTHER: {item}"
            #     # system = StarsSystem()
            #     # system.update_from_edsm(item)
            #     # # out_body.append(item)
            #     # bodies = self.__get_bodies_information(system)
            #     # if bodies and 'bodies' in bodies:
            #     #     system.data['bodies'] = len(bodies['bodies'])
            #     #     if system.data['bodycount'] != system.data['bodies']:
            #     #         count += 1
            #     #         out.append(system)

        self.logger.info = f"Found {count} systems"
        return out

    def __get_bodies_information(self, system: StarsSystem) -> Optional[Dict]:
        """Try to get information about system bodies."""
        if not isinstance(system, StarsSystem):
            raise Raise.type_error(
                self.__class__.__name__,
                inspect.currentframe(),
                f"StarsSystem type expected, '{type(system)}' received",
            )
        url = Url()
        out_url = url.bodies_url(system)
        if not out_url:
            return {}
        # quering EDSM
        out = url.url_query(out_url)
        if out is None:
            return {}
        return out

    def __flightroute_systems(self, systems: List[StarsSystem]) -> Optional[List]:
        """Try to find the optimal order of flight."""
        jump = 50
        out = []
        if self.__data.jumprange is not None:
            jump = int(self.__data.jumprange) - 4
        if len(systems) > 10:
            alg = AlgGeneticGPT(
                self.start_system,
                systems,
                jump,
                self.logger.queue,
                self.__math,
                self.__data.pluginname,
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
                self.__data.pluginname,
            )
            alg.run()
            for item in alg.get_final:
                out.append(item)
        if out:
            return out
        return systems


# #[EOF]#######################################################################
