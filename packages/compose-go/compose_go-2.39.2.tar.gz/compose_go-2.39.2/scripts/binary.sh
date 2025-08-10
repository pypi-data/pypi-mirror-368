#!/bin/bash

PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && cd .. && pwd )"
COMPOSE_DIR="$PROJECT_DIR/build/compose"

set -ex

rm -rf "$COMPOSE_DIR"
git clone https://github.com/docker/compose "$COMPOSE_DIR"

# Check if Docker Engine is installed
DOCKER_VERSION="$(docker --version)"
if [ -n "$DOCKER_VERSION" ]; then
  echo "🐳 Docker installed"
else
  echo "⛔ Docker Engine not found, please install Docker"
  echo "https://docs.docker.com/engine/install/"
  exit 1
fi

# Create binary / Update if exists
cd "$COMPOSE_DIR"
COMPOSE_VERSION="$(git tag --sort=-v:refname|head -n 1)"

git checkout "$COMPOSE_VERSION"

"${PROJECT_DIR}/scripts/versioning.sh" "$COMPOSE_VERSION"

make binary
cp -f "$COMPOSE_DIR/bin/build/docker-compose" "$PROJECT_DIR/src/compose"
rm -rf "$COMPOSE_DIR"
set +ex
