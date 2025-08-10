from dataclasses import dataclass, field
from typing import Dict, List, Tuple

import numpy as np
from numpy.typing import NDArray
from sklearn.metrics import precision_recall_fscore_support, roc_auc_score

from vut.base import Base
from vut.config import Config, VideoAnomalyEvaluationConfig
from vut.util import to_np, to_segments


def accuracy_framewise(
    ground_truth: List[int] | NDArray, prediction: List[int] | NDArray
) -> float:
    """Calculate frame-wise accuracy for action segmentation.

    Args:
        ground_truth (List[int] | NDArray): Ground truth labels
        prediction (List[int] | NDArray): Predicted labels

    Returns:
        float: Frame-wise accuracy
    """
    gt = to_np(ground_truth)
    pred = to_np(prediction)
    assert gt.shape == pred.shape, "Shape mismatch between ground truth and prediction"
    return np.mean(gt == pred)


def accuracy_classwise(
    ground_truth: List[int] | NDArray, prediction: List[int] | NDArray
) -> Dict[int, float]:
    """Calculate class-wise accuracy for action segmentation.

    Args:
        ground_truth (List[int] | NDArray): Ground truth labels
        prediction (List[int] | NDArray): Predicted labels

    Returns:
        Dict[int, float]: Class-wise accuracy
    """
    gt = to_np(ground_truth)
    pred = to_np(prediction)
    assert gt.shape == pred.shape, "Shape mismatch between ground truth and prediction"
    classes = np.unique(np.concatenate((gt, pred)))
    classes = sorted(classes)
    acc = {}
    for c in classes:
        mask = gt == c
        acc[c] = np.mean(pred[mask] == c) if np.any(mask) else 0.0
    return acc


def accuracy(
    ground_truth: List[int] | NDArray,
    prediction: List[int] | NDArray,
    classwise: bool = False,
) -> float | Dict[int, float]:
    """Calculate accuracy for action segmentation.

    Args:
        ground_truth (List[int] | NDArray): Ground truth labels
        prediction (List[int] | NDArray): Predicted labels
        classwise (bool, optional): If True, return class-wise accuracies instead of overall accuracy. Defaults to False.

    Returns:
        float | Dict[int, float]: Overall accuracy (float) or class-wise accuracies (dict)
    """
    if classwise:
        return accuracy_classwise(ground_truth, prediction)
    return accuracy_framewise(ground_truth, prediction)


def edit_distance(x: List[int], y: List[int]) -> int:
    """Calculate the Levenshtein edit distance between two sequences.

    Args:
        x (List[int]): First sequence
        y (List[int]): Second sequence

    Returns:
        int: Levenshtein edit distance
    """
    m, n = len(x), len(y)
    dp = np.zeros((m + 1, n + 1), dtype=int)
    for i in range(m + 1):
        dp[i, 0] = i
    for j in range(n + 1):
        dp[0, j] = j
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            dp[i, j] = min(
                dp[i - 1, j] + 1,  # Deletion
                dp[i, j - 1] + 1,  # Insertion
                dp[i - 1, j - 1] + (x[i - 1] != y[j - 1]),  # Substitution
            )
    return dp[m, n]


def edit_score(
    ground_truth: List[int] | NDArray,
    prediction: List[int] | NDArray,
    backgrounds: List[int] | NDArray = [],
) -> float:
    """Calculate edit score (normalized Levenshtein distance) for action segmentation.

    Args:
        ground_truth (List[int] | NDArray): Ground truth labels
        prediction (List[int] | NDArray): Predicted labels
        backgrounds (List[int] | NDArray, optional): Background class indices. Defaults to [].

    Returns:
        float: Edit score (0-100)
    """
    gt_seq = [s[0] for s in to_segments(ground_truth, backgrounds)]
    pred_seq = [s[0] for s in to_segments(prediction, backgrounds)]
    dist = edit_distance(gt_seq, pred_seq)
    return (1.0 - dist / max(len(gt_seq), len(pred_seq), 1)) * 100.0


