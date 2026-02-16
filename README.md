# Trello Kanban Replica - RL Environment Framework

A comprehensive framework for developing and managing reinforcement learning environments at Verita AI, built on **Gymnasium** (the modern successor to OpenAI Gym).

## Overview

This repository provides a structured approach to building, testing, and deploying reinforcement learning environments. It includes templates, guidelines, and tools optimized for RL environment engineers.

## Project Structure

```
.
├── environments/          # RL environment implementations
├── configs/              # Configuration files for environments
├── tests/                # Test suites for environments
├── docs/                 # Comprehensive documentation
├── examples/             # Example implementations
└── tools/                # Utility tools and scripts
```

## Quick Start

1. **Setup Development Environment**
   ```bash
   pip install -r requirements.txt
   # Optional: install torch for deep RL
   pip install torch>=2.0.0
   ```

2. **Create a New Environment**
   ```bash
   python tools/create_env.py --name my_env
   ```

3. **Run Tests**
   ```bash
   pytest tests/
   ```

4. **Try Examples**
   ```bash
   # Simple grid world demo
   python examples/simple_gridworld.py
   
   # Train a Q-Learning agent
   python examples/q_learning_agent.py
   ```

## Key Features

- **Modern Gymnasium API**: Full compatibility with Gymnasium's 5-tuple step API (terminated/truncated)
- **Modular Environment Design**: Easily extensible base classes
- **Proper Seeding**: Reproducible experiments with per-environment RNG
- **Action Validation**: Built-in action space validation
- **Configuration Management**: YAML-based configuration system with nested structure support
- **Reward Shaping**: Configurable reward scaling, clipping, and dense/sparse options
- **Multi-Agent Support**: Built-in multi-agent environment with cooperative/competitive modes
- **Continuous Control**: Ready-to-use continuous action space environments
- **Deep RL Integration**: PyTorch-based DQN agent with experience replay
- **Curriculum Learning**: Automatic difficulty adjustment based on agent performance
- **Vectorized Environments**: Parallel environment execution (sync/async)
- **Performance Benchmarking**: Comprehensive suite for measuring throughput and latency
- **Comprehensive Testing**: 183+ tests with Gymnasium API compliance validation
- **Documentation**: Auto-generated API documentation
- **Example Implementations**: Including Q-Learning and DQN agents with training visualization
- **CI/CD Ready**: GitHub Actions workflow for automated testing and deployment

## Advanced Features

The framework includes seven powerful advanced features for modern RL development:

### 1. Multi-Agent Environments

Build cooperative or competitive multi-agent scenarios:

```python
from environments.multi_agent_env import MultiAgentBaseEnvironment, MultiAgentGridWorld

# Create a 2-agent cooperative gridworld
config = {
    "num_agents": 2,
    "reward_mode": "cooperative",  # or "competitive"
    "collision_mode": "block",     # or "pass-through", "penalty"
    "grid_size": 10
}
env = MultiAgentGridWorld(config)

# Get observations for all agents
observations, info = env.reset()
actions = {0: 1, 1: 2}  # Actions for agent 0 and 1
obs, rewards, terminated, truncated, info = env.step(actions)
```

### 2. Continuous Action Spaces

Test deep RL algorithms with continuous control:

```python
from environments.continuous_env import ContinuousControlEnv

# 2D point-mass control with physics
config = {
    "dt": 0.1,
    "friction": 0.1,
    "max_velocity": 5.0,
    "goal_threshold": 0.1
}
env = ContinuousControlEnv(config)

# Apply continuous forces
observation, info = env.reset()
action = np.array([0.5, 0.3])  # [fx, fy] in range [-1, 1]
obs, reward, terminated, truncated, info = env.step(action)
```

### 3. DQN Agent with PyTorch

Production-ready deep Q-learning implementation:

```python
from examples.dqn_agent import DQNAgent, train_dqn

# Create and train a DQN agent
agent = DQNAgent(
    state_dim=2,
    action_dim=4,
    hidden_layers=[64, 64],
    learning_rate=1e-3,
    gamma=0.99,
    buffer_size=10000
)

# Train with experience replay and target networks
training_rewards = train_dqn(
    env,
    agent,
    num_episodes=1000,
    target_update_frequency=10
)
```

### 4. Curriculum Learning

Automatically adjust difficulty based on performance:

```python
from environments.curriculum_wrapper import CurriculumWrapper

# Wrap any environment with curriculum learning
env = CurriculumWrapper(
    base_env,
    initial_difficulty=0.0,
    window_size=100,
    success_threshold=0.8,
    difficulty_step=0.1
)

# Environment automatically increases difficulty as agent improves
obs, info = env.reset()
# Training loop...
# Difficulty adjusts based on success rate
```

### 5. Vectorized Environments

Parallel environment execution for faster training:

```python
from environments.vec_env import SyncVectorEnv, AsyncVectorEnv

# Synchronous vectorization (sequential)
vec_env = SyncVectorEnv(lambda: SimpleGridWorld(), num_envs=4)

# Asynchronous vectorization (multiprocessing)
vec_env = AsyncVectorEnv(lambda: SimpleGridWorld(), num_envs=8)

# Interact with all environments in parallel
observations = vec_env.reset()
actions = np.array([1, 2, 0, 3])  # Actions for each env
obs, rewards, dones, infos = vec_env.step(actions)
```

### 6. Performance Benchmarking

Comprehensive performance measurement suite:

```bash
# Benchmark any environment
python tools/benchmark.py \
    --env SimpleGridWorld \
    --episodes 1000 \
    --output results/benchmark.json

# Measures: throughput, latency (p50/p95/p99), memory usage
```

### 7. GitHub Actions CI/CD

Automated testing and deployment pipeline:

- Runs full test suite on every push/PR
- Tests on Python 3.8, 3.9, 3.10, 3.11
- Validates Gymnasium API compliance
- Generates coverage reports
- Automatic deployment on release tags

## Documentation

- [Environment Development Guide](docs/environment_development.md)
- [API Reference](docs/api_reference.md)
- [Testing Guidelines](docs/testing_guidelines.md)
- [Deployment Guide](docs/deployment.md)
- [Curriculum Learning Guide](docs/curriculum_wrapper.md)

## Contributing

Please refer to [CONTRIBUTING.md](docs/CONTRIBUTING.md) for guidelines on contributing to this project.

## License

MIT License - see LICENSE file for details.