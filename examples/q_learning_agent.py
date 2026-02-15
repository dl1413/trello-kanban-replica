"""
Q-Learning Agent Example

This module demonstrates a simple tabular Q-Learning agent trained on
the SimpleGridWorld environment. It shows how a learning agent can
improve over time compared to the random baseline.
"""

import numpy as np
import matplotlib.pyplot as plt
from collections import defaultdict
from typing import Tuple, Dict, Any, Optional
from examples.simple_gridworld import SimpleGridWorld


class QLearningAgent:
    """
    Tabular Q-Learning agent with epsilon-greedy exploration.

    This agent learns a value function Q(s,a) for discrete state-action
    pairs using the Q-Learning algorithm.
    """

    def __init__(
        self,
        action_space_size: int,
        learning_rate: float = 0.1,
        discount_factor: float = 0.99,
        epsilon: float = 1.0,
        epsilon_decay: float = 0.995,
        epsilon_min: float = 0.01,
        learning_rate_decay: Optional[float] = None,
        seed: Optional[int] = None
    ):
        """
        Initialize Q-Learning agent.

        Args:
            action_space_size: Number of possible actions
            learning_rate: Learning rate (alpha)
            discount_factor: Discount factor (gamma)
            epsilon: Initial exploration rate
            epsilon_decay: Decay rate for epsilon
            epsilon_min: Minimum epsilon value
            learning_rate_decay: Optional decay rate for learning rate (alpha)
            seed: Random seed for reproducibility
        """
        self.action_space_size = action_space_size
        self.learning_rate = learning_rate
        self.initial_learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.epsilon_min = epsilon_min
        self.learning_rate_decay = learning_rate_decay

        # Create seeded RNG for reproducibility
        self.rng = np.random.default_rng(seed)

        # Q-table stored as nested dict: state -> action -> value
        self.q_table = defaultdict(lambda: np.zeros(action_space_size))

        # Statistics
        self.total_steps = 0
        self.episodes_trained = 0

    def _state_to_key(self, state: np.ndarray) -> Tuple:
        """Convert state array to hashable key for Q-table."""
        return tuple(state.flatten())

    def select_action(self, state: np.ndarray, training: bool = True) -> int:
        """
        Select action using epsilon-greedy policy.

        Args:
            state: Current state observation
            training: If True, use epsilon-greedy; if False, use greedy

        Returns:
            Selected action
        """
        state_key = self._state_to_key(state)

        # Epsilon-greedy exploration during training
        if training and self.rng.random() < self.epsilon:
            return int(self.rng.integers(0, self.action_space_size))

        # Greedy action selection
        q_values = self.q_table[state_key]
        return int(np.argmax(q_values))

    def update(
        self,
        state: np.ndarray,
        action: int,
        reward: float,
        next_state: np.ndarray,
        terminated: bool
    ):
        """
        Update Q-value using Q-Learning update rule.

        Args:
            state: Current state
            action: Action taken
            reward: Reward received
            next_state: Next state
            terminated: Whether episode terminated
        """
        state_key = self._state_to_key(state)
        next_state_key = self._state_to_key(next_state)

        # Current Q-value
        current_q = self.q_table[state_key][action]

        # TD target
        if terminated:
            target_q = reward
        else:
            max_next_q = np.max(self.q_table[next_state_key])
            target_q = reward + self.discount_factor * max_next_q

        # Q-Learning update
        self.q_table[state_key][action] += self.learning_rate * (target_q - current_q)

        self.total_steps += 1

    def decay_epsilon(self):
        """Decay exploration rate and optionally learning rate."""
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)

        # Apply learning rate decay if configured
        if self.learning_rate_decay is not None:
            self.learning_rate = max(0.001, self.learning_rate * self.learning_rate_decay)

        self.episodes_trained += 1

    def get_statistics(self) -> Dict[str, Any]:
        """Get agent statistics."""
        return {
            'total_steps': self.total_steps,
            'episodes_trained': self.episodes_trained,
            'epsilon': self.epsilon,
            'learning_rate': self.learning_rate,
            'q_table_size': len(self.q_table)
        }

    def save(self, filepath: str):
        """
        Save Q-table to file.

        Args:
            filepath: Path to save the Q-table
        """
        import json

        # Convert defaultdict to regular dict for JSON serialization
        q_table_serializable = {}
        for k, v in self.q_table.items():
            # Convert key tuple to use Python ints (not numpy ints) for safe serialization
            key_str = str(tuple(int(x) if hasattr(x, 'item') else x for x in k))
            # Convert numpy arrays to lists, handle both arrays and lists
            if hasattr(v, 'tolist'):
                q_table_serializable[key_str] = v.tolist()
            else:
                q_table_serializable[key_str] = list(v)

        save_data = {
            'q_table': q_table_serializable,
            'action_space_size': self.action_space_size,
            'learning_rate': self.learning_rate,
            'initial_learning_rate': self.initial_learning_rate,
            'discount_factor': self.discount_factor,
            'epsilon': self.epsilon,
            'epsilon_decay': self.epsilon_decay,
            'epsilon_min': self.epsilon_min,
            'learning_rate_decay': self.learning_rate_decay,
            'total_steps': self.total_steps,
            'episodes_trained': self.episodes_trained
        }

        with open(filepath, 'w') as f:
            json.dump(save_data, f, indent=2)

    @classmethod
    def load(cls, filepath: str, seed: Optional[int] = None) -> 'QLearningAgent':
        """
        Load Q-table from file.

        Args:
            filepath: Path to load the Q-table from
            seed: Optional seed for the loaded agent's RNG

        Returns:
            Loaded QLearningAgent instance
        """
        import json
        import ast

        with open(filepath, 'r') as f:
            save_data = json.load(f)

        # Create agent with saved parameters
        agent = cls(
            action_space_size=save_data['action_space_size'],
            learning_rate=save_data['learning_rate'],
            discount_factor=save_data['discount_factor'],
            epsilon=save_data['epsilon'],
            epsilon_decay=save_data['epsilon_decay'],
            epsilon_min=save_data['epsilon_min'],
            learning_rate_decay=save_data.get('learning_rate_decay'),
            seed=seed
        )

        # Restore Q-table
        agent.q_table = defaultdict(lambda: np.zeros(agent.action_space_size))
        for k, v in save_data['q_table'].items():
            # Safely convert string key back to tuple using ast.literal_eval
            agent.q_table[ast.literal_eval(k)] = np.array(v)

        # Restore statistics
        agent.initial_learning_rate = save_data.get(
            'initial_learning_rate', save_data['learning_rate']
        )
        agent.total_steps = save_data.get('total_steps', 0)
        agent.episodes_trained = save_data.get('episodes_trained', 0)

        return agent


