#!/usr/bin/env bash
set -euo pipefail

PROJECT_NAME="${PROMPTER_PROJECT:-default}"

pi -p --no-session \
     --tools read,bash,edit,write \
     "./persistence/${PROJECT_NAME}/front-end/instructions.md"
