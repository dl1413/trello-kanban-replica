"""
Benchmarking Suite for RL Environments

This module provides a comprehensive benchmarking tool for evaluating the performance
of RL environments, including throughput, latency, memory usage, and GC pressure.
"""

import argparse
import gc
import json
import sys
import time
import tracemalloc
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np


class EnvironmentBenchmark:
    """
    Benchmark class for measuring RL environment performance.

    Measures:
    - Throughput: steps per second
    - Reset latency: average time for env.reset()
    - Step latency: average/p50/p95/p99 time for env.step()
    - Memory usage: peak RSS memory during episode execution
    - Observation generation time: time spent in _get_observation()
    - GC pressure: number of garbage collection events during benchmark
    """

    def __init__(self, env_class: type, env_config: Optional[Dict[str, Any]] = None):
        """
        Initialize the benchmark.

        Args:
            env_class: The environment class to benchmark
            env_config: Configuration dictionary for the environment
        """
        self.env_class = env_class
        self.env_config = env_config or {}
        self.results: Dict[str, Any] = {}

    def run(self, num_episodes: int = 100) -> Dict[str, Any]:
        """
        Run the complete benchmark suite.

        Args:
            num_episodes: Number of episodes to run for benchmarking

        Returns:
            Dictionary containing all benchmark results
        """
        print(f"Starting benchmark for {self.env_class.__name__}...")
        print(f"Running {num_episodes} episodes...")

        # Create environment
        env = self.env_class(self.env_config)

        try:
            # Measure reset latency
            reset_times = self._benchmark_reset(env, num_episodes)

            # Measure step latency, throughput, observation time, memory, and GC
            step_times, obs_times, total_steps, peak_memory, gc_count = self._benchmark_episodes(env, num_episodes)

            # Calculate metrics
            self.results = {
                "environment": self.env_class.__name__,
                "num_episodes": num_episodes,
                "throughput": {
                    "steps_per_second": total_steps / sum(step_times) if step_times else 0,
                    "total_steps": total_steps,
                    "total_time_seconds": sum(step_times),
                },
                "reset_latency": {
                    "mean_ms": np.mean(reset_times) * 1000,
                    "std_ms": np.std(reset_times) * 1000,
                    "min_ms": np.min(reset_times) * 1000,
                    "max_ms": np.max(reset_times) * 1000,
                },
                "step_latency": {
                    "mean_ms": np.mean(step_times) * 1000,
                    "p50_ms": np.percentile(step_times, 50) * 1000,
                    "p95_ms": np.percentile(step_times, 95) * 1000,
                    "p99_ms": np.percentile(step_times, 99) * 1000,
                    "std_ms": np.std(step_times) * 1000,
                },
                "observation_time": {
                    "mean_ms": np.mean(obs_times) * 1000,
                    "total_ms": sum(obs_times) * 1000,
                    "percentage_of_step": (sum(obs_times) / sum(step_times) * 100) if step_times else 0,
                },
                "memory": {"peak_mb": peak_memory / (1024 * 1024), "peak_bytes": peak_memory},
                "gc_pressure": {
                    "total_collections": gc_count,
                    "collections_per_episode": gc_count / num_episodes if num_episodes > 0 else 0,
                },
            }

            print("Benchmark complete!")
            return self.results
        finally:
            # Ensure environment is properly closed even if an error occurs
            env.close()

    def _benchmark_reset(self, env: Any, num_resets: int) -> List[float]:
        """
        Benchmark environment reset operations.

        Args:
            env: The environment instance
            num_resets: Number of reset operations to measure

        Returns:
            List of reset times in seconds
        """
        reset_times = []

        for _ in range(num_resets):
            start = time.perf_counter()
            env.reset()
            elapsed = time.perf_counter() - start
            reset_times.append(elapsed)

        return reset_times

    def _benchmark_episodes(self, env: Any, num_episodes: int) -> Tuple[List[float], List[float], int, int, int]:
        """
        Benchmark episode execution, measuring steps, observations, memory, and GC.

        Args:
            env: The environment instance
            num_episodes: Number of episodes to run

        Returns:
            Tuple of (step_times, obs_times, total_steps, peak_memory, gc_count)
        """
        step_times = []
        obs_times = []
        total_steps = 0

        # Start memory tracking
        tracemalloc.start()

        # Get initial GC stats
        gc_before = sum(gc.get_count())

        for episode in range(num_episodes):
            env.reset()
            done = False

            while not done:
                # Sample random action
                action = env.action_space.sample()

                # Measure step time
                step_start = time.perf_counter()
                obs, reward, terminated, truncated, info = env.step(action)
                step_elapsed = time.perf_counter() - step_start

                # Estimate observation time (this is approximate)
                # We measure a separate call to _get_observation
                if hasattr(env, "_get_observation"):
                    obs_measure_start = time.perf_counter()
                    _ = env._get_observation()
                    obs_elapsed = time.perf_counter() - obs_measure_start
                    obs_times.append(obs_elapsed)

                step_times.append(step_elapsed)
                total_steps += 1

                done = terminated or truncated

            # Progress indicator
            if (episode + 1) % max(1, num_episodes // 10) == 0:
                print(f"  Progress: {episode + 1}/{num_episodes} episodes")

        # Get memory stats
        current, peak_memory = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        # Get GC stats
        gc_after = sum(gc.get_count())
        gc_count = gc_after - gc_before

        return step_times, obs_times, total_steps, peak_memory, gc_count

    def save_results(self, output_path: str):
        """
        Save benchmark results to a JSON file.

        Args:
            output_path: Path to the output JSON file
        """
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, "w") as f:
            json.dump(self.results, f, indent=2)

        print(f"\nResults saved to: {output_path}")

    def print_summary(self):
        """Print a formatted summary of benchmark results to stdout."""
        if not self.results:
            print("No results to display. Run benchmark first.")
            return

        print("\n" + "=" * 80)
        print(f"BENCHMARK RESULTS: {self.results['environment']}")
        print("=" * 80)

        print("\nConfiguration:")
        print(f"  Episodes: {self.results['num_episodes']}")

        print("\nThroughput:")
        print(f"  Steps per second: {self.results['throughput']['steps_per_second']:.2f}")
        print(f"  Total steps:      {self.results['throughput']['total_steps']}")
        print(f"  Total time:       {self.results['throughput']['total_time_seconds']:.3f}s")

        print("\nReset Latency:")
        print(f"  Mean:  {self.results['reset_latency']['mean_ms']:.3f} ms")
        print(f"  Std:   {self.results['reset_latency']['std_ms']:.3f} ms")
        print(f"  Min:   {self.results['reset_latency']['min_ms']:.3f} ms")
        print(f"  Max:   {self.results['reset_latency']['max_ms']:.3f} ms")

        print("\nStep Latency:")
        print(f"  Mean:  {self.results['step_latency']['mean_ms']:.3f} ms")
        print(f"  P50:   {self.results['step_latency']['p50_ms']:.3f} ms")
        print(f"  P95:   {self.results['step_latency']['p95_ms']:.3f} ms")
        print(f"  P99:   {self.results['step_latency']['p99_ms']:.3f} ms")
        print(f"  Std:   {self.results['step_latency']['std_ms']:.3f} ms")

        print("\nObservation Generation:")
        print(f"  Mean time:        {self.results['observation_time']['mean_ms']:.3f} ms")
        print(f"  Total time:       {self.results['observation_time']['total_ms']:.3f} ms")
        print(f"  % of step time:   {self.results['observation_time']['percentage_of_step']:.2f}%")

        print("\nMemory Usage:")
        print(f"  Peak memory: {self.results['memory']['peak_mb']:.2f} MB")

        print("\nGC Pressure:")
        print(f"  Total collections:       {self.results['gc_pressure']['total_collections']}")
        print(f"  Collections per episode: {self.results['gc_pressure']['collections_per_episode']:.2f}")

        print("=" * 80 + "\n")


