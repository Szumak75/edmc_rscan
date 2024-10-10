# -*- coding: UTF-8 -*-
"""
  Author:  Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
  Created: 19.12.2023

  Purpose: cartesian math classes.
"""

from inspect import currentframe
import math
import time
from queue import Queue, SimpleQueue
from typing import List, Union, Optional
from types import FrameType, MethodType

from rscan.jsktoolbox.attribtool import ReadOnlyClass
from rscan.jsktoolbox.raisetool import Raise
from rscan.jsktoolbox.edmctool.base import BLogClient
from rscan.jsktoolbox.edmctool.logs import LogClient
from rscan.data import RscanData


try:
    import numpy as np
except ModuleNotFoundError:
    pass

try:
    from scipy.spatial import distance
except ModuleNotFoundError:
    pass


class _Keys(object, metaclass=ReadOnlyClass):
    """Internal Keys container class."""

    DATA: str = "__e_data__"
    TEST: str = "__e_test__"


class Euclid(BLogClient):
    """Euclid.

    A class that calculates the length of a vector in Cartesian space.
    """

    def __init__(self, queue: Union[Queue, SimpleQueue], data: RscanData) -> None:
        """Create class object."""

        self._set_data(
            key=_Keys.TEST,
            set_default_type=List,
            value=[
                self.__numpy_l2,
                self.__numpy,
                self.__einsum,
                self.__scipy,
                self.__math,
                self.__core,
            ],
        )

        # init log subsystem
        if isinstance(queue, (Queue, SimpleQueue)):
            self.logger = LogClient(queue)
        else:
            raise Raise.error(
                f"Queue or SimpleQueue type expected, '{type(queue)}' received.",
                TypeError,
                self._c_name,
                currentframe(),
            )

        if isinstance(data, RscanData):
            self._set_data(
                key=_Keys.DATA,
                set_default_type=RscanData,
                value=data,
            )
            self.debug(currentframe(), f"{data}")
        else:
            raise Raise.error(
                f"RscanData type expected, '{type(data)}' received",
                TypeError,
                self._c_name,
                currentframe(),
            )

        self.debug(currentframe(), "Initialize dataset")

    @property
    def __data(self) -> RscanData:
        """Return data."""
        return self._get_data(key=_Keys.DATA)  # type: ignore

    @property
    def __test(self) -> List[MethodType]:
        """Return test list."""
        return self._get_data(key=_Keys.TEST)  # type: ignore

    def benchmark(self) -> None:
        """Do benchmark test.

        Compare the computational efficiency of functions for real data
        and choose the right priority of their use.
        """
        p_name: str = f"{self.__data.plugin_name}"
        c_name: str = f"{self._c_name}"

        if self.logger:
            self.logger.info = f"{p_name}->{c_name}: Warming up math system..."
        data1: List[List[float]] = [
            [641.71875, -536.06250, -6886.37500],
            [10.31250, -160.53125, 74.18750],
            [51.40625, -54.40625, -30.50000],
            [45.59375, -51.90625, -39.46875],
            [22.28125, -43.40625, -36.18750],
            [11.18750, -37.37500, -31.84375],
            [5.90625, -30.50000, -36.37500],
            [11.18750, -37.37500, -31.84375],
            [5.62500, -36.65625, -33.87500],
            [-0.56250, -43.71875, -30.81250],
        ]
        data2: List[List[float]] = [
            [67.50000, -74.90625, -93.68750],
            [134.12500, 15.09375, -63.87500],
            [124.50000, 4.31250, -49.12500],
            [118.93750, -8.53125, -33.46875],
            [105.96875, -20.87500, -22.21875],
            [95.40625, -33.50000, -11.40625],
            [78.34375, -42.96875, -2.21875],
            [66.84375, -60.65625, -3.84375],
            [60.93750, -75.25000, 10.87500],
            [58.28125, -92.09375, 23.71875],
        ]

        # build test
        test = []
        bench_out = {}

        for item in self.__test:
            if item(data1[0], data2[0]) is not None:
                test.append(item)

        # start test
        for item in test:
            t_start: float = time.time()
            for idx in range(0, len(data1)):
                item(data1[idx], data2[idx])
            t_stop: float = time.time()
            bench_out[t_stop - t_start] = item

        # optimize list of the methods
        self.__test.clear()
        for idx in sorted(bench_out.keys()):
            self.__test.append(bench_out[idx])
            self.debug(currentframe(), f"{idx}: {bench_out[idx]}")

        if self.logger:
            self.logger.info = f"{p_name}->{c_name}: done."

    def debug(self, currentframe: Optional[FrameType], message: str = "") -> None:
        """Build debug message."""
        p_name: str = f"{self.__data.plugin_name}"
        c_name: str = f"{self._c_name}"
        m_name: str = (
            f"{currentframe.f_code.co_name}" if currentframe is not None else ""
        )
        if message != "":
            message = f": {message}"
        if self.logger:
            self.logger.debug = f"{p_name}->{c_name}.{m_name}{message}"

    def __core(self, points_1: List[float], points_2: List[float]) -> float:
        """Do calculations without math libraries.

        The method iterates over each pair of vector elements,
        performs calculations on it and sums up the intermediate results.
        """
        return sum((i - j) ** 2 for i, j in zip(points_1, points_2)) ** 0.5

    def __math(self, points_1: List[float], points_2: List[float]) -> Optional[float]:
        """Try to use math lib."""
        try:
            return math.dist(points_1, points_2)
        except Exception as ex:
            self.debug(currentframe(), f"{ex}")
        return None

    def __numpy_l2(self, points_1: List[float], points_2: List[float]) -> Optional[float]:
        """Try to use numpy lib.

        The method uses the fact that the Euclidean distance of two vectors
        is nothing but the L^2 norm of their difference.
        """
        try:
            return np.linalg.norm(np.array(points_1) - np.array(points_2))  # type: ignore
        except Exception as ex:
            self.debug(currentframe(), f"{ex}")
        return None

    def __numpy(self, points_1: List[float], points_2: List[float]) -> Optional[float]:
        """Try to use numpy lib.

        The method is an optimization of the core method using numpy
        and vectorization.
        """
        try:
            return np.sqrt(np.sum((np.array(points_1) - np.array(points_2)) ** 2))
        except Exception as ex:
            self.debug(currentframe(), f"{ex}")
        return None

    def __einsum(self, points_1: List[float], points_2: List[float]) -> Optional[float]:
        """Try to use numpy lib.

        Einstein summation convention.
        """
        try:
            tmp = np.array(points_1) - np.array(points_2)
            return np.sqrt(np.einsum("i,i->", tmp, tmp))
        except Exception as ex:
            self.debug(currentframe(), f"{ex}")
        return None

    def __scipy(self, points_1: List, points_2: List) -> Optional[float]:
        """Try to use scipy lib.

        The scipy library has a built-in function to calculate
        the Euclidean distance.
        """
        try:
            return distance.euclidean(points_1, points_2)
        except Exception as ex:
            self.debug(currentframe(), f"{ex}")
        return None

    def distance(self, points_1: List[float], points_2: List[float]) -> float:
        """Find the first working algorithm and do the calculations."""
        out: float = None  # type: ignore
        i = 0

        while out is None:
            if i < len(self.__test):
                out = self.__test[i](points_1, points_2)
            else:
                break
            i += 1

        return out


# #[EOF]#######################################################################
