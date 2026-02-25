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

    # Pre-computed movement vectors (class-level constant to avoid per-step allocation)
    _MOVEMENTS = np.array([
        [-1,  0],  # 0: up
        [ 0,  1],  # 1: right
        [ 1,  0],  # 2: down
        [ 0, -1],  # 3: left
    ], dtype=np.int32)

    _MAX_PLACEMENT_ATTEMPTS = 10_000

    def __init__(self, config=None):
        """Initialize the grid world environment."""
        super().__init__(config)

        self.grid_size = self.config.get('grid_size', 10)
        self.reward_type = self.config.get('reward_type', 'sparse')
        self.randomize_goal = self.config.get('randomize_goal', False)
        self.fixed_goal_pos = self.config.get('fixed_goal_pos', None)
        self.num_obstacles = self.config.get('num_obstacles', 0)
        self.obstacles = set()

        self.action_space = spaces.Discrete(4)
        self.observation_space = spaces.Box(
            low=0.0, high=1.0, shape=(2,), dtype=np.float32
        )

        self.agent_pos = None
        self.goal_pos = None
        self.prev_distance = None

        # Cache frequently used derived values
        self._grid_max = self.grid_size - 1
        self._obs_scale = 1.0 / self._grid_max if self._grid_max > 0 else 1.0
        self.max_distance = self.grid_size * np.sqrt(2)
        
    def _get_initial_state(self):
        """Initialize agent and goal positions."""
        self._generate_obstacles()

        # Random starting position avoiding obstacles
        for _ in range(self._MAX_PLACEMENT_ATTEMPTS):
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
                for _ in range(self._MAX_PLACEMENT_ATTEMPTS):
                    self.goal_pos = np.array([
                        self.np_random.integers(0, self.grid_size),
                        self.np_random.integers(0, self.grid_size)
                    ], dtype=np.int32)
                    if (not np.array_equal(self.agent_pos, self.goal_pos) and
                            tuple(self.goal_pos) not in self.obstacles):
                        break

        self.prev_distance = np.linalg.norm(self.agent_pos - self.goal_pos)

        return self.agent_pos.copy()

    def _generate_obstacles(self):
        """Generate random obstacles on the grid."""
        self.obstacles = set()
        for _ in range(self.num_obstacles):
            for _ in range(self._MAX_PLACEMENT_ATTEMPTS):
                obstacle_pos = (
                    int(self.np_random.integers(0, self.grid_size)),
                    int(self.np_random.integers(0, self.grid_size))
                )
                if obstacle_pos not in self.obstacles:
                    self.obstacles.add(obstacle_pos)
                    break
    
    def _get_observation(self):
        """Return current agent position, normalized to [0, 1]."""
        return (self.agent_pos * self._obs_scale).astype(np.float32)
    
    def _update_state(self, action):
        """Update agent position based on action (avoids obstacles)."""
        new_pos = self.agent_pos + self._MOVEMENTS[action]
        np.clip(new_pos, 0, self._grid_max, out=new_pos)

        if tuple(new_pos) not in self.obstacles:
            self.agent_pos = new_pos
    
    def _calculate_reward(self, action):
        """Calculate reward based on goal proximity."""
        if np.array_equal(self.agent_pos, self.goal_pos):
            return 100.0

        if self.reward_type == 'dense':
            diff = self.agent_pos - self.goal_pos
            current_distance = np.sqrt(diff[0] * diff[0] + diff[1] * diff[1])
            reward = (self.prev_distance - current_distance) / self.max_distance
            self.prev_distance = current_distance
            return reward

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
        goal_reached = self.terminated
        diff = self.agent_pos - self.goal_pos
        info['agent_pos'] = self.agent_pos.tolist()
        info['goal_pos'] = self.goal_pos.tolist()
        info['distance_to_goal'] = 0.0 if goal_reached else float(np.sqrt(diff[0] * diff[0] + diff[1] * diff[1]))
        info['goal_reached'] = goal_reached
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
        half_cell = cell_size // 2
        img_size = self.grid_size * cell_size
        img = np.full((img_size, img_size, 3), 255, dtype=np.uint8)

        # Draw grid lines
        grid_color = (200, 200, 200)
        for i in range(self.grid_size + 1):
            pos = i * cell_size
            cv2.line(img, (0, pos), (img_size, pos), grid_color, 1)
            cv2.line(img, (pos, 0), (pos, img_size), grid_color, 1)

        # Draw obstacles (gray)
        for obs_y, obs_x in self.obstacles:
            cv2.rectangle(
                img,
                (obs_x * cell_size, obs_y * cell_size),
                ((obs_x + 1) * cell_size, (obs_y + 1) * cell_size),
                (100, 100, 100), -1
            )

        # Draw goal (green)
        gy, gx = self.goal_pos
        cv2.circle(img, (gx * cell_size + half_cell, gy * cell_size + half_cell),
                   cell_size // 3, (0, 255, 0), -1)

        # Draw agent (blue)
        ay, ax = self.agent_pos
        cv2.circle(img, (ax * cell_size + half_cell, ay * cell_size + half_cell),
                   cell_size // 4, (255, 0, 0), -1)

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
