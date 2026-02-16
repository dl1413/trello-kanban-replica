"""
Continuous Action Space Environment

This module provides a continuous control environment with physics simulation
for testing deep RL agents with continuous action spaces.
"""

import gymnasium as gym
from gymnasium import spaces
import numpy as np
from typing import Tuple, Dict, Any, Optional
from environments.base_env import BaseEnvironment


class ContinuousControlEnv(BaseEnvironment):
    """
    2D point-mass control environment with continuous action space.
    
    The agent controls a point mass in 2D space by applying continuous forces.
    Goal is to reach a target position while minimizing control effort.
    
    State: [x, y, vx, vy] - position and velocity
    Action: [fx, fy] - continuous force in range [-1, 1]
    
    Features:
    - Simple Euler integration for physics
    - Friction and velocity clamping
    - Dense reward based on distance to goal and control penalty
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize continuous control environment.
        
        Args:
            config: Configuration dictionary with physics parameters
        """
        super().__init__(config)
        
        # Physics parameters
        self.dt = self.config.get('dt', 0.1)  # Time step
        self.friction = self.config.get('friction', 0.1)  # Friction coefficient
        self.mass = self.config.get('mass', 1.0)  # Mass of the point
        self.max_velocity = self.config.get('max_velocity', 5.0)  # Max velocity
        self.goal_threshold = self.config.get('goal_threshold', 0.1)  # Distance threshold for goal
        self.action_penalty = self.config.get('action_penalty', 0.01)  # Penalty for large actions
        
        # Workspace bounds
        self.workspace_size = self.config.get('workspace_size', 10.0)
        
        # Define action and observation spaces
        self.action_space = spaces.Box(
            low=-1.0, high=1.0, shape=(2,), dtype=np.float32
        )
        
        # Observation: [x, y, vx, vy, goal_x, goal_y] or just [x, y, vx, vy] depending on config
        self.include_goal_in_obs = self.config.get('include_goal_in_obs', True)
        obs_dim = 6 if self.include_goal_in_obs else 4
        
        self.observation_space = spaces.Box(
            low=-np.inf, high=np.inf, shape=(obs_dim,), dtype=np.float32
        )
        
        # State variables
        self.position = None
        self.velocity = None
        self.goal_position = None
        self._out_of_hard_bounds = False
    
    def _get_initial_state(self) -> np.ndarray:
        """Initialize position, velocity, and goal."""
        # Random starting position
        self.position = self.np_random.uniform(
            -self.workspace_size/2, self.workspace_size/2, size=2
        ).astype(np.float32)
        
        # Zero initial velocity
        self.velocity = np.zeros(2, dtype=np.float32)
        
        # Random goal position (at least some distance away)
        min_distance = self.workspace_size / 4
        while True:
            self.goal_position = self.np_random.uniform(
                -self.workspace_size/2, self.workspace_size/2, size=2
            ).astype(np.float32)
            
            distance = np.linalg.norm(self.position - self.goal_position)
            if distance >= min_distance:
                break
        
        self._out_of_hard_bounds = False
        
        return self._get_state_vector()
    
    def _get_state_vector(self) -> np.ndarray:
        """Get state vector from position and velocity."""
        if self.include_goal_in_obs:
            return np.concatenate([self.position, self.velocity, self.goal_position])
        else:
            return np.concatenate([self.position, self.velocity])
    
    def _get_observation(self) -> np.ndarray:
        """Return current state observation."""
        obs = self._get_state_vector()
        
        # Optionally normalize observations
        if self.config.get('normalize_obs', False):
            obs = self._normalize_observation(obs)
        
        return obs.astype(np.float32)
    
    def _normalize_observation(self, obs: np.ndarray) -> np.ndarray:
        """Normalize observations to reasonable ranges."""
        normalized = obs.copy()
        # Normalize positions by workspace size
        if self.include_goal_in_obs:
            normalized[0:2] /= self.workspace_size  # position
            normalized[2:4] /= self.max_velocity    # velocity
            normalized[4:6] /= self.workspace_size  # goal position
        else:
            normalized[0:2] /= self.workspace_size  # position
            normalized[2:4] /= self.max_velocity    # velocity
        return normalized
    
    def _update_state(self, action: np.ndarray):
        """Update physics using Euler integration."""
        # Action is force
        force = action.astype(np.float32)
        
        # Acceleration = Force / Mass
        acceleration = force / self.mass
        
        # Apply friction (proportional to velocity)
        friction_force = -self.friction * self.velocity
        acceleration += friction_force
        
        # Update velocity: v = v + a * dt
        self.velocity = self.velocity + acceleration * self.dt
        
        # Clamp velocity to max
        velocity_norm = np.linalg.norm(self.velocity)
        if velocity_norm > self.max_velocity:
            self.velocity = self.velocity * (self.max_velocity / velocity_norm)
        
        # Update position: x = x + v * dt
        self.position = self.position + self.velocity * self.dt
        
        # Check if out of bounds before clamping (for truncation)
        self._out_of_hard_bounds = np.any(np.abs(self.position) > self.workspace_size * 1.5)
        
        # Keep within workspace bounds (soft boundary - allow some overshoot but penalize)
        # Hard clamp to prevent going too far out
        max_bound = self.workspace_size * 1.5
        self.position = np.clip(self.position, -max_bound, max_bound)
    
    def _calculate_reward(self, action: np.ndarray) -> float:
        """
        Calculate reward based on distance to goal and action penalty.
        
        Reward = -distance_to_goal - action_penalty * ||action||^2
        """
        # Distance to goal (negative reward)
        distance = np.linalg.norm(self.position - self.goal_position)
        distance_reward = -distance
        
        # Action penalty (encourage efficiency)
        action_magnitude = np.linalg.norm(action)
        action_cost = -self.action_penalty * (action_magnitude ** 2)
        
        # Bonus for reaching goal
        if distance < self.goal_threshold:
            goal_bonus = 100.0
        else:
            goal_bonus = 0.0
        
        # Penalty for going out of workspace
        out_of_bounds_penalty = 0.0
        if np.any(np.abs(self.position) > self.workspace_size):
            out_of_bounds_penalty = -10.0
        
        total_reward = distance_reward + action_cost + goal_bonus + out_of_bounds_penalty
        
        return float(total_reward)
    
    def _is_terminated(self) -> bool:
        """Episode terminates when goal is reached."""
        distance = np.linalg.norm(self.position - self.goal_position)
        return distance < self.goal_threshold
    
    def _is_truncated(self) -> bool:
        """
        Episode is truncated when max steps reached or agent goes too far out of bounds.
        """
        # Time limit
        if self.current_step >= self.episode_length:
            return True
        
        # Out of bounds (hard boundary) - check flag set during update
        if hasattr(self, '_out_of_hard_bounds') and self._out_of_hard_bounds:
            return True
        
        return False
    
    def _get_info(self) -> Dict[str, Any]:
        """Return additional information about the episode."""
        info = super()._get_info()
        distance = np.linalg.norm(self.position - self.goal_position)
        info.update({
            'position': self.position.tolist(),
            'velocity': self.velocity.tolist(),
            'goal_position': self.goal_position.tolist(),
            'distance_to_goal': float(distance),
            'goal_reached': distance < self.goal_threshold,
            'out_of_bounds': np.any(np.abs(self.position) > self.workspace_size)
        })
        return info
    
    def render(self, mode: str = 'human'):
        """Render the environment (text-based visualization)."""
        if mode == 'human':
            distance = np.linalg.norm(self.position - self.goal_position)
            velocity_norm = np.linalg.norm(self.velocity)
            
            print('\n' + '=' * 60)
            print('Continuous Control Environment')
            print('=' * 60)
            print(f'Step: {self.current_step}/{self.episode_length}')
            print(f'Position: [{self.position[0]:6.2f}, {self.position[1]:6.2f}]')
            print(f'Velocity: [{self.velocity[0]:6.2f}, {self.velocity[1]:6.2f}] (norm: {velocity_norm:.2f})')
            print(f'Goal:     [{self.goal_position[0]:6.2f}, {self.goal_position[1]:6.2f}]')
            print(f'Distance to goal: {distance:.3f} (threshold: {self.goal_threshold})')
            
            # Simple ASCII visualization
            grid_size = 20
            grid = np.full((grid_size, grid_size), '.', dtype=str)
            
            # Convert positions to grid coordinates
            def to_grid(pos):
                x = int((pos[0] / self.workspace_size + 0.5) * (grid_size - 1))
                y = int((pos[1] / self.workspace_size + 0.5) * (grid_size - 1))
                x = np.clip(x, 0, grid_size - 1)
                y = np.clip(y, 0, grid_size - 1)
                return x, y
            
            gx, gy = to_grid(self.goal_position)
            px, py = to_grid(self.position)
            
            grid[gy, gx] = 'G'
            if (px, py) == (gx, gy):
                grid[py, px] = '*'  # Agent on goal
            else:
                grid[py, px] = 'A'
            
            # Print grid (flip y-axis for intuitive display)
            for row in reversed(grid):
                print(' '.join(row))
            print('=' * 60)


