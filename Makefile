# Makefile for RL Environment Framework

.PHONY: help install test lint format type-check clean docs run-example

help:  ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:  ## Install dependencies
	pip install -r requirements.txt

install-dev:  ## Install development dependencies
	pip install -r requirements.txt
	pip install pre-commit safety bandit

test:  ## Run all tests
	pytest tests/ -v

test-cov:  ## Run tests with coverage report
	pytest tests/ -v --cov=environments --cov=examples --cov-report=html --cov-report=term

test-fast:  ## Run tests without slow tests
	pytest tests/ -v -m "not slow"

lint:  ## Run linting checks
	flake8 environments/ examples/ tests/ --count --max-complexity=10 --max-line-length=127 --statistics

format:  ## Format code with black
	black environments/ examples/ tests/

format-check:  ## Check code formatting without making changes
	black --check environments/ examples/ tests/

type-check:  ## Run type checking with mypy
	mypy environments/ examples/ --ignore-missing-imports

security:  ## Run security checks
	safety check
	bandit -r environments/ examples/ -ll

clean:  ## Clean up temporary files
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type d -name "htmlcov" -exec rm -rf {} +
	find . -type f -name ".coverage" -delete
	find . -type f -name "coverage.xml" -delete

run-example:  ## Run the simple gridworld example
	python examples/simple_gridworld.py

train-q-learning:  ## Train Q-Learning agent
	python examples/q_learning_agent.py

train-baseline:  ## Train random baseline agent
	python examples/train_example.py

train-easy:  ## Train on easy configuration
	python examples/q_learning_agent.py --config configs/easy_config.yaml

train-medium:  ## Train on medium configuration  
	python examples/q_learning_agent.py --config configs/medium_config.yaml

train-hard:  ## Train on hard configuration
	python examples/q_learning_agent.py --config configs/hard_config.yaml

setup-hooks:  ## Setup pre-commit hooks
	pre-commit install

run-hooks:  ## Run pre-commit hooks on all files
	pre-commit run --all-files

docs:  ## Generate documentation (placeholder)
	@echo "Documentation generation not yet implemented"

all: lint test  ## Run linting and tests
