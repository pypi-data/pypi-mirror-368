"""
Random position locator strategy.

This module defines the `RandomLocator` class, which implements a locator
strategy that returns a random valid position within a given grid.

@Author: Eric Santos <ericshantos13@gmail.com>
"""

from ..global_typing import GridType, PosType
from ..utils.geo_coordinate import GeoCoordinate
from .locator_interface import LocatorStrategy


class RandomLocator(LocatorStrategy):
    """
    Locator strategy that returns a random position within the grid.
    """

    def locate(self, grid_size: GridType) -> PosType:
        """
        Returns a random position inside the grid boundaries.

        Args:
            grid_size (GridType): The size of the grid as (height, width).

        Returns:
            Tuple[int, int]: A random (row, column) position within the grid.
        """
        return GeoCoordinate.random(grid_size)
