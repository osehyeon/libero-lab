#!/usr/bin/env python
"""Drive a LIBERO task by hand. Nothing is recorded.

  python teleop.py                                  # libero_spatial task 0
  python teleop.py --suite libero_goal --task 3
  python teleop.py --device spacemouse

Keys (keyboard device):
  w a s d   move in the xy plane        z x / t g / c v   rotate about x / y / z
  r f       move up and down            space             toggle gripper
  q         reset the task              ctrl-c            quit

On macOS the terminal needs Accessibility permission, otherwise the window
opens but keys do nothing. System Settings > Privacy & Security > Accessibility.
"""
import argparse

import numpy as np
import robosuite
from robosuite.utils.input_utils import input2action
from robosuite.wrappers import VisualizationWrapper

from libero.libero import benchmark, get_libero_path
from libero.libero.envs import TASK_MAPPING
from libero.libero.envs import bddl_utils as BDDLUtils


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--suite", default="libero_spatial",
                   choices=["libero_spatial", "libero_object", "libero_goal",
                            "libero_90", "libero_10"])
    p.add_argument("--task", type=int, default=0)
    p.add_argument("--init", type=int, default=0, help="which of the 50 initial states")
    p.add_argument("--device", default="keyboard", choices=["keyboard", "spacemouse"])
    p.add_argument("--camera", default="frontview")
    p.add_argument("--pos-sensitivity", type=float, default=1.5)
    p.add_argument("--rot-sensitivity", type=float, default=1.5)
    args = p.parse_args()

    suite = benchmark.get_benchmark_dict()[args.suite]()
    task = suite.get_task(args.task)
    bddl = f"{get_libero_path('bddl_files')}/{task.problem_folder}/{task.bddl_file}"
    print(f"[{args.suite} #{args.task}] {task.language}")

    problem = BDDLUtils.get_problem_info(bddl)["problem_name"]
    env = TASK_MAPPING[problem](
        bddl_file_name=bddl,
        robots=["Panda"],
        controller_configs=robosuite.load_controller_config(default_controller="OSC_POSE"),
        has_renderer=True,
        has_offscreen_renderer=False,
        use_camera_obs=False,
        render_camera=args.camera,
        ignore_done=True,
        control_freq=20,
    )
    raw = env                       # keep the unwrapped env for sim / success checks
    env = VisualizationWrapper(env)  # draws gripper site markers

    if args.device == "keyboard":
        from robosuite.devices import Keyboard
        device = Keyboard(pos_sensitivity=args.pos_sensitivity,
                          rot_sensitivity=args.rot_sensitivity)
    else:
        from robosuite.devices import SpaceMouse
        device = SpaceMouse(pos_sensitivity=args.pos_sensitivity,
                            rot_sensitivity=args.rot_sensitivity)

    inits = suite.get_task_init_states(args.task)
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
