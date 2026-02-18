"""
Utility script to create a new RL environment from template
"""

import os
import argparse
from pathlib import Path

ENVIRONMENT_TEMPLATE = '''"""
{env_name} Environment

Description: Add your environment description here
"""

from environments.base_env import BaseEnvironment
from gymnasium import spaces
import numpy as np
from typing import Dict, Any, Optional


class {class_name}(BaseEnvironment):
    """
    Custom RL environment: {env_name}
    
    Observation: TODO: Describe observation space
    Actions: TODO: Describe action space
    Reward: TODO: Describe reward function
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the environment."""
        super().__init__(config)
        
        # TODO: Define your action and observation spaces
        self.action_space = spaces.Discrete(4)
        self.observation_space = spaces.Box(
            low=0, high=1, shape=(10,), dtype=np.float32
        )
        
        # TODO: Add custom attributes
        
    def _get_initial_state(self):
        """Initialize environment state."""
        # TODO: Implement initial state
        return np.zeros(10, dtype=np.float32)
    
    def _get_observation(self):
        """Get current observation."""
        # TODO: Implement observation function
        return self.state
    
    def _update_state(self, action: int):
        """Update state based on action."""
        # TODO: Implement state update logic
        pass
    
    def _calculate_reward(self, action: int) -> float:
        """Calculate reward for the action."""
        # TODO: Implement reward function
        return 0.0
    
    def _is_terminated(self) -> bool:
        """Check if episode has reached terminal state."""
        # TODO: Implement terminal state conditions
        return False
    
    def _is_truncated(self) -> bool:
        """Check if episode should be truncated (time limit)."""
        return self.current_step >= self.episode_length
    
    def _get_info(self) -> Dict[str, Any]:
        """Get additional information."""
        info = super()._get_info()
        # TODO: Add custom info
        return info
    
    def render(self, mode: str = 'human'):
        """Render the environment."""
        if mode == 'human':
            # TODO: Implement rendering
            print(f'Step: {{self.current_step}}, State: {{self.state}}')


if __name__ == '__main__':
    """Demo the environment."""
    # Create environment
    env = {class_name}()
    
    # Run a test episode
    obs, info = env.reset(seed=42)
    print(f'Initial observation: {{obs}}')
    
    terminated = False
    truncated = False
    total_reward = 0
    
    while not (terminated or truncated):
        action = env.action_space.sample()
        obs, reward, terminated, truncated, info = env.step(action)
        total_reward += reward
        
        if env.current_step % 10 == 0:
            env.render()
    
    print(f'Episode finished! Total reward: {{total_reward}}')
    env.close()
'''


TEST_TEMPLATE = '''"""
Tests for {env_name} Environment
"""

import pytest
import numpy as np
from environments.{module_name} import {class_name}


class Test{class_name}:
    """Test suite for {class_name}."""
    
    def test_initialization(self):
        """Test that environment initializes correctly."""
        env = {class_name}()
        
        assert env is not None
        assert env.action_space is not None
        assert env.observation_space is not None
    
    def test_reset(self):
        """Test reset functionality."""
        env = {class_name}()
        obs, info = env.reset()
        
        assert env.observation_space.contains(obs)
        assert env.current_step == 0
        assert isinstance(info, dict)
    
    def test_step(self):
        """Test step functionality."""
        env = {class_name}()
        env.reset()
        
        obs, reward, terminated, truncated, info = env.step(0)
        
        assert env.observation_space.contains(obs)
        assert isinstance(reward, (int, float))
        assert isinstance(terminated, bool)
        assert isinstance(truncated, bool)
        assert isinstance(info, dict)
    
    def test_episode_completion(self):
        """Test running a complete episode."""
        env = {class_name}()
        obs, info = env.reset()
        
        terminated = False
        truncated = False
        steps = 0
        
        while not (terminated or truncated) and steps < 1000:
            action = env.action_space.sample()
            obs, reward, terminated, truncated, info = env.step(action)
            steps += 1
        
        assert steps > 0
    
    # TODO: Add more tests specific to your environment


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
'''


def create_environment(name: str, output_dir: str = "environments"):
    """
    Create a new environment from template.

    Args:
        name: Name of the environment (e.g., 'my_custom_env')
        output_dir: Directory to create the environment in
    """
    # Convert name to valid Python identifiers
    module_name = name.lower().replace(" ", "_").replace("-", "_")
    class_name = "".join(word.capitalize() for word in module_name.split("_"))

    # Create environment file
    env_path = Path(output_dir) / f"{module_name}.py"
    env_content = ENVIRONMENT_TEMPLATE.format(env_name=name, class_name=class_name, module_name=module_name)

    with open(env_path, "w") as f:
        f.write(env_content)

    print(f"✓ Created environment: {env_path}")

    # Create test file
    test_path = Path("tests") / f"test_{module_name}.py"
    test_content = TEST_TEMPLATE.format(env_name=name, class_name=class_name, module_name=module_name)

    with open(test_path, "w") as f:
        f.write(test_content)

    print(f"✓ Created test file: {test_path}")

    # Print next steps
    print(f"""
Environment '{name}' created successfully!

Next steps:
1. Edit {env_path} to implement your environment logic
2. Edit {test_path} to add tests
3. Run tests: pytest {test_path}
4. Test your environment: python {env_path}

Documentation:
- See docs/environment_development.md for detailed guide
- See examples/simple_gridworld.py for a complete example
""")


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Create a new RL environment from template")
    parser.add_argument("--name", type=str, required=True, help='Name of the environment (e.g., "my_custom_env")')
    parser.add_argument(
        "--output-dir",
        type=str,
        default="environments",
        help="Directory to create the environment in (default: environments)",
    )

    args = parser.parse_args()

    # Check if directories exist
    if not os.path.exists(args.output_dir):
        print(f"Error: Directory {args.output_dir} does not exist")
        return

    if not os.path.exists("tests"):
        print("Error: tests directory does not exist")
        return

    create_environment(args.name, args.output_dir)


if __name__ == "__main__":
    main()
