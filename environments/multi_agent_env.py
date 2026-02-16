"""
Multi-Agent Environment Module

This module provides base classes for multi-agent reinforcement learning
environments, supporting both cooperative and competitive scenarios.
"""

import gymnasium as gym
from gymnasium import spaces
import numpy as np
from typing import Dict, Tuple, Any, Optional, List
from environments.base_env import BaseEnvironment


class MultiAgentBaseEnvironment(BaseEnvironment):
    """
    Base class for multi-agent reinforcement learning environments.
    
    Supports configurable number of agents with independent observation and
    action spaces, cooperative and competitive reward modes, and collision handling.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize multi-agent environment.
        
        Args:
            config: Configuration dictionary with multi-agent parameters
        """
        super().__init__(config)
        
        # Multi-agent configuration
        self.num_agents = self.config.get('num_agents', 2)
        self.reward_mode = self.config.get('reward_mode', 'cooperative')  # 'cooperative' or 'competitive'
        self.collision_mode = self.config.get('collision_mode', 'block')  # 'block', 'pass-through', 'penalty'
        
        # Store per-agent states
        self.agent_states = {}
        self.agent_terminated = {}
        self.agent_truncated = {}
        
        # Override action/observation spaces to be per-agent
        # Subclasses should set these properly
        self.action_spaces = {i: spaces.Discrete(4) for i in range(self.num_agents)}
        self.observation_spaces = {i: spaces.Box(low=0, high=255, shape=(84, 84, 3), dtype=np.uint8)
                                   for i in range(self.num_agents)}
    
    def reset(self, seed: Optional[int] = None, options: Optional[Dict[str, Any]] = None) -> Tuple[Dict[int, np.ndarray], Dict[int, Dict[str, Any]]]:
        """
        Reset the multi-agent environment.
        
        Args:
            seed: Random seed for reproducibility
            options: Additional options for reset
        
        Returns:
            observations: Dict mapping agent ID to observation
            infos: Dict mapping agent ID to info dict
        """
        if seed is not None:
            super(BaseEnvironment, self).reset(seed=seed)
            self._seed = seed
        
        self.current_step = 0
        self.terminated = False
        self.truncated = False
        
        # Initialize per-agent states
        self.agent_states = self._get_initial_states()
        self.agent_terminated = {i: False for i in range(self.num_agents)}
        self.agent_truncated = {i: False for i in range(self.num_agents)}
        
        # Get observations and info for all agents
        observations = self._get_observations()
        infos = self._get_infos()
        
        return observations, infos
    
    def step(self, actions: Dict[int, int]) -> Tuple[Dict[int, np.ndarray], Dict[int, float], Dict[int, bool], Dict[int, bool], Dict[int, Dict[str, Any]]]:
        """
        Execute one step for all agents.
        
        Args:
            actions: Dict mapping agent ID to action
            
        Returns:
            observations: Dict mapping agent ID to observation
            rewards: Dict mapping agent ID to reward
            terminated: Dict mapping agent ID to terminated flag
            truncated: Dict mapping agent ID to truncated flag
            infos: Dict mapping agent ID to info dict
        """
        # Validate all actions
        for agent_id, action in actions.items():
            if not self.action_spaces[agent_id].contains(action):
                raise ValueError(f"Invalid action {action} for agent {agent_id}")
        
        if self.terminated or self.truncated:
            raise RuntimeError("Episode is done. Call reset() to start a new episode.")
        
        self.current_step += 1
        
        # Store previous termination state before updating
        prev_terminated = self.agent_terminated.copy()
        
        # Update states for all agents
        self._update_states(actions)
        
        # Calculate rewards (can use prev_terminated to check if goal was just reached)
        rewards = self._calculate_rewards(actions, prev_terminated)
        
        # Apply reward scaling and clipping
        for agent_id in rewards:
            rewards[agent_id] = rewards[agent_id] * self.reward_scale
            if self.reward_clip_range is not None:
                rewards[agent_id] = np.clip(rewards[agent_id], self.reward_clip_range[0], self.reward_clip_range[1])
        
        # Check termination and truncation for each agent
        self._update_termination_flags()
        
        # Get observations and info
        observations = self._get_observations()
        infos = self._get_infos()
        
        return observations, rewards, self.agent_terminated.copy(), self.agent_truncated.copy(), infos
    
    # Protected methods to be overridden by subclasses
    
    def _get_initial_states(self) -> Dict[int, Any]:
        """
        Get initial states for all agents.
        
        Returns:
            Dict mapping agent ID to initial state
        """
        return {i: None for i in range(self.num_agents)}
    
    def _get_observations(self) -> Dict[int, np.ndarray]:
        """
        Get observations for all agents.
        
        Returns:
            Dict mapping agent ID to observation
        """
        return {i: np.zeros(self.observation_spaces[i].shape, dtype=np.uint8) for i in range(self.num_agents)}
    
    def _update_states(self, actions: Dict[int, int]):
        """
        Update states for all agents based on their actions.
        
        Args:
            actions: Dict mapping agent ID to action
        """
        pass
    
    def _calculate_rewards(self, actions: Dict[int, int], prev_terminated: Optional[Dict[int, bool]] = None) -> Dict[int, float]:
        """
        Calculate rewards for all agents.
        
        Args:
            actions: Dict mapping agent ID to action
            prev_terminated: Previous termination state (optional, for subclasses)
            
        Returns:
            Dict mapping agent ID to reward
        """
        return {i: 0.0 for i in range(self.num_agents)}
    
    def _update_termination_flags(self):
        """
        Update termination and truncation flags for all agents.
        Updates both per-agent flags and global episode termination.
        """
        # Check individual agent termination
        for agent_id in range(self.num_agents):
            self.agent_terminated[agent_id] = self._is_agent_terminated(agent_id)
            self.agent_truncated[agent_id] = self._is_agent_truncated(agent_id)
        
        # Update global termination based on mode
        if self.reward_mode == 'cooperative':
            # All agents must be done for episode to end
            self.terminated = all(self.agent_terminated.values())
            self.truncated = all(self.agent_truncated.values()) or self.current_step >= self.episode_length
        else:  # competitive
            # Episode ends when any agent is done
            self.terminated = any(self.agent_terminated.values())
            self.truncated = any(self.agent_truncated.values()) or self.current_step >= self.episode_length
    
    def _is_agent_terminated(self, agent_id: int) -> bool:
        """
        Check if a specific agent has reached a terminal state.
        
        Args:
            agent_id: Agent identifier
            
        Returns:
            True if agent terminated, False otherwise
        """
        return False
    
    def _is_agent_truncated(self, agent_id: int) -> bool:
        """
        Check if a specific agent should be truncated.
        
        Args:
            agent_id: Agent identifier
            
        Returns:
            True if agent truncated, False otherwise
        """
        return self.current_step >= self.episode_length
    
    def _get_infos(self) -> Dict[int, Dict[str, Any]]:
        """
        Get info dicts for all agents.
        
        Returns:
            Dict mapping agent ID to info dict
        """
        return {i: {
            'step': self.current_step,
            'episode_length': self.episode_length,
            'agent_id': i
        } for i in range(self.num_agents)}


