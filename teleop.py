#!/usr/bin/env python
"""Drive a LIBERO task by hand. Nothing is recorded.

  python teleop.py                                  # push the plate -- easiest task
  python teleop.py --suite libero_goal --task 7     # turn on the stove
  python teleop.py --suite libero_spatial --task 0  # pick and place, much harder
  python teleop.py --device spacemouse

Add --plus to drive a LIBERO-Plus task instead, and pick one by perturbation:

  python teleop.py --plus --category "Camera Viewpoints" --level 5
  python teleop.py --plus --category "Light Conditions" --nth 3
  python teleop.py --plus --suite libero_10 --category "Objects Layout"

Driving a perturbation by hand is the quickest way to see whether it is even
solvable, which a success rate alone does not tell you.

Keys (keyboard device):
  w a s d   move in the xy plane        z x / t g / c v   rotate about x / y / z
  r f       move up and down            space             toggle gripper
  q         reset the task              ctrl-c            quit

On macOS the terminal needs Accessibility permission, otherwise the window
opens but keys do nothing. System Settings > Privacy & Security > Accessibility.
"""
import sys

import libero_env

# --plus swaps the whole environment, so it has to be read before anything
# imports `libero`. argparse runs far too late for that.
PLUS = "--plus" in sys.argv
libero_env.require("plus" if PLUS else "base")

import argparse
import json
import os

import numpy as np
from robosuite.utils.input_utils import input2action
from robosuite.wrappers import VisualizationWrapper

from libero.libero import benchmark, get_libero_path
from libero.libero.envs.env_wrapper import ControlEnv


CATEGORIES = ["Objects Layout", "Camera Viewpoints", "Robot Initial States",
              "Language Instructions", "Light Conditions", "Background Textures",
              "Sensor Noise"]


def find_plus_task(suite, category, level, nth):
    """LIBERO-Plus has thousands of tasks per suite, so name one by what was
    perturbed instead of by index."""
    path = os.path.join(get_libero_path("benchmark_root"),
                        "benchmark/task_classification.json")
    byname = {c["name"]: c for c in json.load(open(path))[suite]}
    hits = []
    for i in range(suite_obj.n_tasks):
        c = byname.get(suite_obj.get_task(i).name)
        if not c or c["category"] != category:
            continue
        if level and c["difficulty_level"] != level:
            continue
        hits.append(i)
    if not hits:
        raise SystemExit(f"no {suite} task with category {category!r} "
                         f"level {level or 'any'}")
    print(f"{len(hits)} matching tasks, taking #{nth}")
    return hits[nth % len(hits)]


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--plus", action="store_true",
                   help="drive LIBERO-Plus instead of the base benchmark")
    p.add_argument("--suite", default=None,
                   choices=["libero_spatial", "libero_object", "libero_goal",
                            "libero_90", "libero_10"])
    p.add_argument("--category", default="Camera Viewpoints", choices=CATEGORIES,
                   help="--plus only: which perturbation to drive")
    p.add_argument("--level", type=int, default=0,
                   help="--plus only: difficulty 1-5, 0 for any")
    p.add_argument("--nth", type=int, default=0,
                   help="--plus only: which of the matching tasks")
    p.add_argument("--task", type=int, default=None)
    p.add_argument("--init", type=int, default=0, help="which of the 50 initial states")
    p.add_argument("--device", default="keyboard", choices=["keyboard", "spacemouse"])
    p.add_argument("--camera", default="frontview")
    p.add_argument("--pos-sensitivity", type=float, default=1.5)
    p.add_argument("--rot-sensitivity", type=float, default=1.5)
    args = p.parse_args()

    # the base benchmark opens on the easiest task; LIBERO-Plus has no such
    # thing, so it opens on a perturbation of the same spatial task instead
    if args.suite is None:
        args.suite = "libero_spatial" if args.plus else "libero_goal"

    global suite_obj
    suite_obj = suite = benchmark.get_benchmark_dict()[args.suite]()
    if args.plus:
        index = find_plus_task(args.suite, args.category, args.level, args.nth)
    else:
        index = 5 if args.task is None else args.task
    task = suite.get_task(index)
    bddl = f"{get_libero_path('bddl_files')}/{task.problem_folder}/{task.bddl_file}"
    print(f"[{args.suite} #{index}] {task.language}")

    # Go through ControlEnv rather than TASK_MAPPING. LIBERO-Plus encodes the
    # camera parameters and the robot variant in the *file name* and parses them
    # there -- `..._view_13_15_100_0_0_initstate_231` means a shifted camera and
    # a "Panda231" starting pose, and no such .bddl file exists on disk. Calling
    # TASK_MAPPING directly skips that and dies on a missing file.
    control = ControlEnv(
        bddl_file_name=bddl,
        robots=["Panda"],
        controller="OSC_POSE",
        has_renderer=True,
        has_offscreen_renderer=False,
        use_camera_obs=False,
        render_camera=args.camera,
        ignore_done=True,
        control_freq=20,
    )
    raw = control.env               # the robosuite env: sim, robots, success
    env = VisualizationWrapper(raw)  # draws gripper site markers

    if args.device == "keyboard":
        from robosuite.devices import Keyboard
        device = Keyboard(pos_sensitivity=args.pos_sensitivity,
                          rot_sensitivity=args.rot_sensitivity)
    else:
        from robosuite.devices import SpaceMouse
        device = SpaceMouse(pos_sensitivity=args.pos_sensitivity,
                            rot_sensitivity=args.rot_sensitivity)

    inits = suite.get_task_init_states(index)
    print(f"initial states available: {len(inits)}  (using #{args.init})")
    print("ctrl-c to quit\n")

    while True:
        env.reset()
        raw.sim.set_state_from_flattened(inits[args.init])
        raw.sim.forward()
        env.render()
        device.start_control()

        solved = False
        while True:
            action, _ = input2action(device=device, robot=raw.robots[0])
            if action is None:      # q pressed
                break
            env.step(action)
            env.render()
            if not solved and raw._check_success():
                print("solved")
                solved = True


if __name__ == "__main__":
    main()
