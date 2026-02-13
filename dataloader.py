import numpy as np
import torch
from torch.utils.data import Dataset
from torchvision.transforms import v2 as transform

class VaeDataset(Dataset):
    def __init__(self, npy_paths: list, class_dict: dict):

        self.npy_paths = npy_paths
        self.class_dict = class_dict

        self.transform = transform.Compose([
            transform.ToImage(),
            transform.ToDtype(torch.float32)
        ])

    def __len__(self) -> int:
        return len(self.npy_paths)

    def __getitem__(self, index: int) -> tuple[torch.Tensor, int]:
        npy_path = self.npy_paths[index]
        npy_file = np.load(npy_path)

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