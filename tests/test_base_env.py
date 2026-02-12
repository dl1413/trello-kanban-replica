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
        assert env.done is False
    
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
        obs = env.reset()
        
        assert env.observation_space.contains(obs)
        assert env.current_step == 0
        assert env.done is False
        assert env.state is not None
    
    def test_reset_after_episode(self):
        """Test that reset works after an episode."""
        env = BaseEnvironment({'episode_length': 5})
        env.reset()
        
        # Complete an episode
        for _ in range(5):
            env.step(0)
        
        assert env.done is True
        
        # Reset should work
        obs = env.reset()
        assert env.current_step == 0
        assert env.done is False
        assert env.observation_space.contains(obs)
    
    def test_step(self):
        """Test step functionality."""
        env = BaseEnvironment()
        env.reset()
        
        result = env.step(0)
        
        assert len(result) == 4
        obs, reward, done, info = result
        
        assert env.observation_space.contains(obs)
        assert isinstance(reward, (int, float))
        assert isinstance(done, bool)
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
        
        env.step(0)  # Should set done=True
        assert env.done is True
        
        with pytest.raises(RuntimeError):
            env.step(0)
    
    def test_episode_termination(self):
        """Test that episodes terminate at max length."""
        episode_length = 10
        env = BaseEnvironment({'episode_length': episode_length})
        env.reset()
        
        for i in range(episode_length - 1):
            _, _, done, _ = env.step(0)
            assert not done
        
        _, _, done, _ = env.step(0)
        assert done
    
    def test_info_dict(self):
        """Test that info dict contains expected keys."""
        env = BaseEnvironment()
        env.reset()
        
        _, _, _, info = env.step(0)
        
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
        obs = env.reset()
        
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
            obs = env.reset()
            assert env.observation_space.contains(obs)
            
            done = False
            steps = 0
            
            while not done and steps < 20:
                obs, reward, done, info = env.step(env.action_space.sample())
                steps += 1
            
            assert done


class TestBaseEnvironmentEdgeCases:
    """Test edge cases for BaseEnvironment."""
    
    def test_zero_episode_length(self):
        """Test with zero episode length."""
        env = BaseEnvironment({'episode_length': 0})
        env.reset()
        
        _, _, done, _ = env.step(0)
        assert done is True
    
    def test_very_long_episode(self):
        """Test with very long episode length."""
        env = BaseEnvironment({'episode_length': 10000})
        env.reset()
        
        # Should not be done after a few steps
        for _ in range(100):
            _, _, done, _ = env.step(0)
            assert not done
    
    def test_empty_config(self):
        """Test with empty configuration."""
        env = BaseEnvironment({})
        
        assert env.episode_length == 1000  # Default value
        
        obs = env.reset()
        assert env.observation_space.contains(obs)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
