#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
bash build.sh
java -cp out/classes assignment.builder.Main
