# -*- coding: UTF-8 -*-
"""
  Author:  Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
  Created: 19.12.2023

  Purpose: Data container classes.
"""


from inspect import currentframe
from typing import Union

from jsktoolbox.attribtool import ReadOnlyClass
from jsktoolbox.raisetool import Raise
from jsktoolbox.libs.base_data import BData

from rscan_libs.stars import StarsSystem


class _Keys(object, metaclass=ReadOnlyClass):
    """Keys container class."""

    CMDR = "_cmdr_"
    JUMPRANGE = "_jumprange_"
    JUMPSYSTEM = "_jumpsystem_"
    PLUGINNAME = "_pluginname_"
    RDATA = "__rdata__"
    SHUTDOWN = "_shutdown_"
    STARSYSTEM = "_starsystem_"
    VERSION = "_version_"


class RscanData(BData):
    """Data container for username and current system."""

    def __init__(self) -> None:
        """Initialize dataset."""
        self._data[_Keys.RDATA] = {
            _Keys.CMDR: None,
            _Keys.PLUGINNAME: None,
            _Keys.VERSION: None,
            _Keys.JUMPRANGE: None,
            _Keys.STARSYSTEM: StarsSystem(),
            _Keys.JUMPSYSTEM: StarsSystem(),
            _Keys.SHUTDOWN: False,
        }

    def __repr__(self) -> str:
        """Give me class dump."""
        return (
            f"{self._c_name}(cmdr='{self._data[_Keys.RDATA][_Keys.CMDR]}', "
            f"pluginname='{self._data[_Keys.RDATA][_Keys.PLUGINNAME]}', "
            f"version='{self._data[_Keys.RDATA][_Keys.VERSION]}', "
            f"jumprange={self._data[_Keys.RDATA][_Keys.JUMPRANGE]}, "
            f"{self._data[_Keys.RDATA][_Keys.STARSYSTEM]})"
        )

    @property
    def jumpsystem(self) -> StarsSystem:
        """Give me StarsSystem object."""
        return self._data[_Keys.RDATA][_Keys.JUMPSYSTEM]

    @jumpsystem.setter
    def jumpsystem(self, value: StarsSystem) -> None:
        if value is None:
            self._data[_Keys.RDATA][_Keys.JUMPSYSTEM] = StarsSystem()
        elif isinstance(value, StarsSystem):
            self._data[_Keys.RDATA][_Keys.JUMPSYSTEM] = value

    @property
    def starsystem(self) -> StarsSystem:
        """Give me StarsSystem object."""
        return self._data[_Keys.RDATA][_Keys.STARSYSTEM]

    @starsystem.setter
    def starsystem(self, value: StarsSystem) -> None:
        if value is None:
            self._data[_Keys.RDATA][_Keys.STARSYSTEM] = StarsSystem()
        elif isinstance(value, StarsSystem):
            self._data[_Keys.RDATA][_Keys.STARSYSTEM] = value

    @property
    def jumprange(self) -> float:
        """Give me jumprange."""
        return self._data[_Keys.RDATA][_Keys.JUMPRANGE]

    @jumprange.setter
    def jumprange(self, value: Union[str, int, float]) -> None:
        if value is not None and isinstance(value, (str, int, float)):
            try:
                self._data[_Keys.RDATA][_Keys.JUMPRANGE] = float(value)
            except Exception:
                pass

    @property
    def pluginname(self) -> str:
        """Give me pluginname."""
        return self._data[_Keys.RDATA][_Keys.PLUGINNAME]

    @pluginname.setter
    def pluginname(self, value: str) -> None:
        if value is not None and isinstance(value, str):
            self._data[_Keys.RDATA][_Keys.PLUGINNAME] = value

    @property
    def version(self) -> str:
        """Give me version."""
        return self._data[_Keys.RDATA][_Keys.VERSION]

    @version.setter
    def version(self, value: str) -> None:
        if value is not None and isinstance(value, str):
            self._data[_Keys.RDATA][_Keys.VERSION] = value

    @property
    def cmdr(self) -> str:
        """Give me commander name."""
        return self._data[_Keys.RDATA][_Keys.CMDR]

    @cmdr.setter
    def cmdr(self, value) -> None:
        if value is not None and value != self.cmdr:
            self._data[_Keys.RDATA][_Keys.CMDR] = value

    @property
    def shutting_down(self) -> bool:
        """Give me access to shutting_down flag."""
        return self._data[_Keys.RDATA][_Keys.SHUTDOWN]

    @shutting_down.setter
    def shutting_down(self, value: bool) -> None:
        if isinstance(value, bool):
            self._data[_Keys.RDATA][_Keys.SHUTDOWN] = value
        else:
            raise Raise.error(
                f"Boolean type expected, '{type(value)}' received.",
                TypeError,
                self._c_name,
                currentframe(),
            )


# #[EOF]#######################################################################
