# -*- coding: UTF-8 -*-
"""
  Author:  Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
  Created: 19.12.2023

  Purpose: Data container classes.
"""


import inspect
from typing import Union, Optional, Dict, Any
from jsktoolbox.attribtool import NoDynamicAttributes
from jsktoolbox.raisetool import Raise
from rscan_libs.stars import StarsSystem


class RscanData(NoDynamicAttributes):
    """Data container for username and current system."""

    __data: Dict[str, Any] = None  # type: ignore

    def __init__(self) -> None:
        """Initialize dataset."""
        self.__data = {
            "cmdr": None,
            "pluginname": None,
            "version": None,
            "jumprange": None,
            "starsystem": StarsSystem(),
            "jumpsystem": StarsSystem(),
            "shutdown": False,
        }

    def __repr__(self) -> str:
        """Give me class dump."""
        return (
            f"{self.__class__.__name__}(cmdr='{self.__data['cmdr']}', "
            f"pluginname='{self.__data['pluginname']}', "
            f"version='{self.__data['version']}', "
            f"jumprange={self.__data['jumprange']}, "
            f"{self.__data['starsystem']})"
        )

    @property
    def jumpsystem(self) -> StarsSystem:
        """Give me StarsSystem object."""
        return self.__data["jumpsystem"]

    @jumpsystem.setter
    def jumpsystem(self, value: Optional[StarsSystem]) -> None:
        if value is None:
            self.__data["jumpsystem"] = StarsSystem()
        elif isinstance(value, StarsSystem):
            self.__data["jumpsystem"] = value

    @property
    def starsystem(self) -> StarsSystem:
        """Give me StarsSystem object."""
        return self.__data["starsystem"]

    @starsystem.setter
    def starsystem(self, value: StarsSystem) -> None:
        if value is None:
            self.__data["starsystem"] = StarsSystem()
        elif isinstance(value, StarsSystem):
            self.__data["starsystem"] = value

    @property
    def jumprange(self) -> float:
        """Give me jumprange."""
        return self.__data["jumprange"]

    @jumprange.setter
    def jumprange(self, value: Union[str, int, float]) -> None:
        if value is not None and isinstance(value, (str, int, float)):
            try:
                self.__data["jumprange"] = float(value)
            except Exception:
                pass

    @property
    def pluginname(self) -> str:
        """Give me pluginname."""
        return self.__data["pluginname"]

    @pluginname.setter
    def pluginname(self, value: str) -> None:
        if value is not None and isinstance(value, str):
            self.__data["pluginname"] = value

    @property
    def version(self) -> str:
        """Give me version."""
        return self.__data["version"]

    @version.setter
    def version(self, value: str) -> None:
        if value is not None and isinstance(value, str):
            self.__data["version"] = value

    @property
    def cmdr(self) -> str:
        """Give me commander name."""
        return self.__data["cmdr"]

    @cmdr.setter
    def cmdr(self, value) -> None:
        if value is not None and value != self.cmdr:
            self.__data["cmdr"] = value

    @property
    def shutting_down(self) -> bool:
        """Give me access to shutting_down flag."""
        return self.__data["shutdown"]

    @shutting_down.setter
    def shutting_down(self, value: bool) -> None:
        if isinstance(value, bool):
            self.__data["shutdown"] = value
        else:
            raise Raise.error(
                f"Boolean type expected, '{type(value)}' received.",
                TypeError,
                self.__class__.__name__,
                inspect.currentframe(),
            )


# #[EOF]#######################################################################
