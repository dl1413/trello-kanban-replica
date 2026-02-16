"""
Curriculum Learning Wrapper for RL Environments

This module provides a wrapper that automatically adjusts environment difficulty
based on agent performance, implementing curriculum learning strategies.
"""

import logging
from collections import deque
from typing import Any, Dict, Optional, Tuple

import gymnasium as gym
import numpy as np

from environments.base_env import BaseEnvironment


# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CurriculumWrapper(gym.Wrapper):
    """
    Wrapper that implements automatic curriculum learning for any BaseEnvironment.

    The wrapper tracks agent performance over a rolling window of episodes and
    automatically adjusts environment difficulty based on success rate. For GridWorld
    environments, difficulty controls grid size, obstacle density, and goal distance.

    Args:
        env: The environment to wrap (must be a BaseEnvironment subclass)
        initial_difficulty: Starting difficulty level (0.0 to 1.0)
        window_size: Number of episodes to track for performance evaluation
        success_threshold: Success rate above which difficulty increases
        failure_threshold: Success rate below which difficulty decreases (optional)
        difficulty_step: Amount to change difficulty on each adjustment
        min_episodes_before_change: Minimum episodes before first difficulty change
        enable_decrease: Whether to allow difficulty to decrease

    Attributes:
        difficulty: Current difficulty level (0.0 to 1.0)
        success_history: Deque tracking success/failure of recent episodes
        episode_count: Total number of episodes completed
    """

    def __init__(
        self,
        env: BaseEnvironment,
        initial_difficulty: float = 0.0,
        window_size: int = 100,
        success_threshold: float = 0.7,
        failure_threshold: float = 0.3,
        difficulty_step: float = 0.1,
        min_episodes_before_change: int = 10,
        enable_decrease: bool = True
    ):
        """
        Initialize the curriculum wrapper.

        Args:
            env: The environment to wrap
            initial_difficulty: Starting difficulty (0.0 to 1.0)
            window_size: Number of episodes to track for success rate
            success_threshold: Success rate threshold to increase difficulty
            failure_threshold: Success rate threshold to decrease difficulty
            difficulty_step: Step size for difficulty changes
            min_episodes_before_change: Minimum episodes before adjusting difficulty
            enable_decrease: Whether to allow difficulty decreases
        """
        super().__init__(env)

        if not isinstance(env, BaseEnvironment):
            raise TypeError(f"Environment must be a BaseEnvironment subclass, got {type(env)}")

        if not 0.0 <= initial_difficulty <= 1.0:
            raise ValueError(f"initial_difficulty must be in [0, 1], got {initial_difficulty}")

        if not 0.0 < success_threshold <= 1.0:
            raise ValueError(f"success_threshold must be in (0, 1], got {success_threshold}")

        if not 0.0 <= failure_threshold < success_threshold:
            raise ValueError(f"failure_threshold must be in [0, success_threshold), got {failure_threshold}")

        if difficulty_step <= 0:
            raise ValueError(f"difficulty_step must be positive, got {difficulty_step}")

        self._difficulty = initial_difficulty
        self._window_size = window_size
        self._success_threshold = success_threshold
        self._failure_threshold = failure_threshold
        self._difficulty_step = difficulty_step
        self._min_episodes = min_episodes_before_change
        self._enable_decrease = enable_decrease

        self._success_history = deque(maxlen=window_size)
        self._episode_count = 0
        self._current_episode_success = False

        # Apply initial difficulty
        self._apply_difficulty_config()

        logger.info(f"CurriculumWrapper initialized with difficulty={initial_difficulty:.2f}")

    def get_difficulty(self) -> float:
        """
        Get the current difficulty level.

        Returns:
            Current difficulty value between 0.0 and 1.0
        """
        return self._difficulty

    def set_difficulty(self, difficulty: float) -> None:
        """
        Manually set the difficulty level.

        Args:
            difficulty: New difficulty level (0.0 to 1.0)

        Raises:
            ValueError: If difficulty is not in [0, 1]
        """
        if not 0.0 <= difficulty <= 1.0:
            raise ValueError(f"Difficulty must be in [0, 1], got {difficulty}")

        old_difficulty = self._difficulty
        self._difficulty = difficulty
        self._apply_difficulty_config()

        logger.info(f"Difficulty manually set: {old_difficulty:.2f} -> {self._difficulty:.2f}")

    def reset(
        self,
        seed: Optional[int] = None,
        options: Optional[Dict[str, Any]] = None
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Reset the environment with current difficulty settings.

        Args:
            seed: Random seed for reproducibility
            options: Additional reset options

        Returns:
            observation: Initial observation
            info: Additional information including difficulty level
        """
        # Check if previous episode was successful and update curriculum
        if self._episode_count > 0:
            self._update_curriculum()

        # Apply current difficulty configuration
        self._apply_difficulty_config()

        # Reset the wrapped environment
        obs, info = self.env.reset(seed=seed, options=options)

        # Add curriculum info
        info['curriculum_difficulty'] = self._difficulty
        info['curriculum_success_rate'] = self._get_success_rate()
        info['curriculum_episode_count'] = self._episode_count

        # Reset episode success flag
        self._current_episode_success = False

        return obs, info

    def step(self, action: int) -> Tuple[np.ndarray, float, bool, bool, Dict[str, Any]]:
        """
        Execute one step in the environment.

        Args:
            action: Action to take

        Returns:
            observation: Current observation
            reward: Reward for the action
            terminated: Whether a terminal state is reached
            truncated: Whether the episode is truncated
            info: Additional information including curriculum metrics
        """
        obs, reward, terminated, truncated, info = self.env.step(action)

        # Track success for curriculum (goal_reached or positive terminal reward)
        if terminated and not truncated:
            # Check if episode was successful
            self._current_episode_success = info.get('goal_reached', False) or reward > 0

        # If episode ended, record success/failure
        if terminated or truncated:
            self._success_history.append(self._current_episode_success)
            self._episode_count += 1

        # Add curriculum info
        info['curriculum_difficulty'] = self._difficulty
        info['curriculum_success_rate'] = self._get_success_rate()

        return obs, reward, terminated, truncated, info

    def _apply_difficulty_config(self) -> None:
        """
        Apply difficulty-based configuration to the wrapped environment.

        For GridWorld environments, modifies grid_size and obstacle configuration.
        For other environments, subclasses can override this method.
        """
        # Get environment class name
        env_class_name = self.env.__class__.__name__

        if 'GridWorld' in env_class_name or 'Grid' in env_class_name:
            self._apply_gridworld_difficulty()
        else:
            # For generic environments, pass difficulty in config
            if not hasattr(self.env, 'config'):
                self.env.config = {}
            self.env.config['difficulty'] = self._difficulty

    def _apply_gridworld_difficulty(self) -> None:
        """
        Apply difficulty settings specific to GridWorld environments.

        Difficulty mapping:
            0.0: 3x3 grid, no obstacles, close goal
            0.5: 7x7 grid, some obstacles
            1.0: 15x15 grid, many obstacles, far goal
        """
        # Interpolate grid size based on difficulty
        min_size = 3
        max_size = 15
        grid_size = int(min_size + (max_size - min_size) * self._difficulty)

        # Ensure odd grid size for symmetry
        if grid_size % 2 == 0:
            grid_size += 1

        # Update environment config
        if not hasattr(self.env, 'config'):
            self.env.config = {}

        self.env.config['grid_size'] = grid_size
        self.env.config['difficulty'] = self._difficulty

        # Update obstacle configuration
        obstacle_density = self._difficulty * 0.2  # 0% to 20% obstacles
        self.env.config['obstacle_density'] = obstacle_density

        # Update grid size in the environment if it has the attribute
        if hasattr(self.env, 'grid_size'):
            self.env.grid_size = grid_size

        logger.debug(f"Applied GridWorld difficulty: grid_size={grid_size}, "
                     f"obstacle_density={obstacle_density:.2f}")

    def _update_curriculum(self) -> None:
        """
        Update difficulty based on recent performance.

        Increases difficulty if success rate exceeds success_threshold.
        Decreases difficulty if success rate falls below failure_threshold (if enabled).
        Only updates after minimum number of episodes.
        """
        if self._episode_count < self._min_episodes:
            return

        if len(self._success_history) < self._window_size:
            return

        success_rate = self._get_success_rate()
        old_difficulty = self._difficulty

        # Check if difficulty should increase
        if success_rate >= self._success_threshold and self._difficulty < 1.0:
            self._difficulty = min(1.0, self._difficulty + self._difficulty_step)
            logger.info(f"Difficulty increased: {old_difficulty:.2f} -> {self._difficulty:.2f} "
                        f"(success_rate={success_rate:.2f})")

        # Check if difficulty should decrease
        elif self._enable_decrease and success_rate <= self._failure_threshold and self._difficulty > 0.0:
            self._difficulty = max(0.0, self._difficulty - self._difficulty_step)
            logger.info(f"Difficulty decreased: {old_difficulty:.2f} -> {self._difficulty:.2f} "
                        f"(success_rate={success_rate:.2f})")

    def _get_success_rate(self) -> float:
        """
        Calculate success rate over recent episodes.

        Returns:
            Success rate as a float between 0.0 and 1.0, or 0.0 if no history
        """
        if len(self._success_history) == 0:
            return 0.0

        return sum(self._success_history) / len(self._success_history)
