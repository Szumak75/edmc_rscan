# -*- coding: UTF-8 -*-
"""
  Author:  Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
  Created: 19.12.2023

  Purpose: Data container classes.
"""


from inspect import currentframe
from typing import Union, Optional, Dict, Any

from rscan.jsktoolbox.attribtool import ReadOnlyClass
from rscan.jsktoolbox.raisetool import Raise
from rscan.jsktoolbox.edmctool.stars import StarsSystem
from rscan.jsktoolbox.basetool.data import BData


class _Keys(object, metaclass=ReadOnlyClass):
    """Internal Keys container class."""

    CMDR: str = "__cmdr__"
    JUMP_RANGE: str = "__jump_range__"
    JUMP_SYSTEM: str = "__jump_system__"
    PLUGIN_NAME: str = "__plugin_name__"
    SHUTDOWN: str = "__shutdown__"
    STAR_SYSTEM: str = "__star_system__"
    VERSION: str = "__version__"


class RscanData(BData):
    """Data container for username and current system."""

    # __data: Dict[str, Any] = None  # type: ignore

    def __init__(self) -> None:
        """Initialize dataset."""
        self._set_data(
            key=_Keys.CMDR,
            set_default_type=Optional[str],
            value=None,
        )
        self._set_data(
            key=_Keys.PLUGIN_NAME,
            set_default_type=Optional[str],
            value=None,
        )
        self._set_data(
            key=_Keys.VERSION,
            set_default_type=Optional[str],
            value=None,
        )
        self._set_data(
            key=_Keys.JUMP_RANGE,
            set_default_type=Optional[float],
            value=None,
        )
        self._set_data(
            key=_Keys.STAR_SYSTEM,
            set_default_type=StarsSystem,
            value=StarsSystem(),
        )
        self._set_data(
            key=_Keys.JUMP_SYSTEM, set_default_type=StarsSystem, value=StarsSystem()
        )
        self._set_data(
            key=_Keys.SHUTDOWN,
            set_default_type=bool,
            value=False,
        )

    def __repr__(self) -> str:
        """Return class dump."""
        return (
            f"{self._c_name}(cmdr='{self.cmdr}', "
            f"plugin_name='{self.plugin_name}', "
            f"version='{self.version}', "
            f"jump_range={self.jump_range}, "
            f"{self.star_system})"
        )

    @property
    def jump_system(self) -> StarsSystem:
        """Return StarsSystem object."""
        return self._get_data(key=_Keys.JUMP_SYSTEM)  # type: ignore

    @jump_system.setter
    def jump_system(self, value: Optional[StarsSystem]) -> None:
        if value is None:
            self._set_data(key=_Keys.JUMP_SYSTEM, value=StarsSystem())
        self._set_data(
            key=_Keys.JUMP_SYSTEM,
            value=value,
        )

    @property
    def star_system(self) -> StarsSystem:
        """Return StarsSystem object."""
        return self._get_data(key=_Keys.STAR_SYSTEM)  # type: ignore

    @star_system.setter
    def star_system(self, value: Optional[StarsSystem]) -> None:
        if value is None:
            self._set_data(key=_Keys.STAR_SYSTEM, value=StarsSystem())
        self._set_data(
            key=_Keys.STAR_SYSTEM,
            value=value,
        )

    @property
    def jump_range(self) -> float:
        """Return jump_range."""
        return self._get_data(key=_Keys.JUMP_RANGE)  # type: ignore

    @jump_range.setter
    def jump_range(self, value: Union[str, int, float]) -> None:
        if value is not None and isinstance(value, (str, int, float)):
            try:
                self._set_data(
                    key=_Keys.JUMP_RANGE,
                    value=float(value),
                )
            except Exception:
                pass

    @property
    def plugin_name(self) -> str:
        """Return pluginname."""
        return self._get_data(key=_Keys.PLUGIN_NAME)  # type: ignore

    @plugin_name.setter
    def plugin_name(self, value: Optional[str]) -> None:
        if value is not None and isinstance(value, str):
            self._set_data(key=_Keys.PLUGIN_NAME, value=value)

    @property
    def version(self) -> str:
        """Return version."""
        return self._get_data(
            key=_Keys.VERSION,
        )  # type: ignore

    @version.setter
    def version(self, value: Optional[str]) -> None:
        if value is not None and isinstance(value, str):
            self._set_data(
                key=_Keys.VERSION,
                value=value,
            )

    @property
    def cmdr(self) -> str:
        """Return commander name."""
        return self._get_data(
            key=_Keys.CMDR,
        )  # type: ignore

    @cmdr.setter
    def cmdr(self, value: Optional[str]) -> None:
        if value is not None and value != self.cmdr:
            self._set_data(key=_Keys.CMDR, value=value)

    @property
    def shutting_down(self) -> bool:
        """Return access to shutting_down flag."""
        return self._get_data(
            key=_Keys.SHUTDOWN,
        )  # type: ignore

    @shutting_down.setter
    def shutting_down(self, value: bool) -> None:
        self._set_data(
            key=_Keys.SHUTDOWN,
            value=value,
        )


# #[EOF]#######################################################################
