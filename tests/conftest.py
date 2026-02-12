"""
Test fixtures for RL environment tests
"""

import pytest
import numpy as np
from environments.base_env import BaseEnvironment


@pytest.fixture
def base_env():
    """Fixture providing a basic environment instance."""
    env = BaseEnvironment()
    yield env
    env.close()


@pytest.fixture
def configured_env():
    """Fixture providing a configured environment."""
    config = {
        'episode_length': 100,
        'seed': 42
    }
    env = BaseEnvironment(config)
    yield env
    env.close()


@pytest.fixture
def reset_env(base_env):
    """Fixture providing a reset environment."""
    base_env.reset()
    return base_env


@pytest.fixture
def random_seed():
    """Fixture for reproducible random numbers."""
    np.random.seed(42)
    return 42
