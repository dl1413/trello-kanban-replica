"""
Deep Q-Network (DQN) Agent Implementation

This module implements a complete DQN agent with experience replay and target networks
for solving RL problems. It includes training scripts for the SimpleGridWorld environment
with comprehensive logging and comparison baselines.
"""

import numpy as np
import matplotlib.pyplot as plt
from collections import deque
from typing import Tuple, Dict, Any, List, Optional
import random

try:
    import torch
    import torch.nn as nn
    import torch.nn.functional as F
    import torch.optim as optim

    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    print("Warning: PyTorch not available. Install with: pip install torch>=2.0.0")

from examples.simple_gridworld import SimpleGridWorld
from examples.q_learning_agent import QLearningAgent, evaluate_agent as evaluate_q_agent


class QNetwork(nn.Module):
    """
    Q-Network: Neural network that approximates Q-values.

    This is a configurable MLP with ReLU activations that maps
    state observations to action values.
    """

    def __init__(self, state_dim: int, action_dim: int, hidden_layers: Optional[List[int]] = None):
        """
        Initialize Q-Network.

        Args:
            state_dim: Dimension of state space
            action_dim: Number of actions
            hidden_layers: List of hidden layer sizes (e.g., [64, 64]). Defaults to [64, 64] if None.
        """
        super(QNetwork, self).__init__()

        if hidden_layers is None:
            hidden_layers = [64, 64]

        self.state_dim = state_dim
        self.action_dim = action_dim
        self.hidden_layers = hidden_layers

        # Build network layers
        layers = []
        input_dim = state_dim

        for hidden_dim in hidden_layers:
            layers.append(nn.Linear(input_dim, hidden_dim))
            layers.append(nn.ReLU())
            input_dim = hidden_dim

        # Output layer
        layers.append(nn.Linear(input_dim, action_dim))

        self.network = nn.Sequential(*layers)

    def forward(self, state: torch.Tensor) -> torch.Tensor:
        """
        Forward pass through the network.

        Args:
            state: State tensor of shape (batch_size, state_dim)

        Returns:
            Q-values for each action, shape (batch_size, action_dim)
        """
        return self.network(state)


class ReplayBuffer:
    """
    Experience Replay Buffer for storing and sampling transitions.

    Implements a circular buffer that stores (state, action, reward, next_state, done)
    tuples and provides efficient random sampling for training.
    """

    def __init__(self, capacity: int):
        """
        Initialize replay buffer.

        Args:
            capacity: Maximum number of transitions to store
        """
        self.capacity = capacity
        self.buffer = deque(maxlen=capacity)

    def add(self, state: np.ndarray, action: int, reward: float, next_state: np.ndarray, done: bool):
        """
        Add a transition to the buffer.

        Args:
            state: Current state
            action: Action taken
            reward: Reward received
            next_state: Next state
            done: Whether episode terminated
        """
        self.buffer.append((state, action, reward, next_state, done))

    def sample(self, batch_size: int) -> Tuple[np.ndarray, ...]:
        """
        Sample a random batch of transitions.

        Args:
            batch_size: Number of transitions to sample

        Returns:
            Tuple of (states, actions, rewards, next_states, dones) as numpy arrays
        """
        if batch_size > len(self.buffer):
            batch_size = len(self.buffer)

        batch = random.sample(self.buffer, batch_size)

        states = np.array([x[0] for x in batch], dtype=np.float32)
        actions = np.array([x[1] for x in batch], dtype=np.int64)
        rewards = np.array([x[2] for x in batch], dtype=np.float32)
        next_states = np.array([x[3] for x in batch], dtype=np.float32)
        dones = np.array([x[4] for x in batch], dtype=np.float32)

        return states, actions, rewards, next_states, dones

    def __len__(self) -> int:
        """Return current size of the buffer."""
        return len(self.buffer)


