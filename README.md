# Trello Kanban Replica - RL Environment Framework

A comprehensive framework for developing and managing reinforcement learning environments at Verita AI, built on **Gymnasium** (the modern successor to OpenAI Gym).

## 🎯 Overview

This repository provides a structured approach to building, testing, and deploying reinforcement learning environments. It includes templates, guidelines, and tools optimized for RL environment engineers.

## 📊 Key Statistics

| Metric | Value |
|--------|-------|
| **Tests** | 40/40 passing (100%) |
| **Lines of Code** | 4,500+ |
| **Documentation** | 2,100+ lines |
| **Security** | 0 vulnerabilities |
| **API Compliance** | 100% Gymnasium |

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

## 🚀 Quick Start

### 1. Setup Development Environment
```bash
pip install -r requirements.txt
# Optional: install torch for deep RL
pip install torch>=2.0.0
```

### 2. Create a New Environment
```bash
python tools/create_env.py --name my_env
```

### 3. Run Tests
```bash
pytest tests/
```

### 4. Try Examples
```bash
# Simple grid world demo
python examples/simple_gridworld.py

# Train a Q-Learning agent
python examples/q_learning_agent.py
```

## ✨ Key Features

| Feature | Description |
|---------|-------------|
| **Modern Gymnasium API** | Full compatibility with Gymnasium's 5-tuple step API (terminated/truncated) |
| **Modular Design** | Easily extensible base classes for custom environments |
| **Proper Seeding** | Reproducible experiments with per-environment RNG |
| **Action Validation** | Built-in action space validation to catch errors early |
| **Configuration Management** | YAML-based system with nested structure support |
| **Reward Shaping** | Configurable scaling, clipping, and dense/sparse options |
| **Comprehensive Testing** | 40 tests with Gymnasium API compliance validation |
| **Documentation** | Complete API reference and development guides |
| **Example Implementations** | Including Q-Learning agent with training visualization |
| **Deployment Ready** | Docker support and CI/CD integration |

## 📚 Documentation

| Guide | Description |
|-------|-------------|
| [Environment Development Guide](docs/environment_development.md) | Step-by-step guide to creating environments |
| [API Reference](docs/api_reference.md) | Complete API documentation |
| [Testing Guidelines](docs/testing_guidelines.md) | Testing best practices |
| [Deployment Guide](docs/deployment.md) | Production deployment instructions |

## 🤝 Contributing

Please refer to [CONTRIBUTING.md](docs/CONTRIBUTING.md) for guidelines on contributing to this project.

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.