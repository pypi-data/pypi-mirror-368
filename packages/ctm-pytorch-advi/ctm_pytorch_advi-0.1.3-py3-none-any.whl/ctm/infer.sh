#!/bin/bash
set -euo pipefail

# Resolve repo root regardless of where this script is invoked from
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

# Saved checkpoint loading parameters
E=${E:-50}      # number of epochs
B=${B:-128}     # batch size
K=${K:-80}      # number of topics
V=${V:-10000}   # vocabulary size

# Inference parameters
N=${N:-10}                       # number of top words to show
coherence_metric=${coherence_metric:-npmi} # one of: npmi, umass
MC=${MC:-32}                     # Monte Carlo samples for perplexity

# Allow overriding checkpoint via env var CKPT; otherwise build from params
CKPT_PATH=${CKPT:-"${REPO_ROOT}/runs/ctm/ctm_k${K}_v${V}_e${E}_b${B}/ctm.pt"}

export PYTHONPATH="${REPO_ROOT}/src:${PYTHONPATH:-}"
cd "${REPO_ROOT}"
uv run -m ctm.infer \
  --checkpoint "${CKPT_PATH}" \
  --topn "${N}" \
  --mc-samples "${MC}" \
  --coherence-metric "${coherence_metric}"