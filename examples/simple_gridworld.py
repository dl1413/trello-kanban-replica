"""
Example: Simple Grid World Environment

This is a basic example of a custom RL environment that extends BaseEnvironment.
The agent navigates a 2D grid to reach a goal position.
"""

from environments.base_env import BaseEnvironment
from gymnasium import spaces
import numpy as np
import cv2


class SimpleGridWorld(BaseEnvironment):
    """
    A simple grid world environment where an agent navigates to a goal.

    Observation: (x, y) position of the agent, normalized to [0, 1]
    Actions: 0=up, 1=right, 2=down, 3=left
    Reward: -1 per step, +100 for reaching goal (or dense reward based on distance)
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
        self.fixed_goal_pos = self.config.get('fixed_goal_pos', None)

        # Obstacles configuration
        self.num_obstacles = self.config.get('num_obstacles', 0)
        self.obstacles = set()

        # Define spaces - normalized to [0, 1]
        self.action_space = spaces.Discrete(4)
        self.observation_space = spaces.Box(
            low=0.0, high=1.0, shape=(2,), dtype=np.float32
        )

        # Initialize positions
        self.agent_pos = None
        self.goal_pos = None
        self.prev_distance = None
        self.max_distance = self.grid_size * np.sqrt(2)  # Maximum possible distance
        
    def _get_initial_state(self):
        """Initialize agent and goal positions."""
        # Generate obstacles first
        self._generate_obstacles()

        # Random starting position using gymnasium's RNG (avoiding obstacles)
        while True:
            self.agent_pos = np.array([
                self.np_random.integers(0, self.grid_size),
                self.np_random.integers(0, self.grid_size)
            ], dtype=np.int32)
            if tuple(self.agent_pos) not in self.obstacles:
                break

        # Goal position (different from start and obstacles)
        if self.randomize_goal or self.goal_pos is None:
            if self.fixed_goal_pos is not None:
                self.goal_pos = np.array(self.fixed_goal_pos, dtype=np.int32)
            else:
                while True:
                    self.goal_pos = np.array([
                        self.np_random.integers(0, self.grid_size),
                        self.np_random.integers(0, self.grid_size)
                    ], dtype=np.int32)
                    if (not np.array_equal(self.agent_pos, self.goal_pos) and
                            tuple(self.goal_pos) not in self.obstacles):
                        break

        # Initialize distance for dense reward shaping
        self.prev_distance = np.linalg.norm(self.agent_pos - self.goal_pos)

        return self.agent_pos.copy()

    def _generate_obstacles(self):
        """Generate random obstacles on the grid."""
        self.obstacles = set()
        for _ in range(self.num_obstacles):
            while True:
                obstacle_pos = (
                    self.np_random.integers(0, self.grid_size),
                    self.np_random.integers(0, self.grid_size)
                )
                if obstacle_pos not in self.obstacles:
                    self.obstacles.add(obstacle_pos)
                    break
    
    def _get_observation(self):
        """Return current agent position, normalized to [0, 1]."""
        # Normalize position to [0, 1] range for better neural network compatibility
        return (self.agent_pos / (self.grid_size - 1)).astype(np.float32)
    
    def _update_state(self, action):
        """Update agent position based on action (avoids obstacles)."""
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

        # Check for obstacles - don't move if hitting an obstacle
        if tuple(new_pos) not in self.obstacles:
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
            reward = (self.prev_distance - current_distance) / self.max_distance
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
        """
        Render the grid world.

        Args:
            mode: 'human' for console output or 'rgb_array' for numpy array

        Returns:
            RGB array if mode is 'rgb_array', None otherwise
        """
        if mode == 'rgb_array':
            return self._get_rgb_array()
        elif mode == 'human':
            # Create grid visualization
            grid = np.zeros((self.grid_size, self.grid_size), dtype=str)
            grid[:] = '.'

            # Place obstacles
            for obs_pos in self.obstacles:
                grid[obs_pos] = 'X'

            # Place goal
            grid[tuple(self.goal_pos)] = 'G'

            # Place agent
            grid[tuple(self.agent_pos)] = 'A'

            # Print grid
            print('\n' + '=' * (self.grid_size * 2 + 1))
            for row in grid:
                print('|' + ' '.join(row) + '|')
            print('=' * (self.grid_size * 2 + 1))
            print(f'Step: {self.current_step}, Distance to goal: {np.linalg.norm(self.agent_pos - self.goal_pos):.2f}')
        return None

    def _get_rgb_array(self):
        """
        Generate RGB array visualization (64x64 pixels per cell).

        Returns:
            np.ndarray: RGB image of the grid world
        """
        cell_size = 64
        img_size = self.grid_size * cell_size
        img = np.ones((img_size, img_size, 3), dtype=np.uint8) * 255  # White background

        # Draw grid lines
        for i in range(self.grid_size + 1):
            cv2.line(img, (0, i * cell_size), (img_size, i * cell_size), (200, 200, 200), 1)
            cv2.line(img, (i * cell_size, 0), (i * cell_size, img_size), (200, 200, 200), 1)

        # Draw obstacles (gray)
        for obs_pos in self.obstacles:
            y, x = obs_pos
            top_left = (x * cell_size, y * cell_size)
            bottom_right = ((x + 1) * cell_size, (y + 1) * cell_size)
            cv2.rectangle(img, top_left, bottom_right, (100, 100, 100), -1)

        # Draw goal (green)
        y, x = self.goal_pos
        center = (x * cell_size + cell_size // 2, y * cell_size + cell_size // 2)
        cv2.circle(img, center, cell_size // 3, (0, 255, 0), -1)

        # Draw agent (blue)
        y, x = self.agent_pos
        center = (x * cell_size + cell_size // 2, y * cell_size + cell_size // 2)
        cv2.circle(img, center, cell_size // 4, (255, 0, 0), -1)

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
