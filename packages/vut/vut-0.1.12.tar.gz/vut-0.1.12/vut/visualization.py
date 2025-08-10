from pathlib import Path

import matplotlib
import numpy as np
from numpy.typing import NDArray
from sklearn.metrics import auc, roc_curve

from vut.io import get_images, load_image
from vut.palette import RGB, ColorMapName, create_palette, template
from vut.rich import track
from vut.video.writer import VideoWriter

matplotlib.use("Agg")
import matplotlib.pyplot as plt


def plot_palette(
    *,
    name: ColorMapName | None = None,
    palette: NDArray | list[RGB] = None,
    n: int = 256,
    path: str | Path = "palette.png",
    figsize: tuple[int, int] = (8, 2),
) -> None:
    """Plot a color palette.

    Args:
        name (ColorMapName | None, optional): The name of the colormap to use. Defaults to None.
        palette (NDArray | list[RGB], optional): A custom color palette. Defaults to None.
        n (int, optional): The number of colors in the colormap. Defaults to 256.
        path (str | Path, optional): The file path to save the plot. Defaults to "palette.png".
        figsize (tuple[int, int], optional): The size of the figure. Defaults to (8, 2).
    """
    assert name is not None or palette is not None, (
        "Either name or palette must be provided"
    )
    if name is not None:
        cmap = template(n, name)
    else:
        assert palette.ndim == 2, "Palette must be a 2D array"
        cmap = create_palette(palette)
    gradient = np.linspace(0, 1, n)
    fig, ax = plt.subplots(figsize=figsize)
    ax.imshow(
        np.vstack((gradient, gradient)),
        aspect="auto",
        cmap=cmap,
        interpolation="nearest",
    )
    ax.set_axis_off()
    plt.savefig(path, bbox_inches="tight")
    plt.close(fig)


def plot_image(
    data: NDArray,
    path: str | Path = "image.png",
    title: str = None,
    show_axis: bool = False,
    is_jupyter: bool = False,
    return_canvas: bool = False,
    figsize: tuple[int, int] = (8, 6),
) -> NDArray | None:
    """Plot a 3D array as an image.

    Args:
        data (NDArray): The 3D array to plot.
        path (str | Path, optional): The file path to save the image. Defaults to "image.png".
        title (str, optional): The title of the plot. Defaults to None.
        show_axis (bool, optional): Whether to show the axis. Defaults to False.
        is_jupyter (bool, optional): Whether to display the plot in a Jupyter notebook. Defaults to False.
        return_canvas (bool, optional): Whether to return the canvas as a numpy array. Defaults to False.
        figsize (tuple[int, int], optional): The size of the figure. Defaults to (8, 6).

    Returns:
        NDArray: The canvas as a numpy array if return_canvas is True, otherwise None.
    """
    assert data.ndim == 3, "Data must be a 3D array"

    fig, ax = plt.subplots(figsize=figsize)
    ax.imshow(data)
    if not show_axis:
        ax.axis("off")

    if title:
        ax.set_title(title)

    plt.tight_layout()

    if return_canvas:
        fig.canvas.draw()
        canvas = np.array(fig.canvas.buffer_rgba())
        plt.close(fig)
        return canvas[:, :, :3]

    if is_jupyter:
        plt.show()
    else:
        plt.savefig(path, bbox_inches="tight")
    plt.close(fig)


