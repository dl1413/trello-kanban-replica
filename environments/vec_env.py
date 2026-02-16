"""
Vectorized Environment Wrappers for Parallel Environment Execution

This module provides synchronous and asynchronous vectorized environment wrappers
that allow running multiple environment instances in parallel for efficient training.
"""

import multiprocessing as mp
import numpy as np
from typing import Callable, List, Tuple, Dict, Optional
from abc import ABC, abstractmethod
import gymnasium as gym


class VectorizedEnv(ABC):
    """
    Base class for vectorized environments.

    This class defines the interface for vectorized environment wrappers that run
    multiple environment instances in parallel or sequentially.
    """

    def __init__(self, env_fn: Callable[[], gym.Env], num_envs: int):
        """
        Initialize the vectorized environment.

        Args:
            env_fn: Factory function that creates a single environment instance
            num_envs: Number of environment instances to run

        Raises:
            ValueError: If num_envs is less than 1
        """
        if num_envs < 1:
            raise ValueError(f"num_envs must be at least 1, got {num_envs}")

        self.env_fn = env_fn
        self.num_envs = num_envs
        self.closed = False

        # Create a temporary environment to get spaces
        temp_env = env_fn()
        self.single_observation_space = temp_env.observation_space
        self.single_action_space = temp_env.action_space
        temp_env.close()

    @abstractmethod
    def reset(self, seed: Optional[int] = None) -> np.ndarray:
        """
        Reset all environments.

        Args:
            seed: Optional seed for reproducibility. If provided, environments will be
                  seeded as seed, seed+1, seed+2, etc.

        Returns:
            Stacked observations from all environments with shape (num_envs, *obs_shape)
        """
        pass

    @abstractmethod
    def step(self, actions: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, List[Dict]]:
        """
        Step all environments with the given actions.

        Args:
            actions: Array of actions with shape (num_envs,)

        Returns:
            observations: Stacked observations (num_envs, *obs_shape)
            rewards: Array of rewards (num_envs,)
            terminated: Array of terminated flags (num_envs,)
            truncated: Array of truncated flags (num_envs,)
            infos: List of info dictionaries, one per environment
        """
        pass

    @abstractmethod
    def close(self):
        """Clean up all environment resources."""
        pass


class SyncVectorEnv(VectorizedEnv):
    """
    Synchronous vectorized environment wrapper.

    Runs multiple environment instances sequentially. Simpler implementation
    that's easier to debug but slower than async version.
    """

    def __init__(self, env_fn: Callable[[], gym.Env], num_envs: int):
        """
        Initialize synchronous vectorized environment.

        Args:
            env_fn: Factory function that creates a single environment instance
            num_envs: Number of environment instances to run
        """
        super().__init__(env_fn, num_envs)
        self.envs = [env_fn() for _ in range(num_envs)]

    def reset(self, seed: Optional[int] = None) -> np.ndarray:
        """
        Reset all environments.

        Args:
            seed: Optional seed for reproducibility. Environments are seeded sequentially.

        Returns:
            Stacked observations from all environments with shape (num_envs, *obs_shape)
        """
        if self.closed:
            raise RuntimeError("Cannot reset closed environment. Create a new instance.")

        observations = []
        for i, env in enumerate(self.envs):
            env_seed = None if seed is None else seed + i
            obs, _ = env.reset(seed=env_seed)
            observations.append(obs)

        return np.stack(observations, axis=0)

    def step(self, actions: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, List[Dict]]:
        """
        Step all environments with the given actions.

        Automatically resets environments that reach terminal or truncated states.

        Args:
            actions: Array of actions with shape (num_envs,)

        Returns:
            observations: Stacked observations (num_envs, *obs_shape)
            rewards: Array of rewards (num_envs,)
            terminated: Array of terminated flags (num_envs,)
            truncated: Array of truncated flags (num_envs,)
            infos: List of info dictionaries with 'final_observation' and 'final_info'
                   keys added when environment auto-resets
        """
        if self.closed:
            raise RuntimeError("Cannot step closed environment. Create a new instance.")

        if len(actions) != self.num_envs:
            raise ValueError(f"Expected {self.num_envs} actions, got {len(actions)}")

        observations = []
        rewards = []
        terminateds = []
        truncateds = []
        infos = []

        for i, (env, action) in enumerate(zip(self.envs, actions)):
            obs, reward, terminated, truncated, info = env.step(action)
            rewards.append(reward)
            terminateds.append(terminated)
            truncateds.append(truncated)

            # Auto-reset if episode is done
            if terminated or truncated:
                info['final_observation'] = obs
                info['final_info'] = info.copy()
                obs, reset_info = env.reset()
                info['_final_observation'] = True
                info['_final_info'] = True

            observations.append(obs)
            infos.append(info)

        return (
            np.stack(observations, axis=0),
            np.array(rewards, dtype=np.float32),
            np.array(terminateds, dtype=bool),
            np.array(truncateds, dtype=bool),
            infos
        )

    def close(self):
        """Clean up all environment resources."""
        if not self.closed:
            for env in self.envs:
                env.close()
            self.closed = True


