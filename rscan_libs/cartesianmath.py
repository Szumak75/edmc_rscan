# -*- coding: UTF-8 -*-
"""
  Author:  Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
  Created: 19.12.2023

  Purpose: carthesian math classes.
"""

import inspect
import math
import time
from queue import Queue, SimpleQueue
from typing import List, Union
from types import FrameType
from jsktoolbox.attribtool import NoDynamicAttributes
from jsktoolbox.raisetool import Raise

from rscan_libs.data import RscanData
from rscan_libs.mlog import MLogClient
from rscan_libs.system import LogClient


try:
    import numpy as np
except ModuleNotFoundError:
    pass

try:
    from scipy.spatial import distance
except ModuleNotFoundError:
    pass


class Euclid(MLogClient, NoDynamicAttributes):
    """Euclid.

    A class that calculates the length of a vector in Cartesian space.
    """

    __test = None
    __data = None

    def __init__(self, queue: Union[Queue, SimpleQueue], data: RscanData):
        """Create class object."""
        self.__test = [
            self.__numpy_l2,
            self.__numpy,
            self.__einsum,
            self.__scipy,
            self.__math,
            self.__core,
        ]

        # init log subsystem
        if isinstance(queue, (Queue, SimpleQueue)):
            self.logger = LogClient(queue)
        else:
            raise Raise.error(
                f"Queue or SimpleQueue type expected, '{type(queue)}' received.",
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

        self.debug(inspect.currentframe(), "Initialize dataset")

    def benchmark(self):
        """Do benchmark test.

        Compare the computational efficiency of functions for real data
        and choose the right priority of their use.
        """
        pname = f"{self.__data.pluginname}"
        cname = f"{self.__class__.__name__}"

        self.logger.info = f"{pname}->{cname}: Warming up math system..."
        data1 = [
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
        data2 = [
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
            tstart = time.time()
            for idx in range(0, len(data1)):
                item(data1[idx], data2[idx])
            tstop = time.time()
            bench_out[tstop - tstart] = item

        # optimize list of the methods
        self.__test.clear()
        for idx in sorted(bench_out.keys()):
            self.__test.append(bench_out[idx])
            self.debug(inspect.currentframe(), f"{idx}: {bench_out[idx]}")

        self.logger.info = f"{pname}->{cname}: done."

    def debug(self, currentframe: FrameType, message: str = ""):
        """Build debug message."""
        pname = f"{self.__data.pluginname}"
        cname = f"{self.__class__.__name__}"
        mname = f"{currentframe.f_code.co_name}"
        if message != "":
            message = f": {message}"
        self.logger.debug = f"{pname}->{cname}.{mname}{message}"

    def __core(self, point_1: List, point_2: List) -> float:
        """Do calculations without math libraries.

        The method iterates over each pair of vector elements,
        performs calculations on it and sums up the intermediate results.
        """
        return sum((i - j) ** 2 for i, j in zip(point_1, point_2)) ** 0.5

    def __math(self, point_1: List, point_2: List) -> float:
        """Try to use math lib."""
        try:
            return math.dist(point_1, point_2)
        except Exception as ex:
            self.debug(inspect.currentframe(), f"{ex}")
            return None

    def __numpy_l2(self, point_1: List, point_2: List) -> float:
        """Try to use numpy lib.

        The method uses the fact that the Euclidean distance of two vectors
        is nothing but the L^2 norm of their difference.
        """
        try:
            return np.linalg.norm(np.array(point_1) - np.array(point_2))
        except Exception as ex:
            self.debug(inspect.currentframe(), f"{ex}")
            return None

    def __numpy(self, point_1: List, point_2: List) -> float:
        """Try to use numpy lib.

        The method is an optimization of the core method using numpy
        and vectorization.
        """
        try:
            return np.sqrt(np.sum((np.array(point_1) - np.array(point_2)) ** 2))
        except Exception as ex:
            self.debug(inspect.currentframe(), f"{ex}")
            return None

    def __einsum(self, point_1: List, point_2: List) -> float:
        """Try to use numpy lib.

        Einstein summation convention.
        """
        try:
            tmp = np.array(point_1) - np.array(point_2)
            return np.sqrt(np.einsum("i,i->", tmp, tmp))
        except Exception as ex:
            self.debug(inspect.currentframe(), f"{ex}")
            return None

    def __scipy(self, point_1: List, point_2: List) -> float:
        """Try to use scipy lib.

        The scipy library has a built-in function to calculate
        the Euclidean distance.
        """
        try:
            return distance.euclidean(point_1, point_2)
        except Exception as ex:
            self.debug(inspect.currentframe(), f"{ex}")
            return None

    def distance(self, point_1: List, point_2: List) -> float:
        """Find the first working algorithm and do the calculations."""
        out = None
        i = 0

        while out is None:
            if i < len(self.__test):
                out = self.__test[i](point_1, point_2)
            else:
                break
            i += 1

        return out


# #[EOF]#######################################################################
