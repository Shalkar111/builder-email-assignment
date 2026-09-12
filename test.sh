#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
bash build.sh
mkdir -p out/test-classes
javac --release 17 -encoding UTF-8 -Xlint:all -Werror \
  -cp out/classes -d out/test-classes src/test/java/assignment/builder/*.java
java -cp out/classes:out/test-classes assignment.builder.BuilderChecks