def _worker(remote: mp.connection.Connection, parent_remote: mp.connection.Connection, env_fn: Callable):
    """
    Worker function for asynchronous environment execution.

    This function runs in a separate process and handles communication with the
    main process through pipes.

    Args:
        remote: Connection to receive commands from parent
        parent_remote: Connection to send results to parent (closed in worker)
        env_fn: Factory function to create environment instance
    """
    parent_remote.close()
    env = env_fn()

    try:
        while True:
            cmd, data = remote.recv()

            if cmd == 'reset':
                obs, info = env.reset(seed=data)
                remote.send((obs, info))

            elif cmd == 'step':
                obs, reward, terminated, truncated, info = env.step(data)

                # Auto-reset if episode is done
                if terminated or truncated:
                    info['final_observation'] = obs
                    info['final_info'] = info.copy()
                    obs, reset_info = env.reset()
                    info['_final_observation'] = True
                    info['_final_info'] = True

                remote.send((obs, reward, terminated, truncated, info))

            elif cmd == 'close':
                env.close()
                remote.close()
                break

            else:
                raise NotImplementedError(f"Unknown command: {cmd}")

    except KeyboardInterrupt:
        env.close()
        remote.close()


class AsyncVectorEnv(VectorizedEnv):
    """
    Asynchronous vectorized environment wrapper using multiprocessing.

    Runs multiple environment instances in parallel using separate processes.
    More efficient than sync version but slightly more complex.
    """

    def __init__(self, env_fn: Callable[[], gym.Env], num_envs: int):
        """
        Initialize asynchronous vectorized environment.

        Args:
            env_fn: Factory function that creates a single environment instance
            num_envs: Number of environment instances to run
        """
        super().__init__(env_fn, num_envs)

        self.waiting = False
        self.remotes = None
        self.work_remotes = None
        self.processes = []

        self.remotes, self.work_remotes = zip(*[mp.Pipe() for _ in range(num_envs)])

        for work_remote, remote in zip(self.work_remotes, self.remotes):
            process = mp.Process(
                target=_worker,
                args=(work_remote, remote, env_fn),
                daemon=True
            )
            process.start()
            self.processes.append(process)
            work_remote.close()

    def reset(self, seed: Optional[int] = None) -> np.ndarray:
        """
        Reset all environments.

        Args:
            seed: Optional seed for reproducibility. Environments are seeded sequentially.

        Returns:
            Stacked observations from all environments with shape (num_envs, *obs_shape)
        """
        if self.closed:
            raise RuntimeError("Cannot reset closed environment. Create a new instance.")

        for i, remote in enumerate(self.remotes):
            env_seed = None if seed is None else seed + i
            remote.send(('reset', env_seed))

        observations = []
        for remote in self.remotes:
            obs, _ = remote.recv()
            observations.append(obs)

        return np.stack(observations, axis=0)

    def step(self, actions: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, List[Dict]]:
        """
        Step all environments with the given actions.

        Automatically resets environments that reach terminal or truncated states.

        Args:
            actions: Array of actions with shape (num_envs,)

        Returns:
            observations: Stacked observations (num_envs, *obs_shape)
            rewards: Array of rewards (num_envs,)
            terminated: Array of terminated flags (num_envs,)
            truncated: Array of truncated flags (num_envs,)
            infos: List of info dictionaries with 'final_observation' and 'final_info'
                   keys added when environment auto-resets
        """
        if self.closed:
            raise RuntimeError("Cannot step closed environment. Create a new instance.")

        if len(actions) != self.num_envs:
            raise ValueError(f"Expected {self.num_envs} actions, got {len(actions)}")

        # Send actions to all workers
        for remote, action in zip(self.remotes, actions):
            remote.send(('step', action))

        # Collect results
        observations = []
        rewards = []
        terminateds = []
        truncateds = []
        infos = []

        for remote in self.remotes:
            obs, reward, terminated, truncated, info = remote.recv()
            observations.append(obs)
            rewards.append(reward)
            terminateds.append(terminated)
            truncateds.append(truncated)
            infos.append(info)

        return (
            np.stack(observations, axis=0),
            np.array(rewards, dtype=np.float32),
            np.array(terminateds, dtype=bool),
            np.array(truncateds, dtype=bool),
            infos
        )

    def close(self):
        """Clean up all environment resources and terminate worker processes."""
        if not self.closed:
            # Send close command to all workers
            for remote in self.remotes:
                if not remote.closed:
                    try:
                        remote.send(('close', None))
                    except Exception:
                        pass

            # Wait for processes to terminate
            for process in self.processes:
                process.join(timeout=5)
                if process.is_alive():
                    process.terminate()
                    process.join(timeout=1)
                if process.is_alive():
                    process.kill()

            # Close all pipes
            for remote in self.remotes:
                if not remote.closed:
                    remote.close()

            self.closed = True

    def __del__(self):
        """Ensure processes are cleaned up on deletion."""
        if hasattr(self, 'closed') and not self.closed:
            self.close()
