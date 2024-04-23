# -*- coding: UTF-8 -*-
"""
  Author:  Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
  Created: 19.12.2023

  Purpose: tools classes.
"""

import json
import random

from inspect import currentframe
from itertools import permutations
from queue import Queue, SimpleQueue
from sys import maxsize
from types import FrameType
from typing import Dict, Optional, List, Tuple, Union, Any
from jsktoolbox.attribtool import NoDynamicAttributes
from jsktoolbox.raisetool import Raise

import requests
from requests.utils import requote_uri
from rscan_libs.cartesianmath import Euclid
from rscan_libs.interfaces import Ialg
from rscan_libs.base_log import BLogClient
from rscan_libs.stars import StarsSystem
from rscan_libs.system import LogClient


class Url(NoDynamicAttributes):
    """Url.

    Class for serving HTTP/HTTPS requests.
    """

    __options: Dict[str, int] = None  # type: ignore
    __systems_url: str = None  # type: ignore
    __system_url: str = None  # type: ignore

    def __init__(self) -> None:
        """Create Url helper object."""
        self.__options = {
            "showId": 1,
            "showPermit": 1,
            "showCoordinates": 1,
            "showInformation": 0,
            "showPrimaryStar": 0,
            "includeHidden": 0,
        }
        self.__systems_url = "https://www.edsm.net/api-v1/"
        self.__system_url = "https://www.edsm.net/api-system-v1/"

    @property
    def options(self) -> str:
        """Get url options string."""
        out: str = ""
        for key, value in self.__options.items():
            out += f"&{key}={value}"
        return out

    def bodies_url(self, ssystem: StarsSystem) -> str:
        """Return proper API url for getting bodies information data."""
        if not isinstance(ssystem, StarsSystem):
            raise Raise.error(
                f"StarsSystem type expected, '{type(ssystem)}' received",
                TypeError,
                self.__class__.__name__,
                currentframe(),
            )

        if ssystem.address:
            return requote_uri(
                f"{self.__system_url}bodies?systemId={ssystem.address}{self.options}"
            )
        if ssystem.name:
            return requote_uri(
                f"{self.__system_url}bodies?systemName={ssystem.name}{self.options}"
            )
        return ""

    def system_url(self, ssystem: StarsSystem) -> str:
        """Return proper API url for getting system data."""
        if not isinstance(ssystem, StarsSystem):
            raise Raise.error(
                f"StarsSystem type expected, '{type(ssystem)}' received",
                TypeError,
                self.__class__.__name__,
                currentframe(),
            )

        if ssystem.name:
            return requote_uri(
                f"{self.__systems_url}system?systemName={ssystem.name}{self.options}"
            )
        return ""

    def radius_url(self, ssystem: StarsSystem, radius: int) -> str:
        """Return proper API url for getting systems data in radius."""
        if not isinstance(ssystem, StarsSystem):
            raise Raise.error(
                f"StarsSystem type expected, '{type(ssystem)}' received",
                TypeError,
                self.__class__.__name__,
                currentframe(),
            )
        if not isinstance(radius, int):
            radius = 50
        else:
            if radius < 5:
                radius = 5
            elif radius > 100:
                radius = 100

        if ssystem.name:
            return requote_uri(
                f"{self.__systems_url}sphere-systems?systemName={ssystem.name}&radius={radius}{self.options}"
            )
        return ""

    def cube_url(self, ssystem: StarsSystem, size: int) -> str:
        """Return proper API url for getting systems data in radius."""
        if not isinstance(ssystem, StarsSystem):
            raise Raise.error(
                f"StarsSystem type expected, '{type(ssystem)}' received",
                TypeError,
                self.__class__.__name__,
                currentframe(),
            )
        if not isinstance(size, int):
            size = 100
        else:
            if size < 10:
                size = 10
            elif size > 200:
                size = 200

        if ssystem.name:
            return requote_uri(
                f"{self.__systems_url}cube-systems?systemName={ssystem.name}&size={size}{self.options}"
            )
        return ""

    def system_query(self, ssystem: StarsSystem) -> Optional[Dict]:
        """Return result of query for system data."""
        if not isinstance(ssystem, StarsSystem):
            raise Raise.error(
                f"StarsSystem type expected, '{type(ssystem)}' received",
                TypeError,
                self.__class__.__name__,
                currentframe(),
            )
        url: str = self.system_url(ssystem)
        if not url:
            return None

        try:
            response: requests.Response = requests.get(url, timeout=30)
            if response.status_code != 200:
                print(f"Error calling API for system data: {response.status_code}")
                return None
            return json.loads(response.text)
        except Exception as ex:
            print(ex)
        return None

    def url_query(self, url: str) -> List[Dict[str, Any]]:
        """Return result of query for url."""
        out = []
        if not url:
            return out

        try:
            response: requests.Response = requests.get(url, timeout=60)
            if response.status_code != 200:
                print(f"Error calling API for EDSM data: {response.status_code}")
            else:
                out = json.loads(response.text)
        except Exception as ex:
            print(ex)
        return out


