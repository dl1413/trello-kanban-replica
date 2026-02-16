"""
Tests for Multi-Agent Environment
"""

import pytest
import numpy as np
from environments.multi_agent_env import MultiAgentBaseEnvironment, MultiAgentGridWorld


class TestMultiAgentBaseEnvironment:
    """Test suite for MultiAgentBaseEnvironment class."""
    
    def test_initialization_default(self):
        """Test default initialization with 2 agents."""
        env = MultiAgentBaseEnvironment()
        
        assert env is not None
        assert env.num_agents == 2
        assert len(env.action_spaces) == 2
        assert len(env.observation_spaces) == 2
        assert env.reward_mode == 'cooperative'
        assert env.collision_mode == 'block'
    
    def test_initialization_with_config(self):
        """Test initialization with custom agent count."""
        config = {
            'num_agents': 4,
            'reward_mode': 'competitive',
            'collision_mode': 'pass-through'
        }
        env = MultiAgentBaseEnvironment(config)
        
        assert env.num_agents == 4
        assert len(env.action_spaces) == 4
        assert len(env.observation_spaces) == 4
        assert env.reward_mode == 'competitive'
        assert env.collision_mode == 'pass-through'
    
    def test_reset(self):
        """Test reset returns observations for all agents."""
        env = MultiAgentBaseEnvironment({'num_agents': 3})
        obs_dict, info_dict = env.reset()
        
        assert isinstance(obs_dict, dict)
        assert isinstance(info_dict, dict)
        assert len(obs_dict) == 3
        assert len(info_dict) == 3
        
        for i in range(3):
            assert i in obs_dict
            assert i in info_dict
            assert env.observation_spaces[i].contains(obs_dict[i])
    
    def test_step(self):
        """Test step with actions for all agents."""
        env = MultiAgentBaseEnvironment({'num_agents': 2})
        env.reset()
        
        actions = {0: 0, 1: 1}
        result = env.step(actions)
        
        assert len(result) == 5
        obs, rewards, terminated, truncated, info = result
        
        assert len(obs) == 2
        assert len(rewards) == 2
        assert len(terminated) == 2
        assert len(truncated) == 2
        assert len(info) == 2
    
    def test_step_increments_counter(self):
        """Test that step increments counter."""
        env = MultiAgentBaseEnvironment({'num_agents': 2})
        env.reset()
        
        assert env.current_step == 0
        env.step({0: 0, 1: 0})
        assert env.current_step == 1
    
    def test_invalid_action_raises_error(self):
        """Test that invalid action raises ValueError."""
        env = MultiAgentBaseEnvironment({'num_agents': 2})
        env.reset()
        
        with pytest.raises(ValueError):
            env.step({0: 999, 1: 0})
    
    def test_step_after_done_raises_error(self):
        """Test stepping after done raises error."""
        env = MultiAgentBaseEnvironment({'num_agents': 2, 'episode_length': 1})
        env.reset()
        
        env.step({0: 0, 1: 0})
        assert env.truncated or env.terminated
        
        with pytest.raises(RuntimeError):
            env.step({0: 0, 1: 0})


