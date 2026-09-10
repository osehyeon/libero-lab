#!/usr/bin/env python
"""LIBERO demo replayer.

  python replay_demo.py --suite libero_spatial --task 0 --demo 0 --mode states
  python replay_demo.py --suite libero_spatial --task 0 --demo 0 --mode actions

  states  : inject the stored physics state each step -> exact reproduction
  actions : re-run the stored actions through the controller -> error accumulates
"""
import argparse, os, glob, h5py, numpy as np, imageio.v2 as iio
from libero.libero import benchmark, get_libero_path
from libero.libero.envs import OffScreenRenderEnv

p = argparse.ArgumentParser()
p.add_argument("--suite", default="libero_spatial")
p.add_argument("--task", type=int, default=0)
p.add_argument("--demo", type=int, default=0)
p.add_argument("--mode", choices=["states", "actions"], default="states")
p.add_argument("--out", default=None)
a = p.parse_args()

suite = benchmark.get_benchmark_dict()[a.suite]()
task = suite.get_task(a.task)
bddl = "%s/%s/%s" % (get_libero_path("bddl_files"), task.problem_folder, task.bddl_file)
h5 = os.path.join(get_libero_path("datasets"), a.suite,
                  task.bddl_file.replace(".bddl", "_demo.hdf5"))
print("task:", task.language)
print("file:", os.path.basename(h5))

f = h5py.File(h5, "r")
g = f["data/demo_%d" % a.demo]
states, actions = g["states"][:], g["actions"][:]
print("demo %d: %d steps" % (a.demo, len(actions)))

env = OffScreenRenderEnv(bddl_file_name=bddl, camera_heights=256, camera_widths=256)
env.reset()
env.set_init_state(states[0])

frames, success = [], False
if a.mode == "states":
    for s in states:
        obs = env.set_init_state(s)          # inject physics state
        frames.append(obs["agentview_image"][::-1])
        if env.env._check_success():
            success = True
else:
    for act in actions:
        obs, r, done, info = env.step(act)   # re-run through the controller
        frames.append(obs["agentview_image"][::-1])
        if env.env._check_success():
            success = True

out = a.out or "runs/%s_t%d_d%d_%s.mp4" % (a.suite, a.task, a.demo, a.mode)
os.makedirs(os.path.dirname(out), exist_ok=True)
iio.mimsave(out, frames, fps=20)
print("mode %-8s success: %s   -> %s" % (a.mode, "yes" if success else "no", out))
env.close()
