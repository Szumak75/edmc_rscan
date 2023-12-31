# -*- coding: UTF-8 -*-
"""
  Author:  Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
  Created: 19.12.2023

  Purpose: tools classes.
"""


import copy
import json
import random
import requests

from inspect import currentframe
from itertools import permutations
from operator import itemgetter
from queue import Queue
from sys import maxsize
from typing import Dict, Optional, List, Tuple
from types import FrameType

from jsktoolbox.raisetool import Raise
from jsktoolbox.libs.base_data import BData, BClasses


from rscan_libs.cartesianmath import Euclid
from rscan_libs.interfaces import IAlg
from rscan_libs.base_logs import BLogClient
from rscan_libs.stars import StarsSystem
from rscan_libs.system import LogClient


class Url(BData):
    """Url.

    Class for serving HTTP/HTTPS requests.
    """

    __options = None
    __system_url = None
    __systems_url = None

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
        out = ""
        for key, value in self.__options.items():
            out += f"&{key}={value}"
        return out

    def bodies_url(self, ssystem: StarsSystem) -> str:
        """Return proper API url for getting bodies information data."""
        if not isinstance(ssystem, StarsSystem):
            raise Raise.error(
                f"StarsSystem type expected, '{type(ssystem)}' received",
                TypeError,
                self._c_name,
                currentframe(),
            )

        if ssystem.address:
            return requests.utils.requote_uri(
                f"{self.__system_url}bodies?systemId={ssystem.address}{self.options}"
            )
        if ssystem.name:
            return requests.utils.requote_uri(
                f"{self.__system_url}bodies?systemName={ssystem.name}{self.options}"
            )
        return ""

    def system_url(self, ssystem: StarsSystem) -> str:
        """Return proper API url for getting system data."""
        if not isinstance(ssystem, StarsSystem):
            raise Raise.error(
                f"StarsSystem type expected, '{type(ssystem)}' received",
                TypeError,
                self._c_name,
                currentframe(),
            )

        if ssystem.name:
            return requests.utils.requote_uri(
                f"{self.__systems_url}system?systemName={ssystem.name}{self.options}"
            )
        return ""

    def radius_url(self, ssystem: StarsSystem, radius: int) -> str:
        """Return proper API url for getting systems data in radius."""
        if not isinstance(ssystem, StarsSystem):
            raise Raise.error(
                f"StarsSystem type expected, '{type(ssystem)}' received",
                TypeError,
                self._c_name,
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
            return requests.utils.requote_uri(
                f"{self.__systems_url}sphere-systems?systemName={ssystem.name}&radius={radius}{self.options}"
            )
        return ""

    def cube_url(self, ssystem: StarsSystem, size: int) -> str:
        """Return proper API url for getting systems data in radius."""
        if not isinstance(ssystem, StarsSystem):
            raise Raise.error(
                f"StarsSystem type expected, '{type(ssystem)}' received",
                TypeError,
                self._c_name,
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
            return requests.utils.requote_uri(
                f"{self.__systems_url}cube-systems?systemName={ssystem.name}&size={size}{self.options}"
            )
        return ""

    def system_query(self, ssystem: StarsSystem) -> Optional[Dict]:
        """Return result of query for system data."""
        if not isinstance(ssystem, StarsSystem):
            raise Raise.error(
                f"StarsSystem type expected, '{type(ssystem)}' received",
                TypeError,
                self._c_name,
                currentframe(),
            )
        url = self.system_url(ssystem)
        if not url:
            return None

        try:
            response = requests.get(url, timeout=30)
            if response.status_code != 200:
                print(f"Error calling API for system data: {response.status_code}")
                return None
            return json.loads(response.text)
        except Exception as ex:
            print(ex)
        return None

    def url_query(self, url: str) -> Optional[Dict]:
        """Return result of query for url."""
        if not url:
            return None

        try:
            response = requests.get(url, timeout=60)
            if response.status_code != 200:
                print(f"Error calling API for EDSM data: {response.status_code}")
                return None
            return json.loads(response.text)
        except Exception as ex:
            print(ex)
        return None


class Numbers(BClasses):
    """Numbers tool."""

    def is_float(self, element: any) -> bool:
        """Check, if element is proper float variable."""
        if element is None:
            return False
        try:
            float(element)
            return True
        except ValueError:
            return False


class AlgTsp(IAlg, BLogClient):
    """Travelling salesman problem."""

    __data = None
    __final = None
    __jumprange = None
    __math = None
    __pluginname = None
    __tmp = None

    def __init__(
        self,
        start: StarsSystem,
        systems: List[StarsSystem],
        jumprange: int,
        log_queue: Queue,
        euclid_alg: Euclid,
        plugin_name: str,
    ) -> None:
        """Construct instance object.

        params:
        start: StarsSystem - object with starting position.
        systems: list(StarsSystem,...) - list with point of interest to visit
        jumprange: int - jumprange in ly
        log_queue: queue for LogClient
        euclid_alg: Euclid - object of initialized vectors class
        plugin_name: str - name of plugin for debug log
        """
        self.__pluginname = plugin_name
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
        # Euclid's algorithm for calculating the length of vectors
        if isinstance(euclid_alg, Euclid):
            self.__math = euclid_alg
        else:
            raise Raise.error(
                f"Euclid type expected, '{type(euclid_alg)}' received",
                TypeError,
                self._c_name,
                currentframe(),
            )
        if isinstance(jumprange, int):
            self.__jumprange = jumprange
        else:
            raise Raise.error(
                f"Int type expected, '{type(jumprange)}' received",
                TypeError,
                self._c_name,
                currentframe(),
            )
        if not isinstance(start, StarsSystem):
            raise Raise.error(
                f"StarsSystem type expected, '{type(start)}' received.",
                TypeError,
                self._c_name,
                currentframe(),
            )
        if not isinstance(systems, list):
            raise Raise.error(
                f"list type expected, '{type(systems)}' received.",
                TypeError,
                self._c_name,
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
        count = len(self.__data)
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
        out = []
        vertex = []
        start = 0
        for i in range(len(self.__data)):
            if i != start:
                vertex.append(i)
        # store minimum weight Hamilto Cycle
        min_path = maxsize
        next_permutation = permutations(vertex)

        for i in next_permutation:
            # store current Path weight
            current_pathweight = 0

            k = start
            for j in i:
                current_pathweight += self.__tmp[k][j]
                k = j
            current_pathweight += self.__tmp[k][start]

            # update minimum
            if min_path > current_pathweight:
                out = [current_pathweight, i]
                min_path = current_pathweight

        # best solution
        self.logger.debug = f"DATA: {self.__data}"
        self.logger.debug = f"PATH: {out}"
        # add start system as first
        self.__tmp = [0]
        # and merge with output
        self.__tmp.extend(list(out[1]))

    def __final_update(self) -> None:
        """Build final dataset."""
        self.__final = []
        dsum = 0
        for idx in range(1, len(self.__tmp)):
            system = self.__data[self.__tmp[idx]]
            system.data["distance"] = self.__math.distance(
                self.__data[self.__tmp[idx - 1]].star_pos,
                self.__data[self.__tmp[idx]].star_pos,
            )
            dsum += system.data["distance"]
            self.__final.append(system)
        self.logger.debug = f"FINAL Distance: {dsum:.2f} ly"
        self.logger.debug = f"INPUT: {self.__data}"
        self.logger.debug = f"OUTPUT: {self.__final}"

    def debug(self, currentframe: FrameType, message: str = "") -> None:
        """Build debug message."""
        pname = f"{self.__pluginname}"
        cname = f"{self._c_name}"
        mname = f"{currentframe.f_code.co_name}"
        if message != "":
            message = f": {message}"
        self.logger.debug = f"{pname}->{cname}.{mname}{message}"

    @property
    def get_final(self) -> list:
        """Return final data."""
        return self.__final


class AlgGenetic(IAlg, BLogClient):
    """Genetic algorithm solving the problem of finding the best path."""

    __count = None
    __data = None
    __final = None
    __jumprange = None
    __math = None
    __pluginname = None
    __tmp = None

    def __init__(
        self,
        start: StarsSystem,
        systems: List[StarsSystem],
        jumprange: int,
        log_queue: Queue,
        euclid_alg: Euclid,
        plugin_name: str,
    ) -> None:
        """Construct instance object.

        params:
        start: StarsSystem - object with starting position.
        systems: list(StarsSystem,...) - list with point of interest to visit
        jumprange: int - jumprange in ly
        log_queue: queue for LogClient
        euclid_alg: Euclid - object of initialized vectors class
        plugin_name: str - name of plugin for debug log
        """
        self.__count: int = 100
        self.__pluginname = plugin_name
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
        # Euclid's algorithm for calculating the length of vectors
        if isinstance(euclid_alg, Euclid):
            self.__math = euclid_alg
        else:
            raise Raise.error(
                f"Euclid type expected, '{type(euclid_alg)}' received",
                TypeError,
                self._c_name,
                currentframe(),
            )
        if isinstance(jumprange, int):
            self.__jumprange = jumprange
        else:
            raise Raise.error(
                f"Int type expected, '{type(jumprange)}' received",
                TypeError,
                self._c_name,
                currentframe(),
            )
        if not isinstance(start, StarsSystem):
            raise Raise.error(
                f"StarsSystem type expected, '{type(start)}' received.",
                TypeError,
                self._c_name,
                currentframe(),
            )
        if not isinstance(systems, list):
            raise Raise.error(
                f"list type expected, '{type(systems)}' received.",
                TypeError,
                self._c_name,
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
        # stage 1: generate a starting population
        self.__stage_1_generator()
        count = 0
        while count < self.__count:
            count += 1
            # stage 2: crossing
            start = 1
            end = len(self.__tmp) - 2
            while start < end:
                self.__stage_2_crossing(start, end)
                start += 1
                end -= 1
            # stage 3: mutating
            end = len(self.__tmp)
            for _ in range(0, end):
                self.__stage_3_mutating(random.randrange(0, end))
            # stage 4: sorting
            self.__tmp = sorted(self.__tmp, key=itemgetter(0))
            # stage 5: removing bad
            self.__stage_5_remove_bad()
        self.__final_update()

    def __stage_1_generator(self) -> None:
        """Generate a starting population."""
        count = len(self.__data)
        items = int(count * self.__count)
        for _ in range(items):
            tmp = []
            # first item is path length
            tmp.append(0)
            # second item is start system idx in self__data
            tmp.append([0, 0.0])
            rand = [*range(1, count)]
            # self.logger.debug = f"rand: {rand}"
            # randomize data
            random.shuffle(rand)
            # self.logger.debug = f"random rand: {rand}"
            # create dataset
            for idx in rand:
                tmp.append([idx, 0.0])
            # self.logger.debug = f"tmp: {tmp}"
            tmp = self.__compute_path_length(tmp)
            # self.logger.debug = f"tmp: {tmp}"
            # add to population list
            self.__tmp.append(tmp)

    def __stage_2_crossing(self, start: int, end: int) -> None:
        """Stage 2: crossing."""
        # self.logger.debug = f"Start[{start}]: {self.__tmp[start]}"
        # self.logger.debug = f"End[{end}]: {self.__tmp[end]}"
        tmp = []
        # first item is path length
        tmp.append(0)
        # second item is start system idx in self__data
        tmp.append([0, 0.0])
        # [total path, [start system], [first point], ...]
        for idx in range(2, len(self.__tmp[end])):
            if idx < int((len(self.__tmp[end]) + 2) / 2):
                tmp.append(copy.deepcopy(self.__tmp[end][idx]))
        for idx in range(2, len(self.__tmp[start])):
            test = True
            for idx2 in range(2, len(tmp)):
                if self.__tmp[start][idx][0] == tmp[idx2][0]:
                    test = False
            if test:
                tmp.append(copy.deepcopy(self.__tmp[start][idx]))
        tmp = self.__compute_path_length(tmp)
        self.__tmp.append(tmp)

    def __stage_3_mutating(self, start: int) -> None:
        """Stage 3: mutating."""
        first = random.randrange(2, len(self.__tmp[start]))
        second = random.randrange(2, len(self.__tmp[start]))
        while first == second:
            second = random.randrange(2, len(self.__tmp[start]))

        tmp = copy.deepcopy(self.__tmp[start])
        # self.logger.debug = f"TMP-in: {tmp}"
        ifirst = tmp[first]
        tmp[first] = tmp[second]
        tmp[second] = ifirst
        tmp = self.__compute_path_length(tmp)
        # self.logger.debug = f"TMP-out: {tmp}"

        self.__tmp.append(tmp)

    def __stage_5_remove_bad(self) -> None:
        """Stage 5: remove the worst results."""
        count = len(self.__data)
        items = int(count * 2)
        tmp = []
        for idx in range(items):
            tmp.append(copy.deepcopy(self.__tmp[idx]))
        self.__tmp = None
        self.__tmp = tmp

    def __compute_path_length(self, arg: list, flag: bool = False) -> list:
        """Compute path length."""
        # compute partial path length
        for idx in range(2, len(arg)):
            distance = self.__math.distance(
                self.__data[arg[idx - 1][0]].star_pos,
                self.__data[arg[idx][0]].star_pos,
            )
            if not flag:
                if distance > self.__jumprange:
                    distance = distance * 10
            arg[idx][1] = distance
        # compute total path length
        for idx in range(2, len(arg)):
            arg[0] += arg[idx][1]
        # self.logger.debug = f"arg: {arg}"
        return arg

    def __final_update(self) -> None:
        """Build final dataset."""
        self.__final = []
        dsum = 0
        print(self.__tmp[0])
        self.__tmp[0][0] = 0
        self.__tmp[0] = self.__compute_path_length(self.__tmp[0], True)
        print(self.__tmp[0])
        for idx in range(2, len(self.__tmp[0])):
            self.logger.debug = f"FINAL: {idx} -> {self.__tmp[0][idx]}"
            system = self.__data[self.__tmp[0][idx][0]]
            system.data["distance"] = self.__tmp[0][idx][1]
            dsum += system.data["distance"]
            self.__final.append(system)
        self.logger.debug = f"FINAL Distance: {dsum:.2f} ly"
        self.logger.debug = f"INPUT: {self.__data}"
        self.logger.debug = f"OUTPUT: {self.__final}"

    def debug(self, currentframe: FrameType, message: str = "") -> None:
        """Build debug message."""
        pname = f"{self.__pluginname}"
        cname = f"{self._c_name}"
        mname = f"{currentframe.f_code.co_name}"
        if message != "":
            message = f": {message}"
        self.logger.debug = f"{pname}->{cname}.{mname}{message}"

    @property
    def get_final(self) -> list:
        """Return final data."""
        return self.__final


class AlgGeneticGPT(IAlg, BLogClient):
    """Genetic algorithm solving the problem of finding the best path."""

    __crossover_rate = None
    __final = None
    __generations = None
    __math = None
    __max_distance = None
    __mutation_rate = None
    __pluginname = None
    __points = None
    __population_size = None
    __start_point = None

    def __init__(
        self,
        start: StarsSystem,
        systems: List[StarsSystem],
        jumprange: int,
        log_queue: Queue,
        euclid_alg: Euclid,
        plugin_name: str,
    ) -> None:
        """Construct instance object.

        params:
        start: StarsSystem - object with starting position.
        systems: list(StarsSystem,...) - list with point of interest to visit
        jumprange: int - jumprange in ly
        log_queue: queue for LogClient
        euclid_alg: Euclid - object of initialized vectors class
        plugin_name: str - name of plugin for debug log
        """

        self.__pluginname = plugin_name
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
        # Euclid's algorithm for calculating the length of vectors
        if isinstance(euclid_alg, Euclid):
            self.__math = euclid_alg
        else:
            raise Raise.error(
                f"Euclid type expected, '{type(euclid_alg)}' received",
                TypeError,
                self._c_name,
                currentframe(),
            )
        if isinstance(jumprange, int):
            self.__max_distance = jumprange
        else:
            raise Raise.error(
                f"Int type expected, '{type(jumprange)}' received",
                TypeError,
                self._c_name,
                currentframe(),
            )
        if not isinstance(start, StarsSystem):
            raise Raise.error(
                f"StarsSystem type expected, '{type(start)}' received.",
                TypeError,
                self._c_name,
                currentframe(),
            )
        if not isinstance(systems, list):
            raise Raise.error(
                f"list type expected, '{type(systems)}' received.",
                TypeError,
                self._c_name,
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
        crossover_point = random.randint(1, len(parent1) - 2)
        child = parent1[:crossover_point] + [
            point for point in parent2 if point not in parent1[:crossover_point]
        ]
        return child

    def __mutate(self, individual: List[StarsSystem]) -> List[StarsSystem]:
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
        population = self.__generate_population()
        best_individual: List[StarsSystem] = None
        for i in range(self.__generations):
            fitnesses = [self.__get_fitness(individual) for individual in population]
            best_individual = population[fitnesses.index(max(fitnesses))]
            if len(best_individual) == len(self.__points) + 1:
                break
            new_population = [best_individual]
            while len(new_population) < self.__population_size:
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
        dsum: float = 0.0
        start = self.__start_point
        for item in self.__final:
            end: StarsSystem = item
            end._data["distance"] = self.__math.distance(start.star_pos, end.star_pos)
            dsum += end._data["distance"]
            start = end
        self.logger.debug = f"FINAL Distance: {dsum:.2f} ly"

    def debug(self, currentframe: FrameType, message: str = "") -> None:
        """Build debug message."""
        pname = f"{self.__pluginname}"
        cname = f"{self._c_name}"
        mname = f"{currentframe.f_code.co_name}"
        if message != "":
            message = f": {message}"
        self.logger.debug = f"{pname}->{cname}.{mname}{message}"

    @property
    def get_final(self) -> list:
        """Return final data."""
        return self.__final


# #[EOF]#######################################################################