def plot_images(
    data: list[NDArray],
    paths: list[str | Path] | None = None,
    titles: list[str] | None = None,
    show_axis: bool = False,
    is_jupyter: bool = False,
    return_canvas: bool = False,
    ncols: int = None,
    nrows: int = None,
    figsize: tuple[int, int] | None = None,
) -> list[NDArray] | None:
    """Plot a list of 3D arrays as images.

    Args:
        data (list[NDArray]): List of 3D arrays to plot.
        paths (list[str | Path] | None): List of file paths to save the images. Defaults to None.
        titles (list[str] | None, optional): List of titles for each plot. Defaults to None.
        show_axis (bool, optional): Whether to show the axis. Defaults to False.
        is_jupyter (bool, optional): Whether to display the plots in a Jupyter notebook. Defaults to False.
        return_canvas (bool, optional): Whether to return the canvases as numpy arrays. Defaults to False.
        ncols (int, optional): Number of columns in the grid layout. Defaults to None.
        nrows (int, optional): Number of rows in the grid layout. Defaults to None.
        figsize (tuple[int, int] | None, optional): The size of the figure. If None, defaults to (ncols * 5, nrows * 5). Defaults to None.

    Returns:
        list[NDArray]: List of canvases as numpy arrays if return_canvas is True, otherwise None.
    """
    assert all(d.ndim == 3 for d in data), "All data must be 3D arrays"
    assert paths is None or len(paths) == len(data), (
        "Paths must be provided for each image if specified"
    )
    assert titles is None or len(titles) == len(data), (
        "Titles must be provided for each image if specified"
    )

    if paths is None:
        paths = [None] * len(data)
    if titles is None:
        titles = [None] * len(data)

    num_images = len(data)
    if ncols is None and nrows is None:
        ncols = int(np.ceil(np.sqrt(num_images)))
        nrows = int(np.ceil(num_images / ncols))
    elif ncols is None:
        ncols = int(np.ceil(num_images / nrows))
    elif nrows is None:
        nrows = int(np.ceil(num_images / ncols))
    assert ncols * nrows >= num_images, (
        "Number of columns and rows must accommodate all images"
    )

    canvases = []
    if figsize is None:
        figsize = (ncols * 5, nrows * 5)
    fig, axs = plt.subplots(nrows=nrows, ncols=ncols, figsize=figsize)
    axs = axs.flatten() if nrows > 1 or ncols > 1 else [axs]
    for i, (ax, img, path) in enumerate(zip(axs, data, paths)):
        ax.imshow(img)
        if not show_axis:
            ax.axis("off")
        if titles and titles[i]:
            ax.set_title(titles[i])
        if return_canvas:
            fig.canvas.draw()
            canvas = np.array(fig.canvas.buffer_rgba())
            canvases.append(canvas[:, :, :3])
        elif path:
            plt.savefig(path, bbox_inches="tight")
    plt.tight_layout()
    if return_canvas:
        plt.close(fig)
        return canvases
    if is_jupyter:
        plt.show()
        plt.close(fig)


def plot_feature(
    data: NDArray,
    path: str | Path = "feature.png",
    title: str = None,
    is_jupyter: bool = False,
    return_canvas: bool = False,
    palette: ColorMapName | list[RGB] | None = "plasma",
    figsize: tuple[int, int] = (8, 6),
) -> NDArray | None:
    """Plot a 2D feature map.

    Args:
        data (NDArray): The 2D array to plot.
        path (str | Path, optional): The file path to save the image. Defaults to "feature.png".
        title (str, optional): The title of the plot. Defaults to None.
        is_jupyter (bool, optional): Whether to display the plot in a Jupyter notebook. Defaults to False.
        return_canvas (bool, optional): Whether to return the canvas as a numpy array. Defaults to False.
        palette (ColorMapName | list[RGB], optional): The colormap to use. Defaults to "plasma".
        figsize (tuple[int, int], optional): The size of the figure. Defaults to (8, 6).

    Returns:
        NDArray: The canvas as a numpy array if return_canvas is True, otherwise None.
    """
    assert data.ndim == 2, "Data must be a 2D array"

    fig, ax = plt.subplots(figsize=figsize)
    cax = ax.imshow(
        data, cmap=create_palette(palette) if isinstance(palette, list) else palette
    )
    if title:
        ax.set_title(title)
    fig.colorbar(cax)

    plt.tight_layout()

    if return_canvas:
        fig.canvas.draw()
        canvas = np.array(fig.canvas.buffer_rgba())
        plt.close(fig)
        return canvas[:, :, :3]

    if is_jupyter:
        plt.show()
        plt.close(fig)
    else:
        plt.savefig(path, bbox_inches="tight")
        plt.close(fig)


