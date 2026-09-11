#!/usr/bin/env bash
# LIBERO environment setup for macOS and Linux.
# Upstream has been frozen since 2025-03; this automates the manual steps it needs.
set -euo pipefail
cd "$(dirname "$0")"
ROOT="$PWD"

echo "[1/5] LIBERO submodule"
# Fills the submodule if the repo was not cloned with --recursive. Commit is pinned.
git submodule update --init --depth 1 LIBERO

echo "[2/5] Python 3.10 virtualenv"
if ! command -v uv >/dev/null; then
  curl -LsSf https://astral.sh/uv/install.sh | sh
  # the installer drops uv here but only edits interactive shell profiles
  export PATH="$HOME/.local/bin:$PATH"
fi
uv venv --python 3.10 .venv

echo "[3/5] Dependencies"
# Versions come from constraints.txt, frozen from a working install.
# LIBERO declares install_requires=[], so nothing is pulled in. List it all here.
uv pip install --python .venv/bin/python -c "$ROOT/constraints.txt" \
    "numpy<2" "robosuite==1.4.1" "mujoco==2.3.7" "bddl==1.0.1" \
    easydict "hydra-core==1.2.0" opencv-python "gym==0.25.2" \
    matplotlib cloudpickle future einops thop termcolor "imageio[ffmpeg]" \
    huggingface_hub h5py tqdm psutil pillow
# egl_probe is Linux-only and fails to build on macOS
uv pip install --python .venv/bin/python -c "$ROOT/constraints.txt" --no-deps "robomimic==0.3.0"

echo "[4/5] Patches"
# libero is a namespace package that find_packages() misses; inject the path
echo "$ROOT/LIBERO" > .venv/lib/python3.10/site-packages/libero_repo.pth
git -C LIBERO apply --check "$ROOT/patches/libero-fixes.patch" 2>/dev/null \
  && git -C LIBERO apply "$ROOT/patches/libero-fixes.patch" \
  && echo "  applied patches/libero-fixes.patch" \
  || echo "  already applied or conflicting - skipped"

if [[ "$(uname)" == "Darwin" ]]; then
  # mujoco 2.3.7 hardcodes an old macOS OpenGL path (fixed in 3.0.0)
  CGL=.venv/lib/python3.10/site-packages/mujoco/cgl/cgl.py
  sed -i '' "s#'/System/Library/OpenGL.framework/OpenGL'#'/System/Library/Frameworks/OpenGL.framework/OpenGL'#" "$CGL" || true
  echo "  macOS: patched mujoco CGL path"
fi

echo "[5/5] LIBERO config"
mkdir -p ~/.libero
cat > ~/.libero/config.yaml <<CFG
assets: $ROOT/LIBERO/libero/libero/assets
bddl_files: $ROOT/LIBERO/libero/libero/bddl_files
benchmark_root: $ROOT/LIBERO/libero/libero
datasets: $ROOT/datasets
init_states: $ROOT/LIBERO/libero/libero/init_files
CFG

echo
echo "Done. Verify with:"
echo "  .venv/bin/python run_demo.py --list"
