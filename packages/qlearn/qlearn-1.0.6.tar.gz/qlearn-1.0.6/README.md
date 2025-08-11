[🇧🇷] [Lê em português](README.pt.md)

# Q-Learning Library for Object Search in Grid Worlds

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.6+-blue.svg)](https://www.python.org/downloads/)
[![PyPI Version](https://img.shields.io/pypi/v/qlib-py.svg)](https://pypi.org/project/qlib-py/)

A Python reinforcement learning library implementing Q-learning with training workflows for object search tasks in grid worlds.

## Purpose

This library provides a complete library for training reinforcement learning agents to solve object search problems in 2D grid environments. The implementation focuses on:

- Q-learning algorithm with epsilon-greedy exploration
- Customizable observation and action spaces
- Flexible reward strategies
- Entity positioning with locator strategies
- Training workflow management

## Key Components

### Bellman Optimality Equation Implementation

The core learning mechanism implements the Bellman Optimality Equation through Q-value updates:

```python
Q(s, a) ← Q(s, a) + α[r + γ max Q(s', a') - Q(s, a)]
```

Where:
- `α` (learning rate) controls how much new information overrides old knowledge
- `γ` (discount factor) determines the importance of future rewards
- The equation balances immediate rewards with potential future rewards

This is implemented in `MyAgent.learn()` method (src/agent/my_agent.py):

```python
def learn(self, state, action, reward, next_state):
    next_q_values = self.q_table.get(next_state)
    target = reward + self.gamma * np.max(next_q_values)
    self.q_table.update(state, action, target, self.lr)
```

### Main Components

1. **Agent System**:
   - `MyAgent`: The Q-learning agent with exploration/exploitation balance
   - `QTable`: Stores and updates state-action values
   - `EpsilonGreedyPolicy`: Decaying exploration strategy

2. **Environment**:
   - `ObjectSearch`: Grid world environment for object search tasks
   - `ObservationSpace`: Manages entity positions and grid representation
   - `ActionSpace`: Defines available actions and their effects

3. **Training**:
   - `Trainer`: Manages the training loop and performance tracking
   - `RewardDistance`: Distance-based reward strategy implementation

## Installation

```bash
pip install qlib-learn
```

## Usage Example

```python
from qlib_py.agent import MyAgent, EpsilonGreedyPolicy
from qlib_py.controllers import ActionSpace
from qlib_py.search import ObjectSearch
from qlib_py.trainment import Trainer

# Define action space
actions = ActionSpace(
    up=lambda x, y: (x, y+1),
    down=lambda x, y: (x, y-1),
    left=lambda x, y: (x-1, y),
    right=lambda x, y: (x+1, y)
)

# Initialize agent and environment
policy = EpsilonGreedyPolicy()
agent = MyAgent(actions, policy)
env = ObjectSearch(...)  # Configure with observation space, reward strategy, etc.

# Train the agent
trainer = Trainer(env, agent, episodes=1000)
trainer.train()
```

## Features

- **Modular Design**: Components can be easily replaced or extended
- **Type Hints**: Comprehensive typing support throughout the codebase
- **Quality Assurance**:
  - Pre-commit hooks for code formatting (Black, isort, flake8)
  - Type checking with mypy
  - CI/CD workflow for PyPI publishing

## Project Structure

```
qlib-py/
├── src/
│   ├── agent/          # Q-learning agent implementation
│   ├── controllers/    # Action space definitions
│   ├── locators/       # Entity positioning strategies
│   ├── reward_strategy/ # Reward calculation
│   ├── search/         # Environment implementation
│   ├── spaces/         # Observation space management
│   ├── trainment/      # Training workflow
│   └── utils/          # Helper functions
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
