"""
Tests for the benchmarking suite.
"""

import json
import tempfile
from pathlib import Path

import pytest

from tools.benchmark import EnvironmentBenchmark, compare_environments, load_environment_class, print_comparison_table
from environments.base_env import BaseEnvironment
from examples.simple_gridworld import SimpleGridWorld


class TestEnvironmentBenchmark:
    """Test suite for EnvironmentBenchmark class."""

    def test_benchmark_initialization(self):
        """Test that benchmark initializes correctly."""
        benchmark = EnvironmentBenchmark(BaseEnvironment, {})

        assert benchmark.env_class == BaseEnvironment
        assert benchmark.env_config == {}
        assert benchmark.results == {}

    def test_benchmark_with_config(self):
        """Test benchmark initialization with custom config."""
        config = {"episode_length": 50}
        benchmark = EnvironmentBenchmark(SimpleGridWorld, config)

        assert benchmark.env_class == SimpleGridWorld
        assert benchmark.env_config == config

    def test_benchmark_run(self):
        """Test that benchmark runs without error on BaseEnvironment."""
        benchmark = EnvironmentBenchmark(BaseEnvironment, {"episode_length": 10})
        results = benchmark.run(num_episodes=5)

        assert results is not None
        assert isinstance(results, dict)
        assert "environment" in results
        assert results["environment"] == "BaseEnvironment"
        assert results["num_episodes"] == 5

    def test_benchmark_run_simple_gridworld(self):
        """Test benchmark on SimpleGridWorld environment."""
        config = {"grid_size": 5, "episode_length": 20}
        benchmark = EnvironmentBenchmark(SimpleGridWorld, config)
        results = benchmark.run(num_episodes=5)

        assert results is not None
        assert results["environment"] == "SimpleGridWorld"
        assert results["num_episodes"] == 5

    def test_benchmark_results_structure(self):
        """Test that benchmark results have correct structure."""
        benchmark = EnvironmentBenchmark(BaseEnvironment, {"episode_length": 10})
        results = benchmark.run(num_episodes=3)

        # Check top-level keys
        assert "environment" in results
        assert "num_episodes" in results
        assert "throughput" in results
        assert "reset_latency" in results
        assert "step_latency" in results
        assert "observation_time" in results
        assert "memory" in results
        assert "gc_pressure" in results

        # Check throughput metrics
        assert "steps_per_second" in results["throughput"]
        assert "total_steps" in results["throughput"]
        assert "total_time_seconds" in results["throughput"]

        # Check reset latency metrics
        assert "mean_ms" in results["reset_latency"]
        assert "std_ms" in results["reset_latency"]
        assert "min_ms" in results["reset_latency"]
        assert "max_ms" in results["reset_latency"]

        # Check step latency metrics
        assert "mean_ms" in results["step_latency"]
        assert "p50_ms" in results["step_latency"]
        assert "p95_ms" in results["step_latency"]
        assert "p99_ms" in results["step_latency"]
        assert "std_ms" in results["step_latency"]

        # Check observation time metrics
        assert "mean_ms" in results["observation_time"]
        assert "total_ms" in results["observation_time"]
        assert "percentage_of_step" in results["observation_time"]

        # Check memory metrics
        assert "peak_mb" in results["memory"]
        assert "peak_bytes" in results["memory"]

        # Check GC pressure metrics
        assert "total_collections" in results["gc_pressure"]
        assert "collections_per_episode" in results["gc_pressure"]

    def test_benchmark_metrics_are_positive(self):
        """Test that all metric values are positive and reasonable."""
        benchmark = EnvironmentBenchmark(BaseEnvironment, {"episode_length": 10})
        results = benchmark.run(num_episodes=5)

        # Throughput should be positive
        assert results["throughput"]["steps_per_second"] > 0
        assert results["throughput"]["total_steps"] > 0
        assert results["throughput"]["total_time_seconds"] > 0

        # Reset latency should be positive
        assert results["reset_latency"]["mean_ms"] > 0
        assert results["reset_latency"]["min_ms"] >= 0
        assert results["reset_latency"]["max_ms"] >= results["reset_latency"]["min_ms"]

        # Step latency should be positive
        assert results["step_latency"]["mean_ms"] > 0
        assert results["step_latency"]["p50_ms"] > 0
        assert results["step_latency"]["p95_ms"] >= results["step_latency"]["p50_ms"]
        assert results["step_latency"]["p99_ms"] >= results["step_latency"]["p95_ms"]

        # Memory should be positive
        assert results["memory"]["peak_mb"] > 0
        assert results["memory"]["peak_bytes"] > 0

        # GC metrics should be non-negative
        assert results["gc_pressure"]["total_collections"] >= 0
        assert results["gc_pressure"]["collections_per_episode"] >= 0

    def test_benchmark_metrics_non_zero(self):
        """Test that key metrics are non-zero."""
        benchmark = EnvironmentBenchmark(BaseEnvironment, {"episode_length": 10})
        results = benchmark.run(num_episodes=5)

        # These should definitely be non-zero
        assert results["throughput"]["steps_per_second"] != 0
        assert results["throughput"]["total_steps"] != 0
        assert results["reset_latency"]["mean_ms"] != 0
        assert results["step_latency"]["mean_ms"] != 0
        assert results["memory"]["peak_mb"] != 0

    def test_save_results_json(self):
        """Test saving results to JSON file."""
        benchmark = EnvironmentBenchmark(BaseEnvironment, {"episode_length": 10})
        results = benchmark.run(num_episodes=3)

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "benchmark.json"
            benchmark.save_results(str(output_path))

            # Check file exists
            assert output_path.exists()

            # Check JSON is valid
            with open(output_path, "r") as f:
                loaded_results = json.load(f)

            assert loaded_results == results

    def test_save_results_creates_directory(self):
        """Test that save_results creates output directory if needed."""
        benchmark = EnvironmentBenchmark(BaseEnvironment, {"episode_length": 10})
        benchmark.run(num_episodes=3)

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "subdir" / "nested" / "benchmark.json"
            benchmark.save_results(str(output_path))

            assert output_path.exists()
            assert output_path.parent.exists()

    def test_json_output_format(self):
        """Test that JSON output format is valid and complete."""
        benchmark = EnvironmentBenchmark(BaseEnvironment, {"episode_length": 10})
        benchmark.run(num_episodes=3)

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "benchmark.json"
            benchmark.save_results(str(output_path))

            # Load and validate JSON
            with open(output_path, "r") as f:
                data = json.load(f)

            # Verify all expected fields are present
            assert data["environment"] == "BaseEnvironment"
            assert data["num_episodes"] == 3
            assert isinstance(data["throughput"]["steps_per_second"], (int, float))
            assert isinstance(data["reset_latency"]["mean_ms"], (int, float))
            assert isinstance(data["step_latency"]["mean_ms"], (int, float))
            assert isinstance(data["memory"]["peak_mb"], (int, float))

    def test_print_summary_without_results(self):
        """Test that print_summary handles empty results gracefully."""
        benchmark = EnvironmentBenchmark(BaseEnvironment, {})
        # Should not raise an error
        benchmark.print_summary()

    def test_print_summary_with_results(self, capsys):
        """Test that print_summary outputs formatted results."""
        benchmark = EnvironmentBenchmark(BaseEnvironment, {"episode_length": 10})
        benchmark.run(num_episodes=3)
        benchmark.print_summary()

        captured = capsys.readouterr()
        output = captured.out

        # Check that summary contains key information
        assert "BENCHMARK RESULTS" in output
        assert "BaseEnvironment" in output
        assert "Throughput:" in output
        assert "Reset Latency:" in output
        assert "Step Latency:" in output
        assert "Memory Usage:" in output
        assert "GC Pressure:" in output