class Numbers(NoDynamicAttributes):
    """Numbers tool."""

    def is_float(self, element: Any) -> bool:
        """Check, if element is proper float variable."""
        if element is None:
            return False
        try:
            float(element)
            return True
        except ValueError:
            return False


class AlgTsp(Ialg, BLogClient, NoDynamicAttributes):
    """Travelling salesman problem."""

    __plugin_name: str = None  # type: ignore
    __math: Euclid = None  # type: ignore
    __data: List[StarsSystem] = None  # type: ignore
    __tmp: List[Any] = None  # type: ignore
    __jump_range: int = None  # type: ignore
    __final: List[StarsSystem] = None  # type: ignore

    def __init__(
        self,
        start: StarsSystem,
        systems: List[StarsSystem],
        jump_range: int,
        log_queue: Optional[Union[Queue, SimpleQueue]],
        euclid_alg: Euclid,
        plugin_name: str,
    ) -> None:
        """Construct instance object.

        params:
        start: StarsSystem - object with starting position.
        systems: list(StarsSystem,...) - list with point of interest to visit
        jump_range: int - jump range in ly
        log_queue: queue for LogClient
        euclid_alg: Euclid - object of initialized vectors class
        plugin_name: str - name of plugin for debug log
        """
        self.__plugin_name = plugin_name
        # init log subsystem
        if isinstance(log_queue, (Queue, SimpleQueue)):
            self.logger = LogClient(log_queue)
        else:
            raise Raise.error(
                f"Queue or SimpleQueue type expected, '{type(log_queue)}' received.",
                TypeError,
                self.__class__.__name__,
                currentframe(),
            )
        # Euclid's algorithm for calculating the length of vectors
        if isinstance(euclid_alg, Euclid):
            self.__math = euclid_alg
        else:
            raise Raise.error(
                f"Euclid type expected, '{type(euclid_alg)}' received",
                TypeError,
                self.__class__.__name__,
                currentframe(),
            )
        if isinstance(jump_range, int):
            self.__jump_range = jump_range
        else:
            raise Raise.error(
                f"Int type expected, '{type(jump_range)}' received",
                TypeError,
                self.__class__.__name__,
                currentframe(),
            )
        if not isinstance(start, StarsSystem):
            raise Raise.error(
                f"StarsSystem type expected, '{type(start)}' received.",
                TypeError,
                self.__class__.__name__,
                currentframe(),
            )
        if not isinstance(systems, list):
            raise Raise.error(
                f"list type expected, '{type(systems)}' received.",
                TypeError,
                self.__class__.__name__,
                currentframe(),
            )
        self.debug(currentframe(), "Initialize dataset")

        self.__data = []
        self.__tmp = []
        self.__final = []
        self.__data.append(start)
        for item in systems:
            self.__data.append(item)

    def run(self) -> None:
        """Run algorithm."""
        # stage 1: generate a cost table
        self.__stage_1_costs()
        # stage 2: search the solution
        self.__stage_2_solution()
        # finalize
        self.__final_update()

    def __stage_1_costs(self) -> None:
        """Stage 1: generate a cost table."""
        count: int = len(self.__data)
        for idx in range(count):
            self.__tmp.append([])
            for idx2 in range(count):
                self.__tmp[idx].append(
                    self.__math.distance(
                        self.__data[idx].star_pos, self.__data[idx2].star_pos
                    )
                )
        self.debug(currentframe(), f"{self.__tmp}")

    def __stage_2_solution(self) -> None:
        """Stage 2: search the solution."""
        out: List[Any] = []
        vertex: List[int] = []
        start: int = 0
        for i in range(len(self.__data)):
            if i != start:
                vertex.append(i)
        # store minimum weight Hamilton Cycle
        min_path: float = float(maxsize)
        next_permutation = permutations(vertex)

        for i in next_permutation:
            # store current Path weight
            current_path_weight: float = 0.0
            # compute current path weight
            k: int = start
            for j in i:
                current_path_weight += self.__tmp[k][j]
                k = j
            current_path_weight += self.__tmp[k][start]

            # update minimum
            if min_path > current_path_weight:
                out = [current_path_weight, i]
                min_path = current_path_weight

        # best solution
        if self.logger:
            self.logger.debug = f"DATA: {self.__data}"
        if self.logger:
            self.logger.debug = f"PATH: {out}"
        # add start system as first
        self.__tmp = [0]
        # and merge with output
        self.__tmp.extend(list(out[1]))

    def __final_update(self) -> None:
        """Build final dataset."""
        self.__final = []
        d_sum = 0
        if self.logger:
            self.logger.debug = f"TMP: {self.__tmp}"
        for idx in range(1, len(self.__tmp)):
            system = self.__data[self.__tmp[idx]]
            system.data["distance"] = self.__math.distance(
                self.__data[self.__tmp[idx - 1]].star_pos,
                self.__data[self.__tmp[idx]].star_pos,
            )
            d_sum += system.data["distance"]
            self.__final.append(system)
        if self.logger:
            self.logger.debug = f"FINAL Distance: {d_sum:.2f} ly"
        if self.logger:
            self.logger.debug = f"INPUT: {self.__data}"
        if self.logger:
            self.logger.debug = f"OUTPUT: {self.__final}"

    def debug(self, currentframe: Optional[FrameType], message: str = "") -> None:
        """Build debug message."""
        p_name: str = f"{self.__plugin_name}"
        c_name: str = f"{self.__class__.__name__}"
        m_name: str = f"{currentframe.f_code.co_name}" if currentframe else ""
        if message != "":
            message = f": {message}"
        if self.logger:
            self.logger.debug = f"{p_name}->{c_name}.{m_name}{message}"

    @property
    def get_final(self) -> List[StarsSystem]:
        """Return final data."""
        return self.__final


