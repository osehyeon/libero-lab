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
| `CLAUDE.md` | Working notes — bug list, measured facts, next steps |

## Datasets

**Not needed for evaluation.** Initial states (`.pruned_init`) ship with the
LIBERO repo and total 13 MB. The 100 GB of demos is only for training.

## License

MIT — see [LICENSE](LICENSE). Dependencies are permissive too: LIBERO, robosuite,
bddl and robomimic are MIT; MuJoCo is Apache 2.0.

`patches/libero-fixes.patch` derives from LIBERO source; see
[patches/NOTICE.md](patches/NOTICE.md). Images in `ref/` follow
[ref/SOURCES.md](ref/SOURCES.md).
