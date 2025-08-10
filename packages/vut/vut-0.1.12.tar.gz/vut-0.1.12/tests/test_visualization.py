import os
import tempfile

import numpy as np
import pytest
from pytest_mock import MockerFixture

from vut.visualization import (
    make_video,
    plot_action_segmentation,
    plot_feature,
    plot_features,
    plot_image,
    plot_images,
    plot_metrics,
    plot_palette,
    plot_roc_curve,
    plot_scatter,
)


@pytest.fixture
def img():
    return np.ceil(np.random.rand(100, 100, 3) * 255).astype(np.uint8)


@pytest.fixture
def mock_ffmpeg(mocker: MockerFixture):
    """Mock ffmpeg to avoid dependency on ffmpeg installation"""
    mock_stdin = mocker.Mock()
    mock_stdin.write = mocker.Mock()
    mock_stdin.close = mocker.Mock()

    mock_process = mocker.Mock()
    mock_process.stdin = mock_stdin
    mock_process.wait = mocker.Mock()

    mock_stream = mocker.Mock()
    mock_stream.output = mocker.Mock(return_value=mock_stream)
    mock_stream.overwrite_output = mocker.Mock(return_value=mock_stream)
    mock_stream.run_async = mocker.Mock(return_value=mock_process)

    mocker.patch("ffmpeg.input", return_value=mock_stream)

    return {
        "stdin": mock_stdin,
        "process": mock_process,
        "stream": mock_stream,
    }


def test_plot_palette__save_as_file(mocker: MockerFixture):
    mocker.patch("matplotlib.pyplot.get_cmap", return_value="viridis")
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp_file:
        path = tmp_file.name
    plot_palette(name="viridis", path=path)
    assert os.path.exists(path)
    os.remove(path)


def test_plot_palette__with_palette():
    palette = np.random.rand(10, 3)
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp_file:
        path = tmp_file.name
    plot_palette(palette=palette, path=path)
    assert os.path.exists(path)
    os.remove(path)


def test_plot_image__save_as_file(img):
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp_file:
        path = tmp_file.name
    plot_image(img, path=path)
    assert os.path.exists(path)
    os.remove(path)


def test_plot_image__show_in_jupyter(img, mocker: MockerFixture):
    mock = mocker.patch("matplotlib.pyplot.show")
    plot_image(img, is_jupyter=True)
    mock.assert_called_once()


def test_plot_image__return_canvas(img):
    canvas = plot_image(img, return_canvas=True)
    assert canvas.shape == (600, 800, 3)


def test_plot_images__save_as_file(img):
    images = [img, img]
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp_file:
        path1 = tmp_file.name
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp_file:
        path2 = tmp_file.name
    plot_images(images, paths=[path1, path2])
    assert os.path.exists(path1)
    assert os.path.exists(path2)
    os.remove(path1)
    os.remove(path2)


def test_plot_images__show_in_jupyter(img, mocker: MockerFixture):
    images = [img, img]
    mock = mocker.patch("matplotlib.pyplot.show")
    plot_images(images, is_jupyter=True)
    mock.assert_called_once()


def test_plot_images__return_canvas(img):
    images = [img, img]
    canvas = plot_images(images, return_canvas=True)
    assert len(canvas) == 2


def test_plot_feature__save_as_file():
    feature = np.random.rand(10, 10)
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp_file:
        path = tmp_file.name
    plot_feature(feature, path=path)
    assert os.path.exists(path)
    os.remove(path)


def test_plot_feature__show_in_jupyter(mocker: MockerFixture):
    feature = np.random.rand(10, 10)
    mock = mocker.patch("matplotlib.pyplot.show")
    plot_feature(feature, is_jupyter=True)
    mock.assert_called_once()


def test_plot_feature__return_canvas():
    feature = np.random.rand(10, 10)
    canvas = plot_feature(feature, return_canvas=True)
    assert canvas.shape == (600, 800, 3)


def test_plot_features__save_as_file():
    features = [np.random.rand(10, 10), np.random.rand(10, 10)]
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp_file:
        path1 = tmp_file.name
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp_file:
        path2 = tmp_file.name
    plot_features(features, paths=[path1, path2])
    assert os.path.exists(path1)
    assert os.path.exists(path2)
    os.remove(path1)
    os.remove(path2)


def test_plot_features__show_in_jupyter(mocker: MockerFixture):
    features = [np.random.rand(10, 10), np.random.rand(10, 10)]
    mock = mocker.patch("matplotlib.pyplot.show")
    plot_features(features, is_jupyter=True)
    mock.assert_called_once()


def test_plot_features__return_canvas():
    features = [np.random.rand(10, 10), np.random.rand(10, 10)]
    canvas = plot_features(features, return_canvas=True)
    assert len(canvas) == 2


