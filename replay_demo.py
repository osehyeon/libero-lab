#!/usr/bin/env python
"""LIBERO 데모 재생기.

  python replay_demo.py --suite libero_spatial --task 0 --demo 0 --mode states
  python replay_demo.py --suite libero_spatial --task 0 --demo 0 --mode actions

  states  : 저장된 물리 상태를 매 스텝 주입 -> 100% 정확 재현
  actions : 저장된 행동을 컨트롤러로 재실행 -> 오차 누적 가능
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
print("태스크:", task.language)
print("파일  :", os.path.basename(h5))

f = h5py.File(h5, "r")
g = f["data/demo_%d" % a.demo]
states, actions = g["states"][:], g["actions"][:]
print("데모 %d: %d 스텝" % (a.demo, len(actions)))

env = OffScreenRenderEnv(bddl_file_name=bddl, camera_heights=256, camera_widths=256)
env.reset()
env.set_init_state(states[0])

frames, success = [], False
if a.mode == "states":
    for s in states:
        obs = env.set_init_state(s)          # 물리 상태 주입
        frames.append(obs["agentview_image"][::-1])
        if env.env._check_success():
            success = True
else:
    for act in actions:
        obs, r, done, info = env.step(act)   # 컨트롤러로 재실행
        frames.append(obs["agentview_image"][::-1])
        if env.env._check_success():
            success = True

out = a.out or "runs/%s_t%d_d%d_%s.mp4" % (a.suite, a.task, a.demo, a.mode)
os.makedirs(os.path.dirname(out), exist_ok=True)
iio.mimsave(out, frames, fps=20)
print("모드 %-8s 성공: %s   -> %s" % (a.mode, "O" if success else "X", out))
env.close()
