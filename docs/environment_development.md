# Environment Development Guide

## Overview

This guide provides comprehensive instructions for developing reinforcement learning environments at Verita AI.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Environment Architecture](#environment-architecture)
3. [Creating a Custom Environment](#creating-a-custom-environment)
4. [Testing Your Environment](#testing-your-environment)
5. [Best Practices](#best-practices)

## Getting Started

### Prerequisites

- Python 3.8+
- PyTorch 2.0+
- OpenAI Gym

### Installation

```bash
# Clone the repository
git clone https://github.com/dl1413/trello-kanban-replica.git
cd trello-kanban-replica

# Install dependencies
pip install -r requirements.txt
```

## Environment Architecture

Our environments follow the OpenAI Gym interface with additional features:

```python
class CustomEnvironment(BaseEnvironment):
    def __init__(self, config):
        super().__init__(config)
        # Custom initialization
        
    def reset(self):
        # Reset environment state
        return observation
        
    def step(self, action):
        # Execute action and return (obs, reward, done, info)
        return observation, reward, done, info
```

### Key Components

1. **Observation Space**: Defines what the agent can observe
2. **Action Space**: Defines what actions the agent can take
3. **Reward Function**: Provides feedback for actions
4. **Episode Management**: Handles episode start/end conditions

## Creating a Custom Environment

### Step 1: Define Your Environment Class

```python
from environments import BaseEnvironment
from gym import spaces
import numpy as np

class MyCustomEnv(BaseEnvironment):
    def __init__(self, config=None):
        super().__init__(config)
        
        # Define custom action and observation spaces
        self.action_space = spaces.Discrete(5)
        self.observation_space = spaces.Box(
            low=0, high=1, shape=(10,), dtype=np.float32
        )
```

### Step 2: Implement Core Methods

```python
def _get_initial_state(self):
    """Initialize your environment state"""
    return np.random.rand(10)

def _update_state(self, action):
    """Update state based on action"""
    # Your state update logic here
    pass

def _calculate_reward(self, action):
    """Calculate reward for the action"""
    # Your reward calculation logic
    return 1.0 if self._check_goal() else -0.1

def _is_done(self):
    """Check if episode should terminate"""
    return self._check_goal() or self.current_step >= self.episode_length
```

### Step 3: Add Custom Logic

```python
def _check_goal(self):
    """Check if goal state is reached"""
    # Your goal checking logic
    return False

def render(self, mode='human'):
    """Optional: Implement rendering"""
    if mode == 'human':
        print(f"Step: {self.current_step}, State: {self.state}")
```

## Testing Your Environment

### Unit Tests

Create tests in the `tests/` directory:

```python
import pytest
from environments.my_custom_env import MyCustomEnv

def test_environment_creation():
    env = MyCustomEnv()
    assert env is not None

def test_reset():
    env = MyCustomEnv()
    obs = env.reset()
    assert obs.shape == (10,)

def test_step():
    env = MyCustomEnv()
    env.reset()
    obs, reward, done, info = env.step(0)
    assert isinstance(reward, float)
```

### Integration Testing

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest --cov=environments tests/
```

## Best Practices

### 1. Configuration Management

Always use configuration files for environment parameters:

```python
config = {
    'episode_length': 1000,
    'reward_scale': 1.0,
    'observation_type': 'vector'
}
env = MyCustomEnv(config)
```

### 2. Observation Normalization

Normalize observations for better training stability:

```python
def _get_observation(self):
    obs = self.state
    return (obs - obs.mean()) / (obs.std() + 1e-8)
```

### 3. Reward Shaping

Design informative rewards:

```python
def _calculate_reward(self, action):
    # Distance-based reward
    distance_reward = -np.linalg.norm(self.state - self.goal)
    
    # Goal bonus
    goal_reward = 100.0 if self._check_goal() else 0.0
    
    # Time penalty
    time_penalty = -0.01
    
    return distance_reward + goal_reward + time_penalty
```

### 4. Episode Termination

Define clear termination conditions:

```python
def _is_done(self):
    # Success condition
    if self._check_goal():
        return True
    
    # Timeout condition
    if self.current_step >= self.episode_length:
        return True
    
    # Failure condition
    if self._check_failure():
        return True
    
    return False
```

### 5. Reproducibility

Always set seeds for reproducibility:

```python
def reset(self):
    if self.config.get('seed') is not None:
        np.random.seed(self.config['seed'])
    return super().reset()
```

## Advanced Topics

### Vectorized Environments

For parallel training:

```python
from gym.vector import AsyncVectorEnv

def make_env():
    return MyCustomEnv(config)

envs = AsyncVectorEnv([make_env for _ in range(8)])
```

### Rendering and Visualization

Implement custom rendering:

```python
def render(self, mode='human'):
    if mode == 'rgb_array':
        # Return numpy array of shape (H, W, 3)
        return self._render_frame()
    elif mode == 'human':
        # Display using matplotlib or pygame
        self._display_frame()
```

### Logging and Metrics

Track important metrics:

```python
def _get_info(self):
    info = super()._get_info()
    info.update({
        'episode_reward': self.episode_reward,
        'success_rate': self.success_count / self.episode_count,
        'average_steps': self.total_steps / self.episode_count
    })
    return info
```

## Troubleshooting

### Common Issues

1. **Action Space Mismatch**: Ensure your action space matches what your agent produces
2. **Observation Shape**: Check that observations match the declared space
3. **Reward Scale**: Scale rewards appropriately (typically [-10, 10])
4. **Episode Length**: Set reasonable episode lengths for your task

### Debugging Tips

```python
# Enable verbose logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Add assertions
def step(self, action):
    assert action in self.action_space, f"Invalid action: {action}"
    # ... rest of step logic
```

## Resources

- [OpenAI Gym Documentation](https://gym.openai.com/)
- [Stable Baselines3](https://stable-baselines3.readthedocs.io/)
- [RL Algorithms Overview](https://spinningup.openai.com/)

## Support

For questions or issues, please contact the Verita AI RL team or open an issue on GitHub.
