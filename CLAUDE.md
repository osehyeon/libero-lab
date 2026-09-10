# CLAUDE.md

Working notes for this repo. Everything below was measured, not assumed.

## Layout

`LIBERO/` is a submodule pinned to `8f1084e`. Not committed: `.venv/` (1.8 GB),
`datasets/` (100 GB), `demonstration_data/`.

A submodule tracks only an upstream commit, so **local edits must live in
`patches/`** — otherwise a `--recursive` clone gets unpatched source.
`LIBERO (modified content)` in `git status` is expected: it means patches are applied.

## Machines

| | macOS (M4) | CUDA server |
|---|---|---|
| Render backend | CGL | EGL (`MUJOCO_GL=egl`) |
| Speed | 22.6 steps/sec | 118.7 steps/sec |
| Path | `~/Desktop/libero` | `~/libero` |
| Datasets | none | 94 GB, all 5 suites, in `datasets/` |

Both machines run this same repo. Heavy runs go on the server (`ssh 5090`),
where `datasets/` is already populated -- do not re-download it.

## Upstream bugs

All still present upstream. Check here first when something breaks.

| Symptom | Cause | Fix |
|---|---|---|
| `ModuleNotFoundError: libero` | `find_packages()` misses the namespace package | `.pth` path injection (`setup.sh`) |
| `UnpicklingError` | `torch.load` default changed in torch 2.6 | `weights_only=False` (patch) |
| `libero_90` never downloads | `--datasets all` looks for `libero_100`, absent on HF. **Fails silently** | Name each suite |
| `KeyError: 'MountedP'` | `--robots` is `nargs="+"` with a string default | Pass `--robots Panda` |
| `add_keypress_callback() takes 2 args` | Old robosuite signature | Drop the 3 callback lines (patch) |
| `AssertionError` in `get_joint_qpos_addr` | robosuite 1.4.1 vs mujoco 3.x | Pin `mujoco==2.3.7` |
| macOS `dlopen OpenGL` fails | mujoco 2.3.7 hardcodes an old path (fixed in 3.0.0) | Rewrite `cgl.py` path (`setup.sh`) |
| macOS `egl_probe` build fails | Linux-only, required unconditionally by robomimic | Install with `--no-deps` |

## Measured facts

### Benchmark
- 130 tasks: spatial 10, object 10, goal 10, `libero_90` 90, `libero_10` 10
- Per task: 50 eval initial states (`.pruned_init`, in repo) + 50 demos (hdf5, separate) = 6,500 demos
- Evaluation needs no demos — 651 MB repo is enough. The 100 GB is for training
- The two sets of 50 are **different samples**: zero overlap. Policies are evaluated on layouts absent from the demos
- bddl specifies **regions**, not coordinates; the 50 states are sampled within them (objects shift 1–2 cm)

### Success checking
- 8 predicates (`On`, `In`, `Open`, `Close`, `TurnOn`, `TurnOff`, `Up`, `true`) composed by all 130 tasks. No per-task code
- `On` = height + contact + **horizontal distance < 3 cm**. `Open`/`TurnOn` read `qpos`, not contact
- **No failure signal.** `done` only tracks the horizon. Success is instantaneous — no need to hold it
- Eval loops must call `env.env._check_success()` every step; watching `done` misses successes

### Physics and state
- Action `(7,)` = translation 3 (m) + rotation 3 (rad, axis-angle) + gripper 1, all normalized deltas in `[-1, 1]`
- `[-1,1]` maps to `[-0.05, 0.05] m`, clipped beyond. It is a **target, not per-step displacement**
- Gripper uses `np.sign()` only; closing fully takes 100 steps
- Action 7 → OSC → `d.ctrl` 9 (7 torques + 2 finger positions). **No inverse kinematics**: `τ = JᵀF + gravity comp`
- State 92 = `1 + qpos 48 + qvel 43`, but that is **`libero_spatial` only**. Across 130 tasks: 45–123
- In `qvel`, **only angular velocity is in body frame**; the rest is world frame. Inertia is constant in the body frame
- Physics is fully deterministic (re-run difference `0.000e+00`). Failures come from contact discontinuities

### VLA practice (verified on π₀)
- Released checkpoints train and evaluate on **4 suites (40 tasks)**; `libero_90` is excluded
- Training data is 1,693 episodes, not 2,000 — 15% dropped by the **OpenVLA team** (`openvla/modified_libero_rlds`, `no_noops`)
- `no_noops` removes idle frames, so **trajectory lengths change**; lengths appear that are absent from the original
- Reported: spatial 98.8 / object 98.2 / goal 98.0 / 10: 92.4 → mean **96.85%**
- Same checkpoint scores **18%** on `libero_90` ([openpi #734](https://github.com/Physical-Intelligence/openpi/issues/734))
- Eval config: **50 rollouts** per task (not the repo default 20), `max_steps` **220–520** per suite (not 600) — roughly the longest training demo + 10%

## Scripts

| Script | Needs dataset | Note |
|---|---|---|
| `run_demo.py` | no | `--list`, `--gui`, `--video`. Random actions at line 52 |
| `teleop.py` | no | Manual control, nothing recorded. Defaults to `libero_goal` 5 -- push the plate, the easiest task: one `On` condition, no grasping |
| `replay_demo.py` | yes | `--mode states\|actions` |
| `download_datasets.py` | -- | Names each suite, so `libero_90` is not skipped |

`teleop.py` wraps the env in `VisualizationWrapper` so gripper site markers show,
matching `scripts/collect_demonstration.py`. The unwrapped env is kept as `raw`
for `sim`, `robots[0]` and `_check_success()`.

## Conventions

- Commit messages: one line, English, no body, no trailers
- Don't guess numbers. Every value here was measured; keep it that way
- Web search summaries have contradicted raw files. Read the source
- Local LIBERO edits go in `patches/`, applied by `setup.sh`

## Next

- [ ] Use `libero_90` as a held-out eval. Released models score 18%, so headroom is visible. Needs only the 90 `.pruned_init` files (8.8 MB)
- [ ] Replay all 50 demos in `actions` mode to measure reproduction failure rate across versions
- [ ] Wire up a VLA model — 32 GB is enough for 7B inference. Replace the random action at `run_demo.py:52`
- [ ] Diff `openvla/modified_libero_rlds` against the original to pin down the `no_noops` rule (only described in the paper appendix)
