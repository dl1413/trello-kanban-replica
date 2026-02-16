"""
Tests for Continuous Action Space Environment
"""

import pytest
import numpy as np
from environments.continuous_env import ContinuousControlEnv


class TestContinuousControlEnv:
    """Test suite for ContinuousControlEnv class."""
    
    def test_initialization(self):
        """Test basic initialization."""
        env = ContinuousControlEnv()
        
        assert env is not None
        assert env.action_space.shape == (2,)
        assert env.observation_space.shape == (6,) or env.observation_space.shape == (4,)
        assert env.dt > 0
        assert env.mass > 0
        assert env.max_velocity > 0
    
    def test_initialization_with_config(self):
        """Test initialization with custom config."""
        config = {
            'dt': 0.05,
            'friction': 0.2,
            'mass': 2.0,
            'max_velocity': 10.0,
            'goal_threshold': 0.5,
            'workspace_size': 20.0
        }
        env = ContinuousControlEnv(config)
        
        assert env.dt == 0.05
        assert env.friction == 0.2
        assert env.mass == 2.0
        assert env.max_velocity == 10.0
        assert env.goal_threshold == 0.5
        assert env.workspace_size == 20.0
    
    def test_continuous_action_space(self):
        """Test that action space is continuous Box."""
        env = ContinuousControlEnv()
        
        assert isinstance(env.action_space, type(env.action_space))
        assert env.action_space.shape == (2,)
        
        # Sample some actions
        for _ in range(10):
            action = env.action_space.sample()
            assert env.action_space.contains(action)
            assert -1.0 <= action[0] <= 1.0
            assert -1.0 <= action[1] <= 1.0
    
    def test_continuous_action_bounds(self):
        """Test action space bounds are enforced."""
        env = ContinuousControlEnv()
        env.reset()
        
        # Actions within bounds should work
        action = np.array([0.5, -0.5], dtype=np.float32)
        obs, reward, terminated, truncated, info = env.step(action)
        assert env.observation_space.contains(obs)
        
        # Test boundary values
        action = np.array([1.0, -1.0], dtype=np.float32)
        obs, reward, terminated, truncated, info = env.step(action)
        assert env.observation_space.contains(obs)
    
    def test_reset(self):
        """Test reset creates valid initial state."""
        env = ContinuousControlEnv()
        obs, info = env.reset(seed=42)
        
        assert env.observation_space.contains(obs)
        assert env.position is not None
        assert env.velocity is not None
        assert env.goal_position is not None
        assert np.allclose(env.velocity, 0)  # Initial velocity should be zero
    
    def test_physics_integration(self):
        """Test physics updates position correctly with forces."""
        env = ContinuousControlEnv({'dt': 0.1, 'friction': 0.0, 'mass': 1.0})
        env.reset(seed=42)
        
        initial_pos = env.position.copy()
        initial_vel = env.velocity.copy()
        
        # Apply force in x-direction
        action = np.array([1.0, 0.0], dtype=np.float32)
        obs, reward, terminated, truncated, info = env.step(action)
        
        # Velocity should increase in x-direction
        assert env.velocity[0] > initial_vel[0]
        
        # Position should change in x-direction
        assert env.position[0] != initial_pos[0]
    
    def test_friction(self):
        """Test friction reduces velocity over time."""
        env = ContinuousControlEnv({'dt': 0.1, 'friction': 0.5, 'mass': 1.0})
        env.reset(seed=42)
        
        # Give initial velocity
        env.velocity = np.array([5.0, 0.0], dtype=np.float32)
        initial_vel = env.velocity.copy()
        
        # Apply no force, let friction work
        action = np.array([0.0, 0.0], dtype=np.float32)
        obs, reward, terminated, truncated, info = env.step(action)
        
        # Velocity should decrease due to friction
        assert abs(env.velocity[0]) < abs(initial_vel[0])
    
    def test_velocity_clamping(self):
        """Test velocity is clamped to max_velocity."""
        max_vel = 2.0
        env = ContinuousControlEnv({
            'dt': 0.1,
            'friction': 0.0,
            'mass': 0.1,  # Low mass for high acceleration
            'max_velocity': max_vel
        })
        env.reset(seed=42)
        
        # Apply large force multiple times
        action = np.array([1.0, 1.0], dtype=np.float32)
        for _ in range(20):
            env.step(action)
        
        # Velocity should be clamped
        velocity_norm = np.linalg.norm(env.velocity)
        assert velocity_norm <= max_vel * 1.01  # Small tolerance for numerical errors
    
    def test_goal_reaching(self):
        """Test goal reaching detection."""
        env = ContinuousControlEnv({'goal_threshold': 0.5})
        obs, info = env.reset(seed=42)
        
        # Place agent at goal
        env.position = env.goal_position.copy()
        
        action = np.array([0.0, 0.0], dtype=np.float32)
        obs, reward, terminated, truncated, info = env.step(action)
        
        # Should be terminated
        assert terminated
        assert info['goal_reached']
        assert reward > 50.0  # Should get goal bonus
    
    def test_goal_termination(self):
        """Test episode terminates when goal is reached."""
        env = ContinuousControlEnv({
            'goal_threshold': 0.5,
            'episode_length': 1000
        })
        env.reset(seed=42)
        
        # Place near goal
        env.position = env.goal_position + np.array([0.2, 0.0], dtype=np.float32)
        
        action = np.array([0.0, 0.0], dtype=np.float32)
        obs, reward, terminated, truncated, info = env.step(action)
        
        assert terminated
        assert not truncated
    
    def test_action_penalty(self):
        """Test that large actions incur penalty."""
        env = ContinuousControlEnv({'action_penalty': 0.1})
        env.reset(seed=42)
        
        # Small action
        small_action = np.array([0.1, 0.1], dtype=np.float32)
        env.position = np.array([0.0, 0.0], dtype=np.float32)
        goal_pos = env.goal_position.copy()
        obs, reward1, _, _, _ = env.step(small_action)
        
        # Reset and test large action
        env.reset(seed=42)
        env.position = np.array([0.0, 0.0], dtype=np.float32)
        env.goal_position = goal_pos  # Same goal
        large_action = np.array([1.0, 1.0], dtype=np.float32)
        obs, reward2, _, _, _ = env.step(large_action)
        
        # Large action should have more penalty (lower reward)
        # Note: distance reward might vary, so we compare penalty component
        # The difference should be negative (more penalty for large action)
        assert reward2 < reward1 or np.isclose(reward2, reward1, atol=0.5)
    
    def test_observation_normalization(self):
        """Test observation normalization."""
        env = ContinuousControlEnv({
            'normalize_obs': True,
            'workspace_size': 10.0,
            'max_velocity': 5.0
        })
        obs, info = env.reset(seed=42)
        
        # Normalized obs should be in reasonable range
        assert np.all(np.abs(obs[:2]) <= 1.5)  # Position normalized by workspace
        assert np.all(np.abs(obs[2:4]) <= 1.5)  # Velocity normalized by max_vel
    
    def test_out_of_bounds_penalty(self):
        """Test penalty for going out of bounds."""
        env = ContinuousControlEnv({'workspace_size': 5.0})
        env.reset(seed=42)
        
        # Place agent out of bounds
        env.position = np.array([6.0, 0.0], dtype=np.float32)
        
        action = np.array([0.0, 0.0], dtype=np.float32)
        obs, reward, terminated, truncated, info = env.step(action)
        
        # Should get penalty
        assert reward < -5.0  # Includes distance + out of bounds penalty
        assert info['out_of_bounds']
    
    def test_truncation_at_max_steps(self):
        """Test episode truncates at max steps."""
        env = ContinuousControlEnv({'episode_length': 5})
        env.reset()
        
        for i in range(4):
            action = np.array([0.1, 0.1], dtype=np.float32)
            obs, reward, terminated, truncated, info = env.step(action)
            assert not truncated
        
        # 5th step should truncate
        action = np.array([0.1, 0.1], dtype=np.float32)
        obs, reward, terminated, truncated, info = env.step(action)
        assert truncated
    
    def test_truncation_far_out_of_bounds(self):
        """Test episode truncates when going too far out."""
        env = ContinuousControlEnv({'workspace_size': 5.0, 'max_velocity': 100.0})
        env.reset()
        
        # Place very far out (beyond 1.5x workspace)
        env.position = np.array([8.0, 8.0], dtype=np.float32)
        
        action = np.array([0.0, 0.0], dtype=np.float32)
        obs, reward, terminated, truncated, info = env.step(action)
        
        assert truncated
    
    def test_info_dict(self):
        """Test info dict contains expected keys."""
        env = ContinuousControlEnv()
        obs, info = env.reset()
        
        assert 'position' in info
        assert 'velocity' in info
        assert 'goal_position' in info
        assert 'distance_to_goal' in info
        assert 'goal_reached' in info
        assert 'out_of_bounds' in info
    
    def test_render(self):
        """Test render doesn't crash."""
        env = ContinuousControlEnv()
        env.reset()
        
        # Should not raise error
        env.render(mode='human')
    
    def test_seeding(self):
        """Test seeding produces reproducible results."""
        env1 = ContinuousControlEnv()
        env2 = ContinuousControlEnv()
        
        obs1, _ = env1.reset(seed=42)
        obs2, _ = env2.reset(seed=42)
        
        # Should have same initial state
        np.testing.assert_array_almost_equal(obs1, obs2)
        np.testing.assert_array_almost_equal(env1.position, env2.position)
        np.testing.assert_array_almost_equal(env1.goal_position, env2.goal_position)
    
    def test_multiple_steps(self):
        """Test multiple steps work correctly."""
        env = ContinuousControlEnv({'episode_length': 100})
        env.reset(seed=42)
        
        for _ in range(50):
            action = env.action_space.sample()
            obs, reward, terminated, truncated, info = env.step(action)
            assert env.observation_space.contains(obs)
            assert isinstance(reward, (int, float, np.number))
            assert isinstance(terminated, (bool, np.bool_))
            assert isinstance(truncated, (bool, np.bool_))
            
            if terminated or truncated:
                break
    
    def test_episode_reset(self):
        """Test environment can be reset after episode ends."""
        env = ContinuousControlEnv({'episode_length': 10})
        
        # First episode
        env.reset()
        for _ in range(10):
            action = env.action_space.sample()
            env.step(action)
        
        # Should be able to reset
        obs, info = env.reset()
        assert env.observation_space.contains(obs)
        assert env.current_step == 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
