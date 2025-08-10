from pathlib import Path

import cv2

from vut.io import get_images, load_image


class VideoReader:
    def __init__(
        self,
        *,
        video_path: str | Path | None = None,
        image_dir: str | Path | None = None,
    ):
        assert video_path is not None or image_dir is not None, (
            "Either video_path or image_dir must be provided."
        )
        if video_path is not None:
            self.cap = cv2.VideoCapture(str(video_path))
            self.num_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
            self.image_size = (
                int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
                int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
            )
        else:
            self.image_paths = sorted(get_images(image_dir))
            self.num_frames = len(self.image_paths)
            self.image_size = load_image(self.image_paths[0]).shape[:2][::-1]
        self.index = 0

    def __enter__(self):
        self.index = 0
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if hasattr(self, "cap"):
            self.cap.release()
        self.index = 0

    def __len__(self):
        return self.num_frames

    def __iter__(self):
        return self

    def __next__(self):
        if self.index >= self.num_frames:
            raise StopIteration

        if hasattr(self, "cap"):
            ret, frame = self.cap.read()
            if not ret:
                raise StopIteration
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        else:
            image = load_image(self.image_paths[self.index])

        self.index += 1
        return image
