"""
Abstract base class for locator strategies.

This module defines the `LocatorStrategy` interface which requires
implementations to provide a method for locating an entity within
a grid based on the entity's name.

@Author: Eric Santos <ericshantos13@gmail.com>
"""

from abc import ABC, abstractmethod

from ..global_typing import GridType, PosType


class LocatorStrategy(ABC):
    """
    Abstract base class for strategies that locate entities in a grid.

    Subclasses must implement the `locate` method to provide the
    (row, column) position for an entity given the grid size.
    """

    @abstractmethod
    def locate(self, grid_size: GridType) -> PosType:
        """
        Determine the position of the specified entity within the grid.

        Args:
            entity_name (str): The name of the entity to locate.
            grid_size (GridType): The size of the grid as (height, width).

        Returns:
            GridType: The (row, column) position of the entity.

        Raises:
            NotImplementedError: If the method is not overridden by a subclass.
        """
        pass
