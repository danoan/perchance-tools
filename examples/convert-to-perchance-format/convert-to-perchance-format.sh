#! /usr/bin/env bash

SCRIPT_PATH="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

INPUT_FOLDER="${SCRIPT_PATH}/input"
OUTPUT_FOLDER="${SCRIPT_PATH}/output"
mkdir -p "${OUTPUT_FOLDER}"

pushd "${SCRIPT_FOLDER}" >/dev/null
perchance-tools convert-to-perchance-format "${INPUT_FOLDER}/chunk.yml" >"${OUTPUT_FOLDER}/chunk.yml"
popd >/dev/null
