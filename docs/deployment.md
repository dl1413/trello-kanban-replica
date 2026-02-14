# Deployment Guide

## Overview

This guide covers deploying RL environments for production use at Verita AI.

## Table of Contents

1. [Local Deployment](#local-deployment)
2. [Docker Deployment](#docker-deployment)
3. [Cloud Deployment](#cloud-deployment)
4. [CI/CD Integration](#cicd-integration)
5. [Monitoring and Logging](#monitoring-and-logging)

## Local Deployment

### Development Setup

```bash
# Clone repository
git clone https://github.com/dl1413/trello-kanban-replica.git
cd trello-kanban-replica

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run tests
pytest tests/
```

### Running Environments

```bash
# Run example environment
python examples/simple_gridworld.py

# Run training script
python examples/train_example.py
```

## Docker Deployment

### Dockerfile

Create a `Dockerfile` in the project root:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Run tests
RUN pytest tests/

# Default command
CMD ["python", "examples/train_example.py"]
```

### Building Docker Image

```bash
# Build image
docker build -t verita-ai/rl-environments:latest .

# Run container
docker run -it verita-ai/rl-environments:latest

# Run with volume mount for development
docker run -it -v $(pwd):/app verita-ai/rl-environments:latest bash
```

### Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  rl-environment:
    build: .
    image: verita-ai/rl-environments:latest
    volumes:
      - ./configs:/app/configs
      - ./logs:/app/logs
    environment:
      - PYTHONUNBUFFERED=1
      - CUDA_VISIBLE_DEVICES=0
    command: python examples/train_example.py
    
  tensorboard:
    image: tensorflow/tensorflow:latest
    ports:
      - "6006:6006"
    volumes:
      - ./logs:/logs
    command: tensorboard --logdir=/logs --host=0.0.0.0
```

Run with:

```bash
docker-compose up
```

## Cloud Deployment

### AWS Deployment

#### Using EC2

```bash
# Launch EC2 instance (GPU-enabled for training)
aws ec2 run-instances \
    --image-id ami-xxxxxxxxxx \
    --instance-type p3.2xlarge \
    --key-name your-key \
    --security-group-ids sg-xxxxxxxxxx

# SSH into instance
ssh -i your-key.pem ubuntu@ec2-xx-xx-xx-xx.compute.amazonaws.com

# Setup environment
git clone https://github.com/dl1413/trello-kanban-replica.git
cd trello-kanban-replica
pip install -r requirements.txt

# Run training
python examples/train_example.py
```

#### Using ECS (Container Service)

1. Push Docker image to ECR:

```bash
# Authenticate Docker to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin your-account.dkr.ecr.us-east-1.amazonaws.com

# Tag and push image
docker tag verita-ai/rl-environments:latest your-account.dkr.ecr.us-east-1.amazonaws.com/rl-environments:latest
docker push your-account.dkr.ecr.us-east-1.amazonaws.com/rl-environments:latest
```

2. Create ECS task definition
3. Create ECS service
4. Deploy

### Google Cloud Platform

#### Using Compute Engine

```bash
# Create VM instance
gcloud compute instances create rl-training-vm \
    --machine-type=n1-standard-8 \
    --accelerator=type=nvidia-tesla-v100,count=1 \
    --image-family=pytorch-latest-gpu \
    --image-project=deeplearning-platform-release

# SSH and setup
gcloud compute ssh rl-training-vm
```

#### Using Kubernetes (GKE)

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: rl-environment
spec:
  replicas: 3
  selector:
    matchLabels:
      app: rl-environment
  template:
    metadata:
      labels:
        app: rl-environment
    spec:
      containers:
      - name: rl-environment
        image: gcr.io/your-project/rl-environments:latest
        resources:
          limits:
            nvidia.com/gpu: 1
```

Deploy:

```bash
kubectl apply -f deployment.yaml
```

## CI/CD Integration

### GitHub Actions

Create `.github/workflows/ci.yml`:

```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.9
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-cov
    
    - name: Run tests
      run: |
        pytest --cov=environments tests/
    
    - name: Upload coverage
      uses: codecov/codecov-action@v2

  build:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Build Docker image
      run: |
        docker build -t verita-ai/rl-environments:${{ github.sha }} .
    
    - name: Push to registry
      run: |
        echo ${{ secrets.DOCKER_PASSWORD }} | docker login -u ${{ secrets.DOCKER_USERNAME }} --password-stdin
        docker push verita-ai/rl-environments:${{ github.sha }}
```

### GitLab CI

Create `.gitlab-ci.yml`:

```yaml
stages:
  - test
  - build
  - deploy

test:
  stage: test
  image: python:3.9
  script:
    - pip install -r requirements.txt
    - pytest --cov=environments tests/

build:
  stage: build
  image: docker:latest
  services:
    - docker:dind
  script:
    - docker build -t $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA .
    - docker push $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA

deploy:
  stage: deploy
  script:
    - kubectl set image deployment/rl-environment rl-environment=$CI_REGISTRY_IMAGE:$CI_COMMIT_SHA
```

## Monitoring and Logging

### TensorBoard

```python
from torch.utils.tensorboard import SummaryWriter

writer = SummaryWriter('logs/experiment_1')

# Log metrics during training
writer.add_scalar('reward/episode', episode_reward, episode)
writer.add_scalar('length/episode', episode_length, episode)

writer.close()
```

Run TensorBoard:

```bash
tensorboard --logdir=logs --host=0.0.0.0 --port=6006
```

### Weights & Biases

```python
import wandb

# Initialize
wandb.init(project='rl-environments', name='experiment_1')

# Log metrics
wandb.log({
    'episode_reward': episode_reward,
    'episode_length': episode_length,
    'step': step
})
```

### Prometheus Metrics

```python
from prometheus_client import Counter, Histogram, start_http_server

# Define metrics
episode_counter = Counter('episodes_total', 'Total episodes')
reward_histogram = Histogram('episode_reward', 'Episode rewards')

# Start metrics server
start_http_server(8000)

# Record metrics
episode_counter.inc()
reward_histogram.observe(episode_reward)
```

### Logging Best Practices

```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/training.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Use in code
logger.info(f'Starting episode {episode}')
logger.debug(f'State: {state}')
logger.warning(f'Low reward: {reward}')
```

## Production Checklist

- [ ] Tests passing (>80% coverage)
- [ ] Documentation complete
- [ ] Configuration files validated
- [ ] Docker image builds successfully
- [ ] CI/CD pipeline configured
- [ ] Monitoring and logging setup
- [ ] Resource limits defined
- [ ] Backup strategy implemented
- [ ] Security review completed
- [ ] Performance benchmarks met

## Scaling Considerations

### Horizontal Scaling

Use multiple environment instances:

```python
from gym.vector import AsyncVectorEnv

num_envs = 16
envs = AsyncVectorEnv([make_env for _ in range(num_envs)])
```

### Distributed Training

Use Ray for distributed training:

```python
import ray
from ray.rllib.algorithms.ppo import PPO

ray.init()

config = {
    "num_workers": 8,
    "num_gpus": 2,
}

algo = PPO(config=config)
```

## Security

### Environment Variables

Never hardcode secrets:

```bash
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
```

### Network Security

- Use VPCs and security groups
- Enable HTTPS/TLS for APIs
- Implement authentication and authorization
- Regular security audits

## Troubleshooting

### Common Issues

1. **Out of Memory**: Reduce batch size or use gradient accumulation
2. **Slow Training**: Use GPU acceleration and parallel environments
3. **Divergent Training**: Adjust learning rate and reward scaling
4. **Container Crashes**: Check resource limits and logs

### Debug Commands

```bash
# Check container logs
docker logs container_name

# Enter running container
docker exec -it container_name bash

# Monitor resource usage
docker stats

# Kubernetes logs
kubectl logs pod_name
```

## Support

For deployment issues, contact the Verita AI DevOps team or open an issue on GitHub.