class DQNAgent:
    """
    Deep Q-Network Agent with epsilon-greedy exploration and target network.

    Implements the DQN algorithm with:
    - Experience replay
    - Target network (hard or soft/Polyak updates)
    - Epsilon-greedy exploration with linear decay
    - Huber loss
    - Gradient clipping
    """

    def __init__(
        self,
        state_dim: int,
        action_dim: int,
        hidden_layers: Optional[List[int]] = None,
        learning_rate: float = 1e-3,
        discount_factor: float = 0.99,
        epsilon_start: float = 1.0,
        epsilon_end: float = 0.01,
        epsilon_decay_steps: int = 10000,
        buffer_capacity: int = 10000,
        batch_size: int = 64,
        target_update_freq: int = 100,
        tau: Optional[float] = None,
        grad_clip: float = 1.0,
        device: Optional[str] = None,
    ):
        """
        Initialize DQN agent.

        Args:
            state_dim: Dimension of state space
            action_dim: Number of actions
            hidden_layers: List of hidden layer sizes. Defaults to [64, 64] if None.
            learning_rate: Learning rate for optimizer
            discount_factor: Discount factor (gamma)
            epsilon_start: Initial exploration rate
            epsilon_end: Final exploration rate
            epsilon_decay_steps: Number of steps for epsilon decay
            buffer_capacity: Replay buffer capacity
            batch_size: Batch size for training
            target_update_freq: Frequency of target network updates (hard update)
            tau: If provided, use soft (Polyak) updates with this coefficient
            grad_clip: Gradient clipping value
            device: Device to use ('cpu', 'cuda', or None for auto)
        """
        if not TORCH_AVAILABLE:
            raise ImportError("PyTorch is required. Install with: pip install torch>=2.0.0")

        if hidden_layers is None:
            hidden_layers = [64, 64]

        self.state_dim = state_dim
        self.action_dim = action_dim
        self.discount_factor = discount_factor
        self.batch_size = batch_size
        self.target_update_freq = target_update_freq
        self.tau = tau
        self.grad_clip = grad_clip

        # Epsilon decay schedule (linear)
        self.epsilon_start = epsilon_start
        self.epsilon_end = epsilon_end
        self.epsilon_decay_steps = epsilon_decay_steps
        self.epsilon = epsilon_start

        # Device setup
        if device is None:
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        else:
            self.device = torch.device(device)

        # Networks
        self.q_network = QNetwork(state_dim, action_dim, hidden_layers).to(self.device)
        self.target_network = QNetwork(state_dim, action_dim, hidden_layers).to(self.device)
        self.target_network.load_state_dict(self.q_network.state_dict())
        self.target_network.eval()

        # Optimizer
        self.optimizer = optim.Adam(self.q_network.parameters(), lr=learning_rate)

        # Replay buffer
        self.replay_buffer = ReplayBuffer(buffer_capacity)

        # Statistics
        self.total_steps = 0
        self.episodes_trained = 0
        self.update_count = 0
        self.losses = []

    def select_action(self, state: np.ndarray, training: bool = True) -> int:
        """
        Select action using epsilon-greedy policy.

        Args:
            state: Current state observation
            training: If True, use epsilon-greedy; if False, use greedy

        Returns:
            Selected action
        """
        # Epsilon-greedy exploration during training
        if training and random.random() < self.epsilon:
            return random.randint(0, self.action_dim - 1)

        # Greedy action selection
        with torch.no_grad():
            state_tensor = torch.FloatTensor(state).unsqueeze(0).to(self.device)
            q_values = self.q_network(state_tensor)
            return int(q_values.argmax(dim=1).item())

    def update(self, state: np.ndarray, action: int, reward: float, next_state: np.ndarray, done: bool):
        """
        Add transition to replay buffer.

        Args:
            state: Current state
            action: Action taken
            reward: Reward received
            next_state: Next state
            done: Whether episode terminated
        """
        self.replay_buffer.add(state, action, reward, next_state, done)
        self.total_steps += 1

    def train_step(self) -> Optional[float]:
        """
        Perform one training step on a batch from replay buffer.

        Returns:
            Loss value if training occurred, None otherwise
        """
        # Check if we have enough samples
        if len(self.replay_buffer) < self.batch_size:
            return None

        # Sample batch
        states, actions, rewards, next_states, dones = self.replay_buffer.sample(self.batch_size)

        # Convert to tensors
        states = torch.FloatTensor(states).to(self.device)
        actions = torch.LongTensor(actions).to(self.device)
        rewards = torch.FloatTensor(rewards).to(self.device)
        next_states = torch.FloatTensor(next_states).to(self.device)
        dones = torch.FloatTensor(dones).to(self.device)

        # Compute current Q-values
        current_q_values = self.q_network(states).gather(1, actions.unsqueeze(1)).squeeze(1)

        # Compute target Q-values
        with torch.no_grad():
            next_q_values = self.target_network(next_states).max(dim=1)[0]
            target_q_values = rewards + (1 - dones) * self.discount_factor * next_q_values

        # Compute Huber loss
        loss = F.smooth_l1_loss(current_q_values, target_q_values)

        # Optimize
        self.optimizer.zero_grad()
        loss.backward()

        # Gradient clipping
        if self.grad_clip is not None:
            torch.nn.utils.clip_grad_norm_(self.q_network.parameters(), self.grad_clip)

        self.optimizer.step()

        # Update target network
        self.update_count += 1
        if self.tau is not None:
            # Soft (Polyak) update
            self._soft_update_target_network()
        elif self.update_count % self.target_update_freq == 0:
            # Hard update
            self._hard_update_target_network()

        # Record loss
        loss_value = loss.item()
        self.losses.append(loss_value)

        return loss_value

    def _hard_update_target_network(self):
        """Hard update: copy weights from Q-network to target network."""
        self.target_network.load_state_dict(self.q_network.state_dict())

    def _soft_update_target_network(self):
        """Soft update: θ_target = τ * θ_q + (1 - τ) * θ_target."""
        for target_param, param in zip(self.target_network.parameters(), self.q_network.parameters()):
            target_param.data.copy_(self.tau * param.data + (1 - self.tau) * target_param.data)

    def update_epsilon(self):
        """Update exploration rate using linear decay."""
        # Linear decay
        decay_amount = (self.epsilon_start - self.epsilon_end) / self.epsilon_decay_steps
        self.epsilon = max(self.epsilon_end, self.epsilon - decay_amount)

    def end_episode(self):
        """Called at the end of each episode."""
        self.episodes_trained += 1

    def save(self, path: str):
        """
        Save model checkpoint.

        Args:
            path: Path to save checkpoint
        """
        checkpoint = {
            "q_network_state_dict": self.q_network.state_dict(),
            "target_network_state_dict": self.target_network.state_dict(),
            "optimizer_state_dict": self.optimizer.state_dict(),
            "epsilon": self.epsilon,
            "total_steps": self.total_steps,
            "episodes_trained": self.episodes_trained,
            "update_count": self.update_count,
            "config": {
                "state_dim": self.state_dim,
                "action_dim": self.action_dim,
                "discount_factor": self.discount_factor,
                "batch_size": self.batch_size,
                "target_update_freq": self.target_update_freq,
                "tau": self.tau,
                "grad_clip": self.grad_clip,
                "epsilon_start": self.epsilon_start,
                "epsilon_end": self.epsilon_end,
                "epsilon_decay_steps": self.epsilon_decay_steps,
            },
        }
        torch.save(checkpoint, path)

    def load(self, path: str):
        """
        Load model checkpoint.

        Args:
            path: Path to load checkpoint from
        """
        checkpoint = torch.load(path, map_location=self.device)
        self.q_network.load_state_dict(checkpoint["q_network_state_dict"])
        self.target_network.load_state_dict(checkpoint["target_network_state_dict"])
        self.optimizer.load_state_dict(checkpoint["optimizer_state_dict"])
        self.epsilon = checkpoint["epsilon"]
        self.total_steps = checkpoint["total_steps"]
        self.episodes_trained = checkpoint["episodes_trained"]
        self.update_count = checkpoint["update_count"]

    def get_statistics(self) -> Dict[str, Any]:
        """Get agent statistics."""
        return {
            "total_steps": self.total_steps,
            "episodes_trained": self.episodes_trained,
            "epsilon": self.epsilon,
            "update_count": self.update_count,
            "buffer_size": len(self.replay_buffer),
            "mean_loss": np.mean(self.losses[-100:]) if self.losses else 0.0,
        }


