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

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def train_random_agent(env, num_episodes=100, seed=None, early_stopping_reward=None):
    """
    Train a random agent (baseline).
    
    Args:
        env: Environment instance
        num_episodes: Number of episodes to run
        seed: Random seed for reproducibility
        early_stopping_reward: Stop early if this average reward is reached
    
    Returns:
        Training statistics
    """
    if seed is not None:
        np.random.seed(seed)
    
    episode_rewards = []
    episode_lengths = []
    success_count = 0
    
    # Structured metrics collection
    metrics_list = []
    
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
        
        # Collect structured metrics
        metrics_list.append({
            'episode': episode + 1,
            'reward': episode_reward,
            'length': steps,
            'success': goal_reached
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
            
            # Early stopping check
            if early_stopping_reward is not None and avg_reward >= early_stopping_reward:
                logger.info(f'Early stopping: reached target reward {early_stopping_reward}')
                break
    
    metrics_df = pd.DataFrame(metrics_list)
    
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
    """Main training loop."""
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='Train RL agent on SimpleGridWorld')
    parser.add_argument('--config', type=str, default='configs/default_config.yaml',
                       help='Path to configuration file')
    parser.add_argument('--episodes', type=int, default=100,
                       help='Number of training episodes')
    parser.add_argument('--eval-interval', type=int, default=20,
                       help='Evaluation interval')
    parser.add_argument('--seed', type=int, default=42,
                       help='Random seed for reproducibility')
    parser.add_argument('--grid-size', type=int, default=10,
                       help='Grid size for environment')
    parser.add_argument('--early-stopping', type=float, default=None,
                       help='Early stopping reward threshold')
    parser.add_argument('--output-dir', type=str, default='outputs',
                       help='Output directory for results')
    parser.add_argument('--log-level', type=str, default='INFO',
                       choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                       help='Logging level')
    
    args = parser.parse_args()
    
    # Set logging level
    logger.setLevel(getattr(logging, args.log_level))
    
    logger.info('RL Environment Training Example')
    logger.info('=' * 50)
    
    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True, parents=True)
    
    # Load configuration
    config = {}
    try:
        with open(args.config, 'r') as f:
            config = yaml.safe_load(f)
        logger.info(f'Loaded configuration from {args.config}')
    except FileNotFoundError:
        logger.warning(f'Config file not found: {args.config}, using defaults')
    
    # Create environment
    env_config = {
        'grid_size': args.grid_size,
        'episode_length': 100,
        'seed': args.seed
    }
    env = SimpleGridWorld(env_config)
    
    logger.info(f'\nEnvironment: SimpleGridWorld')
    logger.info(f'Grid size: {env_config["grid_size"]}x{env_config["grid_size"]}')
    logger.info(f'Max episode length: {env_config["episode_length"]}')
    logger.info(f'Action space: {env.action_space}')
    logger.info(f'Observation space: {env.observation_space}')
    logger.info(f'Random seed: {args.seed}')
    
    # Train random agent (baseline)
    logger.info('\n' + '=' * 50)
    logger.info('Training Random Agent (Baseline)')
    logger.info('=' * 50)
    
    stats = train_random_agent(
        env, 
        num_episodes=args.episodes,
        seed=args.seed,
        early_stopping_reward=args.early_stopping
    )
    
    logger.info('\n' + '=' * 50)
    logger.info('Training Complete!')
    logger.info('=' * 50)
    logger.info(f'Total Episodes: {len(stats["episode_rewards"])}')
    logger.info(f'Average Reward: {stats["avg_reward"]:.2f}')
    logger.info(f'Average Episode Length: {stats["avg_length"]:.2f}')
    logger.info(f'Success Rate: {stats["success_rate"]:.2%}')
    
    # Save metrics to CSV
    metrics_csv_path = output_dir / 'training_metrics.csv'
    stats['metrics_df'].to_csv(metrics_csv_path, index=False)
    logger.info(f'\nSaved training metrics to {metrics_csv_path}')
    
    # Evaluation
    logger.info('\n' + '=' * 50)
    logger.info('Evaluation')
    logger.info('=' * 50)
    
    eval_stats = evaluate_agent(env, num_episodes=args.eval_interval)
    logger.info(f'Mean Reward: {eval_stats["mean_reward"]:.2f} ± {eval_stats["std_reward"]:.2f}')
    logger.info(f'Mean Length: {eval_stats["mean_length"]:.2f} ± {eval_stats["std_length"]:.2f}')
    logger.info(f'Success Rate: {eval_stats["success_rate"]:.2%}')
    
    # Close environment
    env.close()
    logger.info('\nDone!')


if __name__ == '__main__':
    main()
