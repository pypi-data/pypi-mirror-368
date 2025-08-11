"""
Observation grid management for multi-channel spatial data.

This module defines the `ObservationGrid` class, which stores and manipulates
multi-channel 2D spatial data, typically used in environments such as
reinforcement learning observation spaces or multi-layer game boards.

@Author: Eric Santos <ericshantos13@gmail.com>
"""

from typing import Type

import numpy as np

from ..global_typing import GridType, NumericType, PosType


class ObservationGrid:
    """
    Represents a multi-channel 2D grid for storing spatial observations.

    Each position in the grid can contain multiple channels, allowing the
    representation of layered information such as entities, terrain, or
    other attributes.

    Attributes:
        _grid (np.ndarray): Internal NumPy array storing the grid data.
    """

    def __init__(self, shape: GridType, dtype: Type[np.dtype] = np.int32):
        """
        Initializes the ObservationGrid.

        Args:
            shape (GridType): Shape of the grid as (rows, cols, channels).
            dtype (Type[np.dtype], optional): NumPy data type for storing values.
                Defaults to np.int32.
        """
        self._grid = np.zeros(shape, dtype=dtype)

    def set(self, position: PosType, channel: int, value: NumericType) -> None:
        """
        Sets a value at a specific position and channel.

        Args:
            position (PosType): (row, col) coordinates in the grid.
            channel (int): Channel index.
            value (Union[int, float]): Value to set.
        """
        self._grid[position + (channel,)] = value

    def clear_channel(self, channel: int) -> None:
        """
        Clears (sets to zero) all values in a given channel.

        Args:
            channel (int): Channel index to clear.
        """
        self._grid[:, :, channel] = 0

    def get(self, position: PosType, channel: int) -> NumericType:
        """
        Retrieves the value at a specific position and channel.

        Args:
            position (PosType): (row, col) coordinates.
            channel (int): Channel index.

        Returns:
            Union[int, float]: The value stored at the given position and channel.
        """
        x, y = position[:2]
        return self._grid[x, y, channel]

    def get_channel_matrix(self, channel: int) -> np.ndarray:
        """
        Retrieves the entire 2D matrix for a specific channel.

        Args:
            channel (int): Channel index.

        Returns:
            np.ndarray: A 2D NumPy array representing the channel's values.
        """
        return self._grid[:, :, channel]

    def find_position(self, channel: int, value: NumericType = 1) -> PosType:
        """
        Finds the first position where a given value appears in a specific channel.

        Args:
            channel (int): Channel index to search.
            value (NumericType): Value to locate. Defaults to 1.

        Returns:
            PosType: Coordinates (row, col) of the found value.

        Raises:
            ValueError: If the value is not found in the given channel.
        """
        pos = np.argwhere(self._grid[:, :, channel] == value)
        if len(pos) == 0:
            raise ValueError(f"Value {value} not found in channel {channel}")
        return tuple(pos[0])

    def get_full(self) -> np.ndarray:
        """
        Returns the full multi-channel grid.

        Returns:
            np.ndarray: The complete 3D NumPy array representing the grid.
        """
        return self._grid

    @property
    def shape(self) -> GridType:
        """
        Retrieves the shape of the grid.

        Returns:
            Tuple[int, int, int]: Shape as (rows, cols, channels).
        """
        return self._grid.shape
