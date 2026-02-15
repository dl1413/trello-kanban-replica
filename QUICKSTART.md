# RL Environment Framework - Quick Start Guide

## Installation

### Using pip (recommended)

```bash
pip install -e .
```

This installs the package in editable mode, allowing you to modify the code and see changes immediately.

### Optional Dependencies

```bash
# For deep RL with PyTorch (optional)
pip install -e ".[torch]"

# For development tools
pip install -e ".[dev]"
```

### Manual Installation

```bash
pip install -r requirements.txt
```

## Quick Start

### 1. Create Your First Environment

```bash
python tools/create_env.py --name my_custom_env
```

This creates:
- `environments/my_custom_env.py` - Your environment implementation
- `tests/test_my_custom_env.py` - Test file

### 2. Implement Your Environment

Edit `environments/my_custom_env.py` and implement:
- Action and observation spaces
- State initialization
- State update logic
- Reward function
- Termination conditions

### 3. Test Your Environment

```bash
pytest tests/test_my_custom_env.py
```

### 4. Run Your Environment

```bash
python environments/my_custom_env.py
```

## Examples

### Running the Simple GridWorld Example

```bash
python examples/simple_gridworld.py
```

### Training a Q-Learning Agent

```bash
python examples/q_learning_agent.py
```

### Training an Agent (Random Baseline)

```bash
python examples/train_example.py
```

## Project Structure

```
.
├── environments/          # Your RL environments
│   ├── __init__.py
│   └── base_env.py       # Base class for all environments
├── configs/              # Configuration files
│   ├── default_config.yaml
│   └── custom_env_config.yaml
├── tests/                # Test suites
│   ├── conftest.py
│   └── test_base_env.py
├── examples/             # Example implementations
│   ├── simple_gridworld.py
│   ├── train_example.py
│   └── q_learning_agent.py
├── tools/                # Utility tools
│   └── create_env.py
└── docs/                 # Documentation
    ├── environment_development.md
    ├── testing_guidelines.md
    ├── api_reference.md
    └── deployment.md
```

## Common Tasks

### Create a New Environment

```bash
python tools/create_env.py --name robot_navigation
```

### Run All Tests

```bash
pytest tests/
```

### Run Tests with Coverage

```bash
pytest --cov=environments tests/
```

### Format Code

```bash
black environments/ tests/ examples/
```

### Lint Code

```bash
flake8 environments/ tests/ examples/
```

## Next Steps

1. Read the [Environment Development Guide](docs/environment_development.md)
2. Check out the [API Reference](docs/api_reference.md)
3. Review the [Testing Guidelines](docs/testing_guidelines.md)
4. See [Deployment Guide](docs/deployment.md) for production deployment

## Getting Help

- Read the documentation in the `docs/` directory
- Check the examples in `examples/`
- Open an issue on GitHub
- Contact the Verita AI RL team

## Troubleshooting

### Security Notes

#### Weights & Biases (wandb)

**Note**: WandB versions <= 0.17.0 have a known SSRF vulnerability. This dependency has been removed from the default requirements.

If you need WandB for experiment tracking:
```bash
# Install a newer version manually
pip install "wandb>=0.18.0"
```

Alternatively, use TensorBoard (included by default):
```python
# TensorBoard is included in requirements.txt
tensorboard --logdir=./runs
```

### Common Issues

#### Import Errors

**Problem:** `ModuleNotFoundError: No module named 'gymnasium'`
```bash
# Solution: Install dependencies
pip install -r requirements.txt
```

**Problem:** `ImportError: cannot import name 'spaces'`
```bash
# Solution: Make sure you're using Gymnasium (not Gym)
pip uninstall gym  # Remove old gym if installed
pip install gymnasium==0.29.1
```

#### Gymnasium Version Conflicts

**Problem:** `AttributeError: 'Env' object has no attribute 'np_random'`
```bash
# Solution: Upgrade to Gymnasium >= 0.29.0
pip install --upgrade gymnasium==0.29.1
```

**Problem:** Deprecated warnings about old Gym API
```bash
# Solution: This framework uses modern Gymnasium API
# Update your code to use 5-tuple returns: (obs, reward, terminated, truncated, info)
```

#### Installation Issues

**Problem:** `pip install` fails on opencv-python
```bash
# Solution: Install without opencv or use headless version
pip install opencv-python-headless==4.8.1.78
# Or skip visualization features
pip install gymnasium numpy pyyaml matplotlib pandas pytest
```

**Problem:** Tests fail with `ModuleNotFoundError: No module named 'pandas'`
```bash
# Solution: Install all test dependencies
pip install -r requirements.txt
```

#### Runtime Issues

**Problem:** "Episode is done. Call reset() to start a new episode"
```bash
# Solution: Always reset before starting new episode
obs, info = env.reset()
# Now you can call step()
```

**Problem:** "Invalid action X for space Discrete(4)"
```bash
# Solution: Ensure actions are within valid range
action = env.action_space.sample()  # Always valid
# Or check: 0 <= action < env.action_space.n
```

**Problem:** Memory issues with large Q-tables
```bash
# Solution: Use smaller grid sizes or reduce training episodes
# For 20x20 grid, Q-table can grow to 400+ states
config = {'grid_size': 10}  # Use smaller grid
```

#### Performance Issues

**Problem:** Training is very slow
```bash
# Solution 1: Reduce episode length
config = {'episode_length': 50}  # Instead of 200

# Solution 2: Use fewer training episodes
python examples/q_learning_agent.py --episodes 500

# Solution 3: Disable rendering during training
# Don't call env.render() in training loop
```

**Problem:** Tests take too long
```bash
# Solution: Run tests in parallel
pytest tests/ -n auto  # Requires pytest-xdist

# Or skip slow tests
pytest tests/ -m "not slow"
```

### Getting More Help

If you encounter issues not covered here:

1. Check the [GitHub Issues](https://github.com/dl1413/trello-kanban-replica/issues)
2. Review the [Testing Guidelines](docs/testing_guidelines.md)
3. Consult the [API Reference](docs/api_reference.md)
4. Open a new issue with:
   - Python version (`python --version`)
   - Installed packages (`pip freeze`)
   - Full error traceback
   - Minimal code to reproduce

## Contributing

See [CONTRIBUTING.md](docs/CONTRIBUTING.md) for guidelines on contributing to this project.
