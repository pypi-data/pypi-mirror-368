"""
Reward strategy based on the change in distance between the agent and the target.

This module defines the `RewardDistance` class, which implements a reward
function for reinforcement learning tasks in a 2D grid environment. The
reward is computed based on how much closer or farther the agent moves
relative to the target, plus optional penalties and success rewards.

@Author: Eric Santos <ericshantos13@gmail.com>
"""

import numpy as np

from ..global_typing import GridType, NumericType, PosType, StateType
from .reward_interface import RewardStrategy


class RewardDistance(RewardStrategy):
    """
    Computes rewards based on distance change between agent and target.

    This strategy encourages the agent to move closer to the target
    by providing positive rewards for reduced distance and penalties
    for moving away, moving out of bounds, or simply moving without
    reaching the target.

    Attributes:
        h (int): Height of the grid.
        w (int): Width of the grid.
        scale_factor (int): Multiplier for the distance change reward.
        move_penalty (float): Constant penalty applied on every move.
        out_of_bounds_penalty (int): Penalty for attempting to move outside the grid.
        success_reward (int): Reward for reaching the target.
    """

    def __init__(
        self,
        grid_size: GridType,
        scale_factor: int = 5,
        move_penalty: float = -0.1,
        out_of_bounds_penalty: int = -5,
        success_reward: int = 20,
    ):
        """
        Initializes the distance-based reward strategy.

        Args:
            grid_size (GridType): The size of the grid as (height, width).
            scale_factor (int, optional): Scales the distance change reward.
            move_penalty (float, optional): Constant penalty for each move.
            out_of_bounds_penalty (int, optional): Penalty for moving out of bounds.
            success_reward (int, optional): Reward for reaching the target.
        """
        self.h, self.w = grid_size
        self.scale_factor = scale_factor
        self.move_penalty = move_penalty
        self.out_of_bounds_penalty = out_of_bounds_penalty
        self.success_reward = success_reward

    def _calculate_clidean_distance(self, pos_a: PosType, pos_b: PosType) -> float:
        """
        Computes the Euclidean distance between two positions.

        Args:
            pos_a (PosType): First position.
            pos_b (PosType): Second position.

        Returns:
            float: Euclidean distance between pos_a and pos_b.
        """
        return np.linalg.norm(np.array(pos_a) - np.array(pos_b))

    def _between(self, value: NumericType, max_value: int) -> bool:
        """
        Checks whether a value is within [0, max_value).

        Args:
            value (NumericType): Value to check.
            max_value (int): Maximum allowed value (exclusive).

        Returns:
            bool: True if within bounds, False otherwise.
        """
        return 0 <= value < max_value

    def compute(self, old_state: StateType, new_state: StateType) -> NumericType:
        """
        Computes the reward for a given step based on distance change.

        Args:
            old_state (StateType): The state before the action.
            new_state (StateType): The state after the action.

        Returns:
            NumericType:
                The computed reward, which can be positive, negative, or zero.
        """
        agent_pos, target_pos = old_state
        new_agent_pos, _ = new_state

        # Success condition
        if new_agent_pos == target_pos:
            return self.success_reward

        # Out-of-bounds penalty
        if not self._between(new_agent_pos[0], self.h) or not self._between(
            new_agent_pos[1], self.w
        ):
            return self.out_of_bounds_penalty

        # Distance change reward
        old_distance = self._calculate_clidean_distance(agent_pos, target_pos)
        new_distance = self._calculate_clidean_distance(new_agent_pos, target_pos)
        distance_reward = (old_distance - new_distance) * self.scale_factor

        return distance_reward + self.move_penalty
