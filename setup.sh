#!/usr/bin/env bash
set -euo pipefail

# 1) Create/activate venv
if [ ! -d "venv" ]; then python -m venv venv; fi
# shellcheck disable=SC1091
source venv/bin/activate

python -m pip install --upgrade pip setuptools wheel

# 2) Install base requirements, but never build from source for CuPy-like deps
#    (If requirements.txt still had 'cupy' somehow, this prevents a compile.)
#    We'll install GPU packages explicitly next.
# Make a filtered copy without any 'cupy' lines (case-insensitive, leading spaces ok)
TMP_REQ="$(mktemp)"
grep -viE '^[[:space:]]*cupy([[:space:]=<>!].*)?$' requirements.txt > "$TMP_REQ"

pip install --only-binary=:all: -r "$TMP_REQ"
rm -f "$TMP_REQ"

# 3) Ensure no stray source 'cupy' installed
pip uninstall -y cupy || true

# 4) Auto-detect CUDA via nvidia-smi and install the correct prebuilt CuPy wheel
if command -v nvidia-smi >/dev/null 2>&1; then
  CUDA_MAJOR="$(nvidia-smi | awk '/CUDA Version/ {split($NF,a,"."); print a[1]; exit}')"
  if [ -n "${CUDA_MAJOR:-}" ]; then
    if [ "$CUDA_MAJOR" -ge 12 ]; then
      pip install --only-binary=:all: cupy-cuda12x
    elif [ "$CUDA_MAJOR" -ge 11 ]; then
      pip install --only-binary=:all: cupy-cuda11x
    fi
  fi
fi

echo "✅ Environment ready."

