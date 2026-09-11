# Docs

Standalone pages written while exploring the benchmarks. Open the HTML in a
browser. Grouped by what they are about, not by which repo they came from --
the simulator pages apply to both benchmarks.

## sim/ -- MuJoCo and the robot

Nothing here is LIBERO-specific. It holds for LIBERO-Plus and for any other
robosuite scene.

| File | |
|---|---|
| `mujoco-io.html` | What MuJoCo actually takes in and gives back, measured on a LIBERO scene |
| `panda-joints.html` | Franka Panda joints j1-j7 mapped onto a render, with axes and limits |
| `rotation.html` | Why position is 7 slots and velocity 6 -- quaternions, angular velocity, gimbal lock |
| `rot-playground.html` | Interactive. Drag a Unity-style gizmo and watch the quaternion change |

## libero/ -- the base benchmark

| File | |
|---|---|
| `libero-tasks.html` | Task structure across the 5 suites, with rendered initial states for all 40 tasks |
| `libero-stack.html` | Which library does what, from `.bddl` to `_demo.hdf5`, plus the dependency tree |
| `vla-libero.html` | What released VLA checkpoints actually train and evaluate on |

## libero-plus/ -- the robustness benchmark

| File | |
|---|---|
| `libero-plus.html` | The 7 perturbation axes shown on one task, the counts, and the setup traps |
| `libero-plus-tasks.html` | Gallery: one task across all 7 axes x 5 levels, plus the 4 suites. What each level measures, the name grammar, known defects |
| `libero-successors.md` | LIBERO-PRO, Plus, X and Para compared -- what each adds and which to pick |

## Notes

Text is in Korean. Every number was measured against this repo, with two
exceptions that say so where they appear: `libero-successors.md` is a literature
summary, and `libero-plus-tasks.html` quotes success rates reported in upstream
issues #61, #64 and #65.
