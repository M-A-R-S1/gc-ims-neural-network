import numpy as np
import torch
from torch.utils.data import Dataset
from torchvision.transforms import v2 as transform
import random

class VaeDataset(Dataset):
    """
    Custom pytorch dataset which loads GC-IMS peak windows.

    This class receives a list of paths which point to GC-IMS peak windows saved as .npy files.
    The peak windows full dimension is set to 31x31 pixels. Spatial shifting creates multiple variations of each
    peak window. A random area of 21x21 pixels is calculated from within the 31x31 pixels peak window and is returned

    :param npy_paths: list of paths to .npy files.
    :param class_dict: dictionary that maps class names to indexes.
    :param shifting: whether to shift each peak window.

    .. attribute:: npy_paths: list of paths to .npy files.
    .. attribute:: class_dict: dictionary that maps class names to indexes.
    .. attribute:: shifting: whether to shift each peak window.
    .. attribute:: target_size: size of the returned peak window.
    .. attribute:: full_size: size of the full peak window.
    .. attribute:: transform: torchvision.transforms.Compose.
    """

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
        """
        Returns the length of the dataset.

        :return: dataset count.
        """
        return len(self.npy_paths)


    def __getitem__(self, index: int) -> tuple[torch.Tensor, int]:
        """
        This function receives an index and returns a tuple of a tensor image and a class index.
        The index is used to receive a npy file at the index position from the npy path list.
        The npy file is loaded and an area inside this peak window is calculated. This area is either the center
        of the peak window of a randomly calculated area, depending on weather or not the shifting mode is used.
        This area is then normalized between 0 and 1 and returned as a tensor image together with its class index.

        :param index: index of the image.

        :return: image and class index.
        """

        # Get the path of the .npy file for the current index and load it.
        npy_path = self.npy_paths[index]
        npy_file = np.load(npy_path)

        # Uses a random positioned area of the peak window
        if self.shifting:
            start_ret = random.randint(0, self.full_size - self.target_size)
            start_drift = random.randint(0, self.full_size - self.target_size)
        # Uses the middle of the peak window for the area.
        else:
            start_ret = (self.full_size - self.target_size) // 2
            start_drift = (self.full_size - self.target_size) // 2

        # Apply the area to the peak window.
        npy_file = npy_file[start_ret: start_ret + self.target_size, start_drift: start_drift + self.target_size]

        # Normalizes the intensity values of the peak window between 0-1.
        min_intensity = npy_file.min()
        max_intensity = npy_file.max()
        if max_intensity - min_intensity == 0:
            npy_file_normalized = np.zeros_like(npy_file)
        else:
            npy_file_normalized = (npy_file - min_intensity) / (max_intensity - min_intensity)

        # Transforms the image into a tensor.
        image = self.transform(npy_file_normalized)
        # Get the class name of this peak by looking at the folder where it is saved in.
        class_name = self.npy_paths[index].parent.parent.parent.name
        # Get the class index from the dictionary which fits to the class name.
        class_idx = self.class_dict[class_name]

        return image, class_idx