class MultiAgentGridWorld(MultiAgentBaseEnvironment):
    """
    Multi-agent grid world where agents navigate to goals.
    
    Supports both cooperative mode (all agents reach their goals) and
    competitive mode (race to a single goal).
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize multi-agent grid world."""
        super().__init__(config)
        
        # Grid configuration
        self.grid_size = self.config.get('grid_size', 10)
        
        # Set observation and action spaces for each agent
        for i in range(self.num_agents):
            self.action_spaces[i] = spaces.Discrete(4)  # up, right, down, left
            self.observation_spaces[i] = spaces.Box(
                low=0, high=self.grid_size-1, shape=(2,), dtype=np.int32
            )
        
        # Agent positions
        self.agent_positions = {}
        
        # Goals (one per agent in cooperative, shared in competitive)
        self.goal_positions = {}
        
        # Track previous distances for dense rewards
        self.prev_distances = {}
    
    def _get_initial_states(self) -> Dict[int, np.ndarray]:
        """Initialize agent and goal positions."""
        self.agent_positions = {}
        self.goal_positions = {}
        self.prev_distances = {}
        
        # Place agents at random positions (ensuring no overlaps)
        occupied_positions = set()
        for i in range(self.num_agents):
            while True:
                pos = np.array([
                    self.np_random.integers(0, self.grid_size),
                    self.np_random.integers(0, self.grid_size)
                ], dtype=np.int32)
                pos_tuple = tuple(pos)
                if pos_tuple not in occupied_positions:
                    self.agent_positions[i] = pos
                    occupied_positions.add(pos_tuple)
                    break
        
        # Place goals
        if self.reward_mode == 'cooperative':
            # Each agent gets its own goal
            for i in range(self.num_agents):
                while True:
                    goal = np.array([
                        self.np_random.integers(0, self.grid_size),
                        self.np_random.integers(0, self.grid_size)
                    ], dtype=np.int32)
                    goal_tuple = tuple(goal)
                    if goal_tuple not in occupied_positions:
                        self.goal_positions[i] = goal
                        occupied_positions.add(goal_tuple)
                        break
        else:  # competitive
            # Single shared goal
            while True:
                goal = np.array([
                    self.np_random.integers(0, self.grid_size),
                    self.np_random.integers(0, self.grid_size)
                ], dtype=np.int32)
                goal_tuple = tuple(goal)
                if goal_tuple not in occupied_positions:
                    for i in range(self.num_agents):
                        self.goal_positions[i] = goal
                    break
        
        # Initialize distances
        for i in range(self.num_agents):
            self.prev_distances[i] = np.linalg.norm(self.agent_positions[i] - self.goal_positions[i])
        
        return {i: self.agent_positions[i].copy() for i in range(self.num_agents)}
    
    def _get_observations(self) -> Dict[int, np.ndarray]:
        """Return current positions for all agents."""
        return {i: self.agent_positions[i].astype(np.int32) for i in range(self.num_agents)}
    
    def _update_states(self, actions: Dict[int, int]):
        """Update agent positions based on actions with collision handling."""
        # Map actions to movements
        movements = {
            0: np.array([-1, 0]),  # up
            1: np.array([0, 1]),   # right
            2: np.array([1, 0]),   # down
            3: np.array([0, -1])   # left
        }
        
        # Calculate proposed new positions
        proposed_positions = {}
        for agent_id, action in actions.items():
            new_pos = self.agent_positions[agent_id] + movements[action]
            # Keep within bounds
            new_pos = np.clip(new_pos, 0, self.grid_size - 1)
            proposed_positions[agent_id] = new_pos
        
        # Handle collisions
        if self.collision_mode == 'block':
            # Check for collisions and block moves
            final_positions = {}
            occupied = set()
            
            # First pass: agents that don't collide with anyone
            for agent_id, new_pos in proposed_positions.items():
                pos_tuple = tuple(new_pos)
                # Check collision with other agents' current positions
                other_agents_pos = {tuple(self.agent_positions[j]) for j in range(self.num_agents) if j != agent_id}
                if pos_tuple not in other_agents_pos:
                    final_positions[agent_id] = new_pos
                    occupied.add(pos_tuple)
                else:
                    # Stay in place if collision
                    final_positions[agent_id] = self.agent_positions[agent_id].copy()
            
            self.agent_positions = final_positions
            
        elif self.collision_mode == 'pass-through':
            # Agents can occupy same cell
            self.agent_positions = proposed_positions
            
        elif self.collision_mode == 'penalty':
            # Agents can move but get penalty (handled in reward calculation)
            self.agent_positions = proposed_positions
    
    def _calculate_rewards(self, actions: Dict[int, int], prev_terminated: Optional[Dict[int, bool]] = None) -> Dict[int, float]:
        """Calculate rewards based on goal proximity and mode."""
        rewards = {}
        
        if prev_terminated is None:
            prev_terminated = {i: False for i in range(self.num_agents)}
        
        for agent_id in range(self.num_agents):
            # Check if goal is reached NOW (after step)
            at_goal_now = np.array_equal(self.agent_positions[agent_id], self.goal_positions[agent_id])
            was_at_goal = prev_terminated.get(agent_id, False)
            
            if at_goal_now and not was_at_goal:
                # Just reached goal this step
                if self.reward_mode == 'competitive':
                    rewards[agent_id] = 100.0
                else:  # cooperative
                    rewards[agent_id] = 100.0
            elif at_goal_now and was_at_goal:
                # Was already at goal
                rewards[agent_id] = 0.0
            else:
                # Step penalty
                rewards[agent_id] = -1.0
                
                # Dense reward shaping (optional)
                if self.config.get('reward_type', 'sparse') == 'dense':
                    current_distance = np.linalg.norm(self.agent_positions[agent_id] - self.goal_positions[agent_id])
                    rewards[agent_id] += (self.prev_distances[agent_id] - current_distance)
                    self.prev_distances[agent_id] = current_distance
            
            # Collision penalty
            if self.collision_mode == 'penalty':
                # Check if this agent collides with others
                for other_id in range(self.num_agents):
                    if other_id != agent_id and np.array_equal(self.agent_positions[agent_id], self.agent_positions[other_id]):
                        rewards[agent_id] -= 10.0
                        break
        
        # Cooperative bonus: all agents reach their goals
        if self.reward_mode == 'cooperative':
            all_reached = all(np.array_equal(self.agent_positions[i], self.goal_positions[i]) for i in range(self.num_agents))
            if all_reached:
                for agent_id in range(self.num_agents):
                    if rewards[agent_id] >= 100:  # Only add bonus if just reached
                        rewards[agent_id] += 50.0  # Team bonus
        
        return rewards
    
    def _is_agent_terminated(self, agent_id: int) -> bool:
        """Agent terminates when reaching its goal."""
        return np.array_equal(self.agent_positions[agent_id], self.goal_positions[agent_id])
    
    def _get_infos(self) -> Dict[int, Dict[str, Any]]:
        """Return info with positions and goal status."""
        infos = {}
        for agent_id in range(self.num_agents):
            infos[agent_id] = {
                'step': self.current_step,
                'episode_length': self.episode_length,
                'agent_id': agent_id,
                'agent_pos': self.agent_positions[agent_id].tolist(),
                'goal_pos': self.goal_positions[agent_id].tolist(),
                'distance_to_goal': np.linalg.norm(self.agent_positions[agent_id] - self.goal_positions[agent_id]),
                'goal_reached': np.array_equal(self.agent_positions[agent_id], self.goal_positions[agent_id])
            }
        return infos
    
    def render(self, mode: str = 'human'):
        """Render the multi-agent grid world."""
        if mode == 'human':
            # Create grid visualization
            grid = np.full((self.grid_size, self.grid_size), '.', dtype=str)
            
            # Place goals
            for agent_id in range(self.num_agents):
                goal_pos = tuple(self.goal_positions[agent_id])
                if self.reward_mode == 'cooperative':
                    grid[goal_pos] = f'G{agent_id}'
                else:
                    grid[goal_pos] = 'G'
            
            # Place agents (may overlap goals)
            for agent_id in range(self.num_agents):
                agent_pos = tuple(self.agent_positions[agent_id])
                if grid[agent_pos] == '.':
                    grid[agent_pos] = f'A{agent_id}'
                elif grid[agent_pos].startswith('G'):
                    grid[agent_pos] = f'A{agent_id}*'  # Agent on goal
                else:
                    grid[agent_pos] = 'XX'  # Multiple agents
            
            # Print grid
            print('\n' + '=' * (self.grid_size * 3 + 1))
            for row in grid:
                print('|' + ' '.join(f'{cell:>2}' for cell in row) + '|')
            print('=' * (self.grid_size * 3 + 1))
            print(f'Step: {self.current_step}, Mode: {self.reward_mode}, Collision: {self.collision_mode}')
            for agent_id in range(self.num_agents):
                info = self._get_infos()[agent_id]
                print(f"Agent {agent_id}: pos={info['agent_pos']}, dist={info['distance_to_goal']:.2f}, goal={info['goal_reached']}")