def plot_features(
    data: list[NDArray],
    paths: list[str | Path] | None = None,
    titles: list[str] | None = None,
    is_jupyter: bool = False,
    return_canvas: bool = False,
    ncols: int = None,
    nrows: int = None,
    palette: ColorMapName | list[RGB] | None = "plasma",
    figsize: tuple[int, int] | None = None,
) -> list[NDArray] | None:
    """Plot a list of 2D feature maps.

    Args:
        data (list[NDArray]): List of 2D arrays to plot.
        paths (list[str | Path] | None): List of file paths to save the images. Defaults to None.
        titles (list[str] | None, optional): List of titles for each plot. Defaults to None.
        is_jupyter (bool, optional): Whether to display the plots in a Jupyter notebook. Defaults to False.
        return_canvas (bool, optional): Whether to return the canvases as numpy arrays. Defaults to False.
        ncols (int, optional): Number of columns in the grid layout. Defaults to None.
        nrows (int, optional): Number of rows in the grid layout. Defaults to None.
        palette (ColorMapName | list[RGB], optional): The colormap to use. Defaults to "plasma".
        figsize (tuple[int, int] | None, optional): The size of the figure. If None, defaults to (ncols * 5, nrows * 5). Defaults to None.

    Returns:
        list[NDArray]: List of canvases as numpy arrays if return_canvas is True, otherwise None.
    """
    assert all(d.ndim == 2 for d in data), "All data must be 2D arrays"
    assert paths is None or len(paths) == len(data), (
        "Paths must be provided for each image if specified"
    )
    assert titles is None or len(titles) == len(data), (
        "Titles must be provided for each image if specified"
    )

    if paths is None:
        paths = [None] * len(data)
    if titles is None:
        titles = [None] * len(data)

    num_features = len(data)
    if ncols is None and nrows is None:
        ncols = int(np.ceil(np.sqrt(num_features)))
        nrows = int(np.ceil(num_features / ncols))
    elif ncols is None:
        ncols = int(np.ceil(num_features / nrows))
    elif nrows is None:
        nrows = int(np.ceil(num_features / ncols))

    canvases = []
    if figsize is None:
        if nrows and ncols:
            figsize = (ncols * 5, nrows * 5)
        else:
            figsize = (len(data) * 5, 5)
    fig, axs = plt.subplots(
        nrows=nrows if nrows is not None else 1,
        ncols=ncols if ncols is not None else len(data),
        figsize=figsize,
    )
    axs = axs.flatten() if nrows > 1 or ncols > 1 else [axs]
    for i, (ax, img, path) in enumerate(zip(axs, data, paths)):
        cax = ax.imshow(
            img,
            cmap=create_palette(palette) if isinstance(palette, list) else palette,
        )
        if titles and titles[i]:
            ax.set_title(titles[i])
        fig.colorbar(cax, ax=ax)
        if return_canvas:
            fig.canvas.draw()
            canvas = np.array(fig.canvas.buffer_rgba())
            canvases.append(canvas[:, :, :3])
        elif path:
            plt.savefig(path, bbox_inches="tight")
    plt.tight_layout()
    if return_canvas:
        plt.close(fig)
        return canvases
    if is_jupyter:
        plt.show()
        plt.close(fig)


def plot_scatter(
    data: NDArray,
    labels: list[str] | None = None,
    path: str | Path = "scatter.png",
    title: str | None = None,
    is_jupyter: bool = False,
    return_canvas: bool = False,
    palette: ColorMapName | list[RGB] | None = "plasma",
    figsize: tuple[int, int] = (10, 8),
) -> NDArray | None:
    """Plot a 2D scatter plot of the data.

    Args:
        data (NDArray): 2D array of shape (n_samples, 2) representing the data points.
        labels (list[str] | None, optional): List of labels for each data point. Defaults to None.
        path (str | Path, optional): File path to save the plot. Defaults to "scatter.png".
        title (str | None, optional): Title of the plot. Defaults to None.
        is_jupyter (bool, optional): Whether to display the plot in a Jupyter notebook. Defaults to False.
        return_canvas (bool, optional): Whether to return the canvas as a numpy array. Defaults to False.
        palette (ColorMapName | list[RGB] | None, optional): Colormap to use for the plot. Defaults to "plasma".
        figsize (tuple[int, int], optional): Figure size (width, height). Defaults to (10, 8).

    Returns:
        NDArray | None: The canvas as a numpy array if return_canvas is True, otherwise None.
    """
    assert data.ndim == 2, "Data must be a 2D array"
    assert data.shape[1] == 2, "Data must be 2D embedding (n_samples, 2)"

    fig, ax = plt.subplots(figsize=figsize)
    cmap = (
        create_palette(palette)
        if isinstance(palette, list)
        else template(len(data), palette)
    )
    colors = labels if labels is not None else cmap(np.linspace(0, 1, data.shape[0]))
    scatter = ax.scatter(
        data[:, 0],
        data[:, 1],
        c=colors,
        cmap=cmap if labels is not None else None,
        s=50,
        alpha=0.7,
    )

    if labels is not None:
        assert len(labels) == data.shape[0], "Labels must match number of samples"
        legend = ax.legend(*scatter.legend_elements())
        ax.add_artist(legend)

    if title:
        ax.set_title(title)

    plt.tight_layout()

    if return_canvas:
        fig.canvas.draw()
        canvas = np.array(fig.canvas.buffer_rgba())
        plt.close(fig)
        return canvas[:, :, :3]

    if is_jupyter:
        plt.show()
    else:
        plt.savefig(path, bbox_inches="tight")

    plt.close(fig)


