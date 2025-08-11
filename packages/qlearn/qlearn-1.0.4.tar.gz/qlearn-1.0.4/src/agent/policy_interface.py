"""
Abstract base class for policy strategies in reinforcement learning.

This module defines the `PolicyStrategy` interface, which specifies
methods for action selection based on Q-values and epsilon decay
for exploration-exploitation balance.

@Author: Eric Santos <ericshantos13@gmail.com>
"""

from abc import ABC, abstractmethod

from ..controllers.action_space import ActionSpace
from .typing import QValueType


class PolicyStrategy(ABC):
    """
    Abstract base class for policy strategies.

    Attributes:
        epsilon (float): Current exploration rate.
        min_epsilon (float): Minimum exploration rate.
        decay (float): Decay factor for epsilon after each episode or step.
    """

    def __init__(
        self, epsilon: float = 1.0, min_epsilon: float = 0.1, decay: float = 0.995
    ) -> None:
        """
        Initializes the policy strategy with epsilon parameters.

        Args:
            epsilon (float, optional): Initial exploration rate. Defaults to 1.0.
            min_epsilon (float, optional): Minimum exploration rate. Defaults to 0.1.
            decay (float, optional): Multiplicative decay factor for epsilon. Defaults to 0.995.
        """
        self.epsilon = epsilon
        self.min_epsilon = min_epsilon
        self.decay = decay

    @abstractmethod
    def choose(self, q_values: QValueType, action: ActionSpace) -> int:
        """
        Chooses an action based on the current policy.

        Args:
            q_values (QValueType): List of Q-values for available actions.
            action (ActionSpace): The action space from which to choose.

        Returns:
            int: The index of the selected action.
        """
        pass

    @abstractmethod
    def decay_epsilon(self) -> None:
        """
        Decays the exploration rate (epsilon) according to the decay schedule.
        """
        pass