def tp_fp_fn(
    ground_truth: List[int] | NDArray,
    prediction: List[int] | NDArray,
    overlap: float = 0.1,
    backgrounds: List[int] | NDArray = [],
) -> Tuple[int, int, int]:
    """Calculate true positives, false positives, and false negatives for action segmentation.

    Args:
        ground_truth (List[int] | NDArray): Ground truth labels
        prediction (List[int] | NDArray): Predicted labels
        overlap (float, optional): IoU threshold. Defaults to 0.1.
        backgrounds (List[int] | NDArray, optional): Background class indices. Defaults to [].

    Returns:
        Tuple[int, int, int]: True positives, false positives, false negatives
    """
    gt_segments = to_segments(ground_truth, backgrounds)
    pred_segments = to_segments(prediction, backgrounds)
    n_true = len(gt_segments)
    n_pred = len(pred_segments)
    tp = 0
    used = np.zeros(n_true, dtype=bool)
    for p_cls, (p_start, p_end) in pred_segments:
        ious = np.zeros(n_true)
        for gt_idx, (g_cls, (g_start, g_end)) in enumerate(gt_segments):
            if used[gt_idx] or p_cls != g_cls:
                continue
            intersection = max(0, min(p_end, g_end) - max(p_start, g_start))
            union = max(p_end, g_end) - min(p_start, g_start)
            iou = intersection / union if union > 0 else 0
            ious[gt_idx] = iou
        max_iou_idx = np.argmax(ious)
        if ious[max_iou_idx] >= overlap:
            tp += 1
            used[max_iou_idx] = True
    fp = n_pred - tp
    fn = n_true - tp
    return tp, fp, fn


def f1(
    ground_truth: List[int] | NDArray,
    prediction: List[int] | NDArray,
    overlap: float = 0.1,
    backgrounds: List[int] | NDArray = [],
) -> float:
    """Calculate F1 score for action segmentation.

    Args:
        ground_truth (List[int] | NDArray): Ground truth labels
        prediction (List[int] | NDArray): Predicted labels
        overlap (float, optional): IoU threshold. Defaults to 0.1.
        backgrounds (List[int] | NDArray, optional): Background class indices. Defaults to [].

    Returns:
        float: F1 score (0-100)
    """
    tp, fp, fn = tp_fp_fn(ground_truth, prediction, overlap, backgrounds)
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    if precision + recall == 0:
        return 0.0
    return 2 * precision * recall / (precision + recall)


def f1s(
    ground_truth: List[int] | NDArray,
    prediction: List[int] | NDArray,
    backgrounds: List[int] | NDArray = [],
    overlaps: Tuple[float, ...] = (0.1, 0.25, 0.5),
) -> Dict[float, float]:
    """Calculate F1 scores for multiple overlap thresholds.

    Args:
        ground_truth (List[int] | NDArray): Ground truth labels
        prediction (List[int] | NDArray): Predicted labels
        backgrounds (List[int] | NDArray, optional): Background class indices. Defaults to [].
        overlaps (Tuple[float, ...], optional): IoU thresholds. Defaults to (0.1, 0.25, 0.5).

    Returns:
        Dict[float, float]: F1 scores for each overlap threshold.
    """
    return {thr: f1(ground_truth, prediction, thr, backgrounds) for thr in overlaps}


def anomaly_score(
    ground_truth: List[int] | NDArray,
    prediction: List[int] | NDArray,
    positive_label: int = 1,
) -> Dict[str, float]:
    """Calculate precision, recall, and F1 score for binary anomaly detection.

    Args:
        ground_truth (List[int] | NDArray): Ground truth labels (0/1 or normal/anomalous)
        prediction (List[int] | NDArray): Predicted labels (0/1 or normal/anomalous)
        positive_label (int, optional): Label representing the anomalous class. Defaults to 1.

    Returns:
        Dict[str, float]: Precision, recall, F1 score, and other metrics.
    """
    gt = to_np(ground_truth)
    pred = to_np(prediction)
    precision, recall, f1, _ = precision_recall_fscore_support(
        gt, pred, pos_label=positive_label
    )
    return {
        "precision": precision,
        "recall": recall,
        "f1": f1,
    }


def roc_auc(
    ground_truth: List[int] | NDArray,
    prediction: List[int] | NDArray,
) -> float:
    """Calculate ROC AUC score for binary classification.

    Args:
        ground_truth (List[int] | NDArray): Ground truth labels (0/1 or normal/anomalous)
        prediction (List[int] | NDArray): Predicted labels (0/1 or normal/anomalous)

    Returns:
        float: ROC AUC score
    """
    gt = to_np(ground_truth)
    pred = to_np(prediction)
    return roc_auc_score(gt, pred, average="macro", multi_class="ovr")


