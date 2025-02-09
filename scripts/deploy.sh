# TODO: Add to README file instructions on how to deploy the server with this script

#!/bin/bash

# Exit on error
set -e

# Configuration
REMOTE_USER="morossini"
REMOTE_HOST="20.80.96.49"
REMOTE_DIR="/home/morossini/ai_agent_tool_server"
DOCKER_COMPOSE_FILE="app/docker/docker-compose.yml"
ENV_FILE=".env"

# Check if .env exists
if [ ! -f "$ENV_FILE" ]; then
    echo "Error: $ENV_FILE not found!"
    echo "Please create it from .env.example"
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
          --exclude 'venv' \
          --exclude '.pytest_cache' \
          ./ $REMOTE_USER@$REMOTE_HOST:$REMOTE_DIR/

# SSH into remote server and deploy
echo "Deploying on remote server..."
ssh $REMOTE_USER@$REMOTE_HOST "cd $REMOTE_DIR && \
    docker-compose -f $DOCKER_COMPOSE_FILE down && \
    docker-compose -f $DOCKER_COMPOSE_FILE build --no-cache && \
    docker-compose -f $DOCKER_COMPOSE_FILE up -d"

echo "Deployment completed successfully!"
echo "The server is now running at http://$REMOTE_HOST:8000"
echo "You can check the logs with:"
echo "ssh $REMOTE_USER@$REMOTE_HOST 'docker logs -f fastapi_tool_server'" 
