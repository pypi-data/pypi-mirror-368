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
