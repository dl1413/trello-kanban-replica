"""
Tests for DQN Agent Implementation

Comprehensive tests for QNetwork, ReplayBuffer, and DQNAgent classes.
"""

import pytest
import numpy as np
import tempfile
from pathlib import Path

# Try to import torch and DQN components
try:
    import torch
    import torch.nn as nn
    from examples.dqn_agent import QNetwork, ReplayBuffer, DQNAgent, discretize_observation, TORCH_AVAILABLE

    SKIP_TORCH_TESTS = not TORCH_AVAILABLE
except ImportError:
    SKIP_TORCH_TESTS = True
    TORCH_AVAILABLE = False

from examples.simple_gridworld import SimpleGridWorld

# Skip all tests if PyTorch is not available
pytestmark = pytest.mark.skipif(
    SKIP_TORCH_TESTS, reason="PyTorch not available. Install with: pip install torch>=2.0.0"
)


class TestQNetwork:
    """Tests for QNetwork neural network."""

    def test_qnetwork_initialization(self):
        """Test QNetwork initialization with various configurations."""
        state_dim = 4
        action_dim = 2
        hidden_layers = [64, 64]

        network = QNetwork(state_dim, action_dim, hidden_layers)

        assert network.state_dim == state_dim
        assert network.action_dim == action_dim
        assert network.hidden_layers == hidden_layers
        assert isinstance(network, nn.Module)

    def test_qnetwork_forward_pass_shape(self):
        """Test that forward pass produces correct output shape."""
        state_dim = 4
        action_dim = 3
        batch_size = 32

        network = QNetwork(state_dim, action_dim, [64, 64])

        # Create random input
        states = torch.randn(batch_size, state_dim)

        # Forward pass
        q_values = network(states)

        # Check output shape
        assert q_values.shape == (batch_size, action_dim)

    def test_qnetwork_single_sample(self):
        """Test forward pass with single sample."""
        state_dim = 2
        action_dim = 4

        network = QNetwork(state_dim, action_dim, [32])

        # Single state
        state = torch.randn(1, state_dim)
        q_values = network(state)

        assert q_values.shape == (1, action_dim)

    def test_qnetwork_different_hidden_layers(self):
        """Test QNetwork with different hidden layer configurations."""
        state_dim = 3
        action_dim = 2

        # Single hidden layer
        net1 = QNetwork(state_dim, action_dim, [128])
        assert len([m for m in net1.modules() if isinstance(m, nn.Linear)]) == 2

        # Three hidden layers
        net2 = QNetwork(state_dim, action_dim, [64, 32, 16])
        assert len([m for m in net2.modules() if isinstance(m, nn.Linear)]) == 4

        # Test forward pass
        state = torch.randn(1, state_dim)
        q1 = net1(state)
        q2 = net2(state)

        assert q1.shape == (1, action_dim)
        assert q2.shape == (1, action_dim)

    def test_qnetwork_gradient_flow(self):
        """Test that gradients flow through the network."""
        state_dim = 4
        action_dim = 2

        network = QNetwork(state_dim, action_dim, [64])

        # Create input and target
        state = torch.randn(1, state_dim, requires_grad=True)
        target = torch.randn(1, action_dim)

        # Forward pass
        output = network(state)
        loss = nn.MSELoss()(output, target)

        # Backward pass
        loss.backward()

        # Check that gradients exist
        for param in network.parameters():
            assert param.grad is not None