class AlgGenetic(Ialg, BLogClient, NoDynamicAttributes):
    """Genetic algorithm solving the problem of finding the best path."""

    __plugin_name: str = None  # type: ignore
    __math: Euclid = None  # type: ignore
    __final: List[StarsSystem] = None  # type: ignore

    __points: List[StarsSystem] = None  # type: ignore
    __start_point: StarsSystem = None  # type: ignore
    __max_distance: int = None  # type: ignore
    __population_size: int = None  # type: ignore
    __generations: int = None  # type: ignore
    __mutation_rate: float = None  # type: ignore
    __crossover_rate: float = None  # type: ignore

    def __init__(
        self,
        start: StarsSystem,
        systems: List[StarsSystem],
        jump_range: int,
        log_queue: Optional[Union[Queue, SimpleQueue]],
        euclid_alg: Euclid,
        plugin_name: str,
    ) -> None:
        """Construct instance object.

        params:
        start: StarsSystem - object with starting position.
        systems: list(StarsSystem,...) - list with point of interest to visit
        jump_range: int - jump range in ly
        log_queue: queue for LogClient
        euclid_alg: Euclid - object of initialized vectors class
        plugin_name: str - name of plugin for debug log
        """

        self.__plugin_name = plugin_name
        # init log subsystem
        if isinstance(log_queue, (Queue, SimpleQueue)):
            self.logger = LogClient(log_queue)
        else:
            raise Raise.error(
                f"Queue or SimpleQueue type expected, '{type(log_queue)}' received.",
                TypeError,
                self.__class__.__name__,
                currentframe(),
            )
        # Euclid's algorithm for calculating the length of vectors
        if isinstance(euclid_alg, Euclid):
            self.__math = euclid_alg
        else:
            raise Raise.error(
                f"Euclid type expected, '{type(euclid_alg)}' received",
                TypeError,
                self.__class__.__name__,
                currentframe(),
            )
        if isinstance(jump_range, int):
            self.__max_distance = jump_range
        else:
            raise Raise.error(
                f"Int type expected, '{type(jump_range)}' received",
                TypeError,
                self.__class__.__name__,
                currentframe(),
            )
        if not isinstance(start, StarsSystem):
            raise Raise.error(
                f"StarsSystem type expected, '{type(start)}' received.",
                TypeError,
                self.__class__.__name__,
                currentframe(),
            )
        if not isinstance(systems, list):
            raise Raise.error(
                f"list type expected, '{type(systems)}' received.",
                TypeError,
                self.__class__.__name__,
                currentframe(),
            )
        self.debug(currentframe(), "Initialize dataset")

        self.__points = systems
        self.__start_point = start
        self.__population_size = 100
        self.__generations = 100
        self.__mutation_rate = 0.05
        self.__crossover_rate = 0.4

    def __generate_individual(self) -> List[StarsSystem]:
        individual: List[StarsSystem] = [self.__start_point]
        remaining_points: List[StarsSystem] = self.__points.copy()
        while remaining_points:
            closest_point: StarsSystem = min(
                remaining_points,
                key=lambda point: self.__math.distance(
                    individual[-1].star_pos, point.star_pos
                ),
            )
            if (
                self.__math.distance(individual[-1].star_pos, closest_point.star_pos)
                > self.__max_distance
            ):
                break
            individual.append(closest_point)
            remaining_points.remove(closest_point)
        return individual

    def __generate_population(self) -> List[List[StarsSystem]]:
        population: List[List[StarsSystem]] = []
        for _ in range(self.__population_size):
            population.append(self.__generate_individual())
        return population

    def __get_fitness(self, individual: List[StarsSystem]) -> float:
        distance: float = 0
        for i in range(len(individual) - 1):
            distance += self.__math.distance(
                individual[i].star_pos, individual[i + 1].star_pos
            )
        return 1 / distance if distance > 0 else float("inf")

    def __select_parents(
        self, population: List[List[StarsSystem]]
    ) -> Tuple[List[StarsSystem], List[StarsSystem]]:
        parent1: List[StarsSystem]
        parent2: List[StarsSystem]
        parent1, parent2 = random.choices(
            population,
            weights=[self.__get_fitness(individual) for individual in population],
            k=2,
        )
        return parent1, parent2

    def __crossover(
        self, parent1: List[StarsSystem], parent2: List[StarsSystem]
    ) -> List[StarsSystem]:
        if random.random() > self.__crossover_rate:
            return parent1
        crossover_point: int = random.randint(1, len(parent1) - 2)
        child: List[StarsSystem] = parent1[:crossover_point] + [
            point for point in parent2 if point not in parent1[:crossover_point]
        ]
        return child

    def __mutate(self, individual: List[StarsSystem]) -> List[StarsSystem]:
        mutation_point1: int
        mutation_point2: int
        if random.random() > self.__mutation_rate:
            return individual
        mutation_point1, mutation_point2 = random.sample(
            range(1, len(individual) - 1), 2
        )
        individual[mutation_point1], individual[mutation_point2] = (
            individual[mutation_point2],
            individual[mutation_point1],
        )
        return individual

    def __evolve(self) -> List[StarsSystem]:
        population: List[List[StarsSystem]] = self.__generate_population()
        best_individual: List[StarsSystem] = None  # type: ignore
        for i in range(self.__generations):
            fitnesses: List[float] = [
                self.__get_fitness(individual) for individual in population
            ]
            best_individual = population[fitnesses.index(max(fitnesses))]
            if len(best_individual) == len(self.__points) + 1:
                break
            new_population: List[List[StarsSystem]] = [best_individual]
            while len(new_population) < self.__population_size:
                parent1: List[StarsSystem]
                parent2: List[StarsSystem]
                child: List[StarsSystem]
                parent1, parent2 = self.__select_parents(population)
                child = self.__crossover(parent1, parent2)
                child = self.__mutate(child)
                new_population.append(child)
            population = new_population
        return best_individual

    def run(self) -> None:
        """Run algorithm."""
        self.__final = self.__evolve()
        self.__final.remove(self.__start_point)
        # update distance
        d_sum: float = 0.0
        start: StarsSystem = self.__start_point
        for item in self.__final:
            end: StarsSystem = item
            end.data["distance"] = self.__math.distance(start.star_pos, end.star_pos)
            d_sum += end.data["distance"]
            start = end
        if self.logger:
            self.logger.debug = f"FINAL Distance: {d_sum:.2f} ly"

    def debug(self, currentframe: Optional[FrameType], message: str = "") -> None:
        """Build debug message."""
        p_name: str = f"{self.__plugin_name}"
        c_name: str = f"{self.__class__.__name__}"
        m_name: str = f"{currentframe.f_code.co_name}" if currentframe else ""
        if message != "":
            message = f": {message}"
        if self.logger:
            self.logger.debug = f"{p_name}->{c_name}.{m_name}{message}"

    @property
    def get_final(self) -> List[StarsSystem]:
        """Return final data."""
        return self.__final


# #[EOF]#######################################################################
