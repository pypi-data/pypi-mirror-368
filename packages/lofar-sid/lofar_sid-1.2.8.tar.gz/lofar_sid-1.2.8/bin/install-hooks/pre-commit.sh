#!/bin/bash

if [ ! -f "setup.sh" ]; then
  echo "pre-commit.sh must be executed with repository root as working directory!"
  exit 1
fi

pre-commit install --hook-type pre-push
