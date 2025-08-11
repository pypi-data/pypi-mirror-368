"""
Module for training reinforcement learning agents using the Q-Learning algorithm.

This module provides the `Trainer` class, which manages the training loop,
tracks rewards, and displays training metrics for a reinforcement learning agent
interacting with an environment.

@Author: Eric Santos <ericshantos13@gmail.com>
"""

from typing import List

import numpy as np

from ..agent.my_agent import MyAgent
from ..global_typing import NumericType
from ..search.object_search import ObjectSearch


class Trainer:
    """
    Handles the training process for a reinforcement learning agent.

    This class encapsulates the training loop, tracks episode rewards,
    computes moving averages, and displays performance metrics.

    Attributes:
        env (ObjectSearch): The environment in which the agent is trained.
        agent (MyAgent): The reinforcement learning agent.
        episodes (int): Total number of training episodes.
        max_steps_per_episode (int): Maximum steps allowed per episode.
        rewards_per_episode (List[float]): List of rewards obtained per episode.
        moving_average (List[float]): List of moving average rewards.
    """

    def __init__(
        self,
        env: ObjectSearch,
        agent: MyAgent,
        episodes: int = 500,
        max_steps_per_episode: int = 100,
    ):
        """
        Initializes the Trainer instance.

        Args:
            env (ObjectSearch): The environment in which the agent will be trained.
            agent (MyAgent): The agent to be trained.
            episodes (int, optional): Number of training episodes. Defaults to 500.
            max_steps_per_episode (int, optional): Maximum steps per episode. Defaults to 100.
        """
        self.env = env
        self.agent = agent
        self.episodes = episodes
        self.max_steps_per_episode = max_steps_per_episode

        self.rewards_per_episode: List[NumericType] = []
        self.moving_average: List[NumericType] = []

    def _calculate_avg(self, values: List[NumericType]) -> NumericType:
        """
        Calculates the mean value of a list.

        Args:
            values (List[NumericType]): List of numerical values.

        Returns:
            NumericType: The average of the provided values.
        """
        return np.mean(values)

    def _display_metrics(self, episode: int, total_reward: NumericType) -> None:
        """
        Displays training metrics for a given episode.

        Args:
            episode (int): The current episode number.
            total_reward (NumericType): Total accumulated reward for the episode.
        """
        print(
            f"Episode {episode}, "
            f"Total Reward: {total_reward}, "
            f"Epsilon: {self.agent.policy.epsilon:.4f}"
        )

    def train(self) -> None:
        """
        Executes the training loop for the agent.

        This method iterates through the defined number of episodes, allowing
        the agent to interact with the environment, learn from its experiences,
        and adjust its exploration rate.
        """
        for episode in range(self.episodes + 1):
            total_reward = 0.0
            state = self.env.get_state()[0]

            for _ in range(self.max_steps_per_episode):
                action = self.agent.choose_action(state)
                reward, terminated = self.env.step(action)
                next_state = self.env.get_state()[0]

                self.agent.learn(state, action, reward, next_state)
                state = next_state
                total_reward += reward

                if terminated:
                    break

            self.rewards_per_episode.append(total_reward)
            self.agent.decay_exploration()

            if episode >= 10:
                self.moving_average.append(
                    self._calculate_avg(self.rewards_per_episode[-10:])
                )
            else:
                self.moving_average.append(total_reward)

            if episode % 50 == 0:
                self._display_metrics(episode, total_reward)