def test_plot_scatter__save_as_file():
    tsne_result = np.random.rand(20, 2) * 10
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp_file:
        path = tmp_file.name
    plot_scatter(tsne_result, path=path)
    assert os.path.exists(path)
    os.remove(path)


def test_plot_scatter__with_labels():
    tsne_result = np.random.rand(20, 2) * 10
    labels = [0, 1, 0, 1] * 5
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp_file:
        path = tmp_file.name
    plot_scatter(tsne_result, labels=labels, path=path)
    assert os.path.exists(path)
    os.remove(path)


def test_plot_scatter__show_in_jupyter(mocker: MockerFixture):
    tsne_result = np.random.rand(20, 2) * 10
    mock = mocker.patch("matplotlib.pyplot.show")
    plot_scatter(tsne_result, is_jupyter=True)
    mock.assert_called_once()


def test_plot_scatter__return_canvas():
    tsne_result = np.random.rand(20, 2) * 10
    canvas = plot_scatter(tsne_result, return_canvas=True)
    assert canvas.shape == (800, 1000, 3)


def test_plot_metrics__save_as_file():
    metrics = {
        "train_loss": [1.0, 0.8, 0.6, 0.4, 0.2],
        "val_loss": [1.2, 0.9, 0.7, 0.5, 0.3],
        "accuracy": [0.5, 0.6, 0.7, 0.8, 0.9],
    }
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp_file:
        path = tmp_file.name
    plot_metrics(metrics, path=path)
    assert os.path.exists(path)
    os.remove(path)


def test_plot_metrics__show_in_jupyter(mocker: MockerFixture):
    metrics = {
        "train_loss": [1.0, 0.8, 0.6, 0.4, 0.2],
        "val_loss": [1.2, 0.9, 0.7, 0.5, 0.3],
    }
    mock = mocker.patch("matplotlib.pyplot.show")
    plot_metrics(metrics, is_jupyter=True)
    mock.assert_called_once()


def test_plot_metrics__return_canvas():
    metrics = {
        "train_loss": [1.0, 0.8, 0.6, 0.4, 0.2],
        "val_loss": [1.2, 0.9, 0.7, 0.5, 0.3],
    }
    canvas = plot_metrics(metrics, return_canvas=True)
    assert canvas.shape == (600, 1000, 3)


def test_plot_metrics__invalid_metric_data():
    metrics = {"invalid_metric": [[1, 2], [3, 4]]}
    with pytest.raises(
        AssertionError,
        match="Metric data for 'invalid_metric' must be 1D array or list",
    ):
        plot_metrics(metrics)


def test_plot_action_segmentation__save_as_file():
    ground_truth = [0, 0, 1, 1, 2, 2, 1, 0]
    prediction = [0, 1, 1, 1, 2, 2, 1, 0]
    confidences = [0.9, 0.7, 0.8, 0.9, 0.95, 0.85, 0.9, 0.88]

    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp_file:
        path = tmp_file.name
    plot_action_segmentation(ground_truth, prediction, confidences, path=path)
    assert os.path.exists(path)
    os.remove(path)


def test_plot_action_segmentation__show_in_jupyter(mocker: MockerFixture):
    ground_truth = [0, 0, 1, 1, 2, 2, 1, 0]
    prediction = [0, 1, 1, 1, 2, 2, 1, 0]
    confidences = [0.9, 0.7, 0.8, 0.9, 0.95, 0.85, 0.9, 0.88]

    mock = mocker.patch("matplotlib.pyplot.show")
    plot_action_segmentation(ground_truth, prediction, confidences, is_jupyter=True)
    mock.assert_called_once()


def test_plot_action_segmentation__return_canvas():
    ground_truth = [0, 0, 1, 1, 2, 2, 1, 0]
    prediction = [0, 1, 1, 1, 2, 2, 1, 0]
    confidences = [0.9, 0.7, 0.8, 0.9, 0.95, 0.85, 0.9, 0.88]

    canvas = plot_action_segmentation(
        ground_truth, prediction, confidences, return_canvas=True
    )
    assert canvas.shape == (800, 1600, 3)


def test_plot_action_segmentation__without_prediction():
    ground_truth = [0, 0, 1, 1, 2, 2, 1, 0]
    confidences = [0.9, 0.7, 0.8, 0.9, 0.95, 0.85, 0.9, 0.88]

    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp_file:
        path = tmp_file.name
    plot_action_segmentation(ground_truth, None, confidences, path=path)
    assert os.path.exists(path)
    os.remove(path)


