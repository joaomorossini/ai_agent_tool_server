#!/bin/bash

# Exit on error
set -e

# Configuration
REMOTE_USER="morossini"
REMOTE_HOST="20.80.96.49"
REMOTE_DIR="/home/morossini/ai_agent_tool_server"
DOCKER_COMPOSE_FILE="app/docker/docker-compose.prod.yml"
ENV_FILE="app/docker/.env.prod"

# Check if .env.prod exists
if [ ! -f "$ENV_FILE" ]; then
    echo "Error: $ENV_FILE not found!"
    echo "Please create it from the template at ${ENV_FILE}.template"
    exit 1
fi

# Create remote directory if it doesn't exist
ssh $REMOTE_USER@$REMOTE_HOST "mkdir -p $REMOTE_DIR"

# Copy necessary files to remote server
echo "Copying files to remote server..."
rsync -avz --exclude 'logs' \
          --exclude '.git' \
          --exclude '__pycache__' \
          --exclude '*.pyc' \
          --exclude '.env' \
          --exclude 'venv' \
          --exclude '.pytest_cache' \
          ./ $REMOTE_USER@$REMOTE_HOST:$REMOTE_DIR/

# Copy production environment file
scp $ENV_FILE $REMOTE_USER@$REMOTE_HOST:$REMOTE_DIR/app/docker/.env

# SSH into remote server and deploy
echo "Deploying on remote server..."
ssh $REMOTE_USER@$REMOTE_HOST "cd $REMOTE_DIR && \
    docker-compose -f $DOCKER_COMPOSE_FILE down && \
    docker-compose -f $DOCKER_COMPOSE_FILE build --no-cache && \
    docker-compose -f $DOCKER_COMPOSE_FILE up -d"

echo "Deployment completed successfully!"
echo "You can check the logs with:"
echo "ssh $REMOTE_USER@$REMOTE_HOST 'docker logs -f fastapi_tool_server'" 
