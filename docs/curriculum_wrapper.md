# Curriculum Learning Wrapper

The `CurriculumWrapper` provides automatic curriculum learning for any `BaseEnvironment` subclass. It tracks agent performance and automatically adjusts environment difficulty to maintain an optimal learning curve.

## Overview

Curriculum learning is a training strategy where the agent starts with easier tasks and progressively moves to harder ones. This approach can significantly improve learning efficiency and final performance.

The `CurriculumWrapper` implements this by:
- Tracking success rate over a rolling window of episodes
- Automatically increasing difficulty when the agent performs well
- Optionally decreasing difficulty when the agent struggles
- Providing difficulty-specific configuration to the wrapped environment

## Installation

The wrapper is included in the `environments` package:

```python
from environments import CurriculumWrapper
```

## Quick Start

```python
from environments import CurriculumWrapper
from examples.simple_gridworld import SimpleGridWorld

# Create your environment
env = SimpleGridWorld({'episode_length': 100})

# Wrap it with curriculum learning
curriculum_env = CurriculumWrapper(
    env,
    initial_difficulty=0.0,      # Start easy
    window_size=100,             # Track last 100 episodes
    success_threshold=0.7,       # Increase difficulty at 70% success
    failure_threshold=0.3,       # Decrease difficulty below 30% success
    difficulty_step=0.1,         # Change difficulty by 0.1 each time
    min_episodes_before_change=10,  # Wait 10 episodes before first change
    enable_decrease=True         # Allow difficulty to decrease
)

# Use it like any other environment
obs, info = curriculum_env.reset()
for _ in range(1000):
    action = agent.select_action(obs)
    obs, reward, terminated, truncated, info = curriculum_env.step(action)
    
    # Check current difficulty
    print(f"Difficulty: {info['curriculum_difficulty']:.2f}")
    print(f"Success Rate: {info['curriculum_success_rate']:.2f}")
    
    if terminated or truncated:
        obs, info = curriculum_env.reset()
```

## Parameters

### Constructor Parameters

- **env** (BaseEnvironment): The environment to wrap. Must be a `BaseEnvironment` subclass.

- **initial_difficulty** (float, default=0.0): Starting difficulty level from 0.0 (easiest) to 1.0 (hardest).

- **window_size** (int, default=100): Number of recent episodes to track for success rate calculation.

- **success_threshold** (float, default=0.7): Success rate above which difficulty increases (0.0 to 1.0).

- **failure_threshold** (float, default=0.3): Success rate below which difficulty decreases (0.0 to 1.0). Must be less than `success_threshold`.

- **difficulty_step** (float, default=0.1): Amount to change difficulty on each adjustment.

- **min_episodes_before_change** (int, default=10): Minimum number of episodes before difficulty can change.

- **enable_decrease** (bool, default=True): Whether to allow difficulty to decrease when performance is poor.

## Methods

### get_difficulty()

Returns the current difficulty level.

```python
difficulty = curriculum_env.get_difficulty()
print(f"Current difficulty: {difficulty:.2f}")
```

### set_difficulty(difficulty)

Manually set the difficulty level. Useful for testing or curriculum scheduling.

```python
curriculum_env.set_difficulty(0.5)  # Set to medium difficulty
```

### reset(seed=None, options=None)

Resets the environment with the current difficulty settings. Returns observation and info dict with curriculum metrics.

```python
obs, info = curriculum_env.reset()
# info includes:
# - 'curriculum_difficulty': Current difficulty
# - 'curriculum_success_rate': Rolling success rate
# - 'curriculum_episode_count': Total episodes completed
```

### step(action)

Executes one step in the environment. Returns observation, reward, terminated, truncated, and info dict with curriculum metrics.

```python
obs, reward, terminated, truncated, info = curriculum_env.step(action)
# info includes curriculum_difficulty and curriculum_success_rate
```

## Difficulty Mapping

The wrapper applies difficulty settings to the wrapped environment through its config dictionary.

### GridWorld Environments

For environments with "GridWorld" or "Grid" in their class name, difficulty controls:

| Difficulty | Grid Size | Obstacle Density |
|------------|-----------|------------------|
| 0.0        | 3x3       | 0%               |
| 0.5        | 7x7       | 10%              |
| 1.0        | 15x15     | 20%              |

Grid size interpolates linearly between these values.

### Generic Environments

For other environments, the difficulty value is passed in the config dictionary:

```python
env.config['difficulty'] = difficulty_value
```

Custom environments can use this value to adjust their own difficulty parameters.

## Advanced Usage

