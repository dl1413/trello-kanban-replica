"""
Example: Training Script for RL Environments

This script demonstrates how to train an RL agent on a custom environment.
"""

import numpy as np
import yaml
import logging
import argparse
import pandas as pd
from pathlib import Path
from examples.simple_gridworld import SimpleGridWorld

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


def train_random_agent(env, num_episodes=100, seed=None, early_stopping_threshold=None):
    """
    Train a random agent (baseline) with metrics collection.

    Args:
        env: Environment instance
        num_episodes: Number of episodes to run
        seed: Random seed for reproducibility
        early_stopping_threshold: Stop if reward exceeds this threshold

    Returns:
        Training statistics including pandas DataFrame
    """
    if seed is not None:
        np.random.seed(seed)
        logger.info(f"Set random seed to {seed}")

    episode_rewards = []
    episode_lengths = []
    success_count = 0

    # Collect detailed metrics for each episode
    metrics_data = []

    logger.info(f"Starting training for {num_episodes} episodes")

    for episode in range(num_episodes):
        obs, info = env.reset(seed=seed + episode if seed is not None else None)
        terminated = False
        truncated = False
        episode_reward = 0
        steps = 0

        while not (terminated or truncated):
            # Random policy
            action = env.action_space.sample()
            obs, reward, terminated, truncated, info = env.step(action)

            episode_reward += reward
            steps += 1

        episode_rewards.append(episode_reward)
        episode_lengths.append(steps)

        goal_reached = info.get('goal_reached', False)
        if goal_reached:
            success_count += 1

        # Store metrics
        metrics_data.append({
            'episode': episode + 1,
            'reward': episode_reward,
            'length': steps,
            'success': goal_reached,
            'cumulative_success_rate': success_count / (episode + 1)
        })

        # Log progress
        if (episode + 1) % 10 == 0:
            avg_reward = np.mean(episode_rewards[-10:])
            avg_length = np.mean(episode_lengths[-10:])
            success_rate = success_count / (episode + 1)
            logger.info(f'Episode {episode + 1}/{num_episodes} | '
                        f'Avg Reward: {avg_reward:.2f} | '
                        f'Avg Length: {avg_length:.2f} | '
                        f'Success Rate: {success_rate:.2%}')

        # Early stopping
        if early_stopping_threshold is not None and episode_reward >= early_stopping_threshold:
            logger.info(f"Early stopping triggered at episode {episode + 1} "
                        f"(reward: {episode_reward:.2f} >= threshold: {early_stopping_threshold})")
            break

    # Create DataFrame from metrics
    metrics_df = pd.DataFrame(metrics_data)

    logger.info(f"Training completed after {len(episode_rewards)} episodes")

    return {
        'episode_rewards': episode_rewards,
        'episode_lengths': episode_lengths,
        'success_rate': success_count / len(episode_rewards),
        'avg_reward': np.mean(episode_rewards),
        'avg_length': np.mean(episode_lengths),
        'metrics_df': metrics_df
    }


def evaluate_agent(env, num_episodes=10):
    """
    Evaluate an agent's performance.
    
    Args:
        env: Environment instance
        num_episodes: Number of evaluation episodes
    
    Returns:
        Evaluation metrics
    """
    rewards = []
    lengths = []
    successes = []
    
    for episode in range(num_episodes):
        obs, info = env.reset()
        terminated = False
        truncated = False
        episode_reward = 0
        steps = 0
        
        while not (terminated or truncated):
            action = env.action_space.sample()
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


def main():
    """Main training loop with CLI arguments."""
    parser = argparse.ArgumentParser(description='Train RL agent on SimpleGridWorld')
    parser.add_argument('--episodes', type=int, default=100, help='Number of training episodes')
    parser.add_argument('--eval-episodes', type=int, default=20, help='Number of evaluation episodes')
    parser.add_argument('--grid-size', type=int, default=10, help='Grid size')
    parser.add_argument('--episode-length', type=int, default=100, help='Max episode length')
    parser.add_argument('--seed', type=int, default=None, help='Random seed for reproducibility')
    parser.add_argument('--early-stopping', type=float, default=None,
                        help='Early stopping threshold for episode reward')
    parser.add_argument('--save-metrics', type=str, default=None,
                        help='Path to save metrics CSV file')
    args = parser.parse_args()

    logger.info('RL Environment Training Example')
    logger.info('=' * 50)

    # Create environment
    env_config = {
        'grid_size': args.grid_size,
        'episode_length': args.episode_length
    }
    env = SimpleGridWorld(env_config)

    logger.info(f'Environment: SimpleGridWorld')
    logger.info(f'Grid size: {args.grid_size}x{args.grid_size}')
    logger.info(f'Max episode length: {args.episode_length}')
    logger.info(f'Action space: {env.action_space}')
    logger.info(f'Observation space: {env.observation_space}')
    logger.info(f'Random seed: {args.seed if args.seed is not None else "None"}')

    # Train random agent (baseline)
    logger.info('\n' + '=' * 50)
    logger.info('Training Random Agent (Baseline)')
    logger.info('=' * 50)

    stats = train_random_agent(
        env,
        num_episodes=args.episodes,
        seed=args.seed,
        early_stopping_threshold=args.early_stopping
    )

    logger.info('\n' + '=' * 50)
    logger.info('Training Complete!')
    logger.info('=' * 50)
    logger.info(f'Total Episodes: {len(stats["episode_rewards"])}')
    logger.info(f'Average Reward: {stats["avg_reward"]:.2f}')
    logger.info(f'Average Episode Length: {stats["avg_length"]:.2f}')
    logger.info(f'Success Rate: {stats["success_rate"]:.2%}')

    # Save metrics if requested
    if args.save_metrics:
        metrics_path = Path(args.save_metrics)
        metrics_path.parent.mkdir(parents=True, exist_ok=True)
        stats['metrics_df'].to_csv(metrics_path, index=False)
        logger.info(f'\nMetrics saved to {metrics_path}')

    # Evaluation
    logger.info('\n' + '=' * 50)
    logger.info('Evaluation')
    logger.info('=' * 50)

    eval_stats = evaluate_agent(env, num_episodes=args.eval_episodes)
    logger.info(f'Mean Reward: {eval_stats["mean_reward"]:.2f} ± {eval_stats["std_reward"]:.2f}')
    logger.info(f'Mean Length: {eval_stats["mean_length"]:.2f} ± {eval_stats["std_length"]:.2f}')
    logger.info(f'Success Rate: {eval_stats["success_rate"]:.2%}')

    # Close environment
    env.close()
    logger.info('\nDone!')


if __name__ == '__main__':
    main()