def train_q_learning(
    env: SimpleGridWorld,
    agent: QLearningAgent,
    num_episodes: int = 1000,
    max_steps: int = 200,
    eval_interval: int = 50,
    verbose: bool = True
) -> Dict[str, Any]:
    """
    Train Q-Learning agent on the environment.

    Args:
        env: Environment instance
        agent: Q-Learning agent
        num_episodes: Number of training episodes
        max_steps: Maximum steps per episode
        eval_interval: Evaluate every N episodes
        verbose: Print progress

    Returns:
        Training statistics
    """
    episode_rewards = []
    episode_lengths = []
    success_count = 0
    eval_rewards = []
    eval_success_rates = []

    for episode in range(num_episodes):
        obs, info = env.reset()
        episode_reward = 0
        steps = 0

        terminated = False
        truncated = False

        while not (terminated or truncated) and steps < max_steps:
            # Select action
            action = agent.select_action(obs, training=True)

            # Take step
            next_obs, reward, terminated, truncated, info = env.step(action)

            # Update Q-table
            agent.update(obs, action, reward, next_obs, terminated)

            obs = next_obs
            episode_reward += reward
            steps += 1

        # Decay epsilon
        agent.decay_epsilon()

        # Record statistics
        episode_rewards.append(episode_reward)
        episode_lengths.append(steps)
        if info.get('goal_reached', False):
            success_count += 1

        # Evaluation
        if (episode + 1) % eval_interval == 0:
            eval_stats = evaluate_agent(env, agent, num_episodes=20)
            eval_rewards.append(eval_stats['mean_reward'])
            eval_success_rates.append(eval_stats['success_rate'])

            if verbose:
                avg_reward = np.mean(episode_rewards[-eval_interval:])
                avg_length = np.mean(episode_lengths[-eval_interval:])
                success_rate = success_count / (episode + 1)
                print(f'Episode {episode + 1}/{num_episodes} | '
                      f'Avg Reward: {avg_reward:.2f} | '
                      f'Avg Length: {avg_length:.2f} | '
                      f'Success Rate: {success_rate:.2%} | '
                      f'Epsilon: {agent.epsilon:.3f} | '
                      f'Eval Reward: {eval_stats["mean_reward"]:.2f} | '
                      f'Eval Success: {eval_stats["success_rate"]:.2%}')

    return {
        'episode_rewards': episode_rewards,
        'episode_lengths': episode_lengths,
        'success_rate': success_count / num_episodes,
        'eval_rewards': eval_rewards,
        'eval_success_rates': eval_success_rates,
        'agent_stats': agent.get_statistics()
    }


