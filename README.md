# libero-lab

Reproducible setup for the [LIBERO](https://github.com/Lifelong-Robot-Learning/LIBERO)
benchmark and for [LIBERO-Plus](https://github.com/sylvestf/LIBERO-plus)
(CVPR 2026), plus scripts to explore both.

Neither installs cleanly any more. `setup.sh` and `setup-plus.sh` work around
that. Verified on macOS (Apple Silicon) and CUDA Linux.

## Quickstart

```bash
git clone --recursive git@github.com:osehyeon/libero-lab.git
cd libero-lab

./setup.sh                    # base benchmark, 130 tasks
python run_demo.py --list
python run_demo.py --suite libero_spatial --task 0 --gui

./setup-plus.sh               # LIBERO-Plus, 10,030 perturbed tasks
python plus_demo.py --list
```

Run the scripts with any python. Each one re-execs itself under the virtualenv
and config it needs, so there is nothing to activate and no environment
variable to remember -- see `libero_env.py`.

## Contents

| Path | |
|---|---|
| `setup.sh` | Base environment, including 8 upstream workarounds |
| `setup-plus.sh` | LIBERO-Plus environment — separate venv, same package name |
| `patches/` | Source fixes — a submodule cannot carry local edits |
| `run_demo.py` | List tasks, run with GUI, save video |
| `teleop.py` | Drive a task by hand, nothing recorded |
| `replay_demo.py` | Watch a recorded human demo -- the ground truth |
| `download_datasets.py` | Fetch the 94 GB demo datasets |
| `plus_demo.py` | Browse and render LIBERO-Plus perturbations |
| `libero_env.py` | Sends each script to the right venv and config |
| `docs/` | Write-ups, split into `sim/`, `libero/` and `libero-plus/` |
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

`--plus` drives a LIBERO-Plus task instead. It has thousands per suite, so name
one by what was perturbed rather than by index:

```bash
python teleop.py --plus --category "Camera Viewpoints" --level 5
python teleop.py --plus --category "Robot Initial States" --level 5
python teleop.py --plus --suite libero_10 --category "Objects Layout" --nth 3
```

It prints how many tasks matched and takes `--nth` of them (default 0). Driving
a perturbation by hand is the quickest way to find out whether it is solvable at
all, which a success rate does not tell you.

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
./setup-plus.sh    # .venv-plus, plus a 6.4 GB asset download (9.4 GB unpacked)
```

`--list` counts the tasks per perturbation dimension and difficulty level:

```bash
python plus_demo.py --list                    # libero_spatial
python plus_demo.py --list --suite all        # 10,030
```

`--render` picks one task per dimension and saves the initial states side by
side, so you can see what a perturbation actually does:

```bash
python plus_demo.py --render --category all
python plus_demo.py --render --category "Camera Viewpoints" --level 5
python plus_demo.py --render --suite libero_10 --category "Objects Layout"
```

| Option | |
|---|---|
| `--suite` | `libero_spatial` (default), `libero_object`, `libero_goal`, `libero_10`, `all` |
| `--category` | one of the 7 below, or `all` (default) |
| `--level` | difficulty 1-5; `0` (default) takes any |
| `--out` | image path, default `runs/plus.png` |

The 7 dimensions, with how many tasks each contributes:

| Dimension | Tasks |
|---|---|
| Sensor Noise | 1,601 |
| Camera Viewpoints | 1,599 |
| Robot Initial States | 1,550 |
| Language Instructions | 1,537 |
| Objects Layout | 1,525 |
| Light Conditions | 1,142 |
| Background Textures | 1,076 |

Counted from `LIBERO-plus/libero/libero/benchmark/task_classification.json`,
which is also where a policy evaluation would read each task's dimension and
level from.

**ImageMagick is required**, not optional: `env_wrapper.py` imports `wand` at
module level, so `import libero` fails without it. `brew install imagemagick`
on macOS, `apt install libmagickwand-dev` on Linux. `setup-plus.sh` installs it
on macOS and warns on Linux, where it needs root.

[docs/libero-plus/libero-plus.html](docs/libero-plus/libero-plus.html) shows all
7 perturbations rendered on one task, with the counts and the setup traps.
[libero-plus-tasks.html](docs/libero-plus/libero-plus-tasks.html) lays one task
out across all 7 axes x 5 levels and measures what a level actually means.

Two things to know before evaluating. `task.language` carries the perturbation
id for 84.7% of tasks (`...on the plate view 0 0 100 2 352 initstate 0`); pass the
policy `env.language_instruction` instead. And macOS renders some Light presets
as an all-black frame, so do not evaluate the Light axis on a Mac.
[libero-successors.md](docs/libero-plus/libero-successors.md) compares this
benchmark against LIBERO-PRO, LIBERO-X and LIBERO-Para.

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

The patches in `patches/` derive from LIBERO and LIBERO-plus source; see
[patches/NOTICE.md](patches/NOTICE.md). Note that **LIBERO-plus ships no LICENSE
file** -- it is a fork of MIT-licensed LIBERO, but says nothing itself. Images
in `ref/` follow [ref/SOURCES.md](ref/SOURCES.md).
