#!/usr/bin/env python
"""Browse and render LIBERO-Plus, the CVPR 2026 robustness benchmark.

  export LIBERO_CONFIG_PATH=~/.libero-plus
  export MAGICK_HOME=$(brew --prefix)        # macOS only

  python plus_demo.py --list                            # counts per category
  python plus_demo.py --list --suite libero_goal
  python plus_demo.py --render --category "Camera Viewpoints" --level 5
  python plus_demo.py --render --category all --out grid.png

10,030 tasks: the 4 original suites, each perturbed along 7 dimensions at 5
difficulty levels. Run it from the .venv-plus interpreter, not .venv -- both
provide a package called `libero`.
"""
import argparse
import collections
import json
import os

import libero_env
libero_env.require("plus")          # re-execs under .venv-plus if needed

import numpy as np
import imageio.v2 as iio

from libero.libero import get_libero_path

SUITES = ["libero_spatial", "libero_object", "libero_goal", "libero_10"]
CATEGORIES = ["Objects Layout", "Camera Viewpoints", "Robot Initial States",
              "Language Instructions", "Light Conditions", "Background Textures",
              "Sensor Noise"]


def classification():
    path = os.path.join(get_libero_path("benchmark_root"),
                        "benchmark/task_classification.json")
    return json.load(open(path))


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--suite", default="libero_spatial", choices=SUITES + ["all"])
    p.add_argument("--list", action="store_true")
    p.add_argument("--render", action="store_true")
    p.add_argument("--category", default="all")
    p.add_argument("--level", type=int, default=0, help="1-5, 0 for any")
    p.add_argument("--out", default="runs/plus.png")
    args = p.parse_args()

    global benchmark, OffScreenRenderEnv
    from libero.libero import benchmark
    from libero.libero.envs import OffScreenRenderEnv

    cls = classification()
    suites = SUITES if args.suite == "all" else [args.suite]

    if args.list or not args.render:
        total = 0
        for s in suites:
            items = cls[s]
            total += len(items)
            cat = collections.Counter(i["category"] for i in items)
            lvl = collections.Counter(str(i["difficulty_level"]) for i in items)
            print(f"\n{s}: {len(items)} tasks")
            for c in CATEGORIES:
                print(f"    {c:24s} {cat.get(c, 0):5d}")
            print(f"    {'levels':24s} " +
                  "  ".join(f"L{k}={v}" for k, v in sorted(lvl.items())))
        print(f"\ntotal {total}")
        if not args.render:
            return

    # pick one task per requested category, then render its first initial state
    cats = CATEGORIES if args.category == "all" else [args.category]
    tiles, labels = [], []
    for s in suites:
        bench = benchmark.get_benchmark_dict()[s]()
        byname = {c["name"]: c for c in cls[s]}
        for want in cats:
            hit = None
            for i in range(bench.n_tasks):
                c = byname.get(bench.get_task(i).name)
                if not c or c["category"] != want:
                    continue
                if args.level and c["difficulty_level"] != args.level:
                    continue
                hit = i
                break
            if hit is None:
                print(f"  no task for {want} level {args.level}")
                continue
            t = bench.get_task(hit)
            bddl = f"{get_libero_path('bddl_files')}/{t.problem_folder}/{t.bddl_file}"
            env = OffScreenRenderEnv(bddl_file_name=bddl,
                                     camera_heights=256, camera_widths=256)
            env.reset()
            obs = env.set_init_state(bench.get_task_init_states(hit)[0])
            tiles.append(obs["agentview_image"][::-1])
            labels.append(f"{s} #{hit} {want}")
            env.close()
            print(f"  {want:24s} #{hit}")

    if not tiles:
        raise SystemExit("nothing rendered")
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    iio.imwrite(args.out, np.hstack(tiles))
    print("\n".join(f"  {i+1}. {l}" for i, l in enumerate(labels)))
    print("->", args.out)


if __name__ == "__main__":
    main()
