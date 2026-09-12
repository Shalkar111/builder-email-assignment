#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p out/classes
javac --release 17 -encoding UTF-8 -Xlint:all -Werror \
  -d out/classes src/main/java/assignment/builder/*.java
echo "Compiled successfully (Java 17 compatible)."
