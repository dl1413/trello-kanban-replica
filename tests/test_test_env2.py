"""
Tests for test_env2 Environment
"""

import pytest
import numpy as np
from environments.test_env2 import TestEnv2


class TestTestEnv2:
    """Test suite for TestEnv2."""
    
    def test_initialization(self):
        """Test that environment initializes correctly."""
        env = TestEnv2()
        
        assert env is not None
        assert env.action_space is not None
        assert env.observation_space is not None
    
    def test_reset(self):
        """Test reset functionality."""
        env = TestEnv2()
        obs = env.reset()
        
        assert env.observation_space.contains(obs)
        assert env.current_step == 0
    
    def test_step(self):
        """Test step functionality."""
        env = TestEnv2()
        env.reset()
        
        obs, reward, done, info = env.step(0)
        
        assert env.observation_space.contains(obs)
        assert isinstance(reward, (int, float))
        assert isinstance(done, bool)
        assert isinstance(info, dict)
    
    def test_episode_completion(self):
        """Test running a complete episode."""
        env = TestEnv2()
        obs = env.reset()
        
        done = False
        steps = 0
        
        while not done and steps < 1000:
            action = env.action_space.sample()
            obs, reward, done, info = env.step(action)
            steps += 1
        
        assert steps > 0
    
    # TODO: Add more tests specific to your environment


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
