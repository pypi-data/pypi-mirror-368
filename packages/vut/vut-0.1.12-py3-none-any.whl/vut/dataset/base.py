from pathlib import Path

import torch
from torch import Tensor
from torch.utils.data import DataLoader, Dataset

from vut.base import Base
from vut.config import Config
from vut.io import load_lines, load_np


class BaseDataset[T: Config](Dataset, Base[T]):
    def __init__(self, cfg: T, name: str = "BaseDataset"):
        super().__init__(name, cfg)
        self.cfg = cfg
        self.feature_paths = self._get_feature_paths()

    def _get_feature_paths(self) -> list[Path]:
        split_file_path = (
            f"{self.cfg.dataset.split_dir}/{self.cfg.dataset.split_file_name}"
        )
        feature_paths: list[Path] = load_lines(
            split_file_path, lambda path: Path(path.strip())
        )
        self.logger.info(
            f"Loaded {len(feature_paths)} features from {split_file_path}."
        )
        return feature_paths

    def _load_feature(self, feature_path: Path) -> Tensor:
        feature = load_np(feature_path)
        feature = torch.from_numpy(feature)
        return feature

    def _load_gt(self, feature_path: Path) -> Tensor:
        gt_dir = Path(self.cfg.dataset.gt_dir)
        gt_file = gt_dir / feature_path.with_suffix(".txt").name
        if not gt_file.exists():
            raise FileNotFoundError(f"Ground truth file {gt_file} not found.")
        gt: list[int] = load_lines(
            gt_file, lambda item: self.text_to_index.get(item.strip(), -1)
        )
        return torch.tensor(gt)

    def __len__(self):
        return len(self.feature_paths)

    def __getitem__(self, index: int):
        feature_path = self.feature_paths[index]
        feature = self._load_feature(feature_path)
        gt = self._load_gt(feature_path)
        return feature, gt


class BaseDataLoader[T: Config, U: BaseDataset](DataLoader):
    def __init__(self, cfg: T, dataset: U, collate_fn=None):
        self.dataset = dataset
        super().__init__(
            dataset=dataset,
            batch_size=cfg.training.batch_size,
            shuffle=cfg.training.shuffle,
            collate_fn=collate_fn,
        )
