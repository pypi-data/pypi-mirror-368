import time
from typing import Dict, List

import matplotlib.pyplot as plt
import numpy as np
import torch as tc
import torch.nn as nn
from torch.utils.data import Dataset


def model_size(m: nn.Module):
    a = sum(p.numel() for p in m.parameters())
    b = sum(p.numel() for p in m.parameters() if p.requires_grad)
    return f"trainable: {b}/{a}"


class WindowDataset(Dataset):
    def __init__(s, x, W):
        s.x, s.W = x, W

    def __len__(s):
        return len(s.x) - s.W + 1

    def __getitem__(s, idx):
        return s.x[idx : idx + s.W]


# ==============================

D_TYPE = Dict[str, np.ndarray]
D2_TYPE = Dict[str, D_TYPE]


def slice_xy(xy: D2_TYPE, i1, i2):
    return {sym: {"x": d["x"][i1:i2], "y": d["y"][i1:i2]} for sym, d in xy.items()}


def timer(func):
    def func2(*args, **kwargs):
        t1 = time.time()
        res = func(*args, **kwargs)
        print(f"{func.__name__} took {time.time() - t1:.3f} seconds")
        return res

    return func2


def tensor(x):
    if isinstance(x, dict):
        return {k: tensor(v) for k, v in x.items()}
    if isinstance(x, list):
        return [tensor(v) for v in x]
    if isinstance(x, np.ndarray):
        return tc.from_numpy(x.copy()).float()


# ==================================


def plot_records(records: List[Dict], id, C=1):
    dic = {k: np.array([r[k] for r in records]) for k in records[0]}
    R = int(np.ceil(len(dic) / C))
    plt.figure(figsize=(4 * C, 3 * R))
    i = 0
    for k, v in dic.items():
        i += 1
        plt.subplot(R, C, i)
        plt.title(k)
        plt.plot(v)
    plt.tight_layout()
    plt.savefig(id)
    plt.close()


def plot_xy(xy: D2_TYPE, id="xy"):
    R, C = 5, 2
    plt.figure(figsize=(4 * C, 3 * R))
    i = 0
    for sym, d in xy.items():
        i += 1
        x, y = d["x"], d["y"]
        plt.subplot(R, C, i)
        plt.title(sym)
        for k in range(x.shape[1]):
            plt.plot(x[:, k], label=f"x[:, {k}]")
        plt.legend()
        i += 1
        plt.subplot(R, C, i)
        plt.plot(y)
        if i == R * C:
            break
    plt.tight_layout()
    plt.savefig(id)
    plt.close()
