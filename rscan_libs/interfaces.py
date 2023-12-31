# -*- coding: UTF-8 -*-
"""
  Author:  Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
  Created: 19.12.2023

  Purpose: interface class.
"""

from abc import ABC, abstractmethod


class IAlg(ABC):
    """Interface for algorithm class ."""

    @abstractmethod
    def run(self):
        """Run the work."""

    @abstractmethod
    def debug(self, currentframe, message):
        """Debug formater for logger."""

    @property
    @abstractmethod
    def get_final(self) -> list:
        """Return final data."""


# #[EOF]#######################################################################