def plot_metrics(
    metrics: dict[str, NDArray | list[int] | list[float]],
    path: str | Path = "metrics.png",
    title: str | None = None,
    x_label: str = "Epoch",
    y_label: str = "Value",
    is_jupyter: bool = False,
    return_canvas: bool = False,
    figsize: tuple[int, int] = (10, 6),
) -> NDArray | None:
    """Plot machine learning metrics over time.

    Args:
        metrics (dict[str, NDArray | list[int] | list[float]]): Dictionary where keys are metric names and values are metric data.
        path (str | Path, optional): File path to save the plot. Defaults to "metrics.png".
        title (str | None, optional): Title of the plot. Defaults to None.
        x_label (str, optional): Label for the x-axis. Defaults to "Epoch".
        y_label (str, optional): Label for the y-axis. Defaults to "Value".
        is_jupyter (bool, optional): Whether to display the plot in a Jupyter notebook. Defaults to False.
        return_canvas (bool, optional): Whether to return the canvas as a numpy array. Defaults to False.
        figsize (tuple[int, int], optional): Figure size (width, height). Defaults to (10, 6).

    Returns:
        NDArray | None: The canvas as a numpy array if return_canvas is True, otherwise None.
    """
    fig, ax = plt.subplots(figsize=figsize)

    for name, data in metrics.items():
        data = np.array(data)

        assert data.ndim == 1, f"Metric data for '{name}' must be 1D array or list"

        x = np.arange(len(data))
        ax.plot(x, data, label=name)

    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.legend()
    ax.grid(True, alpha=0.3)

    if title:
        ax.set_title(title)

    plt.tight_layout()

    if return_canvas:
        fig.canvas.draw()
        canvas = np.array(fig.canvas.buffer_rgba())
        plt.close(fig)
        return canvas[:, :, :3]

    if is_jupyter:
        plt.show()
    else:
        plt.savefig(path, bbox_inches="tight")

    plt.close(fig)


def plot_action_segmentation(
    ground_truth: NDArray | list[int],
    prediction: NDArray | list[int] | None = None,
    confidences: NDArray | list[float] | None = None,
    path: str | Path = "action_segmentation.png",
    title: str | None = None,
    labels: list[str] | None = None,
    is_jupyter: bool = False,
    return_canvas: bool = False,
    figsize: tuple[int, int] = (16, 8),
    palette: ColorMapName | list[RGB] | None = "plasma",
    legend_ncol: int = 5,
) -> NDArray | None:
    """Plot action segmentation results with ground truth, predictions, and optional confidences.

    Args:
        ground_truth (NDArray | list[int]): Ground truth action labels.
        prediction (NDArray | list[int] | None, optional): Predicted action labels. Defaults to None.
        confidences (NDArray | list[float] | None, optional): Confidence scores for predictions. Defaults to None.
        path (str | Path, optional): File path to save the plot. Defaults to "action_segmentation.png".
        title (str | None, optional): Title of the plot. Defaults to None.
        labels (list[str] | None, optional): Names of action classes. Defaults to None.
        is_jupyter (bool, optional): Whether to display the plot in a Jupyter notebook. Defaults to False.
        return_canvas (bool, optional): Whether to return the canvas as a numpy array. Defaults to False.
        figsize (tuple[int, int], optional): Figure size (width, height). Defaults to (16, 8).
        palette (ColorMapName | list[RGB] | None, optional): Colormap to use for the plot. Defaults to "plasma".
        legend_ncol (int, optional): Number of columns in the legend. Defaults to 5.

    Returns:
        NDArray | None: The canvas as a numpy array if return_canvas is True, otherwise None.
    """
    ground_truth = np.array(ground_truth)

    assert ground_truth.ndim == 1, "Ground truth must be a 1D array"

    if prediction is not None:
        prediction = np.array(prediction)
        assert prediction.ndim == 1, "Prediction must be a 1D array"
        assert len(ground_truth) == len(prediction), (
            "Ground truth and prediction must have the same length"
        )

    if confidences is not None:
        confidences = np.array(confidences)
        if prediction is not None:
            assert len(confidences) == len(prediction), (
                "Confidences and prediction must have the same length"
            )
        else:
            assert len(confidences) == len(ground_truth), (
                "Confidences and ground truth must have the same length"
            )

    n_frames = len(ground_truth)
    x = np.arange(n_frames)

    if prediction is not None:
        unique_classes = np.unique(np.concatenate([ground_truth, prediction]))
    else:
        unique_classes = np.unique(ground_truth)
    n_classes = len(unique_classes)

    if isinstance(palette, list):
        cmap = create_palette(palette)
    else:
        cmap = plt.get_cmap(palette)

    colors = [cmap(i / max(n_classes - 1, 1)) for i in range(n_classes)]
    class_to_color = {cls: colors[i] for i, cls in enumerate(unique_classes)}

    n_subplots = 1
    if prediction is not None:
        n_subplots += 1
    if confidences is not None:
        n_subplots += 1

    fig, axes = plt.subplots(n_subplots, 1, figsize=figsize, sharex=True)
    if n_subplots == 1:
        axes = [axes]

    ax_gt = axes[0]
    gt_colors = [class_to_color[ground_truth[i]] for i in range(n_frames)]
    ax_gt.bar(x, np.ones(n_frames), color=gt_colors, width=1.0, alpha=0.8)
    ax_gt.set_xlim(0, n_frames - 1)
    ax_gt.set_ylabel("Ground Truth")
    ax_gt.set_ylim(0, 1)
    ax_gt.set_yticks([])

    current_axis_idx = 1
    if prediction is not None:
        ax_pred = axes[current_axis_idx]
        for i in range(n_frames):
            ax_pred.bar(
                x[i], 1, color=class_to_color[prediction[i]], width=1.0, alpha=0.8
            )
        ax_pred.set_xlim(0, n_frames - 1)
        ax_pred.set_ylabel("Prediction")
        ax_pred.set_ylim(0, 1)
        ax_pred.set_yticks([])
        current_axis_idx += 1

    if confidences is not None:
        ax_conf = axes[current_axis_idx]
        confidences = np.array(confidences)

        if confidences.ndim == 1:
            ax_conf.plot(x, confidences, linewidth=2)
        elif confidences.ndim == 2:
            for cls_idx, cls in enumerate(unique_classes):
                if cls_idx < confidences.shape[1]:
                    ax_conf.plot(
                        x,
                        confidences[:, cls_idx],
                        color=class_to_color[cls],
                        linewidth=2,
                    )

        ax_conf.set_xlim(0, n_frames - 1)
        ax_conf.set_ylabel("Confidence")
        ax_conf.set_ylim(0, 1)
        ax_conf.grid(True, alpha=0.3)

    legend_elements = []
    for cls in unique_classes:
        if labels is not None and cls < len(labels):
            label = labels[cls]
        else:
            label = cls
        legend_elements.append(
            plt.Rectangle((0, 0), 1, 1, facecolor=class_to_color[cls], label=label)
        )

    ncol = min(len(legend_elements), legend_ncol)
    nrow = int(np.ceil(len(legend_elements) / ncol))

    grid = []
    for row in range(nrow):
        row_elements = []
        for col in range(ncol):
            idx = row * ncol + col
            if idx < len(legend_elements):
                row_elements.append(legend_elements[idx])
            else:
                row_elements.append(None)
        grid.append(row_elements)

    reordered_elements = []
    for col in range(ncol):
        for row in range(nrow):
            if grid[row][col] is not None:
                reordered_elements.append(grid[row][col])

    fig.legend(
        handles=reordered_elements,
        loc="upper center",
        bbox_to_anchor=(0.5, 0),
        ncol=ncol,
    )

    axes[-1].set_xlabel("Frame")

    if title:
        fig.suptitle(title)

    plt.tight_layout()

    if return_canvas:
        fig.canvas.draw()
        canvas = np.array(fig.canvas.buffer_rgba())
        plt.close(fig)
        return canvas[:, :, :3]

    if is_jupyter:
        plt.show()
    else:
        plt.savefig(path, bbox_inches="tight")

    plt.close(fig)