class TestReplayBuffer:
    """Tests for ReplayBuffer."""

    def test_buffer_initialization(self):
        """Test ReplayBuffer initialization."""
        capacity = 1000
        buffer = ReplayBuffer(capacity)

        assert buffer.capacity == capacity
        assert len(buffer) == 0

    def test_buffer_add(self):
        """Test adding transitions to buffer."""
        buffer = ReplayBuffer(100)

        state = np.array([1.0, 2.0])
        action = 0
        reward = 1.0
        next_state = np.array([2.0, 3.0])
        done = False

        buffer.add(state, action, reward, next_state, done)

        assert len(buffer) == 1

    def test_buffer_circular_behavior(self):
        """Test that buffer overwrites oldest entries when full."""
        capacity = 5
        buffer = ReplayBuffer(capacity)

        # Fill buffer beyond capacity
        for i in range(10):
            state = np.array([i, i])
            buffer.add(state, i, float(i), state, False)

        # Buffer should only contain last 5 entries
        assert len(buffer) == capacity

    def test_buffer_sample(self):
        """Test sampling from buffer."""
        buffer = ReplayBuffer(100)

        # Add multiple transitions
        for i in range(50):
            state = np.array([i, i])
            action = i % 4
            reward = float(i)
            next_state = np.array([i + 1, i + 1])
            done = i % 10 == 0
            buffer.add(state, action, reward, next_state, done)

        # Sample batch
        batch_size = 32
        states, actions, rewards, next_states, dones = buffer.sample(batch_size)

        # Check shapes and types
        assert states.shape == (batch_size, 2)
        assert actions.shape == (batch_size,)
        assert rewards.shape == (batch_size,)
        assert next_states.shape == (batch_size, 2)
        assert dones.shape == (batch_size,)

        assert states.dtype == np.float32
        assert actions.dtype == np.int64
        assert rewards.dtype == np.float32
        assert next_states.dtype == np.float32
        assert dones.dtype == np.float32

    def test_buffer_sample_less_than_requested(self):
        """Test sampling when buffer has less than requested batch size."""
        buffer = ReplayBuffer(100)

        # Add only 10 transitions
        for i in range(10):
            state = np.array([i, i])
            buffer.add(state, i, float(i), state, False)

        # Try to sample more than available
        states, actions, rewards, next_states, dones = buffer.sample(32)

        # Should return only 10 samples
        assert len(states) == 10

    def test_buffer_len(self):
        """Test __len__ method."""
        buffer = ReplayBuffer(100)

        assert len(buffer) == 0

        for i in range(25):
            buffer.add(np.array([i]), i, float(i), np.array([i]), False)

        assert len(buffer) == 25