def discretize_observation(obs: np.ndarray, grid_size: int) -> int:
    """
    Convert grid position to discrete state index.

    Args:
        obs: Observation array [x, y]
        grid_size: Size of the grid

    Returns:
        Integer state index
    """
    x, y = obs
    return int(x * grid_size + y)


def train_dqn(
    env: SimpleGridWorld,
    agent: DQNAgent,
    num_episodes: int = 1000,
    max_steps: int = 200,
    train_freq: int = 1,
    eval_interval: int = 50,
    verbose: bool = True,
) -> Dict[str, Any]:
    """
    Train DQN agent on the environment.

    Args:
        env: Environment instance
        agent: DQN agent
        num_episodes: Number of training episodes
        max_steps: Maximum steps per episode
        train_freq: Train every N steps
        eval_interval: Evaluate every N episodes
        verbose: Print progress

    Returns:
        Training statistics
    """
    episode_rewards = []
    episode_lengths = []
    episode_losses = []
    success_count = 0
    eval_rewards = []
    eval_success_rates = []
    epsilon_history = []

    for episode in range(num_episodes):
        obs, info = env.reset()
        episode_reward = 0
        episode_loss = []
        steps = 0

        terminated = False
        truncated = False

        while not (terminated or truncated) and steps < max_steps:
            # Select action
            action = agent.select_action(obs, training=True)

            # Take step
            next_obs, reward, terminated, truncated, info = env.step(action)

            # Store transition
            agent.update(obs, action, reward, next_obs, terminated or truncated)

            # Train agent
            if agent.total_steps % train_freq == 0:
                loss = agent.train_step()
                if loss is not None:
                    episode_loss.append(loss)

            # Update epsilon
            agent.update_epsilon()

            obs = next_obs
            episode_reward += reward
            steps += 1

        # End episode
        agent.end_episode()

        # Record statistics
        episode_rewards.append(episode_reward)
        episode_lengths.append(steps)
        episode_losses.append(np.mean(episode_loss) if episode_loss else 0.0)
        epsilon_history.append(agent.epsilon)

        if info.get("goal_reached", False):
            success_count += 1

        # Evaluation
        if (episode + 1) % eval_interval == 0:
            eval_stats = evaluate_dqn_agent(env, agent, num_episodes=20)
            eval_rewards.append(eval_stats["mean_reward"])
            eval_success_rates.append(eval_stats["success_rate"])

            if verbose:
                avg_reward = np.mean(episode_rewards[-eval_interval:])
                avg_length = np.mean(episode_lengths[-eval_interval:])
                avg_loss = np.mean([loss_val for loss_val in episode_losses[-eval_interval:] if loss_val > 0])
                success_rate = success_count / (episode + 1)
                agent_stats = agent.get_statistics()

                print(
                    f"Episode {episode + 1}/{num_episodes} | "
                    f"Reward: {avg_reward:.2f} | "
                    f"Length: {avg_length:.2f} | "
                    f"Loss: {avg_loss:.4f} | "
                    f"Success: {success_rate:.2%} | "
                    f"Epsilon: {agent.epsilon:.3f} | "
                    f'Buffer: {agent_stats["buffer_size"]} | '
                    f'Eval Reward: {eval_stats["mean_reward"]:.2f} | '
                    f'Eval Success: {eval_stats["success_rate"]:.2%}'
                )

    return {
        "episode_rewards": episode_rewards,
        "episode_lengths": episode_lengths,
        "episode_losses": episode_losses,
        "epsilon_history": epsilon_history,
        "success_rate": success_count / num_episodes,
        "eval_rewards": eval_rewards,
        "eval_success_rates": eval_success_rates,
        "agent_stats": agent.get_statistics(),
    }


