# Testing Guidelines for RL Environments

## Overview

Comprehensive testing is crucial for reliable RL environments. This guide covers testing strategies and best practices.

## Test Structure

```
tests/
├── __init__.py
├── test_base_env.py           # Tests for base environment
├── test_custom_envs.py        # Tests for custom environments
├── test_integration.py        # Integration tests
└── conftest.py                # Pytest fixtures
```

## Unit Testing

### Testing Environment Initialization

```python
import pytest
from environments import BaseEnvironment

def test_base_environment_initialization():
    """Test that base environment initializes correctly"""
    env = BaseEnvironment()
    
    assert env is not None
    assert env.action_space is not None
    assert env.observation_space is not None
    assert env.current_step == 0
    assert env.done is False

def test_environment_with_config():
    """Test environment initialization with custom config"""
    config = {'episode_length': 500}
    env = BaseEnvironment(config)
    
    assert env.episode_length == 500
```

### Testing Reset Functionality

```python
def test_reset_returns_valid_observation():
    """Test that reset returns a valid observation"""
    env = BaseEnvironment()
    obs = env.reset()
    
    assert env.observation_space.contains(obs)
    assert env.current_step == 0
    assert env.done is False

def test_reset_reproducibility():
    """Test that reset with same seed produces same results"""
    env1 = BaseEnvironment({'seed': 42})
    env2 = BaseEnvironment({'seed': 42})
    
    obs1 = env1.reset()
    obs2 = env2.reset()
    
    assert np.allclose(obs1, obs2)
```

### Testing Step Functionality

```python
def test_step_returns_correct_tuple():
    """Test that step returns (obs, reward, done, info)"""
    env = BaseEnvironment()
    env.reset()
    
    result = env.step(0)
    
    assert len(result) == 4
    obs, reward, done, info = result
    assert env.observation_space.contains(obs)
    assert isinstance(reward, (int, float))
    assert isinstance(done, bool)
    assert isinstance(info, dict)

def test_step_with_invalid_action():
    """Test that invalid actions are handled"""
    env = BaseEnvironment()
    env.reset()
    
    # Test with action outside action space
    with pytest.raises(Exception):
        env.step(999)

def test_step_after_done():
    """Test that stepping after done raises error"""
    env = BaseEnvironment({'episode_length': 1})
    env.reset()
    env.step(0)  # This should set done=True
    
    with pytest.raises(RuntimeError):
        env.step(0)
```

### Testing Episode Termination

```python
def test_episode_length_termination():
    """Test that episodes terminate at max length"""
    episode_length = 10
    env = BaseEnvironment({'episode_length': episode_length})
    env.reset()
    
    for i in range(episode_length - 1):
        _, _, done, _ = env.step(0)
        assert not done
    
    # Final step should trigger termination
    _, _, done, _ = env.step(0)
    assert done
```

### Testing Reward Function

```python
def test_reward_bounds():
    """Test that rewards are within expected bounds"""
    env = BaseEnvironment()
    env.reset()
    
    for _ in range(100):
        _, reward, done, _ = env.step(env.action_space.sample())
        assert -1000 <= reward <= 1000  # Adjust bounds as needed
        if done:
            break

def test_reward_consistency():
    """Test that same state-action pairs give same rewards"""
    env = BaseEnvironment({'seed': 42})
    
    # Run same sequence twice
    rewards1 = []
    env.reset()
    for _ in range(10):
        _, r, _, _ = env.step(0)
        rewards1.append(r)
    
    rewards2 = []
    env.reset()
    for _ in range(10):
        _, r, _, _ = env.step(0)
        rewards2.append(r)
    
    assert rewards1 == rewards2
```

## Integration Testing

### Testing with RL Agents

```python
def test_environment_with_random_agent():
    """Test environment with random agent"""
    env = BaseEnvironment()
    
    num_episodes = 10
    for episode in range(num_episodes):
        obs = env.reset()
        done = False
        total_reward = 0
        steps = 0
        
        while not done and steps < 1000:
            action = env.action_space.sample()
            obs, reward, done, info = env.step(action)
            total_reward += reward
            steps += 1
        
        assert steps > 0
        assert isinstance(total_reward, (int, float))

def test_parallel_environments():
    """Test running multiple environments in parallel"""
    from gym.vector import AsyncVectorEnv
    
    def make_env():
        return BaseEnvironment()
    
    num_envs = 4
    envs = AsyncVectorEnv([make_env for _ in range(num_envs)])
    
    obs = envs.reset()
    assert obs.shape[0] == num_envs
    
    actions = [env.action_space.sample() for env in envs.envs]
    obs, rewards, dones, infos = envs.step(actions)
    
    assert len(rewards) == num_envs
    assert len(dones) == num_envs
```

