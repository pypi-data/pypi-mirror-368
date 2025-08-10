#!/usr/bin/env bash
PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && cd .. && pwd )"

set -e

if [ "$1" == "" ]; then
  echo "Version parameter is required."
  exit 1
fi

SEARCH_BY="version\s*=\s*\"v[0-9]*\.[0-9]*\.[0-9]*\"\s*#\s*docker-compose\sversion"
REPLACE_BY="version = \"$1\"  # docker-compose version"

PYPROJECT_PATH="${PROJECT_DIR}/pyproject.toml"

ORIGINAL_CONTENT=$(cat "${PYPROJECT_PATH}")
sed -i "s/$SEARCH_BY/$REPLACE_BY/" "$PYPROJECT_PATH"
NEW_CONTENT=$(cat "${PYPROJECT_PATH}")

if [ "${ORIGINAL_CONTENT}" == "${NEW_CONTENT}" ]; then
  echo "[EE] The project uses already the latest docker-compose version."
  exit 0
fi
