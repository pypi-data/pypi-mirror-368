"""
This module provides the main agent and policy strategy implementations for reinforcement learning.

Classes:
    MyAgent: The primary agent class for interacting with the environment.
    EpsilonGreedyPolicy: Implements the epsilon-greedy exploration strategy.
    PolicyStrategy: Interface for defining custom policy strategies.
"""

from .epsilon_greedy_policy import EpsilonGreedyPolicy
from .my_agent import MyAgent
from .policy_interface import PolicyStrategy

__all__ = ["EpsilonGreedyPolicy", "MyAgent", "PolicyStrategy"]

__author__ = "Eric Santos <ericshantos13@gmail.com>"