def evaluate_agent(
    env: SimpleGridWorld,
    agent: QLearningAgent,
    num_episodes: int = 100,
    max_steps: Optional[int] = None
) -> Dict[str, float]:
    """
    Evaluate agent performance without exploration.

    Args:
        env: Environment instance
        agent: Trained agent
        num_episodes: Number of evaluation episodes
        max_steps: Maximum steps per episode (defaults to env.episode_length)

    Returns:
        Evaluation metrics
    """
    if max_steps is None:
        max_steps = env.episode_length

    rewards = []
    lengths = []
    successes = []

    for _ in range(num_episodes):
        obs, info = env.reset()
        episode_reward = 0
        steps = 0

        terminated = False
        truncated = False

        while not (terminated or truncated) and steps < max_steps:
            # Greedy action selection (no exploration)
            action = agent.select_action(obs, training=False)
            obs, reward, terminated, truncated, info = env.step(action)
            episode_reward += reward
            steps += 1

        rewards.append(episode_reward)
        lengths.append(steps)
        successes.append(info.get('goal_reached', False))

    return {
        'mean_reward': np.mean(rewards),
        'std_reward': np.std(rewards),
        'mean_length': np.mean(lengths),
        'std_length': np.std(lengths),
        'success_rate': np.mean(successes)
    }


def plot_training_results(stats: Dict[str, Any], save_path: str = None):
    """
    Plot training results.

    Args:
        stats: Training statistics dictionary
        save_path: Optional path to save figure
    """
    fig, axes = plt.subplots(2, 2, figsize=(12, 8))

    # Episode rewards
    ax = axes[0, 0]
    ax.plot(stats['episode_rewards'], alpha=0.3, label='Episode Reward')
    window = 50
    if len(stats['episode_rewards']) >= window:
        moving_avg = np.convolve(
            stats['episode_rewards'],
            np.ones(window) / window,
            mode='valid'
        )
        ax.plot(range(window - 1, len(stats['episode_rewards'])),
                moving_avg, label=f'{window}-Episode Moving Avg', linewidth=2)
    ax.set_xlabel('Episode')
    ax.set_ylabel('Total Reward')
    ax.set_title('Training Rewards')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # Episode lengths
    ax = axes[0, 1]
    ax.plot(stats['episode_lengths'], alpha=0.3, label='Episode Length')
    if len(stats['episode_lengths']) >= window:
        moving_avg = np.convolve(
            stats['episode_lengths'],
            np.ones(window) / window,
            mode='valid'
        )
        ax.plot(range(window - 1, len(stats['episode_lengths'])),
                moving_avg, label=f'{window}-Episode Moving Avg', linewidth=2)
    ax.set_xlabel('Episode')
    ax.set_ylabel('Steps')
    ax.set_title('Episode Lengths')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # Evaluation rewards
    ax = axes[1, 0]
    eval_episodes = np.arange(len(stats['eval_rewards'])) * 50 + 50
    ax.plot(eval_episodes, stats['eval_rewards'], marker='o', linewidth=2)
    ax.set_xlabel('Episode')
    ax.set_ylabel('Mean Evaluation Reward')
    ax.set_title('Evaluation Performance')
    ax.grid(True, alpha=0.3)

    # Success rate
    ax = axes[1, 1]
    ax.plot(eval_episodes, stats['eval_success_rates'], marker='o', linewidth=2, color='green')
    ax.set_xlabel('Episode')
    ax.set_ylabel('Success Rate')
    ax.set_title('Evaluation Success Rate')
    ax.set_ylim([0, 1.05])
    ax.grid(True, alpha=0.3)

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f'Saved plot to {save_path}')

    return fig


