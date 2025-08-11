"""
Fixed position locator strategy.

This module defines the `FixedLocator` class, which implements a locator
strategy that always returns the same fixed position within a grid.

@Author: Eric Santos <ericshantos13@gmail.com>
"""

from ..global_typing import GridType, PosType
from .locator_interface import LocatorStrategy


class FixedLocator(LocatorStrategy):
    """
    Locator strategy that returns a fixed position.

    Attributes:
        position (Tuple[int, int]): The fixed (x, y) position within the grid.
    """

    def __init__(self, position: PosType):
        """
        Initializes the FixedLocator with a fixed position.

        Args:
            position (PosType): The fixed position to always return.
        """
        self.position = position

    def locate(self, grid_size: GridType) -> PosType:
        """
        Returns the fixed position if it lies within the grid bounds.

        Args:
            grid_size (GridType): The size of the grid as (height, width).

        Returns:
            Tuple[int, int]: The fixed position.

        Raises:
            ValueError: If the fixed position is outside the grid bounds.
        """
        h, w = grid_size
        x, y = self.position

        if not (0 <= x < w and 0 <= y < h):
            raise ValueError(
                f"Position {
                    self.position} outside grid {grid_size}."
            )
        return self.position
