"""
Base Environment Class for RL Environments

This module provides a base class for creating custom RL environments
that are compatible with OpenAI Gym interface.
"""

import gym
from gym import spaces
import numpy as np
from typing import Tuple, Dict, Any, Optional


class BaseEnvironment(gym.Env):
    """
    Base class for all RL environments at Verita AI.
    
    This class provides a template for creating custom environments
    with standard observation and action spaces, reward shaping,
    and episode management.
    """
    
    metadata = {'render.modes': ['human', 'rgb_array']}
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the base environment.
        
        Args:
            config: Configuration dictionary for the environment
        """
        super(BaseEnvironment, self).__init__()
        
        self.config = config or {}
        self.episode_length = self.config.get('episode_length', 1000)
        self.current_step = 0
        
        # Define action and observation space
        # These should be overridden in derived classes
        self.action_space = spaces.Discrete(4)
        self.observation_space = spaces.Box(
            low=0, high=255, shape=(84, 84, 3), dtype=np.uint8
        )
        
        self.state = None
        self.done = False
        
    def reset(self) -> np.ndarray:
        """
        Reset the environment to initial state.
        
        Returns:
            Initial observation
        """
        self.current_step = 0
        self.done = False
        self.state = self._get_initial_state()
        return self._get_observation()
    
    def step(self, action: int) -> Tuple[np.ndarray, float, bool, Dict]:
        """
        Execute one step in the environment.
        
        Args:
            action: Action to take
            
        Returns:
            observation: Current observation
            reward: Reward for the action
            done: Whether episode is complete
            info: Additional information
        """
        if self.done:
            raise RuntimeError("Episode is done. Call reset() to start a new episode.")
        
        self.current_step += 1
        
        # Execute action and update state
        self._update_state(action)
        
        # Calculate reward
        reward = self._calculate_reward(action)
        
        # Check if episode is done
        self.done = self._is_done()
        
        # Get observation
        observation = self._get_observation()
        
        # Additional info
        info = self._get_info()
        
        return observation, reward, self.done, info
    
    def render(self, mode: str = 'human'):
        """
        Render the environment.
        
        Args:
            mode: Rendering mode ('human' or 'rgb_array')
        """
        if mode == 'rgb_array':
            return self._get_rgb_array()
        elif mode == 'human':
            # Override this method for custom rendering
            pass
    
    def close(self):
        """Clean up resources."""
        pass
    
    # Protected methods to be overridden by subclasses
    
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
    
    def _is_done(self) -> bool:
        """Check if episode is done. Override in subclass."""
        return self.current_step >= self.episode_length
    
    def _get_info(self) -> Dict[str, Any]:
        """Get additional info. Override in subclass."""
        return {
            'step': self.current_step,
            'episode_length': self.episode_length
        }
    
    def _get_rgb_array(self) -> np.ndarray:
        """Get RGB array for rendering. Override in subclass."""
        return self.state if self.state is not None else np.zeros(
            self.observation_space.shape, dtype=np.uint8
        )
