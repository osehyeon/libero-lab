# libero-lab

Reproducible setup for the [LIBERO](https://github.com/Lifelong-Robot-Learning/LIBERO)
benchmark, plus scripts to explore it.

Upstream has not changed since `8f1084e` (2025-03) and no longer installs cleanly.
`setup.sh` works around that. Verified on macOS (Apple Silicon) and CUDA Linux.

## Quickstart

```bash
git clone --recursive git@github.com:osehyeon/libero-lab.git
cd libero-lab && ./setup.sh
python run_demo.py --list
python run_demo.py --suite libero_spatial --task 0 --gui
```

## Contents

| Path | |
|---|---|
| `setup.sh` | Environment setup, including 8 upstream workarounds |
| `patches/` | Source fixes for LIBERO — a submodule cannot carry local edits |
| `run_demo.py` | List tasks, run with GUI, save video |
| `teleop.py` | Drive a task by hand, nothing recorded |
| `replay_demo.py` | Watch a recorded human demo -- the ground truth |
| `download_datasets.py` | Fetch the 94 GB demo datasets |
| `libero_env.py` | Sends each script to the right venv and config |
| `setup-plus.sh` | Second environment for LIBERO-Plus (CVPR 2026 robustness benchmark) |
| `plus_demo.py` | Browse and render LIBERO-Plus perturbations |
| `docs/` | HTML write-ups on task structure, MuJoCo I/O, rotations, VLA practice |
| `CLAUDE.md` | Working notes — bug list, measured facts, next steps |

## Drive it yourself

Control a task by hand. Nothing is recorded.

```bash
python teleop.py                                   # push the plate to the front of the stove
python teleop.py --suite libero_goal --task 7      # turn on the stove
python teleop.py --suite libero_spatial --task 0   # pick and place
```

The default is the easiest task in the benchmark: slide the plate with `w a s d`,
no grasping, no rotation. Pick-and-place tasks are far harder by keyboard -- `space` toggles the gripper
and the fingers need about 100 steps to close, so press it once and wait a few seconds.

| Key | |
|---|---|
| `w` `a` `s` `d` | move in the xy plane |
| `r` `f` | move up and down |
| `z` `x` / `t` `g` / `c` `v` | rotate about x / y / z |
| `space` | toggle gripper |
| `q` | reset the task |

Add `--device spacemouse` for a 3D mouse (`pip install hidapi` first).

On macOS, add your terminal under **System Settings → Privacy & Security →
Accessibility**, then restart it. Without this the window opens but keys do nothing.

## LIBERO-Plus

[LIBERO-Plus](https://github.com/sylvestf/LIBERO-plus) (CVPR 2026) takes the 4
original suites and perturbs them along 7 dimensions at 5 difficulty levels:
10,030 tasks. Released VLA checkpoints score over 90% on plain LIBERO and drop
below 30% when the camera or the robot's starting pose moves.

It is a fork of LIBERO and ships a package with the same name, `libero`, so it
gets its own virtualenv and its own config.

```bash
./setup-plus.sh                       # .venv-plus + 6.4 GB of assets

python plus_demo.py --list --suite all
python plus_demo.py --render --category all
python plus_demo.py --render --category "Camera Viewpoints" --level 5
```

Any python will do. Each script calls `libero_env.require()` and re-execs
itself under the interpreter and config it needs, so there is nothing to
activate and no environment variable to remember.

The 7 dimensions: objects layout, camera viewpoints, robot initial states,
language instructions, light conditions, background textures, sensor noise.

`env_wrapper.py` imports `wand` at module level, so ImageMagick must be present
or nothing runs -- `brew install imagemagick` on macOS (plus `MAGICK_HOME`),
`apt install libmagickwand-dev` on Linux.

## Watch the ground truth

Every task ships with 50 recorded human demos. Replay one in a window:

```bash
python replay_demo.py --gui                    # exact reproduction
python replay_demo.py --gui --mode actions     # re-run through the controller
python replay_demo.py --gui --loop --fps 40    # faster, on repeat
```

| Mode | |
|---|---|
| `states` | Inject the stored physics state each step. Always exact |
| `actions` | Feed the stored actions back through OSC. Error accumulates, so it can fail |

Without `--gui` it writes an mp4 to `runs/` instead.

Needs the dataset for that suite. Only `states` and `actions` are read -- 4 MB per
task; the 485 MB on disk is almost entirely recorded camera images.

## Collect your own demos

Drive the simulator by hand and record it. This is how the original 6,500 demos
were made — one episode per demonstration.

```bash
cd LIBERO
../.venv/bin/python scripts/collect_demonstration.py \
    --device keyboard --robots Panda \
    --bddl-file libero/libero/bddl_files/libero_spatial/pick_up_the_black_bowl_between_the_plate_and_the_ramekin_and_place_it_on_the_plate.bddl
```

Same keys, but `q` ends the episode and starts the next one.
`--robots Panda` is required — omitting it hits an upstream argparse bug.

Episodes land in `demonstration_data/` as states and actions, without images.
`scripts/create_dataset.py` replays them to render the observations and write the
final hdf5.

## Datasets

**Not needed for evaluation.** Initial states (`.pruned_init`) ship with the
LIBERO repo and total 13 MB. The 94 GB of demos is only for training and replay.

```bash
python download_datasets.py                       # all 5 suites, 94 GB
python download_datasets.py --suite libero_spatial
```

Do not use LIBERO's own `--datasets all`: it looks for a `libero_100` directory
that is not on HuggingFace, fails silently, and leaves out `libero_90`.

## License

MIT — see [LICENSE](LICENSE). Dependencies are permissive too: LIBERO, robosuite,
bddl and robomimic are MIT; MuJoCo is Apache 2.0.

`patches/libero-fixes.patch` derives from LIBERO source; see
[patches/NOTICE.md](patches/NOTICE.md). Images in `ref/` follow
[ref/SOURCES.md](ref/SOURCES.md).
