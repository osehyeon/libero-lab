#!/usr/bin/env python
"""Replay a recorded human demo -- the ground truth for a task.

  python replay_demo.py --gui                        # watch it in a window
  python replay_demo.py --mode actions --gui
  python replay_demo.py                              # no window, writes an mp4

  states  : inject the stored physics state each step -> exact reproduction
  actions : re-run the stored actions through the controller -> error accumulates

Needs the demo dataset. Only `states` and `actions` are read, which is 4 MB per
task; the 485 MB on disk is almost all recorded camera images.
"""
import libero_env
libero_env.require("base")      # re-execs under .venv if needed

import argparse, os, time
import h5py
from libero.libero import benchmark, get_libero_path
from libero.libero.envs import OffScreenRenderEnv
from libero.libero.envs.env_wrapper import ControlEnv  # not re-exported by envs/__init__

p = argparse.ArgumentParser()
p.add_argument("--suite", default="libero_spatial")
p.add_argument("--task", type=int, default=0)
p.add_argument("--demo", type=int, default=0)
p.add_argument("--mode", choices=["states", "actions"], default="states")
p.add_argument("--gui", action="store_true", help="show a window instead of writing an mp4")
p.add_argument("--loop", action="store_true", help="with --gui, replay forever")
p.add_argument("--fps", type=float, default=20, help="with --gui, playback speed. 0 = as fast as possible")
p.add_argument("--out", default=None)
a = p.parse_args()

suite = benchmark.get_benchmark_dict()[a.suite]()
task = suite.get_task(a.task)
bddl = "%s/%s/%s" % (get_libero_path("bddl_files"), task.problem_folder, task.bddl_file)
h5 = os.path.join(get_libero_path("datasets"), a.suite,
                  task.bddl_file.replace(".bddl", "_demo.hdf5"))
if not os.path.exists(h5):
    raise SystemExit("missing %s\nrun: python download_datasets.py --suite %s" % (h5, a.suite))

print("task:", task.language)
print("file:", os.path.basename(h5))

with h5py.File(h5, "r") as f:
    g = f["data/demo_%d" % a.demo]
    states, actions = g["states"][:], g["actions"][:]
print("demo %d: %d steps" % (a.demo, len(actions)))

if a.gui:
    # on-screen: no camera observations to render, so replay runs at full speed
    env = ControlEnv(bddl_file_name=bddl, has_renderer=True,
                     has_offscreen_renderer=False, use_camera_obs=False,
                     render_camera="frontview", ignore_done=True)
else:
    env = OffScreenRenderEnv(bddl_file_name=bddl, camera_heights=256, camera_widths=256)

frames = []


def show(obs):
    if a.gui:
        env.env.render()
        if a.fps:                       # demos were recorded at 20 Hz
            time.sleep(1.0 / a.fps)
    else:
        frames.append(obs["agentview_image"][::-1])


while True:
    env.reset()
    obs = env.set_init_state(states[0])
    show(obs)
    success = False

    if a.mode == "states":
        for s in states:
            show(env.set_init_state(s))     # inject physics state
            success = success or env.env._check_success()
    else:
        for act in actions:
            obs, r, done, info = env.step(act)   # re-run through the controller
            show(obs)
            success = success or env.env._check_success()

    print("mode %-8s success: %s" % (a.mode, "yes" if success else "no"))
    if not (a.gui and a.loop):
        break

if not a.gui:
    import imageio.v2 as iio
    out = a.out or "runs/%s_t%d_d%d_%s.mp4" % (a.suite, a.task, a.demo, a.mode)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    iio.mimsave(out, frames, fps=20)
    print("->", out)

env.close()