def test_plot_action_segmentation__without_confidences():
    ground_truth = [0, 0, 1, 1, 2, 2, 1, 0]
    prediction = [0, 1, 1, 1, 2, 2, 1, 0]

    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp_file:
        path = tmp_file.name
    plot_action_segmentation(ground_truth, prediction, None, path=path)
    assert os.path.exists(path)
    os.remove(path)


def test_plot_action_segmentation__ground_truth_only():
    ground_truth = [0, 0, 1, 1, 2, 2, 1, 0]

    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp_file:
        path = tmp_file.name
    plot_action_segmentation(ground_truth, path=path)
    assert os.path.exists(path)
    os.remove(path)


def test_plot_action_segmentation__with_labels():
    ground_truth = [0, 0, 1, 1, 2, 2, 1, 0]
    prediction = [0, 1, 1, 1, 2, 2, 1, 0]
    labels = ["Background", "Action1", "Action2"]

    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp_file:
        path = tmp_file.name
    plot_action_segmentation(ground_truth, prediction, labels=labels, path=path)
    assert os.path.exists(path)
    os.remove(path)


def test_plot_action_segmentation__custom_palette():
    ground_truth = [0, 0, 1, 1, 2, 2, 1, 0]
    prediction = [0, 1, 1, 1, 2, 2, 1, 0]
    palette = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]

    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp_file:
        path = tmp_file.name
    plot_action_segmentation(ground_truth, prediction, palette=palette, path=path)
    assert os.path.exists(path)
    os.remove(path)


def test_plot_action_segmentation__custom_legend_ncol():
    ground_truth = [0, 0, 1, 1, 2, 2, 1, 0]
    prediction = [0, 1, 1, 1, 2, 2, 1, 0]

    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp_file:
        path = tmp_file.name
    plot_action_segmentation(ground_truth, prediction, legend_ncol=3, path=path)
    assert os.path.exists(path)
    os.remove(path)


def test_plot_action_segmentation__invalid_ground_truth_dimension():
    ground_truth = [[0, 1], [2, 3]]
    prediction = [0, 1, 2, 3]

    with pytest.raises(AssertionError, match="Ground truth must be a 1D array"):
        plot_action_segmentation(ground_truth, prediction)


def test_plot_action_segmentation__invalid_prediction_dimension():
    ground_truth = [0, 1, 2, 3]
    prediction = [[0, 1], [2, 3]]

    with pytest.raises(AssertionError, match="Prediction must be a 1D array"):
        plot_action_segmentation(ground_truth, prediction)


def test_plot_action_segmentation__length_mismatch():
    ground_truth = [0, 1, 2]
    prediction = [0, 1, 2, 3]

    with pytest.raises(
        AssertionError, match="Ground truth and prediction must have the same length"
    ):
        plot_action_segmentation(ground_truth, prediction)


def test_plot_action_segmentation__confidences_length_mismatch_with_prediction():
    ground_truth = [0, 1, 2, 3]
    prediction = [0, 1, 2, 3]
    confidences = [0.1, 0.2, 0.3]

    with pytest.raises(
        AssertionError, match="Confidences and prediction must have the same length"
    ):
        plot_action_segmentation(ground_truth, prediction, confidences)


def test_plot_roc_curve__save_as_file():
    ground_truth = [0, 0, 1, 1]
    prediction = [0.1, 0.4, 0.35, 0.8]
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp_file:
        path = tmp_file.name
    plot_roc_curve(ground_truth, prediction, path=path)
    assert os.path.exists(path)
    os.remove(path)


def test_plot_roc_curve__show_in_jupyter(mocker: MockerFixture):
    ground_truth = [0, 0, 1, 1]
    prediction = [0.1, 0.4, 0.35, 0.8]
    mock = mocker.patch("matplotlib.pyplot.show")
    plot_roc_curve(ground_truth, prediction, is_jupyter=True)
    mock.assert_called_once()


def test_plot_roc_curve__return_canvas():
    ground_truth = [0, 0, 1, 1]
    prediction = [0.1, 0.4, 0.35, 0.8]
    canvas = plot_roc_curve(ground_truth, prediction, return_canvas=True)
    assert canvas.shape == (600, 800, 3)


def test_plot_roc_curve__ground_truth_not_1d():
    ground_truth = [[0, 1], [1, 0]]
    prediction = [0.1, 0.8]

    with pytest.raises(AssertionError, match="Ground truth must be a 1D array"):
        plot_roc_curve(ground_truth, prediction)


def test_plot_roc_curve__prediction_not_1d():
    ground_truth = [0, 1]
    prediction = [[0.1, 0.2], [0.8, 0.9]]

    with pytest.raises(AssertionError, match="Prediction must be a 1D array"):
        plot_roc_curve(ground_truth, prediction)