class ActionSegmentationEvaluator[T: Config](Base):
    def __init__(self, cfg: T, name="Evaluator"):
        super().__init__(name, cfg)
        self.cfg: T = cfg
        self.count = 0
        self.accuracy = 0.0
        self.edit = 0.0
        self.overlaps = (
            cfg.evaluation.overlaps
            if hasattr(cfg.evaluation, "overlaps")
            else [0.1, 0.25, 0.5]
        )
        self.tp = [0] * len(self.overlaps)
        self.fp = [0] * len(self.overlaps)
        self.fn = [0] * len(self.overlaps)

    def update(self, ground_truth: List[int], prediction: List[int]) -> None:
        """Update evaluator with new ground truth and prediction.

        Args:
            ground_truth (List[int]): Ground truth labels.
            prediction (List[int]): Predicted labels.
        """
        self.count += 1
        self.accuracy += accuracy(ground_truth, prediction)
        self.edit += edit_score(ground_truth, prediction)
        for i, overlap in enumerate(self.overlaps):
            tp, fp, fn = tp_fp_fn(
                ground_truth, prediction, overlap, self.cfg.dataset.backgrounds
            )
            self.tp[i] += tp
            self.fp[i] += fp
            self.fn[i] += fn

    def compute(self) -> Dict[str, float]:
        """Compute final evaluation metrics.

        Returns:
            Dict[str, float]: Evaluation metrics including accuracy, edit score, F1 scores for different overlaps.
        """
        if self.count == 0:
            return {}

        avg_accuracy = self.accuracy / self.count
        avg_edit = self.edit / self.count
        f1_scores = {
            overlap: 2 * self.tp[i] / (2 * self.tp[i] + self.fp[i] + self.fn[i]) * 100.0
            for i, overlap in enumerate(self.overlaps)
        }

        return {
            "accuracy": avg_accuracy,
            "edit_score": avg_edit,
            "f1_scores": f1_scores,
        }

    def reset(self) -> None:
        """Reset the evaluator state."""
        self.count = 0
        self.accuracy = 0.0
        self.edit = 0.0
        self.tp = [0] * len(self.overlaps)
        self.fp = [0] * len(self.overlaps)
        self.fn = [0] * len(self.overlaps)


@dataclass
class VideoAnomalyConfig(Config):
    evaluation: VideoAnomalyEvaluationConfig = field(
        default_factory=lambda: VideoAnomalyEvaluationConfig()
    )


class VideoAnomalyEvaluator[T: VideoAnomalyConfig](Base):
    def __init__(self, cfg: T, name="VideoAnomalyEvaluator"):
        super().__init__(name, cfg)
        self.cfg: T = cfg
        self.count = 0
        self.correct = 0.0
        self.tp = 0
        self.fp = 0
        self.fn = 0
        self.store: List[Dict[str, float]] = []

    def update(
        self,
        ground_truth: str,
        prediction_label: str = None,
        prediction_score: float = None,
    ) -> None:
        """Update evaluator with new ground truth and prediction.

        Args:
            ground_truth (str): Ground truth label.
            prediction_label (str, optional): Predicted label. Defaults to None.
            prediction_score (float, optional): Prediction score. Defaults to None.
        """
        assert prediction_label is not None or prediction_score is not None, (
            "Either label or score must be provided"
        )
        self.count += 1
        if prediction_label is not None:
            self.correct += ground_truth == prediction_label
            if ground_truth == self.cfg.evaluation.positive_label:
                if prediction_label == self.cfg.evaluation.positive_label:
                    self.tp += 1
                else:
                    self.fp += 1
            else:
                if prediction_label == self.cfg.evaluation.positive_label:
                    self.fn += 1
        else:
            if ground_truth == self.cfg.evaluation.positive_label:
                self.fn += 1
            else:
                self.fp += 1
        self.store.append(
            {
                "ground_truth": ground_truth,
                "prediction_label": prediction_label,
                "prediction_score": prediction_score,
            }
        )

    def compute(self) -> Dict[str, float]:
        """Compute final evaluation metrics.

        Returns:
            Dict[str, float]: Evaluation metrics including accuracy, precision, recall, F1 score.
        """
        if self.count == 0:
            return {}

        accuracy = self.correct / self.count
        precision = self.tp / (self.tp + self.fp) if (self.tp + self.fp) > 0 else 0.0
        recall = self.tp / (self.tp + self.fn) if (self.tp + self.fn) > 0 else 0.0
        f1 = (
            2 * precision * recall / (precision + recall)
            if (precision + recall) > 0
            else 0.0
        )
        auc = (
            roc_auc(
                [
                    1 if x == self.cfg.evaluation.positive_label else 0
                    for x in self.store
                ],
                [
                    x["prediction_score"]
                    for x in self.store
                    if x["prediction_score"] is not None
                ],
            )
            if any(x["prediction_score"] is not None for x in self.store)
            else 0.0
        )

        return {
            "accuracy": accuracy,
            "precision": precision,
            "recall": recall,
            "f1": f1,
            "auc": auc,
        }
