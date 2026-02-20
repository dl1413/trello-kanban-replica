# RL Environment Framework - Quick Start Guide

## 📦 Installation

### Using pip (recommended)

```bash
pip install -e .
```

This installs the package in editable mode, allowing you to modify the code and see changes immediately.

### Optional Dependencies

| Package | Command | Use Case |
|---------|---------|----------|
| **PyTorch** | `pip install -e ".[torch]"` | Deep RL with neural networks |
| **Development Tools** | `pip install -e ".[dev]"` | Testing, linting, formatting |

### Manual Installation

```bash
pip install -r requirements.txt
```

## 🚀 Quick Start

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

## 📂 Project Structure

```
.
├── environments/          # Your RL environments
│   ├── __init__.py
│   └── base_env.py       # Base class for all environments
├── configs/              # Configuration files
│   ├── default_config.yaml
│   └── custom_env_config.yaml
├── tests/                # Test suites (40 tests)
│   ├── conftest.py
│   ├── test_base_env.py
│   ├── test_env_checker.py
│   └── test_optimizations.py
├── examples/             # Example implementations
│   ├── simple_gridworld.py
│   ├── train_example.py
│   └── q_learning_agent.py
├── tools/                # Utility tools
│   └── create_env.py
└── docs/                 # Documentation (2,100+ lines)
    ├── environment_development.md
    ├── testing_guidelines.md
    ├── api_reference.md
    └── deployment.md
```

## 🛠️ Common Tasks

| Task | Command |
|------|---------|
| **Create New Environment** | `python tools/create_env.py --name robot_navigation` |
| **Run All Tests** | `pytest tests/` |
| **Run Tests with Coverage** | `pytest --cov=environments tests/` |
| **Format Code** | `black environments/ tests/ examples/` |
| **Lint Code** | `flake8 environments/ tests/ examples/` |

## 📖 Next Steps

| Step | Guide | Purpose |
|------|-------|---------|
| 1 | [Environment Development Guide](docs/environment_development.md) | Learn to create custom environments |
| 2 | [API Reference](docs/api_reference.md) | Explore the complete API |
| 3 | [Testing Guidelines](docs/testing_guidelines.md) | Best practices for testing |
| 4 | [Deployment Guide](docs/deployment.md) | Deploy to production |

## 💡 Getting Help

- 📚 Read the documentation in the `docs/` directory
- 💻 Check the examples in `examples/`
- 🐛 Open an issue on GitHub
- 📧 Contact the Verita AI RL team

## 🤝 Contributing

See [CONTRIBUTING.md](docs/CONTRIBUTING.md) for guidelines on contributing to this project.
