"""Pick the right interpreter and config for a script, before `libero` loads.

The repo holds two benchmarks that both ship a package called `libero`, so it
also holds two virtualenvs and two configs. Four combinations of those are
wrong and one of them fails silently: the base venv with the plus config lists
plus tasks happily, then renders them with base code.

Rather than make the caller remember, every script calls `require()` first and
re-execs itself under the right interpreter with the right environment. So
`python run_demo.py` works no matter which python starts it.

Import this before anything from `libero`.
"""
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FLAVORS = {
    "base": (ROOT / ".venv", Path.home() / ".libero", "setup.sh"),
    "plus": (ROOT / ".venv-plus", Path.home() / ".libero-plus", "setup-plus.sh"),
}


def _magick_home():
    """wand dlopens ImageMagick through this. Homebrew does not install it
    where the loader looks, so the prefix has to be passed explicitly."""
    if sys.platform != "darwin":
        return None
    try:
        return subprocess.run(["brew", "--prefix"], capture_output=True,
                              text=True, timeout=10).stdout.strip() or None
    except (OSError, subprocess.SubprocessError):
        return None


def require(flavor):
    venv, config, setup = FLAVORS[flavor]
    python = venv / "bin" / "python"

    if not python.exists():
        raise SystemExit(f"{venv.name} is missing. run ./{setup}")
    if not (config / "config.yaml").exists():
        raise SystemExit(f"{config}/config.yaml is missing. run ./{setup}")

    env = dict(os.environ)
    env["LIBERO_CONFIG_PATH"] = str(config)
    if flavor == "plus" and "MAGICK_HOME" not in env:
        home = _magick_home()
        if home:
            env["MAGICK_HOME"] = home

    same_python = Path(sys.executable).resolve() == python.resolve()
    if same_python and env == os.environ:
        return                                  # already correct, carry on

    # a re-exec that does not satisfy the check above would spin forever, so
    # only ever do it once
    if os.environ.get("LIBERO_ENV_REEXEC") == flavor:
        raise SystemExit(
            f"re-exec into {venv.name} did not take. run it directly:\n"
            f"  LIBERO_CONFIG_PATH={config} {python} {' '.join(sys.argv)}")
    env["LIBERO_ENV_REEXEC"] = flavor

    os.execve(str(python), [str(python), *sys.argv], env)
