#!/bin/bash

# Build and run the libadic Docker container
set -e

echo "Building libadic Docker image..."
docker-compose build

echo "Starting libadic container..."
docker-compose up -d

echo "Building the library inside container..."
docker-compose exec libadic bash -c "cd build && cmake .. && make -j$(nproc)"

echo "Running tests..."
docker-compose exec libadic bash -c "cd build && ctest --verbose"

echo "Build complete. To enter the container, run:"
echo "  docker-compose exec libadic bash"