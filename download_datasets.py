#!/usr/bin/env python
"""Download the LIBERO demo datasets (94 GB, all 5 suites).

  .venv/bin/python download_datasets.py            # into ./datasets
  .venv/bin/python download_datasets.py --dir /mnt/data/libero
  .venv/bin/python download_datasets.py --suite libero_spatial libero_goal

Only needed for training and for replay_demo.py. Evaluation runs off the
initial states that ship with the LIBERO repo.

Upstream's own downloader takes `--datasets all`, which looks for a
`libero_100` directory that does not exist on HuggingFace. It fails silently,
so libero_90 never arrives. Naming each suite avoids that.
"""
import argparse
import os

from libero.libero.utils.download_utils import download_from_huggingface

SUITES = ["libero_spatial", "libero_object", "libero_goal", "libero_10", "libero_90"]


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--dir", default="datasets", help="where to put the hdf5 files")
    p.add_argument("--suite", nargs="+", default=SUITES, choices=SUITES)
    args = p.parse_args()

    dest = os.path.abspath(os.path.expanduser(args.dir))
    os.makedirs(dest, exist_ok=True)
    print(f"downloading {len(args.suite)} suite(s) into {dest}\n")

    for name in args.suite:
        print(f"=== {name}", flush=True)
        download_from_huggingface(dataset_name=name, download_dir=dest,
                                  check_overwrite=False)
    print("\ndone", flush=True)


if __name__ == "__main__":
    main()
