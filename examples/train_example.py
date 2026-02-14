"""
Example: Training Script for RL Environments

This script demonstrates how to train an RL agent on a custom environment.
"""

import numpy as np
import yaml
from examples.simple_gridworld import SimpleGridWorld


def train_random_agent(env, num_episodes=100):
    """
    Train a random agent (baseline).
    
    Args:
        env: Environment instance
        num_episodes: Number of episodes to run
    
    Returns:
        Training statistics
    """
    episode_rewards = []
    episode_lengths = []
    success_count = 0
    
    for episode in range(num_episodes):
        obs, info = env.reset()
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
        
        if info.get('goal_reached', False):
            success_count += 1
        
        # Print progress
        if (episode + 1) % 10 == 0:
            avg_reward = np.mean(episode_rewards[-10:])
            avg_length = np.mean(episode_lengths[-10:])
            success_rate = success_count / (episode + 1)
            print(f'Episode {episode + 1}/{num_episodes} | '
                  f'Avg Reward: {avg_reward:.2f} | '
                  f'Avg Length: {avg_length:.2f} | '
                  f'Success Rate: {success_rate:.2%}')
    
    return {
        'episode_rewards': episode_rewards,
        'episode_lengths': episode_lengths,
        'success_rate': success_count / num_episodes,
        'avg_reward': np.mean(episode_rewards),
        'avg_length': np.mean(episode_lengths)
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
    print('RL Environment Training Example')
    print('=' * 50)
    
    # Load configuration
    config_path = 'configs/default_config.yaml'
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
    except FileNotFoundError:
        print(f'Config file not found: {config_path}')
        config = {}
    
    # Create environment
    env_config = {
        'grid_size': 10,
        'episode_length': 100,
        'seed': config.get('training', {}).get('seed', 42)
    }
    env = SimpleGridWorld(env_config)
    
    print(f'\nEnvironment: SimpleGridWorld')
    print(f'Grid size: {env_config["grid_size"]}x{env_config["grid_size"]}')
    print(f'Max episode length: {env_config["episode_length"]}')
    print(f'Action space: {env.action_space}')
    print(f'Observation space: {env.observation_space}')
    
    # Train random agent (baseline)
    print('\n' + '=' * 50)
    print('Training Random Agent (Baseline)')
    print('=' * 50)
    
    num_episodes = 100
    stats = train_random_agent(env, num_episodes)
    
    print('\n' + '=' * 50)
    print('Training Complete!')
    print('=' * 50)
    print(f'Total Episodes: {num_episodes}')
    print(f'Average Reward: {stats["avg_reward"]:.2f}')
    print(f'Average Episode Length: {stats["avg_length"]:.2f}')
    print(f'Success Rate: {stats["success_rate"]:.2%}')
    
    # Evaluation
    print('\n' + '=' * 50)
    print('Evaluation')
    print('=' * 50)
    
    eval_stats = evaluate_agent(env, num_episodes=20)
    print(f'Mean Reward: {eval_stats["mean_reward"]:.2f} ± {eval_stats["std_reward"]:.2f}')
    print(f'Mean Length: {eval_stats["mean_length"]:.2f} ± {eval_stats["std_length"]:.2f}')
    print(f'Success Rate: {eval_stats["success_rate"]:.2%}')
    
    # Close environment
    env.close()
    print('\nDone!')


if __name__ == '__main__':
    main()
