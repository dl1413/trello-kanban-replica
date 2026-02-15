"""
Tests for optimized features in the RL framework.

This module tests the new optimizations added to the BaseEnvironment,
SimpleGridWorld, and Q-Learning agent.
"""

import pytest
import numpy as np
import tempfile
from pathlib import Path
from examples.simple_gridworld import SimpleGridWorld
from examples.q_learning_agent import QLearningAgent


class TestBaseEnvironmentOptimizations:
    """Test optimized BaseEnvironment features."""

    def test_episode_return_tracking(self):
        """Test that episode return is tracked correctly."""
        env = SimpleGridWorld({'grid_size': 5, 'episode_length': 100})
        obs, info = env.reset(seed=42)

        assert env.episode_return == 0.0
        assert env.episode_steps == 0

        # Take a few steps
        for _ in range(5):
            obs, reward, terminated, truncated, info = env.step(env.action_space.sample())
            if terminated or truncated:
                break

        # Episode return should be sum of rewards
        assert env.episode_return != 0.0
        assert env.episode_steps > 0

    def test_info_dict_enhancements(self):
        """Test enhanced info dict with episode return and success flag."""
        env = SimpleGridWorld({'grid_size': 5, 'episode_length': 100})
        obs, info = env.reset(seed=42)

        # Info should include episode tracking
        assert 'episode_return' in info
        assert 'episode_steps' in info

        # Take steps until done
        while True:
            obs, reward, terminated, truncated, info = env.step(env.action_space.sample())
            if terminated or truncated:
                break

        # Info should include success flag when done
        assert 'is_success' in info
        assert isinstance(info['is_success'], bool)

    def test_config_validation(self):
        """Test that config validation catches invalid values."""
        # Negative episode_length should raise error
        with pytest.raises(ValueError, match="episode_length must be a non-negative integer"):
            env = SimpleGridWorld({'episode_length': -10})

        # Invalid reward_scale type should raise error
        with pytest.raises(ValueError, match="reward_scale must be a number"):
            env = SimpleGridWorld({'environment': {'reward': {'scale': 'invalid'}}})

        # Invalid clip_range should raise error
        with pytest.raises(ValueError, match="reward_clip_range must be a list/tuple"):
            env = SimpleGridWorld({
                'environment': {'reward': {'clip': True, 'clip_range': 'invalid'}}
            })

    def test_rgb_rendering(self):
        """Test RGB array rendering."""
        env = SimpleGridWorld({'grid_size': 5})
        obs, info = env.reset(seed=42)

        # Render as RGB array
        rgb_array = env.render(mode='rgb_array')

        assert rgb_array is not None
        assert isinstance(rgb_array, np.ndarray)
        assert rgb_array.ndim == 3
        assert rgb_array.shape[2] == 3  # RGB channels
        assert rgb_array.dtype == np.uint8


class TestSimpleGridWorldOptimizations:
    """Test optimized SimpleGridWorld features."""

    def test_normalized_observations(self):
        """Test that observations are normalized to [0, 1]."""
        env = SimpleGridWorld({'grid_size': 10})
        obs, info = env.reset(seed=42)

        # Observations should be in [0, 1] range
        assert obs.dtype == np.float32
        assert np.all(obs >= 0.0)
        assert np.all(obs <= 1.0)

        # Take some steps
        for _ in range(10):
            obs, reward, terminated, truncated, info = env.step(env.action_space.sample())
            assert np.all(obs >= 0.0)
            assert np.all(obs <= 1.0)
            if terminated or truncated:
                break

    def test_obstacles(self):
        """Test obstacle generation and collision."""
        env = SimpleGridWorld({'grid_size': 10, 'num_obstacles': 5})
        obs, info = env.reset(seed=42)

        # Should have obstacles
        assert len(env.obstacles) == 5

        # Agent shouldn't spawn on obstacle
        assert tuple(env.agent_pos) not in env.obstacles

        # Goal shouldn't be on obstacle
        assert tuple(env.goal_pos) not in env.obstacles

    def test_goal_randomization(self):
        """Test goal randomization option."""
        env = SimpleGridWorld({'grid_size': 10, 'randomize_goal': True})

        # Reset multiple times and check that goal changes
        goals = set()
        for i in range(10):
            obs, info = env.reset(seed=i)
            goals.add(tuple(env.goal_pos))

        # Should have different goals across resets
        assert len(goals) > 1

    def test_normalized_dense_rewards(self):
        """Test that dense rewards are normalized."""
        env = SimpleGridWorld({'grid_size': 10, 'reward_type': 'dense'})
        obs, info = env.reset(seed=42)

        rewards = []
        for _ in range(20):
            obs, reward, terminated, truncated, info = env.step(env.action_space.sample())
            rewards.append(reward)
            if terminated or truncated:
                break

        # Dense rewards should be small and normalized
        rewards = np.array(rewards)
        non_goal_rewards = rewards[rewards != 100.0]  # Exclude goal reward
        if len(non_goal_rewards) > 0:
            assert np.abs(non_goal_rewards).max() < 1.0  # Should be normalized


