#!/usr/bin/env bash
# LIBERO-Plus environment setup (CVPR 2026 robustness benchmark).
#
# LIBERO-Plus is a fork of LIBERO and ships a package with the same name,
# `libero`, so it cannot share a virtualenv with the base benchmark. This
# builds a second one, .venv-plus, and a second config under ~/.libero-plus.
# Point LIBERO_CONFIG_PATH at it; both repos read that variable.
set -euo pipefail
cd "$(dirname "$0")"
ROOT="$PWD"

echo "[1/5] LIBERO-plus submodule"
git submodule update --init --depth 1 LIBERO-plus

echo "[2/5] Python 3.10 virtualenv (separate from .venv)"
if ! command -v uv >/dev/null; then
  curl -LsSf https://astral.sh/uv/install.sh | sh
  export PATH="$HOME/.local/bin:$PATH"
fi
uv venv --python 3.10 .venv-plus

echo "[3/5] Dependencies"
# Versions come from constraints.txt, frozen from a working install.
# Same stack as setup.sh. Upstream asks for robosuite 1.4.0 and numpy 1.22.4;
# 1.4.1 and numpy<2 work and are what the base env already proved out.
uv pip install --python .venv-plus/bin/python -c "$ROOT/constraints.txt" \
    "numpy<2" "robosuite==1.4.1" "mujoco==2.3.7" "bddl==1.0.1" \
    easydict "hydra-core==1.2.0" opencv-python "gym==0.25.2" \
    matplotlib cloudpickle future einops thop termcolor "imageio[ffmpeg]" \
    huggingface_hub h5py tqdm psutil pillow scikit-image "usd-core>=25.5" wand
uv pip install --python .venv-plus/bin/python -c "$ROOT/constraints.txt" --no-deps "robomimic==0.3.0"

# `wand` binds to ImageMagick at import time and env_wrapper.py imports it at
# module level, so evaluation does not start without it.
if [[ "$(uname)" == "Darwin" ]]; then
  command -v brew >/dev/null && brew list imagemagick >/dev/null 2>&1 || brew install imagemagick
else
  dpkg -s libmagickwand-dev >/dev/null 2>&1 \
    || echo "  WARNING: apt install libmagickwand-dev (needs root), else wand fails to load"
fi

echo "[4/5] Patches and paths"
echo "$ROOT/LIBERO-plus" > .venv-plus/lib/python3.10/site-packages/libero_repo.pth
git -C LIBERO-plus apply --check "$ROOT/patches/libero-plus-fixes.patch" 2>/dev/null \
  && git -C LIBERO-plus apply "$ROOT/patches/libero-plus-fixes.patch" \
  && echo "  applied patches/libero-plus-fixes.patch" \
  || echo "  already applied or conflicting - skipped"

if [[ "$(uname)" == "Darwin" ]]; then
  CGL=.venv-plus/lib/python3.10/site-packages/mujoco/cgl/cgl.py
  sed -i '' "s#'/System/Library/OpenGL.framework/OpenGL'#'/System/Library/Frameworks/OpenGL.framework/OpenGL'#" "$CGL" || true
  echo "  macOS: patched mujoco CGL path"
fi

mkdir -p ~/.libero-plus
cat > ~/.libero-plus/config.yaml <<CFG
assets: $ROOT/LIBERO-plus/libero/libero/assets
bddl_files: $ROOT/LIBERO-plus/libero/libero/bddl_files
benchmark_root: $ROOT/LIBERO-plus/libero/libero
datasets: $ROOT/datasets-plus
init_states: $ROOT/LIBERO-plus/libero/libero/init_files
CFG

echo "[5/5] Assets (6.4 GB download, 9.4 GB extracted; not in the repo)"
ASSETS="$ROOT/LIBERO-plus/libero/libero/assets"
if [[ -d "$ASSETS" ]]; then
  echo "  already extracted"
else
  .venv-plus/bin/python - <<'PY'
import os, zipfile
from huggingface_hub import hf_hub_download
z = hf_hub_download("Sylvest/LIBERO-plus", "assets.zip", repo_type="dataset")
dest = os.path.join(os.environ["PWD"], "LIBERO-plus/libero/libero")
# the zip carries the uploader's absolute path, .../LIBERO-plus-0/assets/...,
# so strip everything above "assets/" instead of extracting it verbatim
print("  extracting", z)
with zipfile.ZipFile(z) as f:
    for m in f.infolist():
        i = m.filename.find("/assets/")
        if i < 0:
            continue
        rel = m.filename[i + 1:]
        out = os.path.join(dest, rel)
        if m.is_dir():
            os.makedirs(out, exist_ok=True)
        else:
            os.makedirs(os.path.dirname(out), exist_ok=True)
            with f.open(m) as src, open(out, "wb") as dst:
                dst.write(src.read())
PY
fi

echo
echo "Done. Every command needs these two:"
echo "  export LIBERO_CONFIG_PATH=~/.libero-plus"
[[ "$(uname)" == "Darwin" ]] && echo "  export MAGICK_HOME=$(brew --prefix)   # wand finds ImageMagick through this"
echo "  .venv-plus/bin/python plus_demo.py --list"
