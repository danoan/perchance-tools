#! /usr/bin/env bash

SCRIPT_PATH="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

INPUT_FOLDER="${SCRIPT_PATH}/input"
OUTPUT_FOLDER="${SCRIPT_PATH}/output"
mkdir -p "${OUTPUT_FOLDER}"

pushd "${SCRIPT_FOLDER}" >/dev/null
perchance-tools markdown-to-yml "${INPUT_FOLDER}/chunk.md" >"${OUTPUT_FOLDER}/chunk.yml"
popd >/dev/null
