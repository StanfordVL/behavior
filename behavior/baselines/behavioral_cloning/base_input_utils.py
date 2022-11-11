"""
Base behavior dataset class.
"""
import argparse
import logging
import time

import h5py
import numpy as np

log = logging.getLogger(__name__)

# Constants
IMG_DIM = 128
ACT_DIM = 28
PROPRIOCEPTION_DIM = 22
TASK_OBS_DIM = 456


class BHDataset(object):
    def __init__(self, spec_file):
        self.files = read_spec_file(spec_file)
        t1 = time.time()
        log.info("Reading all training data into memory...")
        (
            self.actions,
            self.proprioceptions,
            self.rgbs,
            self.task_obss,
        ) = read_proc_parallel(self.files)
        self.size = len(self.actions)
        log.debug("Time spent to read data: %.1fs" % (time.time() - t1))

    def to_device(self):
        log.info("Sending data to gpu...")
        import torch

        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.actions = torch.tensor(self.actions, dtype=torch.float32).to(self.device)
        self.proprioceptions = torch.tensor(self.proprioceptions, dtype=torch.float32).to(self.device)
        self.rgbs = torch.tensor(self.rgbs, dtype=torch.float32).permute(0, 3, 1, 2).to(self.device)
        self.task_obss = torch.tensor(self.task_obss, dtype=torch.float32).to(self.device)
        log.debug("Done.")


def read_spec_file(fname):
    files = []
    f = open(fname, "r")
    for line in f:
        items = line.split()
        if len(items) == 0 or line.startswith("#"):
            continue
        elif items[0] == "DIR":
            dir_proc = items[1]
        else:
            files.append(dir_proc + items[0] + "_episode.hdf5")
    return files


def read_proc_parallel(files):
    # read action and state information from processed files
    actions, proprioceptions, rgbs, task_obss = (
        np.empty((0, ACT_DIM)),
        np.empty((0, PROPRIOCEPTION_DIM)),
        np.empty((0, IMG_DIM, IMG_DIM, 3)),
        np.empty((0, TASK_OBS_DIM)),
    )
    for f in files:
        log.info("Processing file %s..." % f)
        hf = h5py.File(f)
        actions = np.append(actions, np.asarray(hf["action"]), axis=0)
        proprioceptions = np.append(proprioceptions, np.asarray(hf["proprioception"]), axis=0)
        rgbs = np.append(rgbs, np.asarray(hf["rgb"]), axis=0)
        task_obss = np.append(task_obss, np.asarray(hf["task_obs"]), axis=0)
        hf.close()
    return actions, proprioceptions, rgbs, task_obss


if __name__ == "__main__":

    def parse_args():
        parser = argparse.ArgumentParser(description="Dataset loader")
        parser.add_argument("--spec", type=str, help="spec file name")
        return parser.parse_args()

    args = parse_args()
    data = BHDataset(args.spec)
    data.to_device()
