"""
Tests for Gymnasium API Compliance

This module uses gymnasium's built-in env_checker to validate
that our environments comply with the Gymnasium API specifications.
"""

import pytest
from gymnasium.utils.env_checker import check_env
from environments.base_env import BaseEnvironment
from examples.simple_gridworld import SimpleGridWorld


class TestEnvironmentAPICompliance:
    """Test suite for Gymnasium API compliance."""

    def test_base_environment_compliance(self):
        """Test that BaseEnvironment complies with Gymnasium API."""
        env = BaseEnvironment()

        # Run gymnasium's built-in environment checker
        # This validates observation/action spaces, reset/step APIs, etc.
        try:
            check_env(env, skip_render_check=True)
        except Exception as e:
            pytest.fail(f"BaseEnvironment failed Gymnasium API compliance check: {e}")
        finally:
            env.close()

    def test_simple_gridworld_compliance(self):
        """Test that SimpleGridWorld complies with Gymnasium API."""
        config = {"grid_size": 5, "episode_length": 50}
        env = SimpleGridWorld(config)

        # Run gymnasium's built-in environment checker
        try:
            check_env(env, skip_render_check=True)
        except Exception as e:
            pytest.fail(f"SimpleGridWorld failed Gymnasium API compliance check: {e}")
        finally:
            env.close()

    def test_simple_gridworld_dense_rewards_compliance(self):
        """Test SimpleGridWorld with dense rewards complies with API."""
        config = {"grid_size": 5, "episode_length": 50, "reward_type": "dense"}
        env = SimpleGridWorld(config)

        try:
            check_env(env, skip_render_check=True)
        except Exception as e:
            pytest.fail(f"SimpleGridWorld (dense rewards) failed compliance check: {e}")
        finally:
            env.close()

    def test_environment_with_nested_config(self):
        """Test environment with nested YAML config structure."""
        config = {
            "environment": {"episode_length": 100, "reward": {"scale": 2.0, "clip": True, "clip_range": [-10, 10]}}
        }
        env = BaseEnvironment(config)

        try:
            check_env(env, skip_render_check=True)
        except Exception as e:
            pytest.fail(f"BaseEnvironment with nested config failed compliance check: {e}")
        finally:
            env.close()

    def test_seeded_environment_compliance(self):
        """Test that seeded environments comply with API."""
        env = SimpleGridWorld()

        # Reset with seed
        obs, info = env.reset(seed=42)

        # Verify seeding worked
        assert hasattr(env, "np_random")
        assert env.np_random is not None

        try:
            check_env(env, skip_render_check=True)
        except Exception as e:
            pytest.fail(f"Seeded environment failed compliance check: {e}")
        finally:
            env.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