def main():
    """Main training and evaluation loop."""
    print('=' * 70)
    print('Q-Learning Agent Training on SimpleGridWorld')
    print('=' * 70)

    # Environment configuration
    env_config = {
        'grid_size': 5,
        'episode_length': 100,
        'reward_type': 'sparse'  # or 'dense' for shaped rewards
    }

    # Create environment
    env = SimpleGridWorld(env_config)

    print('\nEnvironment Configuration:')
    print(f'  Grid Size: {env.grid_size}x{env.grid_size}')
    print(f'  Max Episode Length: {env.episode_length}')
    print(f'  Reward Type: {env.reward_type}')
    print(f'  Action Space: {env.action_space}')
    print(f'  Observation Space: {env.observation_space}')

    # Create Q-Learning agent
    agent = QLearningAgent(
        action_space_size=env.action_space.n,
        learning_rate=0.1,
        discount_factor=0.95,
        epsilon=1.0,
        epsilon_decay=0.995,
        epsilon_min=0.01
    )

    print('\nAgent Configuration:')
    print(f'  Learning Rate: {agent.learning_rate}')
    print(f'  Discount Factor: {agent.discount_factor}')
    print(f'  Initial Epsilon: {agent.epsilon}')
    print(f'  Epsilon Decay: {agent.epsilon_decay}')
    print(f'  Min Epsilon: {agent.epsilon_min}')

    # Train agent
    print('\n' + '=' * 70)
    print('Training Agent')
    print('=' * 70 + '\n')

    num_episodes = 500
    stats = train_q_learning(
        env=env,
        agent=agent,
        num_episodes=num_episodes,
        max_steps=100,
        eval_interval=50,
        verbose=True
    )

    # Final evaluation
    print('\n' + '=' * 70)
    print('Final Evaluation')
    print('=' * 70)

    final_eval = evaluate_agent(env, agent, num_episodes=100)
    print('\nFinal Performance (100 episodes):')
    print(f'  Mean Reward: {final_eval["mean_reward"]:.2f} ± {final_eval["std_reward"]:.2f}')
    print(f'  Mean Length: {final_eval["mean_length"]:.2f} ± {final_eval["std_length"]:.2f}')
    print(f'  Success Rate: {final_eval["success_rate"]:.2%}')

    # Agent statistics
    agent_stats = agent.get_statistics()
    print('\nAgent Statistics:')
    print(f'  Total Steps: {agent_stats["total_steps"]:,}')
    print(f'  Episodes Trained: {agent_stats["episodes_trained"]:,}')
    print(f'  Final Epsilon: {agent_stats["epsilon"]:.4f}')
    print(f'  Q-Table Size: {agent_stats["q_table_size"]:,} states')

    # Compare with random baseline
    print('\n' + '=' * 70)
    print('Random Baseline Comparison')
    print('=' * 70)

    # Create a dummy agent for random baseline
    class RandomAgent:
        def select_action(self, state, training=True):
            return env.action_space.sample()

    random_agent = RandomAgent()
    random_eval = evaluate_agent(env, random_agent, num_episodes=100)

    print('\nRandom Agent Performance (100 episodes):')
    print(f'  Mean Reward: {random_eval["mean_reward"]:.2f} ± {random_eval["std_reward"]:.2f}')
    print(f'  Mean Length: {random_eval["mean_length"]:.2f} ± {random_eval["std_length"]:.2f}')
    print(f'  Success Rate: {random_eval["success_rate"]:.2%}')

    improvement = (
        (final_eval["mean_reward"] - random_eval["mean_reward"])
        / abs(random_eval["mean_reward"]) * 100
        if abs(random_eval["mean_reward"]) > 1e-8 else float('inf')
    )
    improvement_str = f'{improvement:+.1f}%' if improvement != float('inf') else '+∞%'
    print(f'\nImprovement over Random: {improvement_str}')

    # Plot results
    print('\n' + '=' * 70)
    print('Generating Training Plots')
    print('=' * 70)

    try:
        import matplotlib
        # Use Agg backend for non-GUI environments
        matplotlib.use('Agg')
        plot_training_results(stats, save_path='/tmp/q_learning_results.png')
        print('\nPlot saved to /tmp/q_learning_results.png')
    except Exception as e:
        print(f'\nCould not generate plots: {e}')

    # Close environment
    env.close()
    print('\nTraining complete!')


if __name__ == '__main__':
    main()
