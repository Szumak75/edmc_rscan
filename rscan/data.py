# -*- coding: UTF-8 -*-
"""
  Author:  Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
  Created: 19.12.2023

  Purpose: Data container classes.
"""


from inspect import currentframe
from typing import Union, Optional, Dict, Any
from rscan.jsktoolbox.attribtool import NoDynamicAttributes
from rscan.jsktoolbox.raisetool import Raise
from rscan.jsktoolbox.edmctool.stars import StarsSystem


class RscanData(NoDynamicAttributes):
    """Data container for username and current system."""

    __data: Dict[str, Any] = None  # type: ignore

    def __init__(self) -> None:
        """Initialize dataset."""
        self.__data = {
            "cmdr": None,
            "pluginname": None,
            "version": None,
            "jump_range": None,
            "star_system": StarsSystem(),
            "jump_system": StarsSystem(),
            "shutdown": False,
        }

    def __repr__(self) -> str:
        """Give me class dump."""
        return (
            f"{self.__class__.__name__}(cmdr='{self.__data['cmdr']}', "
            f"pluginname='{self.__data['pluginname']}', "
            f"version='{self.__data['version']}', "
            f"jump_range={self.__data['jump_range']}, "
            f"{self.__data['star_system']})"
        )

    @property
    def jump_system(self) -> StarsSystem:
        """Give me StarsSystem object."""
        return self.__data["jump_system"]

    @jump_system.setter
    def jump_system(self, value: Optional[StarsSystem]) -> None:
        if value is None:
            self.__data["jump_system"] = StarsSystem()
        elif isinstance(value, StarsSystem):
            self.__data["jump_system"] = value

    @property
    def star_system(self) -> StarsSystem:
        """Give me StarsSystem object."""
        return self.__data["star_system"]

    @star_system.setter
    def star_system(self, value: StarsSystem) -> None:
        if value is None:
            self.__data["star_system"] = StarsSystem()
        elif isinstance(value, StarsSystem):
            self.__data["star_system"] = value

    @property
    def jump_range(self) -> float:
        """Give me jump_range."""
        return self.__data["jump_range"]

    @jump_range.setter
    def jump_range(self, value: Union[str, int, float]) -> None:
        if value is not None and isinstance(value, (str, int, float)):
            try:
                self.__data["jump_range"] = float(value)
            except Exception:
                pass

    @property
    def plugin_name(self) -> str:
        """Give me pluginname."""
        return self.__data["pluginname"]

    @plugin_name.setter
    def plugin_name(self, value: str) -> None:
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
                currentframe(),
            )


# #[EOF]#######################################################################
