"""
Tests for new features added in code audit fixes
"""

import pytest
import numpy as np
import tempfile
import os
from environments.base_env import BaseEnvironment
from examples.simple_gridworld import SimpleGridWorld
from examples.q_learning_agent import QLearningAgent


class TestEpisodeRewardTracking:
    """Test suite for episode reward accumulation."""
    
    def test_episode_reward_initialized(self):
        """Test that episode_reward is initialized to 0."""
        env = BaseEnvironment()
        env.reset()
        assert env.episode_reward == 0.0
    
    def test_episode_reward_accumulates(self):
        """Test that episode_reward accumulates during episode."""
        class TestEnv(BaseEnvironment):
            def _calculate_reward(self, action):
                return 1.0
        
        env = TestEnv()
        env.reset()
        
        # Take a few steps
        for _ in range(5):
            _, reward, _, _, _ = env.step(0)
        
        # Episode reward should be 5.0
        assert env.episode_reward == 5.0
    
    def test_episode_reward_in_info(self):
        """Test that episode_reward is included in info dict."""
        env = BaseEnvironment()
        env.reset()
        _, _, _, _, info = env.step(0)
        
        assert 'episode_reward' in info
    
    def test_episode_reward_resets(self):
        """Test that episode_reward resets to 0 on reset."""
        class TestEnv(BaseEnvironment):
            def _calculate_reward(self, action):
                return 1.0
        
        env = TestEnv({'episode_length': 5})
        env.reset()
        
        # Complete an episode
        for _ in range(5):
            env.step(0)
        
        # Reset and check episode_reward is 0
        env.reset()
        assert env.episode_reward == 0.0
    
    def test_episode_info_at_termination(self):
        """Test that 'episode' key is added to info at termination."""
        env = BaseEnvironment({'episode_length': 2})
        env.reset()
        
        # Take steps until truncation
        env.step(0)
        _, _, _, truncated, info = env.step(0)
        
        assert truncated
        assert 'episode' in info
        assert 'r' in info['episode']
        assert 'l' in info['episode']
        assert info['episode']['l'] == 2


class TestRenderMode:
    """Test suite for render_mode parameter."""
    
    def test_render_mode_initialization(self):
        """Test that render_mode is properly initialized."""
        env = BaseEnvironment(render_mode='human')
        assert env.render_mode == 'human'
        
        env = BaseEnvironment(render_mode='rgb_array')
        assert env.render_mode == 'rgb_array'
    
    def test_render_mode_none(self):
        """Test that render_mode can be None."""
        env = BaseEnvironment()
        assert env.render_mode is None
    
    def test_simple_gridworld_render_mode(self):
        """Test that SimpleGridWorld accepts render_mode."""
        env = SimpleGridWorld(config={'grid_size': 5}, render_mode='human')
        assert env.render_mode == 'human'
        env.reset()
        env.render()  # Should not crash


class TestSimpleGridWorldObservationSpace:
    """Test suite for SimpleGridWorld observation space fix."""
    
    def test_observation_space_dtype(self):
        """Test that observation space uses float32."""
        env = SimpleGridWorld({'grid_size': 5})
        assert env.observation_space.dtype == np.float32
    
    def test_observation_space_range(self):
        """Test that observation space is normalized to [0, 1]."""
        env = SimpleGridWorld({'grid_size': 5})
        assert env.observation_space.low[0] == 0.0
        assert env.observation_space.high[0] == 1.0
    
    def test_observation_normalized(self):
        """Test that observations are normalized."""
        env = SimpleGridWorld({'grid_size': 10})
        obs, _ = env.reset()
        
        # Observations should be in [0, 1] range
        assert np.all(obs >= 0.0)
        assert np.all(obs <= 1.0)
        assert obs.dtype == np.float32
    
    def test_observation_contains_check(self):
        """Test that observation space contains normalized observations."""
        env = SimpleGridWorld({'grid_size': 5})
        obs, _ = env.reset()
        
        assert env.observation_space.contains(obs)


