"""
Q-table implementation for Q-Learning algorithms.

This module provides a simple Q-table data structure using a defaultdict
to store Q-values for discrete states and actions.

@Author: Eric Santos <ericshantos13@gmail.com>
"""

from collections import defaultdict
from typing import Dict

import numpy as np

from .typing import TrainStateType


class QTable:
    """
    Q-table for storing and updating action-value estimates.

    Attributes:
        q_table (defaultdict): Maps states to numpy arrays of action values.
    """

    def __init__(self, n_actions: int) -> None:
        """
        Initializes the Q-table.

        Args:
            n_actions (int): Number of possible discrete actions.
        """
        self.q_table: Dict[TrainStateType, np.ndarray] = defaultdict(
            lambda: np.zeros(n_actions)
        )

    def get(self, state: TrainStateType) -> np.ndarray:
        """
        Retrieves the Q-values for a given state.

        Args:
            state (StateType): The state identifier.

        Returns:
            np.ndarray: Array of Q-values for all actions in the state.
        """
        return self.q_table[state]

    def update(
        self, state: TrainStateType, action: int, target: float, lr: float
    ) -> None:
        """
        Updates the Q-value for a specific state-action pair using the learning rate.

        Args:
            state (TrainStateType): The state identifier.
            action (int): The action index.
            target (float): The target Q-value.
            lr (float): The learning rate.
        """
        predict = self.q_table[state][action]
        self.q_table[state][action] += lr * (target - predict)
