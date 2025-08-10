from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Self

import yaml


@dataclass
class BaseConfig:
    @classmethod
    def from_dict(cls, config_dict: dict[str, Any]) -> Self:
        """Create a Config object from a dictionary.

        Args:
            config_dict (dict[str, Any]): The configuration dictionary.

        Raises:
            ValueError: If the configuration dictionary contains unexpected fields.

        Returns:
            Self: The created Config object.
        """
        field_types = {f.name: f.type for f in cls.__dataclass_fields__.values()}
        init_args = {}
        for key, value in config_dict.items():
            if key in field_types:
                field_type = field_types[key]
                if hasattr(field_type, "__dataclass_fields__"):
                    init_args[key] = field_type.from_dict(value)
                else:
                    init_args[key] = value
            else:
                raise ValueError(f"Unexpected field '{key}' in '{cls.__name__}'.")
        return cls(**init_args)

    @classmethod
    def from_yaml(cls, yaml_path: str | Path) -> Self:
        """Load configuration from a YAML file.

        Args:
            yaml_path (str | Path): Path to the YAML file.

        Returns:
            Self: The created Config object.

        Raises:
            FileNotFoundError: If the YAML file does not exist.
            yaml.YAMLError: If there is an error parsing the YAML file.
            ValueError: If the YAML file contains unexpected fields.
        """
        yaml_path = Path(yaml_path)
        if not yaml_path.exists():
            raise FileNotFoundError(f"YAML file not found: {yaml_path}")

        with open(yaml_path, "r", encoding="utf-8") as f:
            config_dict = yaml.safe_load(f)

        if config_dict is None:
            config_dict = {}

        return cls.from_dict(config_dict)


@dataclass
class ModelConfig(BaseConfig):
    name: str


@dataclass
class DatasetConfig(BaseConfig):
    name: str
    num_classes: int = 0
    num_actions: int = 0
    backgrounds: list[str] = field(default_factory=list)
    input_dim: int = 0

    split_dir: str = None
    split_file_name: str = None
    gt_dir: str = None
    feature_dir: str = None
    video_dir: str = None
    class_mapping_path: str = None
    class_mapping_has_header: bool = False
    class_mapping_separator: str = ","
    action_mapping_path: str = None
    action_mapping_has_header: bool = False
    action_mapping_action_separator: str = ","
    action_mapping_step_separator: str = " "
    video_action_mapping_path: str = None
    video_action_mapping_has_header: bool = False
    video_action_mapping_separator: str = ","
    video_boundary_dir_path: str = None
    video_boundary_has_header: bool = False
    video_boundary_separator: str = ","


@dataclass
class TrainingConfig(BaseConfig):
    epochs: int = 100
    split: int = 0
    num_fold: int = 0
    lr: float = 0.001
    batch_size: int = 32
    sampling_rate: int = 1
    shuffle: bool = True


@dataclass
class VisualizationConfig(BaseConfig):
    legend_ncols: int = 3


@dataclass
class ActionSegmentationEvaluationConfig(BaseConfig):
    overlaps: list[float] = field(default_factory=lambda: [0.1, 0.25, 0.5])


@dataclass
class VideoAnomalyEvaluationConfig(BaseConfig):
    positive_label: str = "anomaly"


@dataclass
class Config(BaseConfig):
    seed: int = 42
    device: str = "cuda"
    result_dir: str = "results"
    val_skip: bool = False
    model_dir: str = "models"
    model_file_name: str = "model.pth"

    model: ModelConfig = field(default_factory=lambda: ModelConfig(name="none"))
    dataset: DatasetConfig = field(default_factory=lambda: DatasetConfig(name="none"))
    training: TrainingConfig = field(default_factory=lambda: TrainingConfig())
    visualization: VisualizationConfig = field(
        default_factory=lambda: VisualizationConfig()
    )
    evaluation: ActionSegmentationEvaluationConfig = field(
        default_factory=lambda: ActionSegmentationEvaluationConfig()
    )
