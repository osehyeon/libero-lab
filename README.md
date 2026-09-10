# libero-lab

Reproducible setup for the [LIBERO](https://github.com/Lifelong-Robot-Learning/LIBERO)
benchmark, plus scripts to explore it.

Upstream has not changed since `8f1084e` (2025-03) and no longer installs cleanly.
`setup.sh` works around that. Verified on macOS (Apple Silicon) and CUDA Linux.

## Quickstart

```bash
git clone --recursive git@github.com:osehyeon/libero-lab.git
cd libero-lab && ./setup.sh
.venv/bin/python run_demo.py --list
.venv/bin/python run_demo.py --suite libero_spatial --task 0 --gui
```

## Contents

| Path | |
|---|---|
| `setup.sh` | Environment setup, including 8 upstream workarounds |
| `patches/` | Source fixes for LIBERO — a submodule cannot carry local edits |
| `run_demo.py` | List tasks, run with GUI, save video |
| `replay_demo.py` | Replay human demos (needs the dataset) |
| `docs/` | HTML write-ups on task structure, MuJoCo I/O, rotations, VLA practice |
| `CLAUDE.md` | Working notes — bug list, measured facts, next steps |

## Collect your own demos

Drive the simulator by hand and record it. This is how the original 6,500 demos
were made — one episode per demonstration.

```bash
cd LIBERO
../.venv/bin/python scripts/collect_demonstration.py \
    --device keyboard --robots Panda \
    --bddl-file libero/libero/bddl_files/libero_spatial/pick_up_the_black_bowl_between_the_plate_and_the_ramekin_and_place_it_on_the_plate.bddl
```

| Key | |
|---|---|
| `w` `a` `s` `d` | move in the xy plane |
| `r` `f` | move up and down |
| `z` `x` / `t` `g` / `c` `v` | rotate about x / y / z |
| `space` | toggle gripper |
| `q` | end this episode, start the next |

`--robots Panda` is required — omitting it hits an upstream argparse bug.
Use `--device spacemouse` for a 3D mouse (`pip install hidapi` first).

Episodes land in `demonstration_data/` as states and actions, without images.
`scripts/create_dataset.py` replays them to render the observations and write the
final hdf5.

On macOS, add your terminal under **System Settings → Privacy & Security →
Accessibility**, then restart it. Without this the window opens but keys do nothing.

## Datasets

**Not needed for evaluation.** Initial states (`.pruned_init`) ship with the
LIBERO repo and total 13 MB. The 100 GB of demos is only for training.

## License

MIT — see [LICENSE](LICENSE). Dependencies are permissive too: LIBERO, robosuite,
bddl and robomimic are MIT; MuJoCo is Apache 2.0.

`patches/libero-fixes.patch` derives from LIBERO source; see
[patches/NOTICE.md](patches/NOTICE.md). Images in `ref/` follow
[ref/SOURCES.md](ref/SOURCES.md).