class TestQLearningAgentRNG:
    """Test suite for Q-Learning agent RNG seeding."""
    
    def test_seeded_rng_initialization(self):
        """Test that seeded RNG is properly initialized."""
        agent = QLearningAgent(action_space_size=4, seed=42)
        assert agent.rng is not None
    
    def test_reproducible_action_selection(self):
        """Test that action selection is reproducible with seed."""
        state = np.array([0, 1])
        
        agent1 = QLearningAgent(action_space_size=4, seed=42)
        agent2 = QLearningAgent(action_space_size=4, seed=42)
        
        # Both agents should select the same actions
        actions1 = [agent1.select_action(state, training=True) for _ in range(10)]
        actions2 = [agent2.select_action(state, training=True) for _ in range(10)]
        
        assert actions1 == actions2
    
    def test_different_seeds_different_actions(self):
        """Test that different seeds produce different actions."""
        state = np.array([0, 1])
        
        agent1 = QLearningAgent(action_space_size=4, seed=42)
        agent2 = QLearningAgent(action_space_size=4, seed=123)
        
        # Different seeds should produce different actions
        actions1 = [agent1.select_action(state, training=True) for _ in range(100)]
        actions2 = [agent2.select_action(state, training=True) for _ in range(100)]
        
        # They should be different (with very high probability)
        assert actions1 != actions2


class TestQLearningAgentSaveLoad:
    """Test suite for Q-Learning agent save/load functionality."""
    
    def test_save_and_load(self):
        """Test that agent can be saved and loaded."""
        # Create and train an agent
        agent = QLearningAgent(action_space_size=4, seed=42)
        state = np.array([0, 1])
        
        # Add some Q-values
        agent.q_table[tuple(state)] = np.array([1.0, 2.0, 3.0, 4.0])
        agent.total_steps = 100
        agent.episodes_trained = 10
        
        # Save agent
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            filepath = f.name
        
        try:
            agent.save(filepath)
            
            # Load agent
            loaded_agent = QLearningAgent.load(filepath)
            
            # Check that parameters match
            assert loaded_agent.action_space_size == agent.action_space_size
            assert loaded_agent.learning_rate == agent.learning_rate
            assert loaded_agent.discount_factor == agent.discount_factor
            assert loaded_agent.epsilon == agent.epsilon
            assert loaded_agent.total_steps == agent.total_steps
            assert loaded_agent.episodes_trained == agent.episodes_trained
            
            # Check that Q-table matches
            np.testing.assert_array_equal(
                loaded_agent.q_table[tuple(state)],
                agent.q_table[tuple(state)]
            )
        finally:
            if os.path.exists(filepath):
                os.remove(filepath)
    
    def test_save_empty_agent(self):
        """Test that empty agent can be saved and loaded."""
        agent = QLearningAgent(action_space_size=4)
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            filepath = f.name
        
        try:
            agent.save(filepath)
            loaded_agent = QLearningAgent.load(filepath)
            
            assert len(loaded_agent.q_table) == 0
        finally:
            if os.path.exists(filepath):
                os.remove(filepath)


class TestLearningRateDecay:
    """Test suite for learning rate decay."""
    
    def test_learning_rate_decay_initialization(self):
        """Test that learning rate decay can be initialized."""
        agent = QLearningAgent(
            action_space_size=4,
            learning_rate=0.1,
            learning_rate_decay=0.99
        )
        assert agent.learning_rate_decay == 0.99
        assert agent.learning_rate == 0.1
    
    def test_learning_rate_decays(self):
        """Test that learning rate decays over episodes."""
        agent = QLearningAgent(
            action_space_size=4,
            learning_rate=0.1,
            learning_rate_decay=0.9
        )
        
        initial_lr = agent.learning_rate
        agent.decay_epsilon()
        
        assert agent.learning_rate < initial_lr
        assert agent.learning_rate == pytest.approx(0.09, rel=1e-5)
    
    def test_learning_rate_has_minimum(self):
        """Test that learning rate doesn't decay below minimum."""
        agent = QLearningAgent(
            action_space_size=4,
            learning_rate=0.01,
            learning_rate_decay=0.5
        )
        
        # Decay many times
        for _ in range(100):
            agent.decay_epsilon()
        
        # Should not go below 0.001
        assert agent.learning_rate >= 0.001
    
    def test_no_decay_without_parameter(self):
        """Test that learning rate doesn't decay without decay parameter."""
        agent = QLearningAgent(
            action_space_size=4,
            learning_rate=0.1
        )
        
        initial_lr = agent.learning_rate
        agent.decay_epsilon()
        
        assert agent.learning_rate == initial_lr


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
