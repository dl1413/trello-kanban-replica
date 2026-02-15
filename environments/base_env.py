"""
Base Environment Class for RL Environments

This module provides a base class for creating custom RL environments
that are compatible with Gymnasium interface.
"""

import gymnasium as gym
from gymnasium import spaces
import numpy as np
from typing import Tuple, Dict, Any, Optional, Union


class BaseEnvironment(gym.Env):
    """
    Base class for all RL environments at Verita AI.
    
    This class provides a template for creating custom environments
    with standard observation and action spaces, reward shaping,
    and episode management.
    """
    
    metadata = {'render_modes': ['human', 'rgb_array']}
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the base environment.
        
        Args:
            config: Configuration dictionary for the environment
        """
        super(BaseEnvironment, self).__init__()
        
        self.config = config or {}
        self._load_config(self.config)
        self.current_step = 0
        
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
        self._episode_return = 0.0  # Track cumulative reward
        
    def reset(self, seed: Optional[int] = None, options: Optional[Dict[str, Any]] = None) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Reset the environment to initial state.
        
        Args:
            seed: Random seed for reproducibility
            options: Additional options for reset
        
        Returns:
            Tuple containing:
                observation: Initial observation as numpy array
                info: Additional information dictionary
        """
        # Call parent reset for seeding
        if seed is not None:
            super().reset(seed=seed)
            self._seed = seed
        
        self.current_step = 0
        self.terminated = False
        self.truncated = False
        self._episode_return = 0.0  # Reset episode return
        self.state = self._get_initial_state()
        observation = self._get_observation()
        info = self._get_info()
        
        return observation, info
    
    def step(self, action: int) -> Tuple[np.ndarray, float, bool, bool, Dict[str, Any]]:
        """
        Execute one step in the environment.
        
        Args:
            action: Action to take
            
        Returns:
            Tuple containing:
                observation: Current observation as numpy array
                reward: Reward for the action as float
                terminated: Whether a terminal state is reached
                truncated: Whether the episode is truncated (time limit)
                info: Additional information dictionary
                
        Raises:
            ValueError: If action is not in action space
            RuntimeError: If episode is already done
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
        
        # Apply reward processing (scaling and clipping)
        reward = self._apply_reward_processing(reward)
        
        # Track cumulative reward
        self._episode_return += reward
        
        # Check if episode is terminated or truncated
        self.terminated = self._is_terminated()
        self.truncated = self._is_truncated()
        
        # Get observation
        observation = self._get_observation()
        
        # Additional info
        info = self._get_info()
        
        return observation, reward, self.terminated, self.truncated, info
    
    def render(self, mode: str = 'human') -> Optional[np.ndarray]:
        """
        Render the environment.
        
        Args:
            mode: Rendering mode ('human' or 'rgb_array')
            
        Returns:
            RGB array if mode is 'rgb_array', None otherwise
            
        Raises:
            ValueError: If mode is not supported
        """
        if mode == 'rgb_array':
            return self._get_rgb_array()
        elif mode == 'human':
            # Override this method for custom rendering
            pass
        else:
            raise ValueError(f"Unsupported render mode: {mode}. Supported modes: {self.metadata['render_modes']}")
    
    def close(self):
        """Clean up resources."""
        pass
    
    # Protected methods to be overridden by subclasses
    
    def _load_config(self, config: Dict[str, Any]):
        """
        Load configuration from nested YAML structure with validation.
        
        Args:
            config: Configuration dictionary
            
        Raises:
            ValueError: If config contains invalid values
        """
        # Load episode configuration
        env_config = config.get('environment', {})
        self.episode_length = env_config.get('episode_length', config.get('episode_length', 1000))
        
        # Validate episode length
        if self.episode_length < 0:
            raise ValueError(f"episode_length must be non-negative, got {self.episode_length}")
        
        # Load reward configuration
        reward_config = env_config.get('reward', {})
        self.reward_scale = reward_config.get('scale', 1.0)
        
        # Validate reward scale
        if not isinstance(self.reward_scale, (int, float)):
            raise ValueError(f"reward scale must be numeric, got {type(self.reward_scale)}")
        
        clip_enabled = reward_config.get('clip', False)
        self.reward_clip_range = reward_config.get('clip_range', [-10, 10]) if clip_enabled else None
        
        # Validate clip range if enabled
        if self.reward_clip_range is not None:
            if not isinstance(self.reward_clip_range, (list, tuple)) or len(self.reward_clip_range) != 2:
                raise ValueError(f"reward_clip_range must be a list/tuple of 2 values, got {self.reward_clip_range}")
            if self.reward_clip_range[0] >= self.reward_clip_range[1]:
                raise ValueError(f"reward_clip_range[0] must be < reward_clip_range[1], got {self.reward_clip_range}")
    
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
    
    def _apply_reward_processing(self, reward: float) -> float:
        """
        Apply reward scaling and clipping.
        
        Args:
            reward: Raw reward value
            
        Returns:
            Processed reward
        """
        # Apply scaling
        processed_reward = reward * self.reward_scale
        
        # Apply clipping if configured
        if self.reward_clip_range is not None:
            processed_reward = np.clip(
                processed_reward,
                self.reward_clip_range[0],
                self.reward_clip_range[1]
            )
        
        return float(processed_reward)
    
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
        """
        Get additional info about the current state.
        
        Returns:
            Dictionary with diagnostic information including:
                - step: current step count
                - episode_length: maximum episode length
                - episode_return: cumulative reward (on termination/truncation)
                - is_success: whether episode was successful (on termination)
        """
        info = {
            'step': self.current_step,
            'episode_length': self.episode_length
        }
        
        # Add episode return and success flag on episode end
        if self.terminated or self.truncated:
            info['episode_return'] = self._episode_return
            info['is_success'] = self.terminated  # True if naturally terminated (not truncated)
        
        return info
    
    def _get_rgb_array(self) -> np.ndarray:
        """Get RGB array for rendering. Override in subclass."""
        return self.state if self.state is not None else np.zeros(
            self.observation_space.shape, dtype=np.uint8
        )
