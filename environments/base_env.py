"""
Base Environment Class for RL Environments

This module provides a base class for creating custom RL environments
that are compatible with Gymnasium interface.
"""

import gymnasium as gym
from gymnasium import spaces
import numpy as np
from typing import Tuple, Dict, Any, Optional


class BaseEnvironment(gym.Env):
    """
    Base class for all RL environments at Verita AI.

    This class provides a template for creating custom environments
    with standard observation and action spaces, reward shaping,
    and episode management.
    """

    metadata = {'render_modes': ['human', 'rgb_array']}

    def __init__(self, config: Optional[Dict[str, Any]] = None, render_mode: Optional[str] = None):
        """
        Initialize the base environment.

        Args:
            config: Configuration dictionary for the environment
            render_mode: Rendering mode ('human' or 'rgb_array')
        """
        super().__init__()

        self.config = config or {}
        self._load_config(self.config)
        self.current_step = 0
        self.episode_reward = 0.0

        # Define action and observation space
        # These should be overridden in derived classes
        self.action_space = spaces.Discrete(4)
        self.observation_space = spaces.Box(
            low=0, high=255, shape=(84, 84, 3), dtype=np.uint8
        )

        self.state = None
        self.terminated = False
        self.truncated = False
        self._seed = None
        self.render_mode = render_mode

    def reset(
        self,
        seed: Optional[int] = None,
        options: Optional[Dict[str, Any]] = None
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Reset the environment to initial state.

        Args:
            seed: Random seed for reproducibility
            options: Additional options for reset

        Returns:
            observation: Initial observation
            info: Additional information
        """
        # Call parent reset for seeding
        if seed is not None:
            super().reset(seed=seed)
            self._seed = seed

        self.current_step = 0
        self.episode_reward = 0.0
        self.terminated = False
        self.truncated = False
        self.state = self._get_initial_state()
        observation = self._get_observation()
        info = self._get_info()

        return observation, info

    def step(self, action: int) -> Tuple[np.ndarray, float, bool, bool, Dict]:
        """
        Execute one step in the environment.

        Args:
            action: Action to take

        Returns:
            observation: Current observation
            reward: Reward for the action
            terminated: Whether a terminal state is reached
            truncated: Whether the episode is truncated (time limit)
            info: Additional information
        """
        # Validate action
        if not self.action_space.contains(action):
            raise ValueError(f"Invalid action {action} for space {self.action_space}")

        if self.terminated or self.truncated:
            raise RuntimeError("Episode is done. Call reset() to start a new episode.")

        self.current_step += 1

        # Execute action and update state
        self._update_state(action)

        # Calculate reward
        reward = self._calculate_reward(action)

        # Apply reward scaling and clipping
        reward = reward * self.reward_scale
        if self.reward_clip_range is not None:
            reward = np.clip(reward, self.reward_clip_range[0], self.reward_clip_range[1])

        # Accumulate episode reward
        self.episode_reward += reward

        # Check if episode is terminated or truncated
        self.terminated = self._is_terminated()
        self.truncated = self._is_truncated()

        # Get observation
        observation = self._get_observation()

        # Additional info
        info = self._get_info()

        return observation, reward, self.terminated, self.truncated, info

    def render(self):
        """
        Render the environment.

        Returns:
            RGB array if render_mode is 'rgb_array', otherwise None
        """
        if self.render_mode == 'rgb_array':
            return self._get_rgb_array()
        elif self.render_mode == 'human':
            # Override this method for custom rendering
            pass

    def close(self):
        """Clean up resources."""
        pass

    # Protected methods to be overridden by subclasses

    def _load_config(self, config: Dict[str, Any]):
        """
        Load configuration from nested YAML structure.

        Args:
            config: Configuration dictionary
        """
        # Load episode configuration
        env_config = config.get('environment', {})
        self.episode_length = env_config.get('episode_length', config.get('episode_length', 1000))

        # Load reward configuration
        reward_config = env_config.get('reward', {})
        self.reward_scale = reward_config.get('scale', 1.0)
        clip_enabled = reward_config.get('clip', False)
        self.reward_clip_range = (
            reward_config.get('clip_range', [-10, 10])
            if clip_enabled else None
        )

    def _get_initial_state(self) -> Any:
        """Get initial state. Override in subclass."""
        return np.zeros(self.observation_space.shape, dtype=np.uint8)

    def _get_observation(self) -> np.ndarray:
        """Get current observation. Override in subclass."""
        return self.state

    def _update_state(self, action: int):
        """Update state based on action. Override in subclass."""
        pass

    def _calculate_reward(self, action: int) -> float:
        """Calculate reward for action. Override in subclass."""
        return 0.0

    def _is_terminated(self) -> bool:
        """
        Check if episode has reached a terminal state.
        Override in subclass for task-specific termination.

        Returns:
            True if terminal state reached, False otherwise
        """
        return False

    def _is_truncated(self) -> bool:
        """
        Check if episode should be truncated (e.g., time limit).

        Returns:
            True if episode should be truncated, False otherwise
        """
        return self.current_step >= self.episode_length

    def _get_info(self) -> Dict[str, Any]:
        """Get additional info. Override in subclass."""
        info = {
            'step': self.current_step,
            'episode_length': self.episode_length,
            'episode_reward': self.episode_reward
        }

        # Add standard episode info at termination (SB3/CleanRL convention)
        if self.terminated or self.truncated:
            info['episode'] = {
                'r': self.episode_reward,
                'l': self.current_step
            }

        return info

    def _get_rgb_array(self) -> np.ndarray:
        """Get RGB array for rendering. Override in subclass."""
        return self.state if self.state is not None else np.zeros(
            self.observation_space.shape, dtype=np.uint8
        )
