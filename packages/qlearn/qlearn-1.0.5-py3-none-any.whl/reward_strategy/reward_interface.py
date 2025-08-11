"""
Abstract base class for reward calculation strategies.

This module defines the `RewardStrategy` abstract class, which specifies
the interface for computing rewards in a reinforcement learning environment.

@Author: Eric Santos <ericshantos13@gmail.com>
"""

from abc import ABC, abstractmethod

from ..global_typing import NumericType, StateType


class RewardStrategy(ABC):
    """
    Abstract base class for reward strategies.

    Subclasses must implement the `compute` method, which calculates
    a reward based on the previous and new environment states and the
    action taken by the agent.
    """

    @abstractmethod
    def compute(
        self,
        old_state: StateType,
        new_state: StateType,
    ) -> NumericType:
        """
        Compute the reward for a given transition in the environment.

        Args:
            old_state (StateFn):
                The state before the action was taken. Typically a tuple
                containing positions or environment status.
            new_state (StateFn):
                The state after the action was taken.
            action (int):
                The index of the action performed by the agent.

        Returns:
            NumericType:
                The computed reward, which can be positive, negative, or zero.
        """
        pass
