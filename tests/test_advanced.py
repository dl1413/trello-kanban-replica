"""
Advanced Tests for RL Environment Framework

This module contains comprehensive tests for:
- Deterministic seeding
- Boundary conditions
- Reward type verification
- Performance benchmarks
- Config validation
- Q-Learning convergence
"""

import pytest
import numpy as np
import time
from environments.base_env import BaseEnvironment
from examples.simple_gridworld import SimpleGridWorld
from examples.q_learning_agent import QLearningAgent


class TestDeterministicSeeding:
    """Test that seeding produces reproducible results."""
    
    def test_identical_seeds_produce_identical_trajectories(self):
        """Test that same seed produces identical episode trajectories."""
        seed = 42
        num_steps = 20
        
        # Create two environments with same seed
        env1 = SimpleGridWorld({'grid_size': 5, 'episode_length': 100})
        env2 = SimpleGridWorld({'grid_size': 5, 'episode_length': 100})
        
        obs1, _ = env1.reset(seed=seed)
        obs2, _ = env2.reset(seed=seed)
        
        # Initial observations should be identical
        np.testing.assert_array_almost_equal(obs1, obs2)
        
        # Take same actions and verify identical trajectories
        for _ in range(num_steps):
            action = env1.action_space.sample()
            
            obs1, reward1, term1, trunc1, info1 = env1.step(action)
            obs2, reward2, term2, trunc2, info2 = env2.step(action)
            
            np.testing.assert_array_almost_equal(obs1, obs2)
            assert reward1 == reward2
            assert term1 == term2
            assert trunc1 == trunc2
            
            if term1 or trunc1:
                break
    
    def test_different_seeds_produce_different_trajectories(self):
        """Test that different seeds produce different trajectories."""
        env1 = SimpleGridWorld({'grid_size': 10, 'episode_length': 100})
        env2 = SimpleGridWorld({'grid_size': 10, 'episode_length': 100})
        
        obs1, _ = env1.reset(seed=42)
        obs2, _ = env2.reset(seed=123)
        
        # Different seeds should produce different initial states
        # (with high probability for reasonable grid sizes)
        # Check if they're different (allow for small chance they could be same)
        same_count = 0
        for _ in range(10):
            o1, _ = env1.reset(seed=42)
            o2, _ = env2.reset(seed=123)
            if np.array_equal(o1, o2):
                same_count += 1
        
        # Should be different most of the time
        assert same_count < 8
    
    def test_seed_affects_random_actions(self):
        """Test that seed affects environment's random number generator."""
        env1 = SimpleGridWorld({'grid_size': 10, 'episode_length': 100})
        env2 = SimpleGridWorld({'grid_size': 10, 'episode_length': 100})
        
        # Reset with same seed
        obs1, _ = env1.reset(seed=42)
        obs2, _ = env2.reset(seed=42)
        
        # Should get same initial observation
        np.testing.assert_array_almost_equal(obs1, obs2)


class TestBoundaryConditions:
    """Test environment with extreme configurations."""
    
    def test_minimal_grid_size(self):
        """Test with 2x2 grid (small but functional)."""
        env = SimpleGridWorld({'grid_size': 2, 'episode_length': 20})
        obs, info = env.reset(seed=42)
        
        assert env.observation_space.contains(obs)
        
        # Take some steps
        for _ in range(10):
            action = env.action_space.sample()
            obs, reward, terminated, truncated, info = env.step(action)
            if terminated or truncated:
                break
    
    def test_large_grid_size(self):
        """Test with large grid (100x100)."""
        env = SimpleGridWorld({'grid_size': 100, 'episode_length': 1000})
        obs, info = env.reset(seed=42)
        
        assert env.observation_space.contains(obs)
        assert obs.shape == (2,)
        
        # Should be able to take steps without error
        for _ in range(10):
            action = env.action_space.sample()
            obs, reward, term, trunc, info = env.step(action)
            assert env.observation_space.contains(obs)
            if term or trunc:
                break
    
    def test_zero_episode_length_edge_case(self):
        """Test with zero episode length."""
        env = SimpleGridWorld({'grid_size': 5, 'episode_length': 0})
        obs, info = env.reset()
        
        # First step should immediately truncate
        _, _, terminated, truncated, _ = env.step(0)
        assert truncated
    
    def test_many_obstacles(self):
        """Test with many obstacles filling most of the grid."""
        env = SimpleGridWorld({
            'grid_size': 5,
            'episode_length': 100,
            'num_obstacles': 20  # Many obstacles for 5x5 grid
        })
        obs, info = env.reset(seed=42)
        
        # Should still initialize without error
        assert env.observation_space.contains(obs)
        # Agent should still be able to move
        obs, reward, term, trunc, info = env.step(0)
        assert env.observation_space.contains(obs)


