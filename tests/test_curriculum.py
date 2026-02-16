"""
Tests for Curriculum Learning Wrapper

This module tests the CurriculumWrapper's ability to automatically adjust
environment difficulty based on agent performance.
"""

import pytest
import numpy as np

from environments.base_env import BaseEnvironment
from environments.curriculum_wrapper import CurriculumWrapper
from examples.simple_gridworld import SimpleGridWorld


class MockEnvironment(BaseEnvironment):
    """Mock environment for testing curriculum wrapper."""

    def __init__(self, config=None):
        """Initialize mock environment."""
        super().__init__(config)
        self.reset_count = 0
        self.step_count = 0

        # Define proper observation space
        from gymnasium import spaces
        self.observation_space = spaces.Box(low=0, high=10, shape=(2,), dtype=np.int32)

    def _get_initial_state(self):
        """Get initial state."""
        self.reset_count += 1
        self.step_count = 0
        return np.array([0, 0], dtype=np.int32)

    def _get_observation(self):
        """Get observation."""
        return np.array([0, 0], dtype=np.int32)

    def _update_state(self, action):
        """Update state."""
        self.step_count += 1

    def _calculate_reward(self, action):
        """Calculate reward."""
        return 0.0

    def _is_terminated(self):
        """Check termination."""
        return self.step_count >= 10

    def _get_info(self):
        """Get info."""
        info = super()._get_info()
        info['goal_reached'] = self.step_count >= 10
        return info


