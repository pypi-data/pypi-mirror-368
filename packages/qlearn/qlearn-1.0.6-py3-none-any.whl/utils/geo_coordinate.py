"""
Utility for generating random geographic coordinates.

This module provides the `GeoCoordinate` class, which contains methods
for generating random coordinates within specified bounds.

@Author: Eric Santos <ericshantos13@gmail.com>
"""

import random

from ..global_typing import GridType, PosType


class GeoCoordinate:
    """
    Utility class for working with geographic coordinates.

    This class currently provides a method to generate random coordinates
    within a given size or grid range.
    """

    @staticmethod
    def random(size: GridType) -> PosType:
        """
        Generates a random coordinate within the specified size limits.

        Args:
            size (GridType): A tuple (width, height) specifying the maximum
                bounds for the coordinate generation. Coordinates will be in the
                range [0, width-1] for the x-axis and [0, height-1] for the y-axis.

        Returns:
            PosType: A tuple containing two integers (x, y) representing
            the generated coordinate.
        """
        x = random.randint(0, size[0] - 1)
        y = random.randint(0, size[1] - 1)
        return (x, y)
