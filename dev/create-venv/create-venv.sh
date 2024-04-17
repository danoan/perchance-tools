#! /usr/bin/env bash

SCRIPT_PATH="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_PATH="$(cd "${SCRIPT_PATH}" && cd ../.. && pwd)"
PROJECT_NAME="$(basename "${PROJECT_PATH}")"

INPUT_FOLDER="${SCRIPT_PATH}/input"
OUTPUT_FOLDER="${SCRIPT_PATH}/output"
mkdir -p "${OUTPUT_FOLDER}"

set -e

pushd "${PROJECT_PATH}" >/dev/null

trap "echo 'Aborted!'" err

./dev/clean/clean.sh
python -m venv .venv

source .venv/bin/activate

pip install --upgrade pip
pip install -e .
pip install build tox twine

popd >/dev/null