class TestMultiAgentGridWorld:
    """Test suite for MultiAgentGridWorld."""
    
    def test_initialization(self):
        """Test grid world initialization."""
        config = {
            'num_agents': 2,
            'grid_size': 5,
            'reward_mode': 'cooperative'
        }
        env = MultiAgentGridWorld(config)
        
        assert env.num_agents == 2
        assert env.grid_size == 5
        assert env.reward_mode == 'cooperative'
    
    def test_reset_creates_positions(self):
        """Test that reset creates valid positions."""
        env = MultiAgentGridWorld({'num_agents': 3, 'grid_size': 10})
        obs, info = env.reset(seed=42)
        
        # Check all agents have positions
        assert len(env.agent_positions) == 3
        assert len(env.goal_positions) == 3
        
        # Check positions are within bounds
        for i in range(3):
            assert 0 <= env.agent_positions[i][0] < 10
            assert 0 <= env.agent_positions[i][1] < 10
            assert 0 <= env.goal_positions[i][0] < 10
            assert 0 <= env.goal_positions[i][1] < 10
    
    def test_cooperative_mode_goals(self):
        """Test cooperative mode creates separate goals."""
        env = MultiAgentGridWorld({
            'num_agents': 2,
            'grid_size': 10,
            'reward_mode': 'cooperative'
        })
        obs, info = env.reset(seed=42)
        
        # Each agent should have different goal
        assert not np.array_equal(env.goal_positions[0], env.goal_positions[1])
    
    def test_competitive_mode_goals(self):
        """Test competitive mode creates shared goal."""
        env = MultiAgentGridWorld({
            'num_agents': 2,
            'grid_size': 10,
            'reward_mode': 'competitive'
        })
        obs, info = env.reset(seed=42)
        
        # All agents should have same goal
        assert np.array_equal(env.goal_positions[0], env.goal_positions[1])
    
    def test_movement(self):
        """Test agent movement."""
        env = MultiAgentGridWorld({'num_agents': 1, 'grid_size': 5})
        obs, info = env.reset(seed=42)
        
        initial_pos = env.agent_positions[0].copy()
        
        # Move up (action 0)
        obs, rewards, terminated, truncated, info = env.step({0: 0})
        
        # Position should change (or stay at boundary)
        assert env.agent_positions[0][0] <= initial_pos[0]  # row decreased or same
    
    def test_collision_block_mode(self):
        """Test collision blocking."""
        env = MultiAgentGridWorld({
            'num_agents': 2,
            'grid_size': 5,
            'collision_mode': 'block'
        })
        
        # Manually set positions for predictable collision
        obs, info = env.reset(seed=42)
        env.agent_positions[0] = np.array([2, 2], dtype=np.int32)
        env.agent_positions[1] = np.array([3, 2], dtype=np.int32)
        
        # Agent 1 tries to move up to where Agent 0 is
        obs, rewards, terminated, truncated, info = env.step({0: 2, 1: 0})  # 0 moves down, 1 moves up
        
        # Agents should not overlap (one should be blocked)
        assert not np.array_equal(env.agent_positions[0], env.agent_positions[1])
    
    def test_collision_pass_through_mode(self):
        """Test pass-through collision mode."""
        env = MultiAgentGridWorld({
            'num_agents': 2,
            'grid_size': 5,
            'collision_mode': 'pass-through'
        })
        obs, info = env.reset(seed=42)
        
        # Set adjacent positions
        env.agent_positions[0] = np.array([2, 2], dtype=np.int32)
        env.agent_positions[1] = np.array([3, 2], dtype=np.int32)
        
        # Both try to move to same position
        obs, rewards, terminated, truncated, info = env.step({0: 2, 1: 0})
        
        # Agents can be at same position
        # We just verify no error is raised
        assert len(env.agent_positions) == 2
    
    def test_collision_penalty_mode(self):
        """Test penalty collision mode."""
        env = MultiAgentGridWorld({
            'num_agents': 2,
            'grid_size': 5,
            'collision_mode': 'penalty'
        })
        obs, info = env.reset(seed=42)
        
        # Manually set to same position to trigger penalty
        env.agent_positions[0] = np.array([2, 2], dtype=np.int32)
        env.agent_positions[1] = np.array([2, 2], dtype=np.int32)
        env.goal_positions[0] = np.array([4, 4], dtype=np.int32)
        env.goal_positions[1] = np.array([4, 3], dtype=np.int32)
        
        # Take step (both at same pos, should get penalty)
        obs, rewards, terminated, truncated, info = env.step({0: 0, 1: 0})
        
        # Both should get collision penalty
        assert rewards[0] < -1.0  # More negative than just step penalty
        assert rewards[1] < -1.0
    
    def test_goal_reaching_reward(self):
        """Test reaching goal gives reward."""
        env = MultiAgentGridWorld({
            'num_agents': 1,
            'grid_size': 5,
            'reward_mode': 'cooperative'
        })
        obs, info = env.reset(seed=42)
        
        # Place agent next to goal and move to it
        goal = env.goal_positions[0].copy()
        env.agent_positions[0] = goal + np.array([1, 0], dtype=np.int32)  # One step away
        
        # Move up to reach goal (action 0 = up)
        obs, rewards, terminated, truncated, info = env.step({0: 0})
        
        # Should get large reward for reaching goal
        assert rewards[0] >= 100.0
        assert terminated[0]
    
    def test_cooperative_termination(self):
        """Test cooperative mode terminates when all agents reach goals."""
        env = MultiAgentGridWorld({
            'num_agents': 2,
            'grid_size': 10,
            'reward_mode': 'cooperative',
            'episode_length': 100
        })
        obs, info = env.reset(seed=42)
        
        # Manually set positions for predictable test - both agents one step from their goals
        env.agent_positions[0] = np.array([2, 2], dtype=np.int32)
        env.agent_positions[1] = np.array([4, 4], dtype=np.int32)
        env.goal_positions[0] = np.array([2, 3], dtype=np.int32)  # Right of agent 0
        env.goal_positions[1] = np.array([4, 5], dtype=np.int32)  # Right of agent 1
        
        # Only agent 0 reaches goal
        obs, rewards, terminated, truncated, info = env.step({0: 1, 1: 0})  # 0 moves right to goal, 1 moves up (away)
        
        # Episode should not terminate (need all agents in cooperative)
        assert not env.terminated
        assert terminated[0] == True  # Agent 0 at goal
        assert terminated[1] == False  # Agent 1 not at goal
        
        # Both agents move to goals simultaneously
        env.agent_positions[0] = np.array([2, 2], dtype=np.int32)  # Reset agent 0
        env.agent_positions[1] = np.array([4, 4], dtype=np.int32)  # Reset agent 1
        
        obs, rewards, terminated, truncated, info = env.step({0: 1, 1: 1})  # Both move right to goals
        
        # Episode should terminate (all agents at goal)
        # In cooperative mode, env.terminated is True when all agents terminate
        assert env.terminated
    
    def test_competitive_termination(self):
        """Test competitive mode terminates when any agent reaches goal."""
        env = MultiAgentGridWorld({
            'num_agents': 2,
            'grid_size': 5,
            'reward_mode': 'competitive',
            'episode_length': 100
        })
        obs, info = env.reset(seed=42)
        
        # Place one agent next to goal
        goal = env.goal_positions[0].copy()  # Shared goal in competitive
        env.agent_positions[0] = goal + np.array([1, 0], dtype=np.int32)
        
        # Agent 0 reaches goal
        obs, rewards, terminated, truncated, info = env.step({0: 0, 1: 0})
        
        # Episode should terminate (competitive)
        assert env.terminated or terminated[0]
        assert rewards[0] >= 100.0  # Winner gets reward
    
    def test_independent_observations(self):
        """Test each agent gets independent observation."""
        env = MultiAgentGridWorld({'num_agents': 3, 'grid_size': 5})
        obs, info = env.reset(seed=42)
        
        # Each observation should be different (different positions)
        assert not np.array_equal(obs[0], obs[1])
        assert not np.array_equal(obs[1], obs[2])
    
    def test_boundary_clipping(self):
        """Test agent stays within grid boundaries."""
        env = MultiAgentGridWorld({'num_agents': 1, 'grid_size': 5})
        obs, info = env.reset(seed=42)
        
        # Place agent at corner
        env.agent_positions[0] = np.array([0, 0], dtype=np.int32)
        
        # Try to move up and left (should stay at 0, 0)
        obs, rewards, terminated, truncated, info = env.step({0: 0})
        assert env.agent_positions[0][0] == 0
        
        obs, rewards, terminated, truncated, info = env.step({0: 3})
        assert env.agent_positions[0][1] == 0
    
    def test_render(self):
        """Test render doesn't crash."""
        env = MultiAgentGridWorld({'num_agents': 2, 'grid_size': 5})
        env.reset()
        
        # Should not raise error
        env.render(mode='human')
    
    def test_seeding_reproducibility(self):
        """Test seeding produces reproducible results."""
        env1 = MultiAgentGridWorld({'num_agents': 2, 'grid_size': 5})
        env2 = MultiAgentGridWorld({'num_agents': 2, 'grid_size': 5})
        
        obs1, _ = env1.reset(seed=42)
        obs2, _ = env2.reset(seed=42)
        
        # Should have same initial positions
        for i in range(2):
            np.testing.assert_array_equal(obs1[i], obs2[i])
    
    def test_episode_length_truncation(self):
        """Test episode truncates at max length."""
        env = MultiAgentGridWorld({
            'num_agents': 2,
            'grid_size': 5,
            'episode_length': 5
        })
        env.reset()
        
        for i in range(4):
            obs, rewards, terminated, truncated, info = env.step({0: 0, 1: 0})
            assert not env.truncated
        
        # 5th step should truncate
        obs, rewards, terminated, truncated, info = env.step({0: 0, 1: 0})
        assert env.truncated
    
    def test_info_dict_contents(self):
        """Test info dict contains expected keys."""
        env = MultiAgentGridWorld({'num_agents': 2, 'grid_size': 5})
        obs, info = env.reset()
        
        for i in range(2):
            assert 'step' in info[i]
            assert 'agent_id' in info[i]
            assert 'agent_pos' in info[i]
            assert 'goal_pos' in info[i]
            assert 'distance_to_goal' in info[i]
            assert 'goal_reached' in info[i]


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
