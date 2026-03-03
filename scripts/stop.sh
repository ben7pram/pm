#!/usr/bin/env bash
# Stop and remove the Docker container (Mac/Linux)
set -e

CONTAINER_NAME="pm-app"

if docker ps -a --format "{{.Names}}" | grep -Eq "^${CONTAINER_NAME}$"; then
    echo "Stopping and removing container $CONTAINER_NAME"
    docker rm -f "$CONTAINER_NAME"
else
    echo "No container named $CONTAINER_NAME found"
fi