class TestCompareEnvironments:
    """Test suite for environment comparison functionality."""

    def test_compare_two_environments(self):
        """Test comparison mode with multiple environments."""
        env_configs = [
            (BaseEnvironment, "BaseEnvironment", {"episode_length": 10}),
            (SimpleGridWorld, "SimpleGridWorld", {"grid_size": 5, "episode_length": 10}),
        ]

        results = compare_environments(env_configs, num_episodes=3)

        assert len(results) == 2
        assert "BaseEnvironment" in results
        assert "SimpleGridWorld" in results
        assert results["BaseEnvironment"]["num_episodes"] == 3
        assert results["SimpleGridWorld"]["num_episodes"] == 3

    def test_compare_environments_structure(self):
        """Test that comparison results have correct structure."""
        env_configs = [
            (BaseEnvironment, "BaseEnv", {"episode_length": 10}),
            (SimpleGridWorld, "GridWorld", {"grid_size": 5, "episode_length": 10}),
        ]

        results = compare_environments(env_configs, num_episodes=2)

        # Each environment should have full benchmark results
        for env_name in ["BaseEnv", "GridWorld"]:
            assert env_name in results
            assert "throughput" in results[env_name]
            assert "reset_latency" in results[env_name]
            assert "step_latency" in results[env_name]
            assert "memory" in results[env_name]
            assert "gc_pressure" in results[env_name]

    def test_print_comparison_table(self, capsys):
        """Test that comparison table prints correctly."""
        # Create mock results
        results = {
            "Env1": {
                "throughput": {"steps_per_second": 100.5},
                "reset_latency": {"mean_ms": 1.5},
                "step_latency": {"mean_ms": 0.5, "p95_ms": 1.0},
                "memory": {"peak_mb": 50.0},
                "gc_pressure": {"collections_per_episode": 2.5},
            },
            "Env2": {
                "throughput": {"steps_per_second": 200.0},
                "reset_latency": {"mean_ms": 1.0},
                "step_latency": {"mean_ms": 0.3, "p95_ms": 0.8},
                "memory": {"peak_mb": 40.0},
                "gc_pressure": {"collections_per_episode": 2.0},
            },
        }

        print_comparison_table(results)

        captured = capsys.readouterr()
        output = captured.out

        # Check table contains environment names and metrics
        assert "COMPARISON TABLE" in output
        assert "Env1" in output
        assert "Env2" in output
        assert "Steps per second" in output
        assert "Reset latency" in output
        assert "Step latency" in output
        assert "Peak memory" in output


