#!/usr/bin/env bash
# Build and run the Docker container (Mac/Linux)
set -e

IMAGE_NAME="pm-app"
CONTAINER_NAME="pm-app"

# determine script directory and project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# build the image using project root as context
docker build -t "$IMAGE_NAME" "$PROJECT_ROOT"

# stop any existing container with the same name
if docker ps -a --format "{{.Names}}" | grep -Eq "^${CONTAINER_NAME}$"; then
    echo "removing existing container $CONTAINER_NAME"
    docker rm -f "$CONTAINER_NAME"
fi

# run container
docker run --name "$CONTAINER_NAME" -p 8000:8000 -d "$IMAGE_NAME"

echo "Container started on http://localhost:8000"