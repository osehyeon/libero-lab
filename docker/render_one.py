"""Render one LIBERO-Plus task's first frame inside the Linux container.

macOS draws the Light axis wrong (see CLAUDE.md), so gallery images of it are
made here instead. Mount the repo at its own absolute path so the paths in
~/.libero-plus/config.yaml resolve inside the container.

  docker build -t libero-plus-render docker/
  docker run --rm -v "$PWD:$PWD" -v ~/.libero-plus:/root/.libero-plus:ro \
      -e LIBERO_CONFIG_PATH=/root/.libero-plus libero-plus-render \
      python "$PWD/docker/render_one.py" libero_goal 2552 320 "$PWD/runs/out.jpg"

usage: render_one.py SUITE INDEX PX OUT.jpg
"""
import os, sys
os.environ.setdefault("MUJOCO_GL", "osmesa"); os.environ.setdefault("PYOPENGL_PLATFORM", "osmesa")
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "LIBERO-plus"))
import numpy as np, imageio.v2 as iio
from libero.libero import benchmark, get_libero_path
from libero.libero.envs import OffScreenRenderEnv
s, idx, px, out = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
b = benchmark.get_benchmark_dict()[s](); t = b.get_task(idx)
env = OffScreenRenderEnv(bddl_file_name=f"{get_libero_path('bddl_files')}/{t.problem_folder}/{t.bddl_file}",
                         camera_heights=px, camera_widths=px)
env.reset(); env.set_init_state(b.get_task_init_states(idx)[0])
img = np.asarray(env.step(np.array([0, 0, 0, 0, 0, 0, -1.0]))[0]["agentview_image"])[::-1]
iio.imwrite(out, img, quality=88); print(f"{s} #{idx} -> {out}  mean {img.astype(float).mean():.2f}")