def test_plot_roc_curve__length_mismatch():
    ground_truth = [0, 1, 1]
    prediction = [0.1, 0.8]

    with pytest.raises(
        AssertionError, match="Ground truth and prediction must have the same length"
    ):
        plot_roc_curve(ground_truth, prediction)


def test_plot_roc_curve__invalid_ground_truth_labels():
    ground_truth = [0, 1, 2]
    prediction = [0.1, 0.4, 0.8]

    with pytest.raises(AssertionError, match="Ground truth must contain only 0 and 1"):
        plot_roc_curve(ground_truth, prediction)


def test_make_video__with_image_paths(mock_ffmpeg):
    image_paths = []
    temp_files = []

    for i in range(3):
        img = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)

        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as temp_file:
            import cv2

            cv2.imwrite(temp_file.name, img)
            image_paths.append(temp_file.name)
            temp_files.append(temp_file.name)

    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as video_file:
        video_path = video_file.name

    try:
        make_video(image_paths=image_paths, path=video_path)

        assert mock_ffmpeg["stream"].output.called
        assert mock_ffmpeg["stream"].overwrite_output.called
        assert mock_ffmpeg["stream"].run_async.called
        assert mock_ffmpeg["stdin"].write.called

    finally:
        for temp_file in temp_files:
            if os.path.exists(temp_file):
                os.remove(temp_file)
        if os.path.exists(video_path):
            os.remove(video_path)


def test_make_video__with_labels_and_data(mock_ffmpeg):
    image_paths = []
    temp_files = []

    for i in range(5):
        img = np.random.randint(0, 256, (120, 120, 3), dtype=np.uint8)

        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as temp_file:
            import cv2

            cv2.imwrite(temp_file.name, img)
            image_paths.append(temp_file.name)
            temp_files.append(temp_file.name)

    ground_truth = [0, 1, 2, 1, 0]
    prediction = [0, 1, 1, 2, 0]
    confidences = [0.9, 0.8, 0.7, 0.6, 0.95]
    labels = ["Background", "Action1", "Action2"]

    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as video_file:
        video_path = video_file.name

    try:
        make_video(
            image_paths=image_paths,
            ground_truth=ground_truth,
            prediction=prediction,
            confidences=confidences,
            labels=labels,
            path=video_path,
            title="Test Video",
            fps=2,
            figsize=(8, 6),
            legend_ncol=3,
        )

        assert mock_ffmpeg["stream"].output.called
        assert mock_ffmpeg["stream"].overwrite_output.called
        assert mock_ffmpeg["stream"].run_async.called
        assert mock_ffmpeg["stdin"].write.called

    finally:
        for temp_file in temp_files:
            if os.path.exists(temp_file):
                os.remove(temp_file)
        if os.path.exists(video_path):
            os.remove(video_path)


def test_make_video__no_segmentation_data(mock_ffmpeg):
    image_paths = []
    temp_files = []

    for i in range(2):
        img = np.random.randint(0, 256, (80, 80, 3), dtype=np.uint8)

        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as temp_file:
            import cv2

            cv2.imwrite(temp_file.name, img)
            image_paths.append(temp_file.name)
            temp_files.append(temp_file.name)

    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as video_file:
        video_path = video_file.name

    try:
        make_video(
            image_paths=image_paths,
            path=video_path,
            show_segmentation=False,
            show_confidence=False,
            fps=1,
        )

        assert mock_ffmpeg["stream"].output.called
        assert mock_ffmpeg["stream"].overwrite_output.called
        assert mock_ffmpeg["stream"].run_async.called
        assert mock_ffmpeg["stdin"].write.called

    finally:
        for temp_file in temp_files:
            if os.path.exists(temp_file):
                os.remove(temp_file)
        if os.path.exists(video_path):
            os.remove(video_path)


def test_make_video__invalid_inputs():
    with pytest.raises(
        AssertionError, match="Either image_dir or image_paths must be provided"
    ):
        make_video()

    with pytest.raises(AssertionError, match="No images found"):
        make_video(image_paths=[])

    image_paths = []
    temp_files = []

    try:
        img = np.random.randint(0, 256, (50, 50, 3), dtype=np.uint8)
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as temp_file:
            import cv2

            cv2.imwrite(temp_file.name, img)
            image_paths.append(temp_file.name)
            temp_files.append(temp_file.name)

        ground_truth = [0, 1]

        with pytest.raises(
            AssertionError, match="Ground truth length must match number of images"
        ):
            make_video(image_paths=image_paths, ground_truth=ground_truth)

    finally:
        for temp_file in temp_files:
            if os.path.exists(temp_file):
                os.remove(temp_file)
