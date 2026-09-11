# Notice

`libero-fixes.patch` modifies [LIBERO](https://github.com/Lifelong-Robot-Learning/LIBERO)
source and therefore contains parts of it.

> MIT License
> Copyright (c) 2023 Lifelong Robot Learning

The full license is in the submodule at `LIBERO/LICENSE`.
Keep this notice if you redistribute the patch on its own.

## Target commit

`8f1084e3132a39270c3a13ebe37270a43ece2a01` (2025-03-15)

Other commits may conflict. `setup.sh` runs `git apply --check` first.

---

# libero-plus-fixes.patch

Modifies [LIBERO-plus](https://github.com/sylvestf/LIBERO-plus) source, applying
the same `torch.load(weights_only=False)` fix the base repo needs -- LIBERO-plus
is a fork and inherited the bug.

**LIBERO-plus ships no LICENSE file.** It is a fork of LIBERO, which is MIT
(Copyright (c) 2023 Lifelong Robot Learning), so the original terms presumably
carry over, but the fork does not say so. Check with the authors before
redistributing their source.

## Target commit

`4976dc30028e805ff8094b55501d532c48fec182`

`setup-plus.sh` runs `git apply --check` first.