class TestLoadEnvironmentClass:
    """Test suite for environment class loading."""

    def test_load_base_environment(self):
        """Test loading BaseEnvironment class."""
        env_class = load_environment_class("BaseEnvironment")
        assert env_class == BaseEnvironment

    def test_load_simple_gridworld(self):
        """Test loading SimpleGridWorld class."""
        env_class = load_environment_class("SimpleGridWorld")
        assert env_class == SimpleGridWorld

    def test_load_invalid_environment(self):
        """Test that loading invalid environment raises ImportError."""
        with pytest.raises(ImportError):
            load_environment_class("NonExistentEnvironment")

    def test_loaded_environment_is_usable(self):
        """Test that loaded environment class can be instantiated."""
        env_class = load_environment_class("SimpleGridWorld")
        env = env_class({"grid_size": 5})

        assert env is not None
        obs, info = env.reset()
        assert obs is not None


class TestBenchmarkReset:
    """Test suite for reset benchmarking."""

    def test_benchmark_reset(self):
        """Test reset benchmarking method."""
        benchmark = EnvironmentBenchmark(BaseEnvironment, {"episode_length": 10})
        env = BaseEnvironment({"episode_length": 10})

        reset_times = benchmark._benchmark_reset(env, 10)

        assert len(reset_times) == 10
        assert all(t > 0 for t in reset_times)
        assert all(isinstance(t, float) for t in reset_times)


class TestBenchmarkEpisodes:
    """Test suite for episode benchmarking."""

    def test_benchmark_episodes(self):
        """Test episode benchmarking method."""
        benchmark = EnvironmentBenchmark(BaseEnvironment, {"episode_length": 10})
        env = BaseEnvironment({"episode_length": 10})

        step_times, obs_times, total_steps, peak_memory, gc_count = benchmark._benchmark_episodes(env, 3)

        assert len(step_times) > 0
        assert len(obs_times) >= 0  # May be 0 if _get_observation not available
        assert total_steps > 0
        assert peak_memory > 0
        assert gc_count >= 0

        # Verify all step times are positive
        assert all(t > 0 for t in step_times)

    def test_benchmark_episodes_step_count(self):
        """Test that step count is accurate."""
        config = {"episode_length": 5}
        benchmark = EnvironmentBenchmark(BaseEnvironment, config)
        env = BaseEnvironment(config)

        step_times, obs_times, total_steps, peak_memory, gc_count = benchmark._benchmark_episodes(env, 2)

        # Should have approximately episode_length * num_episodes steps
        # (may vary slightly depending on termination conditions)
        assert total_steps > 0
        assert len(step_times) == total_steps


class TestBenchmarkIntegration:
    """Integration tests for the complete benchmark workflow."""

    def test_full_benchmark_workflow(self):
        """Test complete benchmark workflow from start to finish."""
        config = {"grid_size": 5, "episode_length": 20}
        benchmark = EnvironmentBenchmark(SimpleGridWorld, config)

        # Run benchmark
        results = benchmark.run(num_episodes=5)

        # Verify results
        assert results is not None
        assert results["num_episodes"] == 5

        # Save to file
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "results" / "benchmark.json"
            benchmark.save_results(str(output_path))

            # Verify file
            assert output_path.exists()
            with open(output_path, "r") as f:
                loaded = json.load(f)
            assert loaded == results

    def test_benchmark_with_different_episode_counts(self):
        """Test benchmark with different episode counts."""
        config = {"episode_length": 10}

        for num_episodes in [1, 5, 10]:
            benchmark = EnvironmentBenchmark(BaseEnvironment, config)
            results = benchmark.run(num_episodes=num_episodes)

            assert results["num_episodes"] == num_episodes
            assert results["throughput"]["total_steps"] > 0

    def test_benchmark_consistency(self):
        """Test that benchmark produces consistent results."""
        config = {"episode_length": 10}
        benchmark1 = EnvironmentBenchmark(BaseEnvironment, config)
        results1 = benchmark1.run(num_episodes=5)

        benchmark2 = EnvironmentBenchmark(BaseEnvironment, config)
        results2 = benchmark2.run(num_episodes=5)

        # Results should be in same ballpark (within 10x)
        # (exact values will vary due to timing)
        assert results1["throughput"]["steps_per_second"] > 0
        assert results2["throughput"]["steps_per_second"] > 0

        ratio = results1["throughput"]["steps_per_second"] / results2["throughput"]["steps_per_second"]
        assert 0.1 < ratio < 10.0  # Should be within 10x
