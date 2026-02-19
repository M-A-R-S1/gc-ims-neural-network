import numpy as np
import torch
from torch.utils.data import Dataset
from torchvision.transforms import v2 as transform
import random

class VaeDataset(Dataset):
    def __init__(self, npy_paths: list, class_dict: dict, window_size: int, shifting: bool = True) -> None:

        self.npy_paths = npy_paths
        self.class_dict = class_dict
        self.shifting = shifting

        self.target_size = 4*window_size + 1
        self.full_size = 6*window_size + 1

        self.transform = transform.Compose([
            transform.ToImage(),
            transform.ToDtype(torch.float32)
        ])

    def __len__(self) -> int:
        return len(self.npy_paths)

    def __getitem__(self, index: int) -> tuple[torch.Tensor, int]:
        npy_path = self.npy_paths[index]
        npy_file = np.load(npy_path)

        if self.shifting:
            # Zufälliger Startpunkt zwischen 0 und 10 (31 - 21 = 10)
            start_ret = random.randint(0, self.full_size - self.target_size)
            start_drift = random.randint(0, self.full_size - self.target_size)
        else:
            # Exakte Mitte für konsistente Feature-Extraktion
            start_ret = (self.full_size - self.target_size) // 2
            start_drift = (self.full_size - self.target_size) // 2

        npy_file = npy_file[start_ret: start_ret + self.target_size, start_drift: start_drift + self.target_size]

        min_intensity = npy_file.min()
        max_intensity = npy_file.max()
        if max_intensity - min_intensity == 0:
            npy_file_normalized = np.zeros_like(npy_file)
        else:
            npy_file_normalized = (npy_file - min_intensity) / (max_intensity - min_intensity)

        image = self.transform(npy_file_normalized)
        class_name = self.npy_paths[index].parent.parent.parent.parent.name
        class_idx = self.class_dict[class_name]

        return image, class_idx