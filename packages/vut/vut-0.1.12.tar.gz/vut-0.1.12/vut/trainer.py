from hydra.core.hydra_config import HydraConfig

from vut.base import Base
from vut.config import Config


class Trainer[T: Config](Base):
    def __init__(self, cfg: T):
        super().__init__("Trainer", cfg=cfg)
        self.logger.info(f"Running on device: {self.device}")
        self.output_dir = HydraConfig.get().runtime.output_dir

    def train(self):
        raise NotImplementedError("Train method must be implemented in subclasses.")

    def validate(self):
        raise NotImplementedError("Validate method must be implemented in subclasses.")

    def test(self):
        raise NotImplementedError("Test method must be implemented in subclasses.")

    def predict(self):
        raise NotImplementedError("Predict method must be implemented in subclasses.")
