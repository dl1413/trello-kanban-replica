# API Reference

## Environments Module

### BaseEnvironment

The base class for all RL environments at Verita AI.

#### Class Definition

```python
class BaseEnvironment(gym.Env):
    """
    Base class for all RL environments.
    
    Attributes:
        action_space: gym.Space defining the action space
        observation_space: gym.Space defining the observation space
        config: dict containing environment configuration
        episode_length: int maximum steps per episode
        current_step: int current step in the episode
        done: bool whether the episode is finished
        state: current internal state
    """
```

#### Methods

##### `__init__(config: Optional[Dict[str, Any]] = None)`

Initialize the environment.

**Parameters:**
- `config` (dict, optional): Configuration dictionary for the environment

**Example:**
```python
config = {'episode_length': 500}
env = BaseEnvironment(config)
```

##### `reset() -> np.ndarray`

Reset the environment to initial state.

**Returns:**
- `observation` (np.ndarray): Initial observation

**Example:**
```python
obs = env.reset()
```

##### `step(action: int) -> Tuple[np.ndarray, float, bool, Dict]`

Execute one step in the environment.

**Parameters:**
- `action` (int): Action to take

**Returns:**
- `observation` (np.ndarray): Current observation
- `reward` (float): Reward for the action
- `done` (bool): Whether episode is complete
- `info` (dict): Additional information

**Raises:**
- `RuntimeError`: If called after episode is done

**Example:**
```python
obs, reward, done, info = env.step(action)
```

##### `render(mode: str = 'human')`

Render the environment.

**Parameters:**
- `mode` (str): Rendering mode ('human' or 'rgb_array')

**Returns:**
- `np.ndarray` (if mode='rgb_array'): RGB array representation

**Example:**
```python
env.render(mode='human')
rgb_array = env.render(mode='rgb_array')
```

##### `close()`

Clean up resources.

**Example:**
```python
env.close()
```

#### Protected Methods (for subclassing)

##### `_get_initial_state() -> Any`

Get initial state. Override in subclass.

##### `_get_observation() -> np.ndarray`

Get current observation. Override in subclass.

##### `_update_state(action: int)`

Update state based on action. Override in subclass.

##### `_calculate_reward(action: int) -> float`

Calculate reward for action. Override in subclass.

##### `_is_done() -> bool`

Check if episode is done. Override in subclass.

##### `_get_info() -> Dict[str, Any]`

Get additional info. Override in subclass.

##### `_get_rgb_array() -> np.ndarray`

Get RGB array for rendering. Override in subclass.

## Configuration

### Configuration File Structure

```yaml
environment:
  episode_length: int         # Maximum steps per episode
  max_steps: int              # Maximum total steps
  
  observation:
    type: str                 # "image", "vector", or "dict"
    shape: list               # Shape of observations
    normalize: bool           # Whether to normalize observations
    
  action:
    type: str                 # "discrete", "continuous", or "multi_discrete"
    n_actions: int            # Number of discrete actions
    shape: list               # Shape for continuous actions
    low: list                 # Minimum values for continuous actions
    high: list                # Maximum values for continuous actions
    
  reward:
    scale: float              # Reward scaling factor
    clip: bool                # Whether to clip rewards
    clip_range: list          # [min, max] for clipping
    
  render:
    mode: str                 # "rgb_array" or "human"
    fps: int                  # Frames per second
    width: int                # Render width
    height: int               # Render height

training:
  seed: int                   # Random seed
  num_episodes: int           # Number of training episodes
  parallel_envs: int          # Number of parallel environments
  
logging:
  tensorboard: bool           # Enable TensorBoard logging
  wandb: bool                 # Enable Weights & Biases logging
  log_interval: int           # Steps between logs
  save_interval: int          # Episodes between saves
```

### Loading Configuration

```python
import yaml

with open('configs/default_config.yaml', 'r') as f:
    config = yaml.safe_load(f)

env = BaseEnvironment(config['environment'])
```

## Examples

### Simple Grid World

A basic navigation task in a 2D grid.

```python
from examples.simple_gridworld import SimpleGridWorld

config = {
    'grid_size': 10,
    'episode_length': 100
}

env = SimpleGridWorld(config)
obs = env.reset()

done = False
while not done:
    action = env.action_space.sample()
    obs, reward, done, info = env.step(action)
    env.render()

env.close()
```

## Utilities

### Training Script

Use the provided training script to train agents:

```bash
python examples/train_example.py
```

### Creating New Environments

Use the environment creation tool:

```bash
python tools/create_env.py --name my_custom_env
```

This generates a template for a new environment with all necessary methods.

## Testing

### Running Tests

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest --cov=environments tests/

# Run specific test file
pytest tests/test_base_env.py
```

### Writing Tests

```python
import pytest
from environments import BaseEnvironment

def test_my_feature():
    env = BaseEnvironment()
    env.reset()
    
    obs, reward, done, info = env.step(0)
    
    assert env.observation_space.contains(obs)
    assert isinstance(reward, float)
```

## Integration with RL Libraries

### Stable-Baselines3

```python
from stable_baselines3 import PPO
from environments import BaseEnvironment

env = BaseEnvironment()
model = PPO("MlpPolicy", env, verbose=1)
model.learn(total_timesteps=10000)
```

### RLlib

```python
from ray.rllib.algorithms.ppo import PPO

config = {
    "env": BaseEnvironment,
    "num_workers": 4,
}

algo = PPO(config=config)
algo.train()
```

## Common Patterns

### Vectorized Environments

```python
from gym.vector import AsyncVectorEnv

def make_env():
    return BaseEnvironment()

envs = AsyncVectorEnv([make_env for _ in range(8)])
observations = envs.reset()
```

### Custom Observation Spaces

```python
from gym import spaces

class CustomEnv(BaseEnvironment):
    def __init__(self, config=None):
        super().__init__(config)
        
        self.observation_space = spaces.Dict({
            'image': spaces.Box(low=0, high=255, shape=(84, 84, 3), dtype=np.uint8),
            'vector': spaces.Box(low=-np.inf, high=np.inf, shape=(10,), dtype=np.float32)
        })
```

### Custom Action Spaces

```python
from gym import spaces

class ContinuousEnv(BaseEnvironment):
    def __init__(self, config=None):
        super().__init__(config)
        
        self.action_space = spaces.Box(
            low=-1.0, high=1.0, shape=(4,), dtype=np.float32
        )
```

## Troubleshooting

### Common Errors

#### `RuntimeError: Episode is done`

Call `reset()` before taking more steps:

```python
env.reset()  # Reset before stepping
obs, reward, done, info = env.step(action)
```

#### Action/Observation Space Mismatch

Ensure actions and observations are within defined spaces:

```python
assert env.action_space.contains(action)
assert env.observation_space.contains(observation)
```

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

env = BaseEnvironment({'debug': True})
```

## Performance Tips

1. **Vectorize Observations**: Use NumPy operations instead of loops
2. **Minimize Rendering**: Only render when necessary
3. **Use Parallel Environments**: Leverage `AsyncVectorEnv` for faster training
4. **Profile Code**: Use `cProfile` to identify bottlenecks
5. **Cache Computations**: Store frequently used values

## References

- [OpenAI Gym Documentation](https://gym.openai.com/)
- [Stable-Baselines3 Documentation](https://stable-baselines3.readthedocs.io/)
- [RLlib Documentation](https://docs.ray.io/en/latest/rllib/)
