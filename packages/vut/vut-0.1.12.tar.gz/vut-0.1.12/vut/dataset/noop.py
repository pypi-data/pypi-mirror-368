import torch
from torch.utils.data import DataLoader, Dataset

from vut.base import Base
from vut.config import Config


class NoopDataset[T: Config](Dataset, Base[T]):
    def __init__(self, cfg: T, name: str = "NoopDataset"):
        super().__init__(name, cfg)

    def __len__(self):
        return 0

    def __getitem__(self, index: int):
        return torch.tensor([])


class NoopDataLoader[T: Config, U: NoopDataset](DataLoader):
    def __init__(self, cfg: T, dataset: U, collate_fn=None):
        self.dataset = dataset
        super().__init__(
            dataset=dataset,
            batch_size=cfg.training.batch_size,
            shuffle=cfg.training.shuffle,
            collate_fn=collate_fn,
        )