def plot_roc_curve(
    ground_truth: NDArray | list[int],
    prediction: NDArray | list[float],
    path: str | Path = "roc_curve.png",
    title: str | None = None,
    is_jupyter: bool = False,
    return_canvas: bool = False,
    figsize: tuple[int, int] = (8, 6),
) -> NDArray | None:
    """Plot ROC (Receiver Operating Characteristic) curve.

    Args:
        ground_truth (NDArray | list[int]): Ground truth binary labels (0 or 1).
        prediction (NDArray | list[float]): Prediction scores or probabilities.
        path (str | Path, optional): File path to save the plot. Defaults to "roc_curve.png".
        title (str | None, optional): Title of the plot. Defaults to None.
        is_jupyter (bool, optional): Whether to display the plot in a Jupyter notebook. Defaults to False.
        return_canvas (bool, optional): Whether to return the canvas as a numpy array. Defaults to False.
        figsize (tuple[int, int], optional): Figure size (width, height). Defaults to (8, 6).

    Returns:
        NDArray | None: The canvas as a numpy array if return_canvas is True, otherwise None.
    """
    ground_truth = np.array(ground_truth)
    prediction = np.array(prediction)

    assert ground_truth.ndim == 1, "Ground truth must be a 1D array"
    assert prediction.ndim == 1, "Prediction must be a 1D array"
    assert len(ground_truth) == len(prediction), (
        "Ground truth and prediction must have the same length"
    )
    assert set(np.unique(ground_truth)).issubset({0, 1}), (
        "Ground truth must contain only 0 and 1"
    )

    fpr, tpr, _ = roc_curve(ground_truth, prediction)
    roc_auc = auc(fpr, tpr)

    fig, ax = plt.subplots(figsize=figsize)

    ax.plot(fpr, tpr, lw=2, label=f"ROC curve (AUC = {roc_auc:.2f})")

    ax.set_xlim([0.0, 1.0])
    ax.set_ylim([0.0, 1.05])
    ax.set_xlabel("False Positive Rate")
    ax.set_ylabel("True Positive Rate")
    ax.legend(loc="lower right")
    ax.grid(True, alpha=0.3)

    if title:
        ax.set_title(title)

    plt.tight_layout()

    if return_canvas:
        fig.canvas.draw()
        canvas = np.array(fig.canvas.buffer_rgba())
        plt.close(fig)
        return canvas[:, :, :3]

    if is_jupyter:
        plt.show()
    else:
        plt.savefig(path, bbox_inches="tight")

    plt.close(fig)