class TestRewardTypes:
    """Test different reward configurations."""
    
    def test_sparse_rewards_only_at_goal(self):
        """Verify sparse rewards are zero except at goal."""
        env = SimpleGridWorld({
            'grid_size': 5,
            'episode_length': 100,
            'reward_type': 'sparse'
        })
        obs, info = env.reset(seed=42)
        
        # Take steps and verify rewards
        rewards = []
        for _ in range(20):
            action = env.action_space.sample()
            obs, reward, term, trunc, info = env.step(action)
            rewards.append(reward)
            
            if term:
                # Terminal reward should be positive
                assert reward == 100.0
                break
            else:
                # Non-terminal rewards should be small negative
                assert reward == -1.0
    
    def test_dense_rewards_provide_shaping(self):
        """Verify dense rewards provide non-zero intermediate signals."""
        env = SimpleGridWorld({
            'grid_size': 10,
            'episode_length': 100,
            'reward_type': 'dense'
        })
        obs, info = env.reset(seed=42)
        
        # Take steps and collect rewards
        non_terminal_rewards = []
        for _ in range(50):
            action = env.action_space.sample()
            obs, reward, term, trunc, info = env.step(action)
            
            if not term:
                non_terminal_rewards.append(reward)
            
            if term or trunc:
                break
        
        # Dense rewards should have some variation (not all the same)
        if len(non_terminal_rewards) > 5:
            reward_std = np.std(non_terminal_rewards)
            assert reward_std > 0, "Dense rewards should vary"
    
    def test_reward_clipping(self):
        """Test that reward clipping works correctly."""
        config = {
            'environment': {
                'reward': {
                    'scale': 10.0,  # Scale up rewards
                    'clip': True,
                    'clip_range': [-5, 5]
                }
            },
            'grid_size': 5,
            'episode_length': 100
        }
        
        # Create custom env that returns large rewards
        class TestEnv(SimpleGridWorld):
            def _calculate_reward(self, action):
                return 100.0  # Large reward
        
        env = TestEnv(config)
        env.reset(seed=42)
        _, reward, _, _, _ = env.step(0)
        
        # Reward should be clipped to max of 5
        assert reward == 5.0


class TestPerformanceBenchmark:
    """Performance regression tests."""
    
    def test_step_throughput(self):
        """Test that environment can process steps quickly enough."""
        env = SimpleGridWorld({'grid_size': 10, 'episode_length': 10000})
        env.reset(seed=42)
        
        num_steps = 10000
        start_time = time.time()
        
        for _ in range(num_steps):
            action = env.action_space.sample()
            _, _, term, trunc, _ = env.step(action)
            
            if term or trunc:
                env.reset()
        
        elapsed = time.time() - start_time
        steps_per_sec = num_steps / elapsed
        
        # Should achieve at least 10k steps/sec
        assert steps_per_sec > 10000, f"Only achieved {steps_per_sec:.0f} steps/sec"
    
    def test_reset_performance(self):
        """Test that reset is fast enough."""
        env = SimpleGridWorld({'grid_size': 10, 'episode_length': 100})
        
        num_resets = 1000
        start_time = time.time()
        
        for i in range(num_resets):
            env.reset(seed=i)
        
        elapsed = time.time() - start_time
        resets_per_sec = num_resets / elapsed
        
        # Should achieve at least 1k resets/sec
        assert resets_per_sec > 1000, f"Only achieved {resets_per_sec:.0f} resets/sec"


