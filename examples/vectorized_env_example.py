"""
Example: Using Vectorized Environments

This example demonstrates how to use SyncVectorEnv and AsyncVectorEnv
to run multiple environment instances in parallel for efficient training.
"""

import numpy as np
from environments.vec_env import SyncVectorEnv, AsyncVectorEnv
from examples.simple_gridworld import SimpleGridWorld


def main():
    """Demonstrate usage of vectorized environments."""

    # Configuration for environments
    config = {"grid_size": 8, "episode_length": 100}

    # Factory function to create environments
    def env_fn():
        return SimpleGridWorld(config)

    num_envs = 8
    num_steps = 50

    print("=" * 80)
    print("Vectorized Environment Example")
    print("=" * 80)

    # Example 1: Using SyncVectorEnv
    print("\n1. SyncVectorEnv (Sequential Execution)")
    print("-" * 80)

    sync_env = SyncVectorEnv(env_fn, num_envs=num_envs)
    print(f"Created {num_envs} environments")

    # Reset all environments
    obs = sync_env.reset(seed=42)
    print(f"Reset complete. Observations shape: {obs.shape}")

    # Run some steps
    total_reward = np.zeros(num_envs)
    episodes_completed = 0

    for step in range(num_steps):
        # Sample random actions for all environments
        actions = np.array([sync_env.single_action_space.sample() for _ in range(num_envs)])

        # Step all environments
        obs, rewards, terminated, truncated, infos = sync_env.step(actions)

        total_reward += rewards

        # Count episodes that completed (auto-reset happens automatically)
        episodes_completed += sum(terminated) + sum(truncated)

    print(f"Completed {num_steps} steps")
    print(f"Episodes completed (with auto-reset): {episodes_completed}")
    print(f"Average reward per environment: {total_reward.mean():.2f}")
    print(f"Total cumulative reward: {total_reward.sum():.2f}")

    sync_env.close()
    print("SyncVectorEnv closed")

    # Example 2: Using AsyncVectorEnv
    print("\n2. AsyncVectorEnv (Parallel Execution)")
    print("-" * 80)

    async_env = AsyncVectorEnv(env_fn, num_envs=num_envs)
    print(f"Created {num_envs} parallel environments")

    # Reset all environments
    obs = async_env.reset(seed=42)
    print(f"Reset complete. Observations shape: {obs.shape}")

    # Run some steps
    total_reward = np.zeros(num_envs)
    episodes_completed = 0

    for step in range(num_steps):
        # Sample random actions for all environments
        actions = np.array([async_env.single_action_space.sample() for _ in range(num_envs)])

        # Step all environments (happens in parallel)
        obs, rewards, terminated, truncated, infos = async_env.step(actions)

        total_reward += rewards

        # Count episodes that completed
        episodes_completed += sum(terminated) + sum(truncated)

    print(f"Completed {num_steps} steps")
    print(f"Episodes completed (with auto-reset): {episodes_completed}")
    print(f"Average reward per environment: {total_reward.mean():.2f}")
    print(f"Total cumulative reward: {total_reward.sum():.2f}")

    async_env.close()
    print("AsyncVectorEnv closed")

    # Example 3: Demonstrating auto-reset behavior
    print("\n3. Auto-Reset Behavior")
    print("-" * 80)

    # Create environment with short episodes
    def short_env_fn():
        return SimpleGridWorld({"grid_size": 5, "episode_length": 5})

    vec_env = SyncVectorEnv(short_env_fn, num_envs=2)
    vec_env.reset(seed=123)

    print("Running until episode terminates (max 5 steps)...")
    for step in range(6):
        actions = np.array([1, 1])  # Move right
        obs, rewards, terminated, truncated, infos = vec_env.step(actions)

        print(f"Step {step + 1}:")
        for i, (term, trunc, info) in enumerate(zip(terminated, truncated, infos)):
            if term or trunc:
                print(f"  Env {i}: Episode ended! Auto-reset occurred.")
                print(f"  Final observation stored in info: {info.get('final_observation')}")
            else:
                print(f"  Env {i}: Continuing (obs: {obs[i]})")

    vec_env.close()

    print("\n" + "=" * 80)
    print("Example complete!")
    print("=" * 80)


if __name__ == "__main__":
    main()
