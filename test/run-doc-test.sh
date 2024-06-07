#! /usr/bin/env bash

SCRIPT_PATH="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_PATH="${SCRIPT_PATH%perchance-tools*}perchance-tools"

pushd "${PROJECT_PATH}" >/dev/null
python -m doctest src/danoan/perchance_tools/**/*.py
popd >/dev/null