### Custom Difficulty Mapping

To implement custom difficulty mapping, subclass `CurriculumWrapper` and override `_apply_difficulty_config()`:

```python
class CustomCurriculumWrapper(CurriculumWrapper):
    def _apply_difficulty_config(self):
        """Apply custom difficulty settings."""
        # Your custom difficulty logic here
        self.env.config['custom_param'] = self._difficulty * 10
        self.env.config['another_param'] = 1.0 - self._difficulty
        super()._apply_difficulty_config()  # Call parent for generic handling
```

### Monitoring Difficulty Progression

The wrapper logs difficulty changes at INFO level:

```python
import logging
logging.basicConfig(level=logging.INFO)

# You'll see logs like:
# INFO:curriculum_wrapper:Difficulty increased: 0.30 -> 0.40 (success_rate=0.75)
```

### Progressive Curriculum

For a more controlled curriculum, disable automatic changes and manually adjust difficulty:

```python
curriculum_env = CurriculumWrapper(
    env,
    initial_difficulty=0.0,
    enable_decrease=False,  # Only increase
    min_episodes_before_change=1000  # Very high to prevent auto-changes
)

# Manually increase every N episodes
for episode in range(10000):
    if episode % 1000 == 0 and episode > 0:
        new_difficulty = min(1.0, curriculum_env.get_difficulty() + 0.2)
        curriculum_env.set_difficulty(new_difficulty)
```

## Success Criteria

The wrapper determines episode success by checking (in order):

1. **goal_reached** flag in the info dict (if present)
2. Positive reward on terminal state
3. Otherwise, episode is considered a failure

For custom success criteria, ensure your environment sets `info['goal_reached'] = True/False`.

## Examples

### Example 1: Basic Usage

```python
from environments import CurriculumWrapper
from examples.simple_gridworld import SimpleGridWorld

env = SimpleGridWorld()
curriculum_env = CurriculumWrapper(env, initial_difficulty=0.0)

for episode in range(100):
    obs, info = curriculum_env.reset()
    while True:
        action = env.action_space.sample()  # Replace with your agent
        obs, reward, terminated, truncated, info = curriculum_env.step(action)
        if terminated or truncated:
            break
    print(f"Episode {episode}: Difficulty={info['curriculum_difficulty']:.2f}")
```

### Example 2: Fixed Curriculum Stages

```python
# Define curriculum stages
stages = [
    (0.0, 1000),   # 1000 episodes at difficulty 0.0
    (0.3, 2000),   # 2000 episodes at difficulty 0.3
    (0.6, 2000),   # 2000 episodes at difficulty 0.6
    (1.0, 5000),   # 5000 episodes at difficulty 1.0
]

curriculum_env = CurriculumWrapper(env, min_episodes_before_change=999999)

episode = 0
for difficulty, num_episodes in stages:
    curriculum_env.set_difficulty(difficulty)
    for _ in range(num_episodes):
        episode += 1
        # Training loop...
```

### Example 3: Adaptive with Custom Thresholds

```python
# Aggressive curriculum: increase difficulty quickly
curriculum_env = CurriculumWrapper(
    env,
    success_threshold=0.6,    # Increase at 60% success
    failure_threshold=0.4,    # Decrease below 40% success
    difficulty_step=0.15,     # Larger steps
    window_size=50,           # Shorter window = more responsive
    min_episodes_before_change=5
)
```

## Best Practices

1. **Start Easy**: Begin with `initial_difficulty=0.0` to give the agent a chance to learn basics.

2. **Tune Thresholds**: Adjust `success_threshold` based on your task:
   - Deterministic tasks: 0.8-0.9
   - Stochastic tasks: 0.6-0.7

3. **Window Size**: Larger windows (100+) provide more stable difficulty changes; smaller windows (20-50) adapt faster.

4. **Monitor Metrics**: Log or plot `curriculum_difficulty` and `curriculum_success_rate` to visualize learning progress.

5. **Disable Decrease for Exploration**: Set `enable_decrease=False` if you want the agent to always face the hardest difficulty it has achieved.

6. **Custom Success**: For complex tasks, implement `goal_reached` in your environment's info dict for accurate success tracking.

## Testing

Run the comprehensive test suite:

```bash
pytest tests/test_curriculum.py -v
```

Run the demo script:

```bash
python examples/curriculum_demo.py
```

## References

- Bengio, Y., et al. (2009). "Curriculum learning." ICML.
- Narvekar, S., et al. (2020). "Curriculum learning for reinforcement learning domains: A framework and survey." JMLR.