def evaluate_dqn_agent(env: SimpleGridWorld, agent: DQNAgent, num_episodes: int = 100) -> Dict[str, float]:
    """
    Evaluate DQN agent performance without exploration.

    Args:
        env: Environment instance
        agent: Trained DQN agent
        num_episodes: Number of evaluation episodes

    Returns:
        Evaluation metrics
    """
    rewards = []
    lengths = []
    successes = []

    for _ in range(num_episodes):
        obs, info = env.reset()
        episode_reward = 0
        steps = 0

        terminated = False
        truncated = False

        while not (terminated or truncated) and steps < 200:
            # Greedy action selection (no exploration)
            action = agent.select_action(obs, training=False)
            obs, reward, terminated, truncated, info = env.step(action)
            episode_reward += reward
            steps += 1

        rewards.append(episode_reward)
        lengths.append(steps)
        successes.append(info.get("goal_reached", False))

    return {
        "mean_reward": np.mean(rewards),
        "std_reward": np.std(rewards),
        "mean_length": np.mean(lengths),
        "std_length": np.std(lengths),
        "success_rate": np.mean(successes),
    }


def plot_dqn_training_results(
    dqn_stats: Dict[str, Any], q_stats: Optional[Dict[str, Any]] = None, save_path: str = None
):
    """
    Plot DQN training results with optional Q-Learning comparison.

    Args:
        dqn_stats: DQN training statistics
        q_stats: Optional Q-Learning statistics for comparison
        save_path: Optional path to save figure
    """
    fig, axes = plt.subplots(2, 3, figsize=(18, 10))

    # Episode rewards
    ax = axes[0, 0]
    ax.plot(dqn_stats["episode_rewards"], alpha=0.3, label="DQN Episode Reward")
    window = 50
    if len(dqn_stats["episode_rewards"]) >= window:
        moving_avg = np.convolve(dqn_stats["episode_rewards"], np.ones(window) / window, mode="valid")
        ax.plot(
            range(window - 1, len(dqn_stats["episode_rewards"])),
            moving_avg,
            label=f"DQN {window}-Ep Moving Avg",
            linewidth=2,
        )

    if q_stats:
        ax.plot(q_stats["episode_rewards"], alpha=0.3, label="Q-Learning Episode Reward", color="orange")
        if len(q_stats["episode_rewards"]) >= window:
            moving_avg_q = np.convolve(q_stats["episode_rewards"], np.ones(window) / window, mode="valid")
            ax.plot(
                range(window - 1, len(q_stats["episode_rewards"])),
                moving_avg_q,
                label=f"Q-Learning {window}-Ep Moving Avg",
                linewidth=2,
                color="darkorange",
            )

    ax.set_xlabel("Episode")
    ax.set_ylabel("Total Reward")
    ax.set_title("Training Rewards")
    ax.legend()
    ax.grid(True, alpha=0.3)

    # Episode losses (DQN only)
    ax = axes[0, 1]
    valid_losses = [loss_val for loss_val in dqn_stats["episode_losses"] if loss_val > 0]
    if valid_losses:
        ax.plot(valid_losses, alpha=0.3, label="Episode Loss")
        if len(valid_losses) >= window:
            moving_avg = np.convolve(valid_losses, np.ones(window) / window, mode="valid")
            ax.plot(range(window - 1, len(valid_losses)), moving_avg, label=f"{window}-Episode Moving Avg", linewidth=2)
    ax.set_xlabel("Episode")
    ax.set_ylabel("Loss")
    ax.set_title("Training Loss (DQN)")
    ax.legend()
    ax.grid(True, alpha=0.3)

    # Epsilon decay
    ax = axes[0, 2]
    ax.plot(dqn_stats["epsilon_history"], linewidth=2, color="purple")
    ax.set_xlabel("Episode")
    ax.set_ylabel("Epsilon")
    ax.set_title("Exploration Rate Decay")
    ax.grid(True, alpha=0.3)

    # Episode lengths
    ax = axes[1, 0]
    ax.plot(dqn_stats["episode_lengths"], alpha=0.3, label="DQN Episode Length")
    if len(dqn_stats["episode_lengths"]) >= window:
        moving_avg = np.convolve(dqn_stats["episode_lengths"], np.ones(window) / window, mode="valid")
        ax.plot(
            range(window - 1, len(dqn_stats["episode_lengths"])),
            moving_avg,
            label=f"DQN {window}-Ep Moving Avg",
            linewidth=2,
        )

    if q_stats:
        ax.plot(q_stats["episode_lengths"], alpha=0.3, label="Q-Learning Episode Length", color="orange")
        if len(q_stats["episode_lengths"]) >= window:
            moving_avg_q = np.convolve(q_stats["episode_lengths"], np.ones(window) / window, mode="valid")
            ax.plot(
                range(window - 1, len(q_stats["episode_lengths"])),
                moving_avg_q,
                label=f"Q-Learning {window}-Ep Moving Avg",
                linewidth=2,
                color="darkorange",
            )

    ax.set_xlabel("Episode")
    ax.set_ylabel("Steps")
    ax.set_title("Episode Lengths")
    ax.legend()
    ax.grid(True, alpha=0.3)

    # Evaluation rewards
    ax = axes[1, 1]
    eval_episodes = np.arange(len(dqn_stats["eval_rewards"])) * 50 + 50
    ax.plot(eval_episodes, dqn_stats["eval_rewards"], marker="o", linewidth=2, label="DQN")

    if q_stats:
        eval_episodes_q = np.arange(len(q_stats["eval_rewards"])) * 50 + 50
        ax.plot(eval_episodes_q, q_stats["eval_rewards"], marker="s", linewidth=2, label="Q-Learning", color="orange")

    ax.set_xlabel("Episode")
    ax.set_ylabel("Mean Evaluation Reward")
    ax.set_title("Evaluation Performance")
    ax.legend()
    ax.grid(True, alpha=0.3)

    # Success rate
    ax = axes[1, 2]
    ax.plot(eval_episodes, dqn_stats["eval_success_rates"], marker="o", linewidth=2, color="green", label="DQN")

    if q_stats:
        eval_episodes_q = np.arange(len(q_stats["eval_success_rates"])) * 50 + 50
        ax.plot(
            eval_episodes_q, q_stats["eval_success_rates"], marker="s", linewidth=2, color="orange", label="Q-Learning"
        )

    ax.set_xlabel("Episode")
    ax.set_ylabel("Success Rate")
    ax.set_title("Evaluation Success Rate")
    ax.set_ylim([0, 1.05])
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches="tight")
        print(f"Saved plot to {save_path}")

    return fig