def compare_environments(env_configs: List[Tuple[type, str, Dict]], num_episodes: int = 100) -> Dict[str, Any]:
    """
    Compare multiple environments side by side.

    Args:
        env_configs: List of tuples (env_class, env_name, env_config)
        num_episodes: Number of episodes to run for each environment

    Returns:
        Dictionary containing comparison results
    """
    results = {}

    print("\n" + "=" * 80)
    print("COMPARISON MODE: Benchmarking multiple environments")
    print("=" * 80 + "\n")

    for env_class, env_name, env_config in env_configs:
        print(f"\nBenchmarking {env_name}...")
        benchmark = EnvironmentBenchmark(env_class, env_config)
        results[env_name] = benchmark.run(num_episodes)

    # Print comparison table
    print_comparison_table(results)

    return results


def print_comparison_table(results: Dict[str, Dict[str, Any]]):
    """
    Print a comparison table for multiple environment benchmarks.

    Args:
        results: Dictionary mapping environment names to their results
    """
    print("\n" + "=" * 120)
    print("COMPARISON TABLE")
    print("=" * 120)

    # Header
    env_names = list(results.keys())
    print(f"\n{'Metric':<40} " + " ".join([f"{name:>20}" for name in env_names]))
    print("-" * 120)

    # Throughput
    print(
        f"{'Steps per second':<40} "
        + " ".join([f"{results[name]['throughput']['steps_per_second']:>20.2f}" for name in env_names])
    )

    # Reset latency
    print(
        f"{'Reset latency (mean ms)':<40} "
        + " ".join([f"{results[name]['reset_latency']['mean_ms']:>20.3f}" for name in env_names])
    )

    # Step latency
    print(
        f"{'Step latency mean (ms)':<40} "
        + " ".join([f"{results[name]['step_latency']['mean_ms']:>20.3f}" for name in env_names])
    )
    print(
        f"{'Step latency P95 (ms)':<40} "
        + " ".join([f"{results[name]['step_latency']['p95_ms']:>20.3f}" for name in env_names])
    )

    # Memory
    print(
        f"{'Peak memory (MB)':<40} " + " ".join([f"{results[name]['memory']['peak_mb']:>20.2f}" for name in env_names])
    )

    # GC pressure
    print(
        f"{'GC collections per episode':<40} "
        + " ".join([f"{results[name]['gc_pressure']['collections_per_episode']:>20.2f}" for name in env_names])
    )

    print("=" * 120 + "\n")