class TestCurriculumWrapper:
    """Test suite for CurriculumWrapper class."""

    def test_initialization(self):
        """Test that wrapper initializes correctly."""
        env = MockEnvironment()
        wrapper = CurriculumWrapper(env, initial_difficulty=0.5)

        assert wrapper is not None
        assert wrapper.get_difficulty() == 0.5
        assert wrapper._episode_count == 0
        assert len(wrapper._success_history) == 0

    def test_initialization_with_invalid_difficulty(self):
        """Test that invalid initial difficulty raises error."""
        env = MockEnvironment()

        with pytest.raises(ValueError, match="initial_difficulty must be in"):
            CurriculumWrapper(env, initial_difficulty=1.5)

        with pytest.raises(ValueError, match="initial_difficulty must be in"):
            CurriculumWrapper(env, initial_difficulty=-0.1)

    def test_initialization_with_invalid_thresholds(self):
        """Test that invalid thresholds raise errors."""
        env = MockEnvironment()

        with pytest.raises(ValueError, match="success_threshold must be in"):
            CurriculumWrapper(env, success_threshold=1.5)

        with pytest.raises(ValueError, match="failure_threshold must be in"):
            CurriculumWrapper(env, failure_threshold=-0.1)

        with pytest.raises(ValueError, match="failure_threshold must be in"):
            CurriculumWrapper(env, failure_threshold=0.8, success_threshold=0.7)

    def test_initialization_with_invalid_step(self):
        """Test that invalid difficulty step raises error."""
        env = MockEnvironment()

        with pytest.raises(ValueError, match="difficulty_step must be positive"):
            CurriculumWrapper(env, difficulty_step=-0.1)

    def test_initialization_with_non_base_env(self):
        """Test that wrapping non-BaseEnvironment raises error."""
        # Create an object that is a gym.Env but not BaseEnvironment
        import gymnasium as gym
        env = gym.make('CartPole-v1')

        with pytest.raises(TypeError, match="must be a BaseEnvironment subclass"):
            CurriculumWrapper(env)

        env.close()

    def test_get_difficulty(self):
        """Test getting current difficulty."""
        env = MockEnvironment()
        wrapper = CurriculumWrapper(env, initial_difficulty=0.3)

        assert wrapper.get_difficulty() == 0.3

    def test_set_difficulty(self):
        """Test manually setting difficulty."""
        env = MockEnvironment()
        wrapper = CurriculumWrapper(env, initial_difficulty=0.0)

        wrapper.set_difficulty(0.7)
        assert wrapper.get_difficulty() == 0.7

        # Test bounds
        wrapper.set_difficulty(0.0)
        assert wrapper.get_difficulty() == 0.0

        wrapper.set_difficulty(1.0)
        assert wrapper.get_difficulty() == 1.0

    def test_set_difficulty_invalid(self):
        """Test that setting invalid difficulty raises error."""
        env = MockEnvironment()
        wrapper = CurriculumWrapper(env)

        with pytest.raises(ValueError, match="Difficulty must be in"):
            wrapper.set_difficulty(1.5)

        with pytest.raises(ValueError, match="Difficulty must be in"):
            wrapper.set_difficulty(-0.1)

    def test_reset(self):
        """Test reset functionality."""
        env = MockEnvironment()
        wrapper = CurriculumWrapper(env, initial_difficulty=0.5)

        obs, info = wrapper.reset()

        assert env.observation_space.contains(obs)
        assert 'curriculum_difficulty' in info
        assert info['curriculum_difficulty'] == 0.5
        assert 'curriculum_success_rate' in info
        assert 'curriculum_episode_count' in info

    def test_step(self):
        """Test step functionality."""
        env = MockEnvironment()
        wrapper = CurriculumWrapper(env)

        wrapper.reset()
        obs, reward, terminated, truncated, info = wrapper.step(0)

        assert env.observation_space.contains(obs)
        assert isinstance(reward, (int, float))
        assert isinstance(terminated, bool)
        assert isinstance(truncated, bool)
        assert 'curriculum_difficulty' in info
        assert 'curriculum_success_rate' in info

    def test_difficulty_increases_on_high_performance(self):
        """Test that difficulty increases when success rate exceeds threshold."""
        env = MockEnvironment({'episode_length': 20})
        wrapper = CurriculumWrapper(
            env,
            initial_difficulty=0.0,
            window_size=10,
            success_threshold=0.7,
            difficulty_step=0.1,
            min_episodes_before_change=5
        )

        initial_difficulty = wrapper.get_difficulty()

        # Run successful episodes (11 episodes to fill window and trigger change)
        for episode in range(11):
            obs, info = wrapper.reset()
            for _ in range(10):  # Run 10 steps to trigger termination
                obs, reward, terminated, truncated, info = wrapper.step(0)
                if terminated or truncated:
                    break

        # Difficulty should have increased
        assert wrapper.get_difficulty() > initial_difficulty

    def test_difficulty_decreases_on_low_performance(self):
        """Test that difficulty decreases when success rate falls below threshold."""
        env = MockEnvironment({'episode_length': 5})
        wrapper = CurriculumWrapper(
            env,
            initial_difficulty=0.5,
            window_size=10,
            success_threshold=0.7,
            failure_threshold=0.3,
            difficulty_step=0.1,
            min_episodes_before_change=5,
            enable_decrease=True
        )

        initial_difficulty = wrapper.get_difficulty()

        # Run failing episodes by truncating before goal
        # Need to run enough episodes to fill window and trigger change
        for episode in range(15):
            obs, info = wrapper.reset()
            # Run until episode ends (will truncate at 5 steps, before goal at 10)
            while True:
                obs, reward, terminated, truncated, info = wrapper.step(0)
                if terminated or truncated:
                    break

        # Difficulty should have decreased
        assert wrapper.get_difficulty() < initial_difficulty

    def test_difficulty_no_decrease_when_disabled(self):
        """Test that difficulty doesn't decrease when enable_decrease=False."""
        env = MockEnvironment({'episode_length': 5})
        wrapper = CurriculumWrapper(
            env,
            initial_difficulty=0.5,
            window_size=10,
            success_threshold=0.7,
            failure_threshold=0.3,
            difficulty_step=0.1,
            min_episodes_before_change=5,
            enable_decrease=False
        )

        initial_difficulty = wrapper.get_difficulty()

        # Run failing episodes
        for episode in range(11):
            obs, info = wrapper.reset()
            for _ in range(3):
                obs, reward, terminated, truncated, info = wrapper.step(0)
                if terminated or truncated:
                    break

        # Difficulty should not have changed
        assert wrapper.get_difficulty() == initial_difficulty

    def test_difficulty_unchanged_below_threshold(self):
        """Test that difficulty doesn't change when success rate is between thresholds."""
        env = MockEnvironment({'episode_length': 20})
        wrapper = CurriculumWrapper(
            env,
            initial_difficulty=0.5,
            window_size=10,
            success_threshold=0.8,
            failure_threshold=0.2,
            difficulty_step=0.1,
            min_episodes_before_change=5
        )

        initial_difficulty = wrapper.get_difficulty()

        # Run mix of successful and failed episodes (50% success rate)
        # Need to run enough episodes to fill window
        for episode in range(15):
            obs, info = wrapper.reset()
            if episode % 2 == 0:
                # Success: run full episode
                for _ in range(10):
                    obs, reward, terminated, truncated, info = wrapper.step(0)
                    if terminated or truncated:
                        break
            else:
                # Failure: truncate early
                for _ in range(3):
                    obs, reward, terminated, truncated, info = wrapper.step(0)
                    if terminated or truncated:
                        break

        # Difficulty should remain unchanged (50% is between 0.2 and 0.8)
        assert wrapper.get_difficulty() == initial_difficulty

    def test_difficulty_respects_bounds(self):
        """Test that difficulty stays within [0, 1] bounds."""
        env = MockEnvironment({'episode_length': 20})
        wrapper = CurriculumWrapper(
            env,
            initial_difficulty=0.9,
            window_size=5,
            success_threshold=0.7,
            difficulty_step=0.2,
            min_episodes_before_change=3
        )

        # Run many successful episodes to try to push difficulty above 1.0
        for episode in range(20):
            obs, info = wrapper.reset()
            for _ in range(10):
                obs, reward, terminated, truncated, info = wrapper.step(0)
                if terminated or truncated:
                    break

        # Difficulty should be capped at 1.0
        assert wrapper.get_difficulty() <= 1.0
        assert wrapper.get_difficulty() == 1.0

    def test_difficulty_respects_lower_bound(self):
        """Test that difficulty doesn't go below 0.0."""
        env = MockEnvironment({'episode_length': 5})
        wrapper = CurriculumWrapper(
            env,
            initial_difficulty=0.15,
            window_size=5,
            success_threshold=0.9,
            failure_threshold=0.5,
            difficulty_step=0.1,
            min_episodes_before_change=3,
            enable_decrease=True
        )

        # Run many failing episodes to try to push difficulty below 0.0
        for episode in range(25):
            obs, info = wrapper.reset()
            # Run until episode ends (will truncate at 5 steps, before goal at 10)
            while True:
                obs, reward, terminated, truncated, info = wrapper.step(0)
                if terminated or truncated:
                    break

        # Difficulty should be capped at 0.0
        assert wrapper.get_difficulty() >= 0.0
        assert wrapper.get_difficulty() == 0.0

    def test_no_change_before_min_episodes(self):
        """Test that difficulty doesn't change before minimum episodes."""
        env = MockEnvironment({'episode_length': 20})
        wrapper = CurriculumWrapper(
            env,
            initial_difficulty=0.5,
            window_size=10,
            success_threshold=0.7,
            difficulty_step=0.1,
            min_episodes_before_change=20
        )

        initial_difficulty = wrapper.get_difficulty()

        # Run only 10 successful episodes
        for episode in range(10):
            obs, info = wrapper.reset()
            for _ in range(10):
                obs, reward, terminated, truncated, info = wrapper.step(0)
                if terminated or truncated:
                    break

        # Difficulty should not have changed
        assert wrapper.get_difficulty() == initial_difficulty

    def test_gridworld_config_modification(self):
        """Test that GridWorld config is modified based on difficulty."""
        # Use SimpleGridWorld
        env = SimpleGridWorld({'grid_size': 5})
        wrapper = CurriculumWrapper(env, initial_difficulty=0.0)

        # Reset to apply config
        wrapper.reset()

        # At difficulty 0.0, grid should be 3x3
        assert env.config['grid_size'] == 3

        # Increase difficulty manually
        wrapper.set_difficulty(1.0)
        wrapper.reset()

        # At difficulty 1.0, grid should be 15x15
        assert env.config['grid_size'] == 15

    def test_gridworld_difficulty_interpolation(self):
        """Test that GridWorld difficulty interpolates correctly."""
        env = SimpleGridWorld()
        wrapper = CurriculumWrapper(env, initial_difficulty=0.5)

        wrapper.reset()

        # At difficulty 0.5, grid should be ~7x7
        grid_size = env.config['grid_size']
        assert 5 <= grid_size <= 9
        assert env.config['difficulty'] == 0.5

    def test_success_rate_calculation(self):
        """Test success rate calculation."""
        env = MockEnvironment({'episode_length': 20})
        wrapper = CurriculumWrapper(env, window_size=5)

        # No history initially
        assert wrapper._get_success_rate() == 0.0

        # Add some successes and failures
        wrapper._success_history.append(True)
        wrapper._success_history.append(True)
        wrapper._success_history.append(False)

        expected_rate = 2.0 / 3.0
        assert abs(wrapper._get_success_rate() - expected_rate) < 0.01

    def test_episode_count_increments(self):
        """Test that episode count increments correctly."""
        env = MockEnvironment({'episode_length': 20})
        wrapper = CurriculumWrapper(env)

        assert wrapper._episode_count == 0

        # Run a few episodes
        for episode in range(5):
            obs, info = wrapper.reset()
            for _ in range(10):
                obs, reward, terminated, truncated, info = wrapper.step(0)
                if terminated or truncated:
                    break

        assert wrapper._episode_count == 5

    def test_success_tracking_with_goal_reached(self):
        """Test that success is tracked correctly via goal_reached flag."""
        env = MockEnvironment({'episode_length': 20})
        wrapper = CurriculumWrapper(env, window_size=5)

        # Run successful episode
        obs, info = wrapper.reset()
        for _ in range(10):  # Enough steps to reach goal
            obs, reward, terminated, truncated, info = wrapper.step(0)
            if terminated or truncated:
                break

        # Success should be recorded
        assert len(wrapper._success_history) == 1
        assert wrapper._success_history[0] is True

    def test_success_tracking_with_truncation(self):
        """Test that truncation is tracked as failure."""
        env = MockEnvironment({'episode_length': 5})
        wrapper = CurriculumWrapper(env, window_size=5)

        # Run episode that truncates
        obs, info = wrapper.reset()
        terminated = False
        truncated = False
        # Run until episode ends
        while not (terminated or truncated):
            obs, reward, terminated, truncated, info = wrapper.step(0)

        # Episode should have truncated before reaching goal (5 steps < 10 needed for goal)
        assert truncated
        # Failure should be recorded
        assert len(wrapper._success_history) == 1
        assert wrapper._success_history[0] is False

    def test_curriculum_info_in_reset(self):
        """Test that curriculum info is included in reset info."""
        env = MockEnvironment()
        wrapper = CurriculumWrapper(env, initial_difficulty=0.6)

        obs, info = wrapper.reset()

        assert 'curriculum_difficulty' in info
        assert 'curriculum_success_rate' in info
        assert 'curriculum_episode_count' in info
        assert info['curriculum_difficulty'] == 0.6
        assert info['curriculum_episode_count'] == 0

    def test_curriculum_info_in_step(self):
        """Test that curriculum info is included in step info."""
        env = MockEnvironment()
        wrapper = CurriculumWrapper(env, initial_difficulty=0.6)

        wrapper.reset()
        obs, reward, terminated, truncated, info = wrapper.step(0)

        assert 'curriculum_difficulty' in info
        assert 'curriculum_success_rate' in info
        assert info['curriculum_difficulty'] == 0.6

    def test_multiple_difficulty_changes(self):
        """Test multiple difficulty adjustments over many episodes."""
        env = MockEnvironment({'episode_length': 20})
        wrapper = CurriculumWrapper(
            env,
            initial_difficulty=0.0,
            window_size=5,
            success_threshold=0.8,
            difficulty_step=0.2,
            min_episodes_before_change=3
        )

        difficulties = [wrapper.get_difficulty()]

        # Run 30 successful episodes
        for episode in range(30):
            obs, info = wrapper.reset()
            for _ in range(10):
                obs, reward, terminated, truncated, info = wrapper.step(0)
                if terminated or truncated:
                    break
            difficulties.append(wrapper.get_difficulty())

        # Difficulty should have increased multiple times
        assert difficulties[-1] > difficulties[0]
        # Should reach max difficulty
        assert wrapper.get_difficulty() == 1.0

    def test_generic_environment_difficulty_config(self):
        """Test that generic environments receive difficulty in config."""
        env = MockEnvironment()
        wrapper = CurriculumWrapper(env, initial_difficulty=0.4)

        wrapper.reset()

        # Generic environment should have difficulty in config
        assert 'difficulty' in env.config
        assert env.config['difficulty'] == 0.4

    def test_wrapper_preserves_env_interface(self):
        """Test that wrapper preserves environment interface."""
        env = MockEnvironment()
        wrapper = CurriculumWrapper(env)

        # Should have standard gym attributes
        assert hasattr(wrapper, 'action_space')
        assert hasattr(wrapper, 'observation_space')
        assert hasattr(wrapper, 'reset')
        assert hasattr(wrapper, 'step')
        assert hasattr(wrapper, 'render')
        assert hasattr(wrapper, 'close')

    def test_difficulty_progression_realistic_scenario(self):
        """Test difficulty progression in a realistic scenario with gradual improvement."""
        env = MockEnvironment({'episode_length': 20})
        wrapper = CurriculumWrapper(
            env,
            initial_difficulty=0.0,
            window_size=10,
            success_threshold=0.7,
            difficulty_step=0.1,
            min_episodes_before_change=5
        )

        # Simulate learning: start with 30% success, gradually improve to 90%
        success_rates = [0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
        difficulties = [wrapper.get_difficulty()]

        for target_rate in success_rates:
            # Run 10 episodes at this success rate
            for episode in range(10):
                obs, info = wrapper.reset()
                # Succeed based on target rate
                should_succeed = np.random.random() < target_rate
                if should_succeed:
                    for _ in range(10):  # Full episode
                        obs, reward, terminated, truncated, info = wrapper.step(0)
                        if terminated or truncated:
                            break
                else:
                    for _ in range(3):  # Truncate early
                        obs, reward, terminated, truncated, info = wrapper.step(0)
                        if terminated or truncated:
                            break
            difficulties.append(wrapper.get_difficulty())

        # Difficulty should generally increase as success rate improves
        # At least some increase should have occurred
        assert difficulties[-1] > difficulties[0]


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