class TestQLearningAgentOptimizations:
    """Test optimized Q-Learning agent features."""

    def test_learning_rate_decay(self):
        """Test learning rate decay."""
        agent = QLearningAgent(
            action_space_size=4,
            learning_rate=0.5,
            learning_rate_decay=0.01
        )

        initial_lr = agent.learning_rate

        # Decay epsilon multiple times
        for _ in range(100):
            agent.decay_epsilon()

        # Learning rate should have decayed
        assert agent.learning_rate < initial_lr

    def test_double_q_learning(self):
        """Test Double Q-Learning mode."""
        agent = QLearningAgent(
            action_space_size=4,
            use_double_q=True
        )

        # Should have two Q-tables
        assert hasattr(agent, 'q_table_2')

        # Update some Q-values
        state = np.array([0.5, 0.5])
        for _ in range(10):
            action = agent.select_action(state)
            next_state = np.array([0.6, 0.6])
            agent.update(state, action, 1.0, next_state, False)

        # Both Q-tables should have entries
        assert len(agent.q_table) > 0
        assert len(agent.q_table_2) > 0

    def test_boltzmann_exploration(self):
        """Test Boltzmann (softmax) exploration."""
        agent = QLearningAgent(
            action_space_size=4,
            exploration_strategy='boltzmann',
            temperature=1.0
        )

        state = np.array([0.5, 0.5])

        # Select actions multiple times
        actions = [agent.select_action(state) for _ in range(100)]

        # Should explore different actions
        unique_actions = set(actions)
        assert len(unique_actions) > 1

    def test_save_load_q_table(self):
        """Test Q-table save and load."""
        agent = QLearningAgent(action_space_size=4)

        # Train a bit
        state = np.array([0.5, 0.5])
        for _ in range(50):
            action = agent.select_action(state)
            next_state = np.array([0.6, 0.6])
            agent.update(state, action, 1.0, next_state, False)

        # Save Q-table
        with tempfile.TemporaryDirectory() as tmpdir:
            save_path = Path(tmpdir) / 'q_table.pkl'
            agent.save_q_table(str(save_path))

            # Create new agent and load
            new_agent = QLearningAgent(action_space_size=4)
            new_agent.load_q_table(str(save_path))

            # Should have same Q-table size
            assert len(new_agent.q_table) == len(agent.q_table)
            assert new_agent.total_steps == agent.total_steps

    def test_from_config(self):
        """Test agent creation from config."""
        config = {
            'agent': {
                'learning_rate': 0.2,
                'discount_factor': 0.95,
                'epsilon': 0.5,
                'use_double_q': True,
                'exploration_strategy': 'boltzmann'
            }
        }

        agent = QLearningAgent.from_config(config, action_space_size=4)

        assert agent.learning_rate == 0.2
        assert agent.discount_factor == 0.95
        assert agent.epsilon == 0.5
        assert agent.use_double_q == True
        assert agent.exploration_strategy == 'boltzmann'

    def test_convergence_tracking(self):
        """Test Q-value delta tracking."""
        agent = QLearningAgent(action_space_size=4)

        state = np.array([0.5, 0.5])
        for _ in range(50):
            action = agent.select_action(state)
            next_state = np.array([0.6, 0.6])
            agent.update(state, action, 1.0, next_state, False)

        # Should track Q-value deltas
        assert len(agent.q_value_deltas) == 50

        # Get statistics
        stats = agent.get_statistics()
        assert 'mean_q_delta' in stats
        assert 'std_q_delta' in stats
