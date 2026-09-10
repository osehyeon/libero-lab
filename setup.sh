#!/usr/bin/env bash
# LIBERO 환경 구축 — macOS / Linux 공통
# 업스트림이 2025-03 이후 멈춰 있어 수동 개입이 필요한 부분을 자동화한다.
set -euo pipefail
cd "$(dirname "$0")"
ROOT="$PWD"

echo "[1/5] LIBERO 서브모듈"
# 저장소를 --recursive 로 받지 않았다면 여기서 채운다. 커밋이 고정되어 있다.
git submodule update --init --depth 1 LIBERO

echo "[2/5] Python 3.10 가상환경"
command -v uv >/dev/null || curl -LsSf https://astral.sh/uv/install.sh | sh
uv venv --python 3.10 .venv

echo "[3/5] 의존성 설치"
# LIBERO 의 setup.py 는 install_requires=[] 라 아무것도 끌어오지 않는다. 직접 지정한다.
uv pip install --python .venv/bin/python \
    "numpy<2" "robosuite==1.4.1" "mujoco==2.3.7" "bddl==1.0.1" \
    easydict "hydra-core==1.2.0" opencv-python "gym==0.25.2" \
    matplotlib cloudpickle future einops thop termcolor "imageio[ffmpeg]" \
    huggingface_hub h5py tqdm psutil pillow
# egl_probe 는 Linux 전용이라 macOS 에서 빌드에 실패한다
uv pip install --python .venv/bin/python --no-deps "robomimic==0.3.0"

echo "[4/5] 패치 적용"
# libero 는 네임스페이스 패키지라 find_packages() 가 못 잡는다 → 경로를 직접 추가
echo "$ROOT/LIBERO" > .venv/lib/python3.10/site-packages/libero_repo.pth
git -C LIBERO apply --check "$ROOT/patches/libero-fixes.patch" 2>/dev/null \
  && git -C LIBERO apply "$ROOT/patches/libero-fixes.patch" \
  && echo "  patches/libero-fixes.patch 적용" \
  || echo "  이미 적용되었거나 충돌 — 건너뜀"

if [[ "$(uname)" == "Darwin" ]]; then
  # mujoco 2.3.7 이 옛 macOS OpenGL 경로를 하드코딩하고 있다 (3.0.0 에서 수정된 버그)
  CGL=.venv/lib/python3.10/site-packages/mujoco/cgl/cgl.py
  sed -i '' "s#'/System/Library/OpenGL.framework/OpenGL'#'/System/Library/Frameworks/OpenGL.framework/OpenGL'#" "$CGL" || true
  echo "  macOS: mujoco CGL 경로 패치"
fi

echo "[5/5] LIBERO 설정 파일"
mkdir -p ~/.libero
cat > ~/.libero/config.yaml <<CFG
assets: $ROOT/LIBERO/libero/libero/assets
bddl_files: $ROOT/LIBERO/libero/libero/bddl_files
benchmark_root: $ROOT/LIBERO/libero/libero
datasets: $ROOT/datasets
init_states: $ROOT/LIBERO/libero/libero/init_files
CFG

echo
echo "완료. 확인:"
echo "  .venv/bin/python run_demo.py --list"
