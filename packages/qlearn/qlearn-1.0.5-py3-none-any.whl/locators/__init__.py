"""
This module provides locator strategies for use in Q-Learning environments.

It exposes the following classes:
    - LocatorStrategy: The interface for locator strategies.
    - FixedLocator: A locator that uses a fixed strategy.
    - RandomLocator: A locator that uses a random strategy.
"""

from .fixed_locator import FixedLocator
from .locator_interface import LocatorStrategy
from .random_locator import RandomLocator

__all__ = ["LocatorStrategy", "FixedLocator", "RandomLocator"]

__author__ = "Eric Santos <ericshantos13@gmail.com>"