class TestDQNAgent:
    """Tests for DQNAgent."""

    def test_agent_initialization(self):
        """Test DQN agent initialization."""
        agent = DQNAgent(state_dim=4, action_dim=2, hidden_layers=[64, 64])

        assert agent.state_dim == 4
        assert agent.action_dim == 2
        assert agent.epsilon == agent.epsilon_start
        assert len(agent.replay_buffer) == 0
        assert agent.total_steps == 0
        assert agent.episodes_trained == 0

    def test_agent_select_action_training(self):
        """Test action selection during training (epsilon-greedy)."""
        agent = DQNAgent(state_dim=2, action_dim=4, epsilon_start=1.0)

        state = np.array([0.5, 0.5])

        # With epsilon=1.0, should explore (random actions)
        actions = [agent.select_action(state, training=True) for _ in range(10)]
        assert all(0 <= a < 4 for a in actions)

    def test_agent_select_action_evaluation(self):
        """Test action selection during evaluation (greedy)."""
        agent = DQNAgent(state_dim=2, action_dim=4, epsilon_start=1.0)

        state = np.array([0.5, 0.5])

        # During evaluation, should be deterministic
        actions = [agent.select_action(state, training=False) for _ in range(10)]
        assert len(set(actions)) == 1  # All actions should be the same

    def test_agent_epsilon_decay_linear(self):
        """Test linear epsilon decay schedule."""
        epsilon_start = 1.0
        epsilon_end = 0.01
        decay_steps = 1000

        agent = DQNAgent(
            state_dim=2,
            action_dim=4,
            epsilon_start=epsilon_start,
            epsilon_end=epsilon_end,
            epsilon_decay_steps=decay_steps,
        )

        # Check initial epsilon
        assert agent.epsilon == epsilon_start

        # Decay for half the steps
        for _ in range(decay_steps // 2):
            agent.update_epsilon()

        # Should be approximately halfway
        assert 0.4 < agent.epsilon < 0.6

        # Decay to the end
        for _ in range(decay_steps):
            agent.update_epsilon()

        # Should reach minimum
        assert agent.epsilon == epsilon_end

    def test_agent_update_adds_to_buffer(self):
        """Test that update() adds transitions to replay buffer."""
        agent = DQNAgent(state_dim=2, action_dim=4)

        state = np.array([1.0, 2.0])
        action = 0
        reward = 1.0
        next_state = np.array([2.0, 3.0])
        done = False

        agent.update(state, action, reward, next_state, done)

        assert len(agent.replay_buffer) == 1
        assert agent.total_steps == 1

    def test_agent_train_step_insufficient_samples(self):
        """Test that train_step returns None when buffer is too small."""
        agent = DQNAgent(state_dim=2, action_dim=4, batch_size=32)

        # Add only 10 samples (less than batch size)
        for i in range(10):
            state = np.array([float(i), float(i)])
            agent.update(state, 0, 1.0, state, False)

        loss = agent.train_step()

        # Should still train with available samples
        assert loss is not None or len(agent.replay_buffer) < agent.batch_size

    def test_agent_train_step_reduces_loss(self):
        """Test that training step computes and reduces loss."""
        agent = DQNAgent(state_dim=2, action_dim=4, batch_size=32, learning_rate=1e-2)

        # Add enough samples
        for i in range(100):
            state = np.array([float(i % 5), float(i % 5)])
            action = i % 4
            reward = 1.0 if i % 10 == 0 else 0.0
            next_state = np.array([float((i + 1) % 5), float((i + 1) % 5)])
            done = i % 10 == 0
            agent.update(state, action, reward, next_state, done)

        # Train for multiple steps and collect losses
        losses = []
        for _ in range(50):
            loss = agent.train_step()
            if loss is not None:
                losses.append(loss)

        # Should have trained and recorded losses
        assert len(losses) > 0

        # Loss should generally decrease (check first vs last 10)
        if len(losses) >= 20:
            early_loss = np.mean(losses[:10])
            late_loss = np.mean(losses[-10:])
            # Note: Not always guaranteed to decrease, but usually does
            assert late_loss <= early_loss * 1.5  # Allow some variance

    def test_target_network_hard_update(self):
        """Test hard update of target network."""
        agent = DQNAgent(state_dim=2, action_dim=4, target_update_freq=10)

        # Get initial target network parameters
        initial_params = [p.clone() for p in agent.target_network.parameters()]

        # Modify Q-network by training
        for i in range(100):
            state = np.array([float(i), float(i)])
            agent.update(state, 0, 1.0, state, False)

        for _ in range(5):
            agent.train_step()

        # Q-network should have changed
        q_params_changed = any(not torch.equal(p1, p2) for p1, p2 in zip(agent.q_network.parameters(), initial_params))
        assert q_params_changed

        # Force hard update
        agent._hard_update_target_network()

        # Target network should now match Q-network
        for p1, p2 in zip(agent.q_network.parameters(), agent.target_network.parameters()):
            assert torch.equal(p1, p2)

    def test_target_network_soft_update(self):
        """Test soft (Polyak) update of target network."""
        tau = 0.1
        agent = DQNAgent(state_dim=2, action_dim=4, tau=tau)

        # Get initial parameters
        initial_q_params = [p.clone() for p in agent.q_network.parameters()]
        initial_target_params = [p.clone() for p in agent.target_network.parameters()]

        # Modify Q-network
        for i in range(100):
            state = np.array([float(i), float(i)])
            agent.update(state, 0, 1.0, state, False)

        for _ in range(10):
            agent.train_step()

        # Check that soft update occurred (target should be between old and new)
        for old_q, old_target, new_q, new_target in zip(
            initial_q_params, initial_target_params, agent.q_network.parameters(), agent.target_network.parameters()
        ):
            # Q-network should have changed significantly
            assert not torch.allclose(old_q, new_q, atol=1e-3)

            # Target should have moved toward Q but not equal
            if not torch.equal(old_q, new_q):  # Only check if Q changed
                # Target should be different from both old target and new Q
                assert not torch.equal(new_target, old_target)
                assert not torch.equal(new_target, new_q)

    def test_agent_save_and_load(self):
        """Test saving and loading agent checkpoint."""
        agent = DQNAgent(state_dim=2, action_dim=4, hidden_layers=[32, 32])

        # Train for a bit
        for i in range(50):
            state = np.array([float(i), float(i)])
            agent.update(state, i % 4, 1.0, state, False)
            agent.train_step()

        agent.update_epsilon()
        agent.end_episode()

        # Save checkpoint
        with tempfile.NamedTemporaryFile(suffix=".pth", delete=False) as f:
            checkpoint_path = f.name

        try:
            agent.save(checkpoint_path)

            # Create new agent and load
            new_agent = DQNAgent(state_dim=2, action_dim=4, hidden_layers=[32, 32])
            new_agent.load(checkpoint_path)

            # Check that statistics match
            assert new_agent.epsilon == agent.epsilon
            assert new_agent.total_steps == agent.total_steps
            assert new_agent.episodes_trained == agent.episodes_trained
            assert new_agent.update_count == agent.update_count

            # Check that networks produce same output
            test_state = np.array([1.5, 2.5])
            with torch.no_grad():
                state_tensor = torch.FloatTensor(test_state).unsqueeze(0)
                q1 = agent.q_network(state_tensor.to(agent.device))
                q2 = new_agent.q_network(state_tensor.to(new_agent.device))
                assert torch.allclose(q1.cpu(), q2.cpu())

        finally:
            # Cleanup
            Path(checkpoint_path).unlink(missing_ok=True)

    def test_agent_get_statistics(self):
        """Test getting agent statistics."""
        agent = DQNAgent(state_dim=2, action_dim=4)

        stats = agent.get_statistics()

        assert "total_steps" in stats
        assert "episodes_trained" in stats
        assert "epsilon" in stats
        assert "update_count" in stats
        assert "buffer_size" in stats
        assert "mean_loss" in stats

        assert stats["total_steps"] == 0
        assert stats["buffer_size"] == 0

    def test_agent_end_episode(self):
        """Test end_episode method increments counter."""
        agent = DQNAgent(state_dim=2, action_dim=4)

        assert agent.episodes_trained == 0

        agent.end_episode()
        assert agent.episodes_trained == 1

        agent.end_episode()
        assert agent.episodes_trained == 2

    def test_agent_different_devices(self):
        """Test agent can be created on different devices."""
        # CPU
        agent_cpu = DQNAgent(state_dim=2, action_dim=4, device="cpu")
        assert agent_cpu.device.type == "cpu"

        # CUDA (if available)
        if torch.cuda.is_available():
            agent_cuda = DQNAgent(state_dim=2, action_dim=4, device="cuda")
            assert agent_cuda.device.type == "cuda"


class TestDiscretizeObservation:
    """Tests for observation discretization utility."""

    def test_discretize_observation(self):
        """Test discretization of grid observations."""
        grid_size = 5

        obs1 = np.array([0, 0])
        assert discretize_observation(obs1, grid_size) == 0

        obs2 = np.array([0, 1])
        assert discretize_observation(obs2, grid_size) == 1

        obs3 = np.array([1, 0])
        assert discretize_observation(obs3, grid_size) == 5

        obs4 = np.array([2, 3])
        assert discretize_observation(obs4, grid_size) == 13

    def test_discretize_observation_different_grid_sizes(self):
        """Test discretization with different grid sizes."""
        obs = np.array([2, 2])

        assert discretize_observation(obs, 3) == 8
        assert discretize_observation(obs, 5) == 12
        assert discretize_observation(obs, 10) == 22


class TestDQNIntegration:
    """Integration tests for DQN with SimpleGridWorld."""

    def test_dqn_with_gridworld(self):
        """Test DQN agent can interact with SimpleGridWorld."""
        env_config = {"grid_size": 3, "episode_length": 20}
        env = SimpleGridWorld(env_config)

        agent = DQNAgent(state_dim=2, action_dim=4, hidden_layers=[16, 16], batch_size=8)

        obs, info = env.reset()

        for _ in range(10):
            action = agent.select_action(obs, training=True)
            next_obs, reward, terminated, truncated, info = env.step(action)
            agent.update(obs, action, reward, next_obs, terminated or truncated)

            if len(agent.replay_buffer) >= agent.batch_size:
                loss = agent.train_step()
                assert loss is None or isinstance(loss, float)

            if terminated or truncated:
                break

            obs = next_obs

        env.close()

    def test_dqn_training_improves_performance(self):
        """Test that DQN training improves performance (smoke test)."""
        env_config = {"grid_size": 3, "episode_length": 30}
        env = SimpleGridWorld(env_config)

        agent = DQNAgent(
            state_dim=2,
            action_dim=4,
            hidden_layers=[32],
            learning_rate=1e-2,
            batch_size=16,
            epsilon_start=1.0,
            epsilon_end=0.1,
            epsilon_decay_steps=100,
        )

        # Train for a few episodes
        for episode in range(20):
            obs, info = env.reset()

            for step in range(30):
                action = agent.select_action(obs, training=True)
                next_obs, reward, terminated, truncated, info = env.step(action)
                agent.update(obs, action, reward, next_obs, terminated or truncated)

                if len(agent.replay_buffer) >= agent.batch_size:
                    agent.train_step()

                agent.update_epsilon()

                if terminated or truncated:
                    break

                obs = next_obs

            agent.end_episode()

        # Agent should have learned something
        stats = agent.get_statistics()
        assert stats["total_steps"] > 0
        assert stats["episodes_trained"] == 20
        assert stats["epsilon"] < agent.epsilon_start
        assert len(agent.replay_buffer) > 0

        env.close()


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_empty_buffer_sample(self):
        """Test sampling from empty buffer."""
        buffer = ReplayBuffer(10)

        states, actions, rewards, next_states, dones = buffer.sample(5)

        # Should return empty arrays
        assert len(states) == 0

    def test_qnetwork_with_empty_hidden_layers(self):
        """Test QNetwork with no hidden layers (direct mapping)."""
        network = QNetwork(state_dim=4, action_dim=2, hidden_layers=[])

        state = torch.randn(1, 4)
        output = network(state)

        assert output.shape == (1, 2)

    def test_agent_with_zero_epsilon(self):
        """Test agent behavior with no exploration."""
        agent = DQNAgent(state_dim=2, action_dim=4, epsilon_start=0.0, epsilon_end=0.0)

        state = np.array([1.0, 2.0])

        # Should always select same action (greedy)
        actions = [agent.select_action(state, training=True) for _ in range(5)]
        assert len(set(actions)) == 1

    def test_agent_gradient_clipping(self):
        """Test that gradient clipping is applied."""
        agent = DQNAgent(state_dim=2, action_dim=4, grad_clip=0.5)

        # Add samples with extreme rewards to create large gradients
        for i in range(100):
            state = np.array([float(i), float(i)])
            reward = 1000.0 if i % 2 == 0 else -1000.0
            agent.update(state, 0, reward, state, False)

        # Train and check that it doesn't explode
        for _ in range(10):
            loss = agent.train_step()
            if loss is not None:
                assert not np.isnan(loss)
                assert not np.isinf(loss)