def make_video(
    image_dir: str | Path | None = None,
    image_paths: list[str | Path] | None = None,
    ground_truth: NDArray | list[int] | None = None,
    prediction: NDArray | list[int] | None = None,
    confidences: NDArray | list[float] | None = None,
    path: str | Path = "video.mp4",
    title: str | None = None,
    labels: list[str] | None = None,
    fps: int = 30,
    figsize: tuple[int, int] = (16, 9),
    palette: ColorMapName | list[RGB] | None = "plasma",
    legend_ncol: int = 5,
    show_segmentation: bool = True,
    show_confidence: bool = True,
) -> None:
    """Create a video from images with optional action segmentation and confidence overlays.

    Args:
        image_dir (str | Path | None, optional): Directory containing images. Defaults to None.
        image_paths (list[str | Path] | None, optional): List of image file paths. Defaults to None.
        ground_truth (NDArray | list[int] | None, optional): Ground truth action labels. Defaults to None.
        prediction (NDArray | list[int] | None, optional): Predicted action labels. Defaults to None.
        confidences (NDArray | list[float] | None, optional): Confidence scores. Defaults to None.
        path (str | Path, optional): Output video file path. Defaults to "video.mp4".
        title (str | None, optional): Title of the video. Defaults to None.
        labels (list[str] | None, optional): Names of action classes. Defaults to None.
        fps (int, optional): Frames per second. Defaults to 30.
        is_jupyter (bool, optional): Whether to display in a Jupyter notebook. Defaults to False.
        return_frames (bool, optional): Whether to return frames as numpy arrays. Defaults to False.
        figsize (tuple[int, int], optional): Figure size (width, height). Defaults to (16, 9).
        palette (ColorMapName | list[RGB] | None, optional): Colormap to use. Defaults to "plasma".
        legend_ncol (int, optional): Number of columns in the legend. Defaults to 5.
        show_segmentation (bool, optional): Whether to show segmentation overlay. Defaults to True.
        show_confidence (bool, optional): Whether to show confidence plot. Defaults to True.
    """
    assert image_dir is not None or image_paths is not None, (
        "Either image_dir or image_paths must be provided"
    )

    if image_dir is not None:
        image_paths = get_images(image_dir)
    else:
        image_paths = [Path(p) for p in image_paths]

    assert len(image_paths) > 0, "No images found"

    n_frames = len(image_paths)

    if ground_truth is not None:
        ground_truth = np.array(ground_truth)
        assert len(ground_truth) == n_frames, (
            "Ground truth length must match number of images"
        )

    if prediction is not None:
        prediction = np.array(prediction)
        assert len(prediction) == n_frames, (
            "Prediction length must match number of images"
        )

    if confidences is not None:
        confidences = np.array(confidences)
        if confidences.ndim == 1:
            assert len(confidences) == n_frames, (
                "Confidences length must match number of images"
            )
        else:
            assert confidences.shape[0] == n_frames, (
                "Confidences first dimension must match number of images"
            )

    unique_classes = None
    if ground_truth is not None or prediction is not None:
        all_labels = []
        if ground_truth is not None:
            all_labels.append(ground_truth)
        if prediction is not None:
            all_labels.append(prediction)
        unique_classes = np.unique(np.concatenate(all_labels))
        n_classes = len(unique_classes)

        if isinstance(palette, list):
            cmap = create_palette(palette)
        else:
            cmap = plt.get_cmap(palette)

        colors = [cmap(i / max(n_classes - 1, 1)) for i in range(n_classes)]
        class_to_color = {cls: colors[i] for i, cls in enumerate(unique_classes)}

    segmentation_canvas = None
    confidence_canvas = None
    legend_canvas = None

    has_segmentation_data = (
        show_segmentation and (ground_truth is not None or prediction is not None)
    ) or (show_confidence and confidences is not None)

    if has_segmentation_data:
        if show_segmentation and (ground_truth is not None or prediction is not None):
            seg_subplots = 0
            if ground_truth is not None:
                seg_subplots += 1
            if prediction is not None:
                seg_subplots += 1

            seg_fig, seg_axes = plt.subplots(
                seg_subplots, 1, figsize=(figsize[0], seg_subplots), sharex=True
            )
            if seg_subplots == 1:
                seg_axes = [seg_axes]

            current_seg_idx = 0

            if ground_truth is not None:
                ax_gt = seg_axes[current_seg_idx]
                segment_starts = []
                current_class = ground_truth[0]
                start_frame = 0

                for frame_idx in range(1, len(ground_truth)):
                    if ground_truth[frame_idx] != current_class:
                        segment_starts.append(
                            (
                                start_frame / n_frames,
                                (frame_idx - start_frame) / n_frames,
                                current_class,
                            )
                        )
                        current_class = ground_truth[frame_idx]
                        start_frame = frame_idx

                segment_starts.append(
                    (
                        start_frame / n_frames,
                        (len(ground_truth) - start_frame) / n_frames,
                        current_class,
                    )
                )

                for start_pos, width, cls in segment_starts:
                    color = (
                        class_to_color[cls] if unique_classes is not None else "blue"
                    )
                    ax_gt.barh(
                        0, width, left=start_pos, height=0.8, color=color, alpha=0.8
                    )

                ax_gt.set_xlim(0, 1)
                ax_gt.set_ylim(-0.5, 0.5)
                ax_gt.set_ylabel("GT", rotation=0, ha="right")
                ax_gt.set_xticks([])
                ax_gt.set_yticks([])
                current_seg_idx += 1

            if prediction is not None:
                ax_pred = seg_axes[current_seg_idx]
                segment_starts = []
                current_class = prediction[0]
                start_frame = 0

                for frame_idx in range(1, len(prediction)):
                    if prediction[frame_idx] != current_class:
                        segment_starts.append(
                            (
                                start_frame / n_frames,
                                (frame_idx - start_frame) / n_frames,
                                current_class,
                            )
                        )
                        current_class = prediction[frame_idx]
                        start_frame = frame_idx

                segment_starts.append(
                    (
                        start_frame / n_frames,
                        (len(prediction) - start_frame) / n_frames,
                        current_class,
                    )
                )

                for start_pos, width, cls in segment_starts:
                    color = class_to_color[cls] if unique_classes is not None else "red"
                    ax_pred.barh(
                        0, width, left=start_pos, height=0.8, color=color, alpha=0.8
                    )

                ax_pred.set_xlim(0, 1)
                ax_pred.set_ylim(-0.5, 0.5)
                ax_pred.set_ylabel("Pred", rotation=0, ha="right")
                ax_pred.set_xticks([])
                ax_pred.set_yticks([])

            plt.tight_layout()
            seg_fig.canvas.draw()
            segmentation_canvas = np.array(seg_fig.canvas.buffer_rgba())[:, :, :3]
            plt.close(seg_fig)

        if show_confidence and confidences is not None:
            conf_fig, ax_conf = plt.subplots(figsize=(figsize[0], 1.5))
            x = np.arange(n_frames)

            if confidences.ndim == 1:
                ax_conf.plot(x, confidences, linewidth=2, color="blue")
            else:
                for cls_idx, cls in enumerate(unique_classes):
                    if cls_idx < confidences.shape[1]:
                        class_conf = confidences[:, cls_idx]
                        color = (
                            class_to_color[cls]
                            if unique_classes is not None
                            else plt.cm.tab10(cls_idx)
                        )
                        ax_conf.plot(x, class_conf, color=color, linewidth=2)

            ax_conf.set_xlim(0, n_frames - 1)
            ax_conf.set_ylim(0, 1)
            ax_conf.set_ylabel("Confidence")
            ax_conf.set_xlabel("Frame")
            ax_conf.grid(True, alpha=0.3)
            plt.tight_layout()
            conf_fig.canvas.draw()
            confidence_canvas = np.array(conf_fig.canvas.buffer_rgba())[:, :, :3]
            plt.close(conf_fig)

        if show_segmentation and unique_classes is not None:
            legend_elements = []
            for cls in unique_classes:
                if labels is not None and cls < len(labels):
                    label = labels[cls]
                else:
                    label = cls
                legend_elements.append(
                    plt.Rectangle(
                        (0, 0), 1, 1, facecolor=class_to_color[cls], label=label
                    )
                )

            ncol = min(len(legend_elements), legend_ncol)
            nrow = int(np.ceil(len(legend_elements) / ncol))

            grid = []
            for row in range(nrow):
                row_elements = []
                for col in range(ncol):
                    idx = row * ncol + col
                    if idx < len(legend_elements):
                        row_elements.append(legend_elements[idx])
                    else:
                        row_elements.append(None)
                grid.append(row_elements)

            reordered_elements = []
            for col in range(ncol):
                for row in range(nrow):
                    if grid[row][col] is not None:
                        reordered_elements.append(grid[row][col])

            legend_fig, legend_ax = plt.subplots(figsize=(figsize[0], 0.5))
            legend_ax.axis("off")
            legend_ax.legend(
                handles=reordered_elements,
                loc="center",
                ncol=ncol,
            )
            plt.tight_layout()
            legend_fig.canvas.draw()
            legend_canvas = np.array(legend_fig.canvas.buffer_rgba())[:, :, :3]
            plt.close(legend_fig)

    frames = []

    for i, img_path in track(
        enumerate(image_paths), total=len(image_paths), description="Processing images"
    ):
        img = load_image(img_path)

        if not has_segmentation_data:
            fig, ax_img = plt.subplots(figsize=figsize)
            ax_img.imshow(img)
            ax_img.axis("off")

            title_parts = []
            if title:
                title_parts.append(f"{title} - Frame {i + 1}/{n_frames}")
            else:
                title_parts.append(f"Frame {i + 1}/{n_frames}")

            label_parts = []
            if ground_truth is not None:
                gt_label = ground_truth[i]
                if labels is not None and gt_label < len(labels):
                    gt_text = labels[gt_label]
                else:
                    gt_text = str(gt_label)
                label_parts.append(f"GT: {gt_text:<15}")

            if prediction is not None:
                pred_label = prediction[i]
                if labels is not None and pred_label < len(labels):
                    pred_text = labels[pred_label]
                else:
                    pred_text = str(pred_label)
                label_parts.append(f"Pred: {pred_text:<15}")

            if label_parts:
                title_parts.append(" | ".join(label_parts))

            final_title = " - ".join(title_parts)
            ax_img.set_title(final_title)
            plt.tight_layout(pad=0.1)
        else:
            n_subplots = 1
            if segmentation_canvas is not None:
                n_subplots += 1
            if confidence_canvas is not None:
                n_subplots += 1
            if legend_canvas is not None:
                n_subplots += 1

            height_ratios = [3]
            if segmentation_canvas is not None:
                height_ratios.append(1.5)
            if confidence_canvas is not None:
                height_ratios.append(1)
            if legend_canvas is not None:
                height_ratios.append(0.3)

            fig = plt.figure(figsize=figsize, constrained_layout=False)
            gs = fig.add_gridspec(
                n_subplots,
                1,
                height_ratios=height_ratios,
                hspace=0,
                top=0.95,
                bottom=0.05,
            )

            ax_img = fig.add_subplot(gs[0])
            ax_img.imshow(img)
            ax_img.axis("off")

            title_parts = []
            if title:
                title_parts.append(f"{title} - Frame {i + 1}/{n_frames}")
            else:
                title_parts.append(f"Frame {i + 1}/{n_frames}")

            label_parts = []
            if ground_truth is not None:
                gt_label = ground_truth[i]
                if labels is not None and gt_label < len(labels):
                    gt_text = labels[gt_label]
                else:
                    gt_text = str(gt_label)
                label_parts.append(f"GT: {gt_text:<15}")

            if prediction is not None:
                pred_label = prediction[i]
                if labels is not None and pred_label < len(labels):
                    pred_text = labels[pred_label]
                else:
                    pred_text = str(pred_label)
                label_parts.append(f"Pred: {pred_text:<15}")

            if label_parts:
                title_parts.append(" | ".join(label_parts))

            final_title = " - ".join(title_parts)
            ax_img.set_title(final_title, pad=2)

            current_subplot = 1

            if segmentation_canvas is not None:
                ax_seg = fig.add_subplot(gs[current_subplot])
                ax_seg.imshow(segmentation_canvas)
                ax_seg.axis("off")

                current_frame_pos = i / n_frames
                seg_width = segmentation_canvas.shape[1]

                label_width_ratio = 0.039
                data_start_x = label_width_ratio * seg_width
                data_width = seg_width * (1 - label_width_ratio)
                line_x = data_start_x + current_frame_pos * data_width

                ax_seg.axvline(
                    x=line_x, color="black", linestyle="-", linewidth=2, alpha=0.8
                )

                current_subplot += 1

            if confidence_canvas is not None:
                ax_conf = fig.add_subplot(gs[current_subplot])
                ax_conf.imshow(confidence_canvas)
                ax_conf.axis("off")

                current_frame_pos = i / n_frames
                conf_width = confidence_canvas.shape[1]

                label_width_ratio = 0.06
                data_start_x = label_width_ratio * conf_width
                data_width = conf_width * (1 - label_width_ratio)
                line_x = data_start_x + current_frame_pos * data_width

                ax_conf.axvline(
                    x=line_x, color="red", linestyle="-", linewidth=2, alpha=0.8
                )

                current_subplot += 1

            if legend_canvas is not None:
                ax_legend = fig.add_subplot(gs[current_subplot])
                ax_legend.imshow(legend_canvas)
                ax_legend.axis("off")

        fig.canvas.draw()
        canvas = np.array(fig.canvas.buffer_rgba())
        frame = canvas[:, :, :3]
        frames.append(frame)

        plt.close(fig)

    if frames:
        height, width = frames[0].shape[:2]
        with VideoWriter(path, framerate=fps, size=(width, height)) as writer:
            for frame in track(frames, description="Writing video frames"):
                writer.update(frame)
