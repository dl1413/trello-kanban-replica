"""
Reinforcement Learning Environments Package

This package contains base classes and implementations for RL environments
optimized for Verita AI's requirements.
"""

from .base_env import BaseEnvironment
from .curriculum_wrapper import CurriculumWrapper
from .vec_env import VectorizedEnv, SyncVectorEnv, AsyncVectorEnv

__version__ = "1.0.0"
__all__ = ["BaseEnvironment", "CurriculumWrapper", "VectorizedEnv", "SyncVectorEnv", "AsyncVectorEnv"]
