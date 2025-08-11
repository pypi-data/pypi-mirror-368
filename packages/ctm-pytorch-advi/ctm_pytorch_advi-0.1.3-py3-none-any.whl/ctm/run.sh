#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
export PYTHONPATH="${REPO_ROOT}/src:${PYTHONPATH:-}"
cd "${REPO_ROOT}"

uv run -m ctm.train \
  --num-topics 80 \
  --vocab-size 10000 \
  --batch-size 128 \
  --epochs 50 \
  --use-lemmatization \
  --spacy-model "en_core_web_sm" \
  --use-tensorboard \
  --plot-metrics \
  --log-every 999999