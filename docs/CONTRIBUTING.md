# Contributing to RL Environment Framework

Thank you for your interest in contributing to Verita AI's RL Environment Framework!

## Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [Getting Started](#getting-started)
3. [Development Process](#development-process)
4. [Coding Standards](#coding-standards)
5. [Testing Guidelines](#testing-guidelines)
6. [Documentation](#documentation)
7. [Pull Request Process](#pull-request-process)

## Code of Conduct

We are committed to providing a welcoming and inclusive environment. Please be respectful and professional in all interactions.

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- Familiarity with reinforcement learning concepts
- Experience with OpenAI Gym

### Setting Up Development Environment

```bash
# Fork and clone the repository
git clone https://github.com/dl1413/trello-kanban-replica.git
cd trello-kanban-replica

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install pytest pytest-cov black flake8

# Run tests to verify setup
pytest tests/
```

## Development Process

### Creating a New Feature

1. Create a new branch from `main`:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes following our coding standards

3. Write tests for your changes

4. Run tests and linters:
   ```bash
   pytest tests/
   black .
   flake8 .
   ```

5. Commit your changes:
   ```bash
   git add .
   git commit -m "Add feature: brief description"
   ```

6. Push to your fork and create a pull request

### Branch Naming Convention

- `feature/` - New features
- `bugfix/` - Bug fixes
- `docs/` - Documentation updates
- `refactor/` - Code refactoring
- `test/` - Test improvements

## Coding Standards

### Python Style Guide

We follow PEP 8 with some modifications:

- Maximum line length: 100 characters
- Use type hints where possible
- Use descriptive variable names
- Add docstrings to all public methods

### Code Formatting

We use `black` for code formatting:

```bash
black environments/ tests/ examples/ tools/
```

### Linting

We use `flake8` for linting:

```bash
flake8 environments/ tests/ examples/ tools/
```

### Type Hints

Use type hints for function signatures:

```python
def calculate_reward(self, state: np.ndarray, action: int) -> float:
    """Calculate reward for state-action pair."""
    return 0.0
```

### Docstrings

Use Google-style docstrings:

```python
def step(self, action: int) -> Tuple[np.ndarray, float, bool, Dict]:
    """
    Execute one step in the environment.
    
    Args:
        action: The action to take
        
    Returns:
        observation: The current observation
        reward: The reward for this step
        done: Whether the episode is finished
        info: Additional information
        
    Raises:
        RuntimeError: If called after episode is done
        
    Example:
        >>> env = MyEnv()
        >>> env.reset()
        >>> obs, reward, done, info = env.step(0)
    """
    pass
```

## Testing Guidelines

### Writing Tests

- Write tests for all new features
- Aim for >80% code coverage
- Use descriptive test names
- Test edge cases and error conditions

### Test Structure

```python
import pytest
from environments import BaseEnvironment


class TestFeature:
    """Test suite for specific feature."""
    
    def test_normal_case(self):
        """Test normal operation."""
        pass
    
    def test_edge_case(self):
        """Test edge case."""
        pass
    
    def test_error_handling(self):
        """Test error handling."""
        with pytest.raises(ValueError):
            # Code that should raise ValueError
            pass
```

### Running Tests

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest --cov=environments tests/

# Run specific test file
pytest tests/test_base_env.py

# Run specific test
pytest tests/test_base_env.py::test_reset
```

## Documentation

### Code Documentation

- Add docstrings to all public classes and methods
- Include type hints
- Provide usage examples
- Document parameters and return values

### README and Guides

- Update README.md for major changes
- Add examples for new features
- Update relevant documentation in `docs/`

### API Reference

Update `docs/api_reference.md` when adding new public APIs.

## Pull Request Process

### Before Submitting

1. ✓ All tests pass
2. ✓ Code is formatted with `black`
3. ✓ No linting errors from `flake8`
4. ✓ Documentation is updated
5. ✓ Commit messages are clear
6. ✓ Branch is up to date with `main`

### Pull Request Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Performance improvement
- [ ] Refactoring

## Testing
- [ ] All existing tests pass
- [ ] New tests added
- [ ] Tested manually

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No breaking changes (or documented)

## Related Issues
Closes #123
```

### Review Process

1. At least one reviewer must approve
2. All CI checks must pass
3. No merge conflicts
4. Documentation is complete

### After Merge

- Delete your feature branch
- Update your local repository:
  ```bash
  git checkout main
  git pull origin main
  ```

## Environment Guidelines

### Creating Custom Environments

1. Inherit from `BaseEnvironment`
2. Override required methods
3. Define clear observation and action spaces
4. Implement informative reward functions
5. Add proper documentation

### Example Structure

```python
class MyCustomEnv(BaseEnvironment):
    """
    Brief description of environment.
    
    Observation: Description
    Actions: Description  
    Reward: Description
    """
    
    def __init__(self, config=None):
        super().__init__(config)
        # Define spaces
        
    def _get_initial_state(self):
        # Initialize state
        
    def _update_state(self, action):
        # Update logic
        
    def _calculate_reward(self, action):
        # Reward logic
        
    def _is_done(self):
        # Termination logic
```

## Common Patterns

### Configuration Management

Always use configuration dictionaries:

```python
config = {
    'episode_length': 1000,
    'reward_scale': 1.0,
    'custom_param': 42
}
env = MyEnv(config)
```

### Observation Normalization

Normalize observations for stability:

```python
def _get_observation(self):
    obs = self.state
    return (obs - self.obs_mean) / (self.obs_std + 1e-8)
```

### Reward Shaping

Design informative rewards:

```python
def _calculate_reward(self, action):
    # Progress reward
    progress = self._calculate_progress()
    
    # Goal bonus
    goal_bonus = 100.0 if self._check_goal() else 0.0
    
    # Efficiency penalty
    time_penalty = -0.01
    
    return progress + goal_bonus + time_penalty
```

## Performance Best Practices

1. **Vectorize Operations**: Use NumPy operations instead of loops
2. **Avoid Copying**: Minimize unnecessary array copies
3. **Cache Values**: Store frequently computed values
4. **Profile Code**: Use `cProfile` to find bottlenecks
5. **Use JIT**: Consider Numba for critical sections

## Security

- Never commit secrets or credentials
- Use environment variables for sensitive data
- Validate all inputs
- Follow security best practices

## Getting Help

- Check existing documentation
- Look at example implementations
- Search closed issues
- Ask in discussions
- Contact the maintainers

## Recognition

Contributors will be recognized in:
- CONTRIBUTORS.md file
- Release notes
- Annual acknowledgments

## License

By contributing, you agree that your contributions will be licensed under the same license as the project (MIT License).

## Questions?

If you have questions about contributing, please open an issue or contact the maintainers.

Thank you for contributing to the RL Environment Framework!
