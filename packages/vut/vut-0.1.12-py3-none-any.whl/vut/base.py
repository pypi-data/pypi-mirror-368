from vut.config import Config
from vut.cuda import get_device
from vut.logger import get_logger
from vut.mapping import (
    load_action_mapping,
    load_class_mapping,
    load_video_action_mapping,
    load_video_boundaries,
    to_class_index,
)
from vut.util import Env, init_seed


class Base[T: Config]:
    env = Env()

    def __init__(
        self,
        name: str = "Base",
        cfg: T | None = None,
    ):
        """Initialize the Base class.

        Args:
            name (str, optional): Name of the base class. Defaults to "Base".
            cfg (T | None, optional): Configuration object. Defaults to None.
        """
        init_seed(cfg.seed if cfg is not None else 42)
        self.logger = get_logger(name)
        self.cfg: T = cfg if cfg is not None else Config()
        self.device = get_device(self.cfg.device)
        if self.cfg.dataset.class_mapping_path is not None:
            text_to_index, index_to_text = load_class_mapping(
                self.cfg.dataset.class_mapping_path,
                self.cfg.dataset.class_mapping_has_header,
                self.cfg.dataset.class_mapping_separator,
            )
            self.text_to_index = text_to_index
            self.index_to_text = index_to_text
        else:
            self.text_to_index = {}
            self.index_to_text = {}
        if self.cfg.dataset.action_mapping_path is not None:
            action_to_steps = load_action_mapping(
                self.cfg.dataset.action_mapping_path,
                self.cfg.dataset.action_mapping_has_header,
                self.cfg.dataset.action_mapping_action_separator,
                self.cfg.dataset.action_mapping_step_separator,
            )
            self.action_to_steps = action_to_steps
        else:
            self.action_to_steps = {}
        if self.cfg.dataset.video_action_mapping_path is not None:
            video_to_action = load_video_action_mapping(
                self.cfg.dataset.video_action_mapping_path,
                self.cfg.dataset.video_action_mapping_has_header,
                self.cfg.dataset.video_action_mapping_separator,
            )
            self.video_to_action = video_to_action
        else:
            self.video_to_action = {}
        if self.cfg.dataset.video_boundary_dir_path is not None:
            video_boundaries = load_video_boundaries(
                self.cfg.dataset.video_boundary_dir_path,
                self.cfg.dataset.video_boundary_has_header,
                self.cfg.dataset.video_boundary_separator,
            )
            self.video_boundaries = video_boundaries
        else:
            self.video_boundaries = {}
        if self.cfg.dataset.backgrounds:
            self.backgrounds = to_class_index(
                self.cfg.dataset.backgrounds, self.text_to_index
            )
        else:
            self.backgrounds = []