def load_environment_class(env_name: str) -> type:
    """
    Dynamically load an environment class by name.

    Args:
        env_name: Name of the environment class

    Returns:
        The environment class

    Raises:
        ImportError: If the environment class cannot be loaded
    """
    # Try to import from environments module
    try:
        from environments.base_env import BaseEnvironment

        if env_name == "BaseEnvironment":
            return BaseEnvironment
    except ImportError:
        pass

    # Try to import from examples module
    try:
        if env_name == "SimpleGridWorld":
            from examples.simple_gridworld import SimpleGridWorld

            return SimpleGridWorld
    except ImportError:
        pass

    # Try other environment modules
    try:
        from environments.continuous_env import ContinuousEnvironment

        if env_name == "ContinuousEnvironment":
            return ContinuousEnvironment
    except ImportError:
        pass

    try:
        from environments.multi_agent_env import MultiAgentEnvironment

        if env_name == "MultiAgentEnvironment":
            return MultiAgentEnvironment
    except ImportError:
        pass

    raise ImportError(f"Could not load environment class: {env_name}")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Benchmark RL environments for performance analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Benchmark a single environment
  python tools/benchmark.py --env SimpleGridWorld --episodes 1000 --output results/benchmark.json

  # Benchmark with custom config
  python tools/benchmark.py --env SimpleGridWorld --episodes 500 --output results/bench.json

  # Compare multiple environments
  python tools/benchmark.py --compare BaseEnvironment,SimpleGridWorld --episodes 100 --output results/compare.json
        """,
    )

    parser.add_argument("--env", type=str, help="Name of the environment class to benchmark")

    parser.add_argument("--episodes", type=int, default=100, help="Number of episodes to run (default: 100)")

    parser.add_argument("--output", type=str, help="Path to output JSON file (optional)")

    parser.add_argument(
        "--compare",
        type=str,
        help='Comma-separated list of environments to compare (e.g., "BaseEnvironment,SimpleGridWorld")',
    )

    args = parser.parse_args()

    # Validate arguments
    if not args.env and not args.compare:
        parser.error("Either --env or --compare must be specified")

    if args.env and args.compare:
        parser.error("Cannot specify both --env and --compare")

    try:
        if args.compare:
            # Comparison mode
            env_names = [name.strip() for name in args.compare.split(",")]
            env_configs = []

            for env_name in env_names:
                env_class = load_environment_class(env_name)
                env_configs.append((env_class, env_name, {}))

            results = compare_environments(env_configs, args.episodes)

            # Save comparison results
            if args.output:
                output_file = Path(args.output)
                output_file.parent.mkdir(parents=True, exist_ok=True)
                with open(output_file, "w") as f:
                    json.dump(results, f, indent=2)
                print(f"\nComparison results saved to: {args.output}")
        else:
            # Single environment mode
            env_class = load_environment_class(args.env)

            benchmark = EnvironmentBenchmark(env_class, {})
            results = benchmark.run(args.episodes)
            benchmark.print_summary()

            if args.output:
                benchmark.save_results(args.output)

    except ImportError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error during benchmark: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
