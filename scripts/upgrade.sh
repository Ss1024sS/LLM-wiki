#!/usr/bin/env bash
set -euo pipefail

if [ $# -lt 1 ]; then
  echo "Usage: bash scripts/upgrade.sh /path/to/bootstrapped-project"
  exit 1
fi

python3 scripts/upgrade_knowledge_system.py "$1"
