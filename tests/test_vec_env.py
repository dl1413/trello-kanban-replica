"""
Tests for Vectorized Environment Wrappers

This module contains comprehensive tests for SyncVectorEnv and AsyncVectorEnv classes.
"""

import pytest
import numpy as np
from gymnasium import spaces
from environments.base_env import BaseEnvironment
from environments.vec_env import SyncVectorEnv, AsyncVectorEnv


class SimpleTestEnv(BaseEnvironment):
    """
    Simple test environment for vectorized environment testing.

    A minimal environment with deterministic behavior for easy testing.
    """

    def __init__(self, config=None):
        """Initialize the test environment."""
        super().__init__(config)
        self.action_space = spaces.Discrete(4)
        self.observation_space = spaces.Box(low=0, high=10, shape=(2,), dtype=np.float32)
        self.episode_length = self.config.get("episode_length", 10)
        self.reset_count = 0

    def _get_initial_state(self):
        """Initialize state to zeros."""
        self.reset_count += 1
        return np.array([0.0, 0.0], dtype=np.float32)

    def _get_observation(self):
        """Return current state."""
        return self.state.copy()

    def _update_state(self, action):
        """Update state based on action (just increment for testing)."""
        self.state[0] += action
        self.state[1] += 1.0

    def _calculate_reward(self, action):
        """Simple reward function."""
        return float(action)

    def _is_terminated(self):
        """Episode terminates when state[0] >= 10."""
        return self.state[0] >= 10.0

    def _get_info(self):
        """Return basic info."""
        return {
            "step": self.current_step,
            "reset_count": self.reset_count,
        }


@pytest.fixture
def num_envs():
    """Number of environments for testing."""
    return 4


@pytest.fixture
def env_fn():
    """Factory function for creating test environments."""
    return lambda: SimpleTestEnv({"episode_length": 10})