def main():
    """Main training and evaluation loop."""
    if not TORCH_AVAILABLE:
        print("ERROR: PyTorch is required for DQN. Install with: pip install torch>=2.0.0")
        return

    print("=" * 80)
    print("DQN Agent Training on SimpleGridWorld")
    print("=" * 80)

    # Environment configuration
    env_config = {"grid_size": 5, "episode_length": 100, "reward_type": "sparse"}

    # Create environment
    env = SimpleGridWorld(env_config)

    print("\nEnvironment Configuration:")
    print(f"  Grid Size: {env.grid_size}x{env.grid_size}")
    print(f"  Max Episode Length: {env.episode_length}")
    print(f"  Reward Type: {env.reward_type}")
    print(f"  Action Space: {env.action_space}")
    print(f"  Observation Space: {env.observation_space}")

    # State dimension for DQN (flatten observation space)
    state_dim = env.observation_space.shape[0]
    action_dim = env.action_space.n

    # Create DQN agent
    dqn_agent = DQNAgent(
        state_dim=state_dim,
        action_dim=action_dim,
        hidden_layers=[64, 64],
        learning_rate=1e-3,
        discount_factor=0.95,
        epsilon_start=1.0,
        epsilon_end=0.01,
        epsilon_decay_steps=5000,
        buffer_capacity=10000,
        batch_size=64,
        target_update_freq=100,
        tau=None,  # Use hard updates
        grad_clip=1.0,
    )

    print("\nDQN Agent Configuration:")
    print(f"  State Dimension: {state_dim}")
    print(f"  Action Dimension: {action_dim}")
    print(f"  Hidden Layers: {dqn_agent.q_network.hidden_layers}")
    print("  Learning Rate: 1e-3")
    print(f"  Discount Factor: {dqn_agent.discount_factor}")
    print(f"  Epsilon Decay Steps: {dqn_agent.epsilon_decay_steps}")
    print(f"  Batch Size: {dqn_agent.batch_size}")
    print(f"  Target Update Freq: {dqn_agent.target_update_freq}")
    print(f"  Device: {dqn_agent.device}")

    # Train DQN agent
    print("\n" + "=" * 80)
    print("Training DQN Agent")
    print("=" * 80 + "\n")

    num_episodes = 500
    dqn_stats = train_dqn(
        env=env, agent=dqn_agent, num_episodes=num_episodes, max_steps=100, train_freq=1, eval_interval=50, verbose=True
    )

    # Save DQN checkpoint
    checkpoint_path = "/tmp/dqn_checkpoint.pth"
    dqn_agent.save(checkpoint_path)
    print(f"\nSaved DQN checkpoint to {checkpoint_path}")

    # Final DQN evaluation
    print("\n" + "=" * 80)
    print("Final DQN Evaluation")
    print("=" * 80)

    dqn_final_eval = evaluate_dqn_agent(env, dqn_agent, num_episodes=100)
    print("\nDQN Performance (100 episodes):")
    print(f'  Mean Reward: {dqn_final_eval["mean_reward"]:.2f} ± {dqn_final_eval["std_reward"]:.2f}')
    print(f'  Mean Length: {dqn_final_eval["mean_length"]:.2f} ± {dqn_final_eval["std_length"]:.2f}')
    print(f'  Success Rate: {dqn_final_eval["success_rate"]:.2%}')

    # DQN Agent statistics
    dqn_agent_stats = dqn_agent.get_statistics()
    print("\nDQN Agent Statistics:")
    print(f'  Total Steps: {dqn_agent_stats["total_steps"]:,}')
    print(f'  Episodes Trained: {dqn_agent_stats["episodes_trained"]:,}')
    print(f'  Final Epsilon: {dqn_agent_stats["epsilon"]:.4f}')
    print(f'  Buffer Size: {dqn_agent_stats["buffer_size"]:,}')
    print(f'  Mean Loss: {dqn_agent_stats["mean_loss"]:.4f}')

    # Train Q-Learning baseline
    print("\n" + "=" * 80)
    print("Training Q-Learning Baseline for Comparison")
    print("=" * 80 + "\n")

    q_agent = QLearningAgent(
        action_space_size=action_dim,
        learning_rate=0.1,
        discount_factor=0.95,
        epsilon=1.0,
        epsilon_decay=0.995,
        epsilon_min=0.01,
    )

    # Import training function
    from examples.q_learning_agent import train_q_learning

    q_stats = train_q_learning(
        env=env, agent=q_agent, num_episodes=num_episodes, max_steps=100, eval_interval=50, verbose=True
    )

    q_final_eval = evaluate_q_agent(env, q_agent, num_episodes=100)
    print("\nQ-Learning Performance (100 episodes):")
    print(f'  Mean Reward: {q_final_eval["mean_reward"]:.2f} ± {q_final_eval["std_reward"]:.2f}')
    print(f'  Mean Length: {q_final_eval["mean_length"]:.2f} ± {q_final_eval["std_length"]:.2f}')
    print(f'  Success Rate: {q_final_eval["success_rate"]:.2%}')

    # Random baseline
    print("\n" + "=" * 80)
    print("Random Baseline Comparison")
    print("=" * 80)

    class RandomAgent:
        def select_action(self, state, training=True):
            return env.action_space.sample()

    random_agent = RandomAgent()
    random_eval = evaluate_q_agent(env, random_agent, num_episodes=100)

    print("\nRandom Agent Performance (100 episodes):")
    print(f'  Mean Reward: {random_eval["mean_reward"]:.2f} ± {random_eval["std_reward"]:.2f}')
    print(f'  Mean Length: {random_eval["mean_length"]:.2f} ± {random_eval["std_length"]:.2f}')
    print(f'  Success Rate: {random_eval["success_rate"]:.2%}')

    # Comparison
    print("\n" + "=" * 80)
    print("Performance Comparison")
    print("=" * 80)

    print("\n                       DQN      Q-Learning    Random")
    print("-" * 60)
    print(
        f'Mean Reward:      {dqn_final_eval["mean_reward"]:8.2f}  {q_final_eval["mean_reward"]:8.2f}  '
        f'{random_eval["mean_reward"]:8.2f}'
    )
    print(
        f'Success Rate:     {dqn_final_eval["success_rate"]:7.1%}   {q_final_eval["success_rate"]:7.1%}   '
        f'{random_eval["success_rate"]:7.1%}'
    )
    print(
        f'Mean Length:      {dqn_final_eval["mean_length"]:8.2f}  {q_final_eval["mean_length"]:8.2f}  '
        f'{random_eval["mean_length"]:8.2f}'
    )

    # Plot results
    print("\n" + "=" * 80)
    print("Generating Training Plots")
    print("=" * 80)

    try:
        import matplotlib

        matplotlib.use("Agg")
        plot_dqn_training_results(dqn_stats, q_stats=q_stats, save_path="/tmp/dqn_training_results.png")
        print("\nPlots saved to /tmp/dqn_training_results.png")
    except Exception as e:
        print(f"\nCould not generate plots: {e}")

    # Test checkpoint loading
    print("\n" + "=" * 80)
    print("Testing Checkpoint Load")
    print("=" * 80)

    test_agent = DQNAgent(state_dim=state_dim, action_dim=action_dim, hidden_layers=[64, 64])
    test_agent.load(checkpoint_path)

    test_eval = evaluate_dqn_agent(env, test_agent, num_episodes=20)
    print("\nLoaded Agent Performance (20 episodes):")
    print(f'  Mean Reward: {test_eval["mean_reward"]:.2f} ± {test_eval["std_reward"]:.2f}')
    print(f'  Success Rate: {test_eval["success_rate"]:.2%}')
    print("Checkpoint load successful!")

    # Close environment
    env.close()
    print("\nTraining complete!")


if __name__ == "__main__":
    main()
