# -*- coding: UTF-8 -*-
"""
  Author:  Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
  Created: 19.12.2023

  Purpose:
"""

from inspect import currentframe
from typing import Optional, Union, Dict, List

from jsktoolbox.raisetool import Raise
from jsktoolbox.attribtool import ReadOnlyClass
from jsktoolbox.libs.base_data import BData


class _Keys(object, metaclass=ReadOnlyClass):
    """Keys container class."""

    NAME = "__name__"
    ADDRESS = "__address__"
    POS_X = "__x__"
    POS_Y = "__y__"
    POS_Z = "__z__"
    DATA = "__data_container__"


class StarsSystem(BData):
    """StarsSystem container class."""

    def __init__(
        self,
        name: Optional[str] = None,
        address: Optional[int] = None,
        star_pos: Optional[List] = None,
    ) -> None:
        """Create Star System object."""
        self.name = name
        self.address = address
        self.star_pos = star_pos

    def __repr__(self) -> str:
        """Give me class dump."""
        return (
            f"{self._c_name}(name='{self.name}', "
            f"address={self.address}, "
            f"starpos={self.star_pos}, "
            f"data={self.data})"
        )

    def update_from_edsm(self, data: Dict) -> None:
        """Update records from given EDSM Api dict."""
        if data is None or not isinstance(data, dict):
            return

        self.name = data.get("name", self.name)
        self.address = data.get("id64", self.address)
        if "coords" in data and "x" in data["coords"]:
            self.pos_x = data["coords"].get("x", self.pos_x)
            self.pos_y = data["coords"].get("y", self.pos_y)
            self.pos_z = data["coords"].get("z", self.pos_z)
        if "bodyCount" in data:
            self.data["bodycount"] = data["bodyCount"]
        if "coordsLocked" in data:
            self.data["coordslocked"] = data["coordsLocked"]
        if "requirePermit" in data:
            self.data["requirepermit"] = data["requirePermit"]
        if "distance" in data:
            self.data["distance"] = data["distance"]

    @property
    def address(self) -> Optional[int]:
        """Give me address of system."""
        if _Keys.ADDRESS not in self._data:
            self._data[_Keys.ADDRESS] = None
        return self._data[_Keys.ADDRESS]

    @address.setter
    def address(self, arg: Optional[Union[int, str]]) -> None:
        if arg is None or isinstance(arg, int):
            self._data[_Keys.ADDRESS] = arg
        elif isinstance(arg, str) and arg.isdigit():
            self._data[_Keys.ADDRESS] = int(arg)
        else:
            raise Raise.error(
                f"Expected Int type, received: '{type(arg)}'",
                TypeError,
                self._c_name,
                currentframe(),
            )

    @property
    def name(self) -> Optional[str]:
        """Give me name of system."""
        if _Keys.NAME not in self._data:
            self._data[_Keys.NAME] = None
        return self._data[_Keys.NAME]

    @name.setter
    def name(self, arg: Optional[str]) -> None:
        if arg is None or isinstance(arg, str):
            self._data[_Keys.NAME] = arg
            if arg is None:
                self.address = None
                self.star_pos = None
        else:
            raise Raise.error(
                f"Expected String type, received: '{type(arg)}'.",
                TypeError,
                self._c_name,
                currentframe(),
            )

    @property
    def pos_x(self) -> Optional[float]:
        """Give me pos_x of system."""
        if _Keys.POS_X not in self._data:
            self._data[_Keys.POS_X] = None
        return self._data[_Keys.POS_X]

    @pos_x.setter
    def pos_x(self, arg: Optional[float]) -> None:
        if arg is None:
            self._data[_Keys.POS_X] = arg
        elif isinstance(arg, (int, float)):
            self._data[_Keys.POS_X] = float(arg)
        else:
            raise Raise.error(
                f"Expected int or float type, received: '{type(arg)}'.",
                TypeError,
                self._c_name,
                currentframe(),
            )

    @property
    def pos_y(self) -> Optional[float]:
        """Give me pos_y of system."""
        if _Keys.POS_Y not in self._data:
            self._data[_Keys.POS_Y] = None
        return self._data[_Keys.POS_Y]

    @pos_y.setter
    def pos_y(self, arg: Optional[float]) -> None:
        if arg is None:
            self._data[_Keys.POS_Y] = arg
        elif isinstance(arg, (int, float)):
            self._data[_Keys.POS_Y] = float(arg)
        else:
            raise Raise.error(
                f"Expected int or float type, received: '{type(arg)}'.",
                TypeError,
                self._c_name,
                currentframe(),
            )

    @property
    def pos_z(self) -> Optional[float]:
        """Give me pos_z of system."""
        if _Keys.POS_Z not in self._data:
            self._data[_Keys.POS_Z] = None
        return self._data[_Keys.POS_Z]

    @pos_z.setter
    def pos_z(self, arg: Optional[float]) -> None:
        if arg is None:
            self._data[_Keys.POS_Z] = arg
        elif isinstance(arg, (int, float)):
            self._data[_Keys.POS_Z] = float(arg)
        else:
            raise Raise.error(
                f"Expected int or float type, received: '{type(arg)}'.",
                TypeError,
                self._c_name,
                currentframe(),
            )

    @property
    def star_pos(self) -> List[float]:
        """Give me star position list."""
        return [self.pos_x, self.pos_y, self.pos_z]

    @star_pos.setter
    def star_pos(self, arg: Optional[List] = None) -> None:
        if arg is None:
            (self.pos_x, self.pos_y, self.pos_z) = (None, None, None)
        elif isinstance(arg, list) and len(arg) == 3:
            (self.pos_x, self.pos_y, self.pos_z) = arg
        else:
            raise Raise.error(
                f"Expected list type, received: '{type(arg)}'.",
                TypeError,
                self._c_name,
                currentframe(),
            )

    @property
    def star_class(self) -> str:
        """Give me star class string."""
        if "StarClass" in self.data:
            return self.data["StarClass"]
        return ""

    @star_class.setter
    def star_class(self, value: str) -> None:
        """Set StarClass string."""
        self.data["StarClass"] = value

    @property
    def data(self) -> Dict:
        """Return data container.

        This is dictionary object for storing various elements.
        """
        if _Keys.DATA not in self._data:
            self._data[_Keys.DATA] = {}
        return self._data[_Keys.DATA]

    @data.setter
    def data(self, value: Optional[Dict]):
        if value is None:
            self._data[_Keys.DATA] = {}
        if not isinstance(value, Dict):
            raise Raise.error(
                f"Type of data containet is dict, '{type(value)}' received, cannot proceed.",
                ValueError,
                self._c_name,
                currentframe(),
            )
        self._data[_Keys.DATA] = value


# #[EOF]#######################################################################