if __name__ == '__main__':
    """Demo the continuous control environment."""
    # Create environment
    config = {
        'dt': 0.1,
        'friction': 0.1,
        'mass': 1.0,
        'max_velocity': 5.0,
        'goal_threshold': 0.3,
        'workspace_size': 5.0,
        'episode_length': 200,
        'action_penalty': 0.01,
        'normalize_obs': False
    }
    
    env = ContinuousControlEnv(config)
    
    print('\nContinuous Control Environment Demo')
    print('=' * 60)
    print('Configuration:')
    for key, value in config.items():
        print(f'  {key}: {value}')
    print(f'\nAction Space: {env.action_space}')
    print(f'Observation Space: {env.observation_space}')
    
    # Run a few episodes with random actions
    for episode in range(2):
        print(f'\n\n{"=" * 60}')
        print(f'EPISODE {episode + 1}')
        print(f'{"=" * 60}')
        
        obs, info = env.reset(seed=42 + episode)
        env.render()
        
        terminated = False
        truncated = False
        total_reward = 0
        step = 0
        
        while not (terminated or truncated) and step < 50:
            # Random action
            action = env.action_space.sample()
            obs, reward, terminated, truncated, info = env.step(action)
            total_reward += reward
            step += 1
            
            # Render every 10 steps or when done
            if step % 10 == 0 or terminated or truncated:
                print(f'\nAction: [{action[0]:6.3f}, {action[1]:6.3f}]')
                print(f'Reward: {reward:7.2f} | Total: {total_reward:7.2f}')
                env.render()
        
        print(f'\nEpisode finished!')
        print(f'Total reward: {total_reward:.2f}')
        print(f'Goal reached: {info["goal_reached"]}')
        print(f'Steps: {step}')
