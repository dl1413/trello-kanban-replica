"""
Example: Simple Grid World Environment

This is a basic example of a custom RL environment that extends BaseEnvironment.
The agent navigates a 2D grid to reach a goal position.
"""

from environments.base_env import BaseEnvironment
from gymnasium import spaces
import numpy as np


class SimpleGridWorld(BaseEnvironment):
    """
    A simple grid world environment where an agent navigates to a goal.
    
    Observation: (x, y) position of the agent
    Actions: 0=up, 1=right, 2=down, 3=left
    Reward: -1 per step, +100 for reaching goal
    """
    
    def __init__(self, config=None):
        """Initialize the grid world environment."""
        super().__init__(config)
        
        # Grid dimensions
        self.grid_size = self.config.get('grid_size', 10)
        
        # Reward configuration
        self.reward_type = self.config.get('reward_type', 'sparse')
        
        # Goal randomization
        self.randomize_goal = self.config.get('randomize_goal', False)
        
        # Obstacles
        self.obstacles = self.config.get('obstacles', [])
        self.num_obstacles = self.config.get('num_obstacles', 0)
        
        # Define spaces
        self.action_space = spaces.Discrete(4)
        self.observation_space = spaces.Box(
            low=0.0, high=1.0, shape=(2,), dtype=np.float32  # Normalized observations
        )
        
        # Initialize positions
        self.agent_pos = None
        self.goal_pos = None
        self.prev_distance = None
        self.obstacle_positions = []
        
    def _get_initial_state(self):
        """Initialize agent and goal positions."""
        # Random starting position using gymnasium's RNG
        self.agent_pos = np.array([
            self.np_random.integers(0, self.grid_size),
            self.np_random.integers(0, self.grid_size)
        ], dtype=np.int32)
        
        # Goal position: randomize if configured, otherwise fixed
        if self.randomize_goal or self.goal_pos is None:
            while True:
                self.goal_pos = np.array([
                    self.np_random.integers(0, self.grid_size),
                    self.np_random.integers(0, self.grid_size)
                ], dtype=np.int32)
                if not np.array_equal(self.agent_pos, self.goal_pos):
                    break
        
        # Generate random obstacles if configured
        self.obstacle_positions = []
        if self.num_obstacles > 0:
            attempts = 0
            max_attempts = self.num_obstacles * 10
            while len(self.obstacle_positions) < self.num_obstacles and attempts < max_attempts:
                obs_pos = (
                    self.np_random.integers(0, self.grid_size),
                    self.np_random.integers(0, self.grid_size)
                )
                # Don't place obstacle on agent or goal
                if (not np.array_equal(obs_pos, tuple(self.agent_pos)) and
                    not np.array_equal(obs_pos, tuple(self.goal_pos)) and
                    obs_pos not in self.obstacle_positions):
                    self.obstacle_positions.append(obs_pos)
                attempts += 1
        
        # Add static obstacles from config
        for obs in self.obstacles:
            obs_tuple = tuple(obs)
            if obs_tuple not in self.obstacle_positions:
                self.obstacle_positions.append(obs_tuple)
        
        # Initialize distance for dense reward shaping
        self.prev_distance = np.linalg.norm(self.agent_pos - self.goal_pos)
        
        return self.agent_pos.copy()
    
    def _get_observation(self):
        """Return current agent position normalized to [0, 1]."""
        return self.agent_pos.astype(np.float32) / (self.grid_size - 1)
    
    def _update_state(self, action):
        """Update agent position based on action."""
        # Map actions to movements
        movements = {
            0: np.array([-1, 0]),  # up
            1: np.array([0, 1]),   # right
            2: np.array([1, 0]),   # down
            3: np.array([0, -1])   # left
        }
        
        # Calculate new position
        new_pos = self.agent_pos + movements[action]
        
        # Keep agent within bounds
        new_pos = np.clip(new_pos, 0, self.grid_size - 1)
        
        # Check for obstacles - don't move if hitting obstacle
        if tuple(new_pos) not in self.obstacle_positions:
            self.agent_pos = new_pos
    
    def _calculate_reward(self, action):
        """Calculate reward based on goal proximity."""
        # Check if goal is reached
        if np.array_equal(self.agent_pos, self.goal_pos):
            return 100.0
        
        # Reward shaping based on configuration
        if self.reward_type == 'dense':
            # Dense reward: potential-based shaping, normalized by max distance
            current_distance = np.linalg.norm(self.agent_pos - self.goal_pos)
            max_distance = np.linalg.norm(np.array([self.grid_size - 1, self.grid_size - 1]))
            reward = (self.prev_distance - current_distance) / max_distance
            self.prev_distance = current_distance
            return reward
        else:
            # Sparse reward: small negative reward for each step
            return -1.0
    
    def _is_terminated(self):
        """Episode terminates when goal is reached."""
        return np.array_equal(self.agent_pos, self.goal_pos)
    
    def _is_truncated(self):
        """Episode is truncated when max steps are reached."""
        return self.current_step >= self.episode_length
    
    def _get_info(self):
        """Return additional information about the episode."""
        info = super()._get_info()
        info.update({
            'agent_pos': self.agent_pos.tolist(),
            'goal_pos': self.goal_pos.tolist(),
            'distance_to_goal': np.linalg.norm(self.agent_pos - self.goal_pos),
            'goal_reached': np.array_equal(self.agent_pos, self.goal_pos)
        })
        return info
    
    def render(self, mode='human'):
        """Render the grid world."""
        if mode == 'human':
            # Create grid visualization
            grid = np.zeros((self.grid_size, self.grid_size), dtype=str)
            grid[:] = '.'
            
            # Place obstacles
            for obs_pos in self.obstacle_positions:
                grid[obs_pos] = '#'
            
            # Place goal
            grid[tuple(self.goal_pos)] = 'G'
            
            # Place agent (overrides goal if on same position)
            grid[tuple(self.agent_pos)] = 'A'
            
            # Print grid
            print('\n' + '=' * (self.grid_size * 2 + 1))
            for row in grid:
                print('|' + ' '.join(row) + '|')
            print('=' * (self.grid_size * 2 + 1))
            print(f'Step: {self.current_step}, Distance to goal: {np.linalg.norm(self.agent_pos - self.goal_pos):.2f}')
        
        elif mode == 'rgb_array':
            # Return RGB array for video recording/visualization
            return self._get_rgb_array()
    
    def _get_rgb_array(self):
        """Generate RGB array representation of the environment."""
        # Create RGB image: each cell is 64x64 pixels
        cell_size = 64
        img = np.ones((self.grid_size * cell_size, self.grid_size * cell_size, 3), dtype=np.uint8) * 255
        
        # Draw grid lines
        for i in range(self.grid_size + 1):
            img[i * cell_size:(i * cell_size + 1), :] = 200  # Horizontal lines
            img[:, i * cell_size:(i * cell_size + 1)] = 200  # Vertical lines
        
        # Draw obstacles (gray)
        for obs_pos in self.obstacle_positions:
            y, x = obs_pos
            img[y * cell_size:(y + 1) * cell_size, x * cell_size:(x + 1) * cell_size] = [100, 100, 100]
        
        # Draw goal (green)
        gy, gx = self.goal_pos
        img[gy * cell_size:(gy + 1) * cell_size, gx * cell_size:(gx + 1) * cell_size] = [0, 255, 0]
        
        # Draw agent (blue)
        ay, ax = self.agent_pos
        margin = cell_size // 4
        img[ay * cell_size + margin:(ay + 1) * cell_size - margin,
            ax * cell_size + margin:(ax + 1) * cell_size - margin] = [0, 0, 255]
        
        return img


if __name__ == '__main__':
    """Demo the environment."""
    # Create environment
    config = {
        'grid_size': 5,
        'episode_length': 50
    }
    env = SimpleGridWorld(config)
    
    # Run a few episodes with random actions
    for episode in range(3):
        print(f'\n--- Episode {episode + 1} ---')
        obs, info = env.reset(seed=42 + episode)
        env.render()
        
        terminated = False
        truncated = False
        total_reward = 0
        
        while not (terminated or truncated):
            # Take random action
            action = env.action_space.sample()
            obs, reward, terminated, truncated, info = env.step(action)
            total_reward += reward
            
            # Render every few steps
            if env.current_step % 5 == 0 or terminated or truncated:
                env.render()
        
        print(f'Episode finished! Total reward: {total_reward}')
        print(f'Goal reached: {info["goal_reached"]}')