### Testing Configuration Loading

```python
import yaml

def test_load_config_from_file():
    """Test loading configuration from YAML file"""
    config_path = 'configs/default_config.yaml'
    
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    env = BaseEnvironment(config['environment'])
    assert env.episode_length == config['environment']['episode_length']
```

## Performance Testing

### Testing Execution Speed

```python
import time

def test_environment_speed():
    """Test that environment runs at acceptable speed"""
    env = BaseEnvironment()
    num_steps = 1000
    
    start_time = time.time()
    env.reset()
    
    for _ in range(num_steps):
        env.step(env.action_space.sample())
    
    elapsed_time = time.time() - start_time
    steps_per_second = num_steps / elapsed_time
    
    # Should achieve at least 100 steps/second
    assert steps_per_second > 100, f"Too slow: {steps_per_second} steps/sec"
```

### Memory Leak Testing

```python
import gc
import sys

def test_memory_leaks():
    """Test that environment doesn't leak memory"""
    env = BaseEnvironment()
    
    # Get initial memory usage
    gc.collect()
    initial_objects = len(gc.get_objects())
    
    # Run many episodes
    for _ in range(100):
        env.reset()
        for _ in range(100):
            env.step(env.action_space.sample())
    
    # Check memory usage hasn't grown significantly
    gc.collect()
    final_objects = len(gc.get_objects())
    
    # Allow some growth but not excessive
    assert final_objects < initial_objects * 1.5
```

## Pytest Fixtures

Create `conftest.py` for shared fixtures:

```python
import pytest
from environments import BaseEnvironment

@pytest.fixture
def base_env():
    """Fixture providing a basic environment instance"""
    env = BaseEnvironment()
    yield env
    env.close()

@pytest.fixture
def configured_env():
    """Fixture providing a configured environment"""
    config = {
        'episode_length': 100,
        'seed': 42
    }
    env = BaseEnvironment(config)
    yield env
    env.close()

@pytest.fixture
def reset_env(base_env):
    """Fixture providing a reset environment"""
    base_env.reset()
    return base_env
```

## Running Tests

### Basic Test Execution

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_base_env.py

# Run specific test
pytest tests/test_base_env.py::test_reset_returns_valid_observation

# Run with verbose output
pytest -v tests/
```

### Coverage Reports

```bash
# Run with coverage
pytest --cov=environments tests/

# Generate HTML coverage report
pytest --cov=environments --cov-report=html tests/

# View coverage report
open htmlcov/index.html
```

### Parallel Testing

```bash
# Install pytest-xdist
pip install pytest-xdist

# Run tests in parallel
pytest -n auto tests/
```

## Continuous Integration

### GitHub Actions Example

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.8
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-cov
    
    - name: Run tests
      run: |
        pytest --cov=environments tests/
```

## Best Practices

1. **Test Coverage**: Aim for >80% code coverage
2. **Fast Tests**: Keep unit tests under 1 second each
3. **Isolated Tests**: Each test should be independent
4. **Clear Names**: Use descriptive test function names
5. **Fixtures**: Use fixtures to reduce code duplication
6. **Assertions**: Include meaningful assertion messages
7. **Edge Cases**: Test boundary conditions
8. **Error Handling**: Test error cases explicitly

## Debugging Failed Tests

```bash
# Run with verbose output and stop on first failure
pytest -vsx tests/

# Run with pdb debugger on failure
pytest --pdb tests/

# Show local variables on failure
pytest -l tests/
```

## Common Testing Patterns

### Parameterized Tests

```python
@pytest.mark.parametrize("action", [0, 1, 2, 3])
def test_all_actions(action):
    env = BaseEnvironment()
    env.reset()
    obs, reward, done, info = env.step(action)
    assert env.observation_space.contains(obs)
```

### Expected Failures

```python
@pytest.mark.xfail(reason="Known issue with action 999")
def test_large_action():
    env = BaseEnvironment()
    env.reset()
    env.step(999)
```

### Skipping Tests

```python
@pytest.mark.skip(reason="Waiting for feature implementation")
def test_future_feature():
    pass
```

## Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Testing Best Practices](https://docs.python-guide.org/writing/tests/)
- [Gym Testing Examples](https://github.com/openai/gym/tree/master/tests)