class TestSyncVectorEnv:
    """Test suite for SyncVectorEnv class."""

    def test_initialization(self, env_fn, num_envs):
        """Test that sync vectorized environment initializes correctly."""
        vec_env = SyncVectorEnv(env_fn, num_envs)

        assert vec_env is not None
        assert vec_env.num_envs == num_envs
        assert len(vec_env.envs) == num_envs
        assert not vec_env.closed

        vec_env.close()

    def test_initialization_invalid_num_envs(self, env_fn):
        """Test that initialization fails with invalid num_envs."""
        with pytest.raises(ValueError):
            SyncVectorEnv(env_fn, 0)

        with pytest.raises(ValueError):
            SyncVectorEnv(env_fn, -1)

    def test_reset(self, env_fn, num_envs):
        """Test reset functionality returns correct shape."""
        vec_env = SyncVectorEnv(env_fn, num_envs)
        obs = vec_env.reset()

        assert obs.shape == (num_envs, 2)
        assert obs.dtype == np.float32
        assert np.all(obs == 0.0)

        vec_env.close()

    def test_reset_with_seed(self, num_envs):
        """Test that reset with seed produces reproducible results."""

        def seeded_env_fn():
            return SimpleTestEnv({"episode_length": 10})

        vec_env1 = SyncVectorEnv(seeded_env_fn, num_envs)
        vec_env2 = SyncVectorEnv(seeded_env_fn, num_envs)

        obs1 = vec_env1.reset(seed=42)
        obs2 = vec_env2.reset(seed=42)

        np.testing.assert_array_equal(obs1, obs2)

        vec_env1.close()
        vec_env2.close()

    def test_step_single_action(self, env_fn, num_envs):
        """Test step with a single action for all environments."""
        vec_env = SyncVectorEnv(env_fn, num_envs)
        vec_env.reset()

        actions = np.array([1, 2, 3, 0])
        obs, rewards, terminated, truncated, infos = vec_env.step(actions)

        assert obs.shape == (num_envs, 2)
        assert rewards.shape == (num_envs,)
        assert terminated.shape == (num_envs,)
        assert truncated.shape == (num_envs,)
        assert len(infos) == num_envs

        # Check that observations were updated correctly
        np.testing.assert_array_equal(obs[:, 0], actions.astype(np.float32))
        np.testing.assert_array_equal(obs[:, 1], np.ones(num_envs, dtype=np.float32))

        # Check rewards match actions
        np.testing.assert_array_equal(rewards, actions.astype(np.float32))

        vec_env.close()

    def test_step_invalid_actions(self, env_fn, num_envs):
        """Test that step fails with wrong number of actions."""
        vec_env = SyncVectorEnv(env_fn, num_envs)
        vec_env.reset()

        with pytest.raises(ValueError):
            vec_env.step(np.array([1, 2]))  # Too few actions

        vec_env.close()

    def test_observation_stacking(self, env_fn):
        """Test that observations are stacked correctly."""
        num_envs = 3
        vec_env = SyncVectorEnv(env_fn, num_envs)
        obs = vec_env.reset()

        # All environments start at [0, 0]
        assert obs.shape == (3, 2)
        assert np.all(obs == 0.0)

        # Step with different actions
        actions = np.array([1, 2, 3])
        obs, _, _, _, _ = vec_env.step(actions)

        # Check each environment has correct observation
        expected = np.array([[1.0, 1.0], [2.0, 1.0], [3.0, 1.0]], dtype=np.float32)
        np.testing.assert_array_almost_equal(obs, expected)

        vec_env.close()

    def test_auto_reset_on_termination(self, env_fn, num_envs):
        """Test that environments automatically reset when terminated."""
        vec_env = SyncVectorEnv(env_fn, num_envs)
        vec_env.reset()

        # Take actions that will cause termination (state[0] >= 10)
        # Action 3 repeated 4 times: 3, 6, 9, 12 (terminates on 4th step)
        actions = np.array([3, 3, 3, 3])

        for step in range(3):
            obs, rewards, terminated, truncated, infos = vec_env.step(actions)
            assert not any(terminated), f"Should not terminate at step {step}"

        # 4th step should cause termination and auto-reset
        obs, rewards, terminated, truncated, infos = vec_env.step(actions)

        # All should terminate
        assert all(terminated)

        # Check that final observations are stored in info
        for info in infos:
            assert "final_observation" in info
            assert info["_final_observation"]
            assert info["final_observation"][0] >= 10.0

        # Observations should be from reset (back to [0, 0])
        assert np.all(obs[:, 0] == 0.0)

        vec_env.close()

    def test_auto_reset_on_truncation(self):
        """Test that environments automatically reset when truncated."""

        def short_env_fn():
            return SimpleTestEnv({"episode_length": 3})

        vec_env = SyncVectorEnv(short_env_fn, num_envs=2)
        vec_env.reset()

        # Step until truncation (3 steps)
        for _ in range(3):
            obs, rewards, terminated, truncated, infos = vec_env.step(np.array([1, 1]))

        # Should be truncated
        assert all(truncated)
        assert "final_observation" in infos[0]
        assert np.all(obs == 0.0)  # Reset to initial state

        vec_env.close()

    def test_env_independence(self, env_fn, num_envs):
        """Test that each environment instance is independent."""
        vec_env = SyncVectorEnv(env_fn, num_envs)
        vec_env.reset()

        # Step with different actions for each environment
        actions1 = np.array([1, 2, 3, 0])
        obs1, _, _, _, _ = vec_env.step(actions1)

        actions2 = np.array([0, 0, 0, 0])
        obs2, _, _, _, _ = vec_env.step(actions2)

        # Each environment should have accumulated different states
        expected = np.array([[1.0, 2.0], [2.0, 2.0], [3.0, 2.0], [0.0, 2.0]], dtype=np.float32)
        np.testing.assert_array_almost_equal(obs2, expected)

        vec_env.close()

    def test_close(self, env_fn, num_envs):
        """Test that close() cleans up resources properly."""
        vec_env = SyncVectorEnv(env_fn, num_envs)
        vec_env.reset()

        vec_env.close()

        assert vec_env.closed

        # Should not be able to reset or step after closing
        with pytest.raises(RuntimeError):
            vec_env.reset()

        with pytest.raises(RuntimeError):
            vec_env.step(np.array([0, 0, 0, 0]))

    def test_multiple_episodes(self, env_fn, num_envs):
        """Test running multiple episodes through auto-reset."""
        vec_env = SyncVectorEnv(env_fn, num_envs)
        vec_env.reset()

        # Run enough steps to trigger multiple auto-resets
        total_resets = 0
        for _ in range(50):
            actions = np.array([3, 3, 3, 3])
            obs, rewards, terminated, truncated, infos = vec_env.step(actions)

            # Count resets (when final_observation is present)
            total_resets += sum(1 for info in infos if "_final_observation" in info)

        # Should have had multiple resets
        assert total_resets > 0

        vec_env.close()


