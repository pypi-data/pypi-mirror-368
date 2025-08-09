#!/usr/bin/env bash
set -euo pipefail

SELF=$(readlink -f "${BASH_SOURCE[0]}")
git -C "${SELF%/*}" submodule update --init --recursive
