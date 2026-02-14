"""
Tests for Base Environment
"""

import pytest
import numpy as np
from environments.base_env import BaseEnvironment


class TestBaseEnvironment:
    """Test suite for BaseEnvironment class."""
    
    def test_initialization(self):
        """Test that environment initializes correctly."""
        env = BaseEnvironment()
        
        assert env is not None
        assert env.action_space is not None
        assert env.observation_space is not None
        assert env.current_step == 0
        assert env.terminated is False
        assert env.truncated is False
    
    def test_initialization_with_config(self):
        """Test initialization with custom configuration."""
        config = {
            'episode_length': 500,
        }
        env = BaseEnvironment(config)
        
        assert env.episode_length == 500
        assert env.config == config
    
    def test_reset(self):
        """Test reset functionality."""
        env = BaseEnvironment()
        obs, info = env.reset()
        
        assert env.observation_space.contains(obs)
        assert env.current_step == 0
        assert env.terminated is False
        assert env.truncated is False
        assert env.state is not None
        assert isinstance(info, dict)
    
    def test_reset_after_episode(self):
        """Test that reset works after an episode."""
        env = BaseEnvironment({'episode_length': 5})
        env.reset()
        
        # Complete an episode
        for _ in range(5):
            env.step(0)
        
        assert env.truncated is True
        
        # Reset should work
        obs, info = env.reset()
        assert env.current_step == 0
        assert env.terminated is False
        assert env.truncated is False
        assert env.observation_space.contains(obs)
    
    def test_step(self):
        """Test step functionality."""
        env = BaseEnvironment()
        env.reset()
        
        result = env.step(0)
        
        assert len(result) == 5
        obs, reward, terminated, truncated, info = result
        
        assert env.observation_space.contains(obs)
        assert isinstance(reward, (int, float))
        assert isinstance(terminated, bool)
        assert isinstance(truncated, bool)
        assert isinstance(info, dict)
    
    def test_step_increments_counter(self):
        """Test that step increments the step counter."""
        env = BaseEnvironment()
        env.reset()
        
        assert env.current_step == 0
        
        env.step(0)
        assert env.current_step == 1
        
        env.step(0)
        assert env.current_step == 2
    
    def test_step_after_done_raises_error(self):
        """Test that stepping after done raises an error."""
        env = BaseEnvironment({'episode_length': 1})
        env.reset()
        
        env.step(0)  # Should set truncated=True
        assert env.truncated is True
        
        with pytest.raises(RuntimeError):
            env.step(0)
    
    def test_episode_termination(self):
        """Test that episodes terminate at max length."""
        episode_length = 10
        env = BaseEnvironment({'episode_length': episode_length})
        env.reset()
        
        for i in range(episode_length - 1):
            _, _, terminated, truncated, _ = env.step(0)
            assert not terminated
            assert not truncated
        
        _, _, terminated, truncated, _ = env.step(0)
        assert truncated  # Should be truncated at max length
        assert not terminated
    
    def test_info_dict(self):
        """Test that info dict contains expected keys."""
        env = BaseEnvironment()
        env.reset()
        
        _, _, _, _, info = env.step(0)
        
        assert 'step' in info
        assert 'episode_length' in info
        assert info['step'] == 1
    
    def test_action_space(self):
        """Test action space is valid."""
        env = BaseEnvironment()
        
        # Should be able to sample actions
        action = env.action_space.sample()
        assert env.action_space.contains(action)
    
    def test_observation_space(self):
        """Test observation space is valid."""
        env = BaseEnvironment()
        obs, info = env.reset()
        
        # Observation should be in observation space
        assert env.observation_space.contains(obs)
    
    def test_render(self):
        """Test that render doesn't crash."""
        env = BaseEnvironment()
        env.reset()
        
        # Should not raise an error
        env.render(mode='human')
        
        # RGB array mode should return array
        result = env.render(mode='rgb_array')
        assert isinstance(result, np.ndarray)
    
    def test_close(self):
        """Test that close doesn't crash."""
        env = BaseEnvironment()
        env.reset()
        
        # Should not raise an error
        env.close()
    
    def test_multiple_episodes(self):
        """Test running multiple episodes."""
        env = BaseEnvironment({'episode_length': 10})
        
        for episode in range(5):
            obs, info = env.reset()
            assert env.observation_space.contains(obs)
            
            terminated = False
            truncated = False
            steps = 0
            
            while not (terminated or truncated) and steps < 20:
                obs, reward, terminated, truncated, info = env.step(env.action_space.sample())
                steps += 1
            
            assert terminated or truncated


class TestBaseEnvironmentEdgeCases:
    """Test edge cases for BaseEnvironment."""
    
    def test_zero_episode_length(self):
        """Test with zero episode length."""
        env = BaseEnvironment({'episode_length': 0})
        env.reset()
        
        _, _, terminated, truncated, _ = env.step(0)
        assert truncated is True
    
    def test_very_long_episode(self):
        """Test with very long episode length."""
        env = BaseEnvironment({'episode_length': 10000})
        env.reset()
        
        # Should not be done after a few steps
        for _ in range(100):
            _, _, terminated, truncated, _ = env.step(0)
            assert not terminated
            assert not truncated
    
    def test_empty_config(self):
        """Test with empty configuration."""
        env = BaseEnvironment({})
        
        assert env.episode_length == 1000  # Default value
        
        obs, info = env.reset()
        assert env.observation_space.contains(obs)
    
    def test_action_validation(self):
        """Test that invalid actions raise ValueError."""
        env = BaseEnvironment()
        env.reset()
        
        # Invalid action should raise ValueError
        with pytest.raises(ValueError):
            env.step(999)  # Out of bounds for Discrete(4)
    
    def test_seeding(self):
        """Test that seeding produces reproducible results."""
        env1 = BaseEnvironment()
        env2 = BaseEnvironment()
        
        obs1, _ = env1.reset(seed=42)
        obs2, _ = env2.reset(seed=42)
        
        # Should produce same initial state
        np.testing.assert_array_equal(obs1, obs2)
    
    def test_nested_config_loading(self):
        """Test loading nested YAML config."""
        config = {
            'environment': {
                'episode_length': 500,
                'reward': {
                    'scale': 2.0,
                    'clip': True,
                    'clip_range': [-5, 5]
                }
            }
        }
        env = BaseEnvironment(config)
        
        assert env.episode_length == 500
        assert env.reward_scale == 2.0
        assert env.reward_clip_range == [-5, 5]
    
    def test_reward_scaling(self):
        """Test that rewards are scaled correctly."""
        config = {
            'environment': {
                'reward': {
                    'scale': 2.0,
                    'clip': False
                }
            }
        }
        env = BaseEnvironment(config)
        env.reset()
        
        # Since base _calculate_reward returns 0.0, we can't test much
        # but we verify the config is loaded
        assert env.reward_scale == 2.0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
