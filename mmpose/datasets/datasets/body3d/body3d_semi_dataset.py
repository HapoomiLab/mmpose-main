import numpy as np
from torch.utils.data import Dataset

from mmpose.datasets.builder import DATASETS, build_dataset


@DATASETS.register_module()
class Body3DSemiDataset(Dataset):
    """Mix Dataset for semi-supervised training in 3D human pose estimation
    task.

    The dataset combines data from two datasets and
    return a dict containing data from two datasets.

    Args:
        labeled_dataset (Dataset): Dataset with 3D keypoint annotations.
        unlabeled_dataset (Dataset): Dataset without 3D keypoint annotations.
    """

    def __init__(self, labeled_dataset, unlabeled_dataset):
        super().__init__()
        self.labeled_dataset = build_dataset(labeled_dataset)
        self.unlabeled_dataset = build_dataset(unlabeled_dataset)
        self.length = len(self.labeled_dataset)

    def __len__(self):
        """Get the size of the dataset."""
        return self.length

    def __getitem__(self, i):
        """Given index, get the data from labeled dataset and randomly sample
        an item from unlabeled dataset.

        Return a dict containing data from labeled and unlabeled dataset.
        """
        data = self.labeled_dataset[i]
        rand_ind = np.random.randint(0, len(self.unlabeled_dataset))
        unlabeled_data = self.unlabeled_dataset[rand_ind]
        data.update(unlabeled_data)
        return data
