#! /usr/bin/env bash

SCRIPT_PATH="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_PATH="$(cd "${SCRIPT_PATH}" && cd ../.. && pwd)"
PROJECT_NAME="$(basename "${PROJECT_PATH}")"

INPUT_FOLDER="${SCRIPT_PATH}/input"
OUTPUT_FOLDER="${SCRIPT_PATH}/output"
mkdir -p "${OUTPUT_FOLDER}"

pushd "${PROJECT_PATH}" >/dev/null

shopt -s globstar

rm -rf ${PROJECT_PATH}/dev/**/output
rm -rf ${PROJECT_PATH}/build

rm -rf ${PROJECT_PATH}/**/__pycache__
rm -rf "${PROJECT_PATH}/.tox"
rm -rf ${PROJECT_PATH}/**/*.egg-info

rm -rf ${PROJECT_PATH}/**/*.c

popd >/dev/null
