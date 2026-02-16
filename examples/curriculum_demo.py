"""
Curriculum Learning Wrapper Demo

This script demonstrates the usage of the CurriculumWrapper with SimpleGridWorld.
It shows how difficulty automatically adjusts based on agent performance.
"""

from environments import CurriculumWrapper
from examples.simple_gridworld import SimpleGridWorld
import numpy as np


def run_demo():
    """Run a demonstration of curriculum learning."""
    print("=" * 80)
    print("Curriculum Learning Wrapper Demo")
    print("=" * 80)

    # Create a GridWorld environment
    env = SimpleGridWorld({'episode_length': 50, 'reward_type': 'dense'})

    # Wrap it with curriculum learning
    curriculum_env = CurriculumWrapper(
        env,
        initial_difficulty=0.0,
        window_size=10,
        success_threshold=0.7,
        failure_threshold=0.3,
        difficulty_step=0.2,
        min_episodes_before_change=5,
        enable_decrease=True
    )

    print(f"\nInitial Configuration:")
    print(f"  - Initial Difficulty: {curriculum_env.get_difficulty():.2f}")
    print(f"  - Window Size: 10 episodes")
    print(f"  - Success Threshold: 0.70 (difficulty increases)")
    print(f"  - Failure Threshold: 0.30 (difficulty decreases)")
    print(f"  - Difficulty Step: 0.20")
    print()

    # Simulate training with improving performance
    print("Simulating agent training with gradually improving performance...")
    print("-" * 80)

    # Phase 1: Poor performance (30% success)
    print("\nPhase 1: Early Training (30% success rate)")
    for episode in range(10):
        obs, info = curriculum_env.reset(seed=42 + episode)
        total_reward = 0

        # Simulate poor performance - succeed only 30% of the time
        succeed = np.random.random() < 0.3

        if succeed:
            # Take good actions to reach goal
            for _ in range(50):
                # Random action (in reality, this would be agent's action)
                action = curriculum_env.action_space.sample()
                obs, reward, terminated, truncated, info = curriculum_env.step(action)
                total_reward += reward
                if terminated or truncated:
                    break
        else:
            # Take few steps (simulating failure)
            for _ in range(5):
                action = curriculum_env.action_space.sample()
                obs, reward, terminated, truncated, info = curriculum_env.step(action)
                total_reward += reward
                if terminated or truncated:
                    break

        print(f"  Episode {episode + 1:2d}: Reward={total_reward:6.1f}, "
              f"Success={info.get('goal_reached', False)}, "
              f"Difficulty={info['curriculum_difficulty']:.2f}, "
              f"SuccessRate={info['curriculum_success_rate']:.2f}")

    # Phase 2: Improving performance (60% success)
    print("\nPhase 2: Learning (60% success rate)")
    for episode in range(10, 20):
        obs, info = curriculum_env.reset(seed=42 + episode)
        total_reward = 0

        # Simulate improving performance
        succeed = np.random.random() < 0.6

        if succeed:
            for _ in range(50):
                action = curriculum_env.action_space.sample()
                obs, reward, terminated, truncated, info = curriculum_env.step(action)
                total_reward += reward
                if terminated or truncated:
                    break
        else:
            for _ in range(5):
                action = curriculum_env.action_space.sample()
                obs, reward, terminated, truncated, info = curriculum_env.step(action)
                total_reward += reward
                if terminated or truncated:
                    break

        print(f"  Episode {episode + 1:2d}: Reward={total_reward:6.1f}, "
              f"Success={info.get('goal_reached', False)}, "
              f"Difficulty={info['curriculum_difficulty']:.2f}, "
              f"SuccessRate={info['curriculum_success_rate']:.2f}")

    # Phase 3: Good performance (80% success)
    print("\nPhase 3: Mastery (80% success rate)")
    for episode in range(20, 30):
        obs, info = curriculum_env.reset(seed=42 + episode)
        total_reward = 0

        # Simulate good performance
        succeed = np.random.random() < 0.8

        if succeed:
            for _ in range(50):
                action = curriculum_env.action_space.sample()
                obs, reward, terminated, truncated, info = curriculum_env.step(action)
                total_reward += reward
                if terminated or truncated:
                    break
        else:
            for _ in range(5):
                action = curriculum_env.action_space.sample()
                obs, reward, terminated, truncated, info = curriculum_env.step(action)
                total_reward += reward
                if terminated or truncated:
                    break

        print(f"  Episode {episode + 1:2d}: Reward={total_reward:6.1f}, "
              f"Success={info.get('goal_reached', False)}, "
              f"Difficulty={info['curriculum_difficulty']:.2f}, "
              f"SuccessRate={info['curriculum_success_rate']:.2f}")

    print("\n" + "=" * 80)
    print("Demo Complete!")
    print(f"\nFinal Difficulty: {curriculum_env.get_difficulty():.2f}")
    print(f"Final Success Rate: {curriculum_env._get_success_rate():.2f}")
    print("\nKey Observations:")
    print("  - Difficulty started at 0.00 (3x3 grid)")
    print("  - As success rate improved above 0.70, difficulty increased")
    print("  - Grid size increased to make the task harder")
    print("  - This enables progressive learning from easy to hard tasks")
    print("=" * 80)


if __name__ == '__main__':
    run_demo()
