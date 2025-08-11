"""
Epsilon-Greedy policy implementation for action selection.

This module defines the `EpsilonGreedyPolicy` class, a concrete
implementation of `PolicyStrategy` that balances exploration and
exploitation using an epsilon-greedy approach.

@Author: Eric Santos <ericshantos13@gmail.com>
"""

import random

import numpy as np

from ..controllers.action_space import ActionSpace
from .policy_interface import PolicyStrategy
from .typing import QValueType


class EpsilonGreedyPolicy(PolicyStrategy):
    """
    Epsilon-Greedy policy for reinforcement learning.

    Attributes:
        epsilon (float): Current exploration rate.
        min_epsilon (float): Minimum exploration rate.
        decay (float): Decay factor applied to epsilon after each step.
    """

    def __init__(
        self, epsilon: float = 1.0, min_epsilon: float = 0.1, decay: float = 0.995
    ) -> None:
        """
        Initializes the epsilon-greedy policy.

        Args:
            epsilon (float, optional): Initial exploration rate. Defaults to 1.0.
            min_epsilon (float, optional): Minimum exploration rate. Defaults to 0.1.
            decay (float, optional): Multiplicative decay factor for epsilon. Defaults to 0.995.
        """
        self.epsilon = epsilon
        self.min_epsilon = min_epsilon
        self.decay = decay

    def choose(self, q_values: QValueType, action: ActionSpace) -> int:
        """
        Chooses an action using epsilon-greedy strategy.

        Args:
            q_values (QValueType): List or array of Q-values for available actions.
            action (ActionSpace): The action space from which to choose.

        Returns:
            int: Selected action index.
        """
        if random.uniform(0, 1) < self.epsilon:
            return action.sample()
        return int(np.argmax(q_values))

    def decay_epsilon(self) -> None:
        """
        Decays the exploration rate epsilon, ensuring it doesn't fall below minimum.
        """
        self.epsilon = max(self.min_epsilon, self.epsilon * self.decay)