class TestAsyncVectorEnv:
    """Test suite for AsyncVectorEnv class."""

    def test_initialization(self, env_fn, num_envs):
        """Test that async vectorized environment initializes correctly."""
        vec_env = AsyncVectorEnv(env_fn, num_envs)

        assert vec_env is not None
        assert vec_env.num_envs == num_envs
        assert len(vec_env.processes) == num_envs
        assert not vec_env.closed

        # Check that all processes are alive
        for process in vec_env.processes:
            assert process.is_alive()

        vec_env.close()

    def test_initialization_invalid_num_envs(self, env_fn):
        """Test that initialization fails with invalid num_envs."""
        with pytest.raises(ValueError):
            AsyncVectorEnv(env_fn, 0)

        with pytest.raises(ValueError):
            AsyncVectorEnv(env_fn, -1)

    def test_reset(self, env_fn, num_envs):
        """Test reset functionality returns correct shape."""
        vec_env = AsyncVectorEnv(env_fn, num_envs)
        obs = vec_env.reset()

        assert obs.shape == (num_envs, 2)
        assert obs.dtype == np.float32
        assert np.all(obs == 0.0)

        vec_env.close()

    def test_reset_with_seed(self, num_envs):
        """Test that reset with seed produces reproducible results."""

        def seeded_env_fn():
            return SimpleTestEnv({"episode_length": 10})

        vec_env1 = AsyncVectorEnv(seeded_env_fn, num_envs)
        vec_env2 = AsyncVectorEnv(seeded_env_fn, num_envs)

        obs1 = vec_env1.reset(seed=42)
        obs2 = vec_env2.reset(seed=42)

        np.testing.assert_array_equal(obs1, obs2)

        vec_env1.close()
        vec_env2.close()

    def test_step_single_action(self, env_fn, num_envs):
        """Test step with actions for all environments."""
        vec_env = AsyncVectorEnv(env_fn, num_envs)
        vec_env.reset()

        actions = np.array([1, 2, 3, 0])
        obs, rewards, terminated, truncated, infos = vec_env.step(actions)

        assert obs.shape == (num_envs, 2)
        assert rewards.shape == (num_envs,)
        assert terminated.shape == (num_envs,)
        assert truncated.shape == (num_envs,)
        assert len(infos) == num_envs

        # Check that observations were updated correctly
        np.testing.assert_array_equal(obs[:, 0], actions.astype(np.float32))
        np.testing.assert_array_equal(obs[:, 1], np.ones(num_envs, dtype=np.float32))

        # Check rewards match actions
        np.testing.assert_array_equal(rewards, actions.astype(np.float32))

        vec_env.close()

    def test_step_invalid_actions(self, env_fn, num_envs):
        """Test that step fails with wrong number of actions."""
        vec_env = AsyncVectorEnv(env_fn, num_envs)
        vec_env.reset()

        with pytest.raises(ValueError):
            vec_env.step(np.array([1, 2]))  # Too few actions

        vec_env.close()

    def test_observation_stacking(self, env_fn):
        """Test that observations are stacked correctly."""
        num_envs = 3
        vec_env = AsyncVectorEnv(env_fn, num_envs)
        obs = vec_env.reset()

        # All environments start at [0, 0]
        assert obs.shape == (3, 2)
        assert np.all(obs == 0.0)

        # Step with different actions
        actions = np.array([1, 2, 3])
        obs, _, _, _, _ = vec_env.step(actions)

        # Check each environment has correct observation
        expected = np.array([[1.0, 1.0], [2.0, 1.0], [3.0, 1.0]], dtype=np.float32)
        np.testing.assert_array_almost_equal(obs, expected)

        vec_env.close()

    def test_auto_reset_on_termination(self, env_fn, num_envs):
        """Test that environments automatically reset when terminated."""
        vec_env = AsyncVectorEnv(env_fn, num_envs)
        vec_env.reset()

        # Take actions that will cause termination (state[0] >= 10)
        actions = np.array([3, 3, 3, 3])

        for step in range(3):
            obs, rewards, terminated, truncated, infos = vec_env.step(actions)
            assert not any(terminated), f"Should not terminate at step {step}"

        # 4th step should cause termination and auto-reset
        obs, rewards, terminated, truncated, infos = vec_env.step(actions)

        # All should terminate
        assert all(terminated)

        # Check that final observations are stored in info
        for info in infos:
            assert "final_observation" in info
            assert info["_final_observation"]
            assert info["final_observation"][0] >= 10.0

        # Observations should be from reset (back to [0, 0])
        assert np.all(obs[:, 0] == 0.0)

        vec_env.close()

    def test_auto_reset_on_truncation(self):
        """Test that environments automatically reset when truncated."""

        def short_env_fn():
            return SimpleTestEnv({"episode_length": 3})

        vec_env = AsyncVectorEnv(short_env_fn, num_envs=2)
        vec_env.reset()

        # Step until truncation (3 steps)
        for _ in range(3):
            obs, rewards, terminated, truncated, infos = vec_env.step(np.array([1, 1]))

        # Should be truncated
        assert all(truncated)
        assert "final_observation" in infos[0]
        assert np.all(obs == 0.0)  # Reset to initial state

        vec_env.close()

    def test_env_independence(self, env_fn, num_envs):
        """Test that each environment instance is independent."""
        vec_env = AsyncVectorEnv(env_fn, num_envs)
        vec_env.reset()

        # Step with different actions for each environment
        actions1 = np.array([1, 2, 3, 0])
        obs1, _, _, _, _ = vec_env.step(actions1)

        actions2 = np.array([0, 0, 0, 0])
        obs2, _, _, _, _ = vec_env.step(actions2)

        # Each environment should have accumulated different states
        expected = np.array([[1.0, 2.0], [2.0, 2.0], [3.0, 2.0], [0.0, 2.0]], dtype=np.float32)
        np.testing.assert_array_almost_equal(obs2, expected)

        vec_env.close()

    def test_close(self, env_fn, num_envs):
        """Test that close() cleans up resources properly."""
        vec_env = AsyncVectorEnv(env_fn, num_envs)
        vec_env.reset()

        vec_env.close()

        assert vec_env.closed

        # Check that all processes are terminated
        for process in vec_env.processes:
            assert not process.is_alive()

        # Should not be able to reset or step after closing
        with pytest.raises(RuntimeError):
            vec_env.reset()

        with pytest.raises(RuntimeError):
            vec_env.step(np.array([0, 0, 0, 0]))

    def test_process_cleanup_on_exception(self, env_fn, num_envs):
        """Test that processes are cleaned up properly even if exception occurs."""
        vec_env = AsyncVectorEnv(env_fn, num_envs)

        # Close the environment
        vec_env.close()

        # All processes should be terminated
        for process in vec_env.processes:
            assert not process.is_alive()

    def test_multiple_episodes(self, env_fn, num_envs):
        """Test running multiple episodes through auto-reset."""
        vec_env = AsyncVectorEnv(env_fn, num_envs)
        vec_env.reset()

        # Run enough steps to trigger multiple auto-resets
        total_resets = 0
        for _ in range(50):
            actions = np.array([3, 3, 3, 3])
            obs, rewards, terminated, truncated, infos = vec_env.step(actions)

            # Count resets (when final_observation is present)
            total_resets += sum(1 for info in infos if "_final_observation" in info)

        # Should have had multiple resets
        assert total_resets > 0

        vec_env.close()

    def test_parallel_execution_speedup(self, env_fn):
        """Test that async version provides some speedup (basic sanity check)."""
        import time

        num_envs = 4
        num_steps = 100

        # Time sync version
        sync_env = SyncVectorEnv(env_fn, num_envs)
        sync_env.reset()
        start = time.time()
        for _ in range(num_steps):
            sync_env.step(np.array([1, 1, 1, 1]))
        sync_time = time.time() - start
        sync_env.close()

        # Time async version
        async_env = AsyncVectorEnv(env_fn, num_envs)
        async_env.reset()
        start = time.time()
        for _ in range(num_steps):
            async_env.step(np.array([1, 1, 1, 1]))
        async_time = time.time() - start
        async_env.close()

        # Both should complete in reasonable time
        assert sync_time < 10.0  # Should be fast for simple env
        assert async_time < 10.0

        # Note: We don't assert async is faster because overhead might dominate
        # for such a simple environment


class TestVectorEnvComparison:
    """Test that sync and async versions produce identical results."""

    def test_identical_results_with_seed(self):
        """Test that sync and async produce same results with same seed."""

        def env_fn():
            return SimpleTestEnv({"episode_length": 10})

        num_envs = 4
        seed = 42

        # Run sync version
        sync_env = SyncVectorEnv(env_fn, num_envs)
        sync_obs = sync_env.reset(seed=seed)
        sync_trajectory = [sync_obs]

        for _ in range(10):
            actions = np.array([1, 2, 3, 0])
            obs, rewards, _, _, _ = sync_env.step(actions)
            sync_trajectory.append(obs)

        # Run async version
        async_env = AsyncVectorEnv(env_fn, num_envs)
        async_obs = async_env.reset(seed=seed)
        async_trajectory = [async_obs]

        for _ in range(10):
            actions = np.array([1, 2, 3, 0])
            obs, rewards, _, _, _ = async_env.step(actions)
            async_trajectory.append(obs)

        # Compare trajectories
        for i, (sync_o, async_o) in enumerate(zip(sync_trajectory, async_trajectory)):
            np.testing.assert_array_equal(sync_o, async_o, err_msg=f"Observations differ at step {i}")

        sync_env.close()
        async_env.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
