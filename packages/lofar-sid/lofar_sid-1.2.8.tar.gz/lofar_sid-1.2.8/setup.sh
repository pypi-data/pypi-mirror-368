#! /usr/bin/env bash
#
# Copyright (C) 2025 ASTRON (Netherlands Institute for Radio Astronomy)
# SPDX-License-Identifier: Apache-2.0
#

# Compatibility with zsh
# shellcheck disable=SC2128
if [ -z "${BASH_SOURCE}" ]; then
  # shellcheck disable=SC2296
  BASH_SOURCE=${(%):-%x}
fi

ABSOLUTE_PATH="$(realpath "$(dirname "${BASH_SOURCE}")")"
export PROJECT_DIR=${1:-${ABSOLUTE_PATH}}

# Create a virtual environment directory if it doesn't exist
VENV_DIR="${PROJECT_DIR}/venv"
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
fi

# Activate the virtual environment
# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate"
python -m pip install pre-commit
python -m pip install "tox>=4.21.0"

# Install git hooks
if [ ! -f "${PROJECT_DIR}/.git/hooks/post-checkout" ]; then
  # shellcheck disable=SC1091
  source "${PROJECT_DIR}/bin/install-hooks/submodule-and-lfs.sh"
fi

# Install git pre-commit pre-push hook
if [ ! -f "${PROJECT_DIR}/.git/hooks/pre-push.legacy" ]; then
  # shellcheck disable=SC1091
  source "${PROJECT_DIR}/bin/install-hooks/pre-commit.sh"
fi