class TestConfigValidation:
    """Test configuration validation."""
    
    def test_invalid_episode_length_raises_error(self):
        """Test that negative episode length raises error."""
        with pytest.raises(ValueError, match="episode_length must be non-negative"):
            env = BaseEnvironment({'episode_length': -1})
    
    def test_invalid_reward_scale_raises_error(self):
        """Test that non-numeric reward scale raises error."""
        with pytest.raises(ValueError, match="reward scale must be numeric"):
            config = {
                'environment': {
                    'reward': {
                        'scale': 'invalid'
                    }
                }
            }
            env = BaseEnvironment(config)
    
    def test_invalid_clip_range_raises_error(self):
        """Test that invalid clip range raises error."""
        with pytest.raises(ValueError, match="reward_clip_range must be a list"):
            config = {
                'environment': {
                    'reward': {
                        'clip': True,
                        'clip_range': 'invalid'
                    }
                }
            }
            env = BaseEnvironment(config)
    
    def test_inverted_clip_range_raises_error(self):
        """Test that inverted clip range (min > max) raises error."""
        with pytest.raises(ValueError, match="must be <"):
            config = {
                'environment': {
                    'reward': {
                        'clip': True,
                        'clip_range': [10, -10]  # Inverted
                    }
                }
            }
            env = BaseEnvironment(config)


class TestQLearningConvergence:
    """Integration test for Q-Learning agent."""
    
    def test_q_learning_converges_on_small_grid(self):
        """Test that Q-Learning agent improves on small grid."""
        # Create simple environment
        env = SimpleGridWorld({
            'grid_size': 5,
            'episode_length': 50,
            'reward_type': 'sparse'
        })
        
        # Create Q-Learning agent
        agent = QLearningAgent(
            action_space_size=env.action_space.n,
            learning_rate=0.1,
            discount_factor=0.95,
            epsilon=1.0,
            epsilon_decay=0.99,
            epsilon_min=0.1
        )
        
        # Train for limited episodes
        num_episodes = 100
        success_count = 0
        
        for episode in range(num_episodes):
            obs, info = env.reset(seed=episode)
            steps = 0
            
            terminated = False
            truncated = False
            
            while not (terminated or truncated) and steps < 50:
                action = agent.select_action(obs, training=True)
                next_obs, reward, terminated, truncated, info = env.step(action)
                agent.update(obs, action, reward, next_obs, terminated)
                obs = next_obs
                steps += 1
            
            agent.decay_epsilon()
            
            # Count successes in last 20 episodes
            if episode >= 80 and info.get('goal_reached', False):
                success_count += 1
        
        # After 100 episodes, should achieve some success
        success_rate = success_count / 20
        assert success_rate > 0.1, f"Q-Learning only achieved {success_rate:.1%} success rate"
    
    def test_q_table_save_load(self):
        """Test that Q-table can be saved and loaded."""
        import tempfile
        import os
        
        agent = QLearningAgent(action_space_size=4, learning_rate=0.1)
        
        # Add some Q-values
        agent.q_table[(0, 0)] = np.array([1.0, 2.0, 3.0, 4.0])
        agent.q_table[(1, 1)] = np.array([5.0, 6.0, 7.0, 8.0])
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.pkl') as f:
            temp_path = f.name
        
        try:
            agent.save_q_table(temp_path, format='pickle')
            
            # Create new agent and load
            agent2 = QLearningAgent(action_space_size=4)
            agent2.load_q_table(temp_path, format='pickle')
            
            # Verify Q-values match
            np.testing.assert_array_equal(
                agent.q_table[(0, 0)],
                agent2.q_table[(0, 0)]
            )
            np.testing.assert_array_equal(
                agent.q_table[(1, 1)],
                agent2.q_table[(1, 1)]
            )
        finally:
            # Clean up
            if os.path.exists(temp_path):
                os.remove(temp_path)


class TestInfoDict:
    """Test info dictionary contents."""
    
    def test_info_contains_episode_return_on_done(self):
        """Test that info dict contains episode_return when done."""
        env = SimpleGridWorld({'grid_size': 3, 'episode_length': 10})
        obs, info = env.reset(seed=42)
        
        total_reward = 0
        for _ in range(20):
            action = env.action_space.sample()
            obs, reward, term, trunc, info = env.step(action)
            total_reward += reward
            
            if term or trunc:
                assert 'episode_return' in info
                assert abs(info['episode_return'] - total_reward) < 0.01
                break
    
    def test_info_contains_is_success_on_done(self):
        """Test that info dict contains is_success flag when done."""
        env = SimpleGridWorld({'grid_size': 3, 'episode_length': 10})
        obs, info = env.reset(seed=42)
        
        for _ in range(20):
            action = env.action_space.sample()
            obs, reward, term, trunc, info = env.step(action)
            
            if term or trunc:
                assert 'is_success' in info
                assert isinstance(info['is_success'], bool)
                # is_success should be True if terminated (not truncated)
                assert info['is_success'] == term
                break


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
