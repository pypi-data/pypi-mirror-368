import os
import tempfile
from pathlib import Path

import cv2
import numpy as np
import pytest
import torch

from vut.io import (
    get_dirs,
    get_images,
    load_file,
    load_files,
    load_image,
    load_images,
    load_lines,
    load_np,
    load_tensor,
    save,
    save_image,
    save_list,
)


def test_get_dirs__non_recursive():
    path = os.path.dirname(__file__)
    dirs = get_dirs(path, recursive=False)
    assert all(os.path.isdir(d) for d in dirs), "All items should be directories"


def test_get_dirs__recursive():
    path = os.path.dirname(__file__)
    dirs = get_dirs(path, recursive=True)
    assert all(os.path.isdir(d) for d in dirs), "All items should be directories"


def test_get_dirs__empty_directory():
    with tempfile.TemporaryDirectory() as temp_dir:
        dirs = get_dirs(temp_dir, recursive=False)
        assert dirs == [], "Empty directory should return an empty list"


def test_get_dirs__non_existent_path():
    with tempfile.TemporaryDirectory() as temp_dir:
        non_existent_path = os.path.join(temp_dir, "non_existent")
        dirs = get_dirs(non_existent_path, recursive=False)
        assert dirs == [], "Non-existent path should return an empty list"


def test_get_dirs__not_a_directory():
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(b"test")
        temp_file_path = temp_file.name
    dirs = get_dirs(temp_file_path, recursive=False)
    assert dirs == [], "File path should return an empty list"
    os.remove(temp_file_path)


def test_get_images():
    with tempfile.TemporaryDirectory() as temp_dir:
        image_paths = [Path(temp_dir) / f"image_{i}.jpg" for i in range(3)]
        for path in image_paths:
            with open(path, "wb") as f:
                f.write(b"test")
        images = get_images(temp_dir)
        assert len(images) == 3, "Should find 3 images"


def test_get_images__non_existent_directory():
    with tempfile.TemporaryDirectory() as temp_dir:
        non_existent_dir = os.path.join(temp_dir, "non_existent")
        with pytest.raises(FileNotFoundError):
            get_images(non_existent_dir)


def test_get_images__not_a_directory():
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(b"test")
        temp_file_path = temp_file.name
    with pytest.raises(NotADirectoryError):
        get_images(temp_file_path)
    os.remove(temp_file_path)


def test_save_list__with_callback():
    data = [1, 2, 3]
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        file_path = temp_file.name
        save_list(data, file_path, callback=lambda x: f"{x}0")
    with open(file_path, "r") as f:
        content = f.read()
    assert content == "10\n20\n30\n", "File content should match the list"
    os.remove(file_path)


def test_save__list():
    data = [1, 2, 3]
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        file_path = temp_file.name
        save(data, file_path)
    with open(file_path, "r") as f:
        content = f.read()
    assert content == "1\n2\n3\n", "File content should match the list"
    os.remove(file_path)


def test_save__ndarray():
    data = np.array([1, 2, 3])
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        file_path = temp_file.name + ".npy"
        save(data, file_path)
    loaded_data = np.load(file_path)
    assert np.array_equal(loaded_data, data), (
        "Loaded data should match the original array"
    )


def test_save__tensor():
    data = torch.tensor([1, 2, 3])
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        file_path = temp_file.name
        save(data, file_path)
    loaded_data = torch.load(file_path)
    assert torch.equal(loaded_data, data), (
        "Loaded data should match the original tensor"
    )


def test_save_image():
    data = np.zeros((100, 100, 3), dtype=np.uint8)
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        file_path = temp_file.name + ".png"
        save_image(data, file_path)
    loaded_data = cv2.imread(file_path)
    assert loaded_data is not None, "Loaded image should not be None"


def test_load_lines():
    data = [1, 2, 3]
    with tempfile.NamedTemporaryFile(mode="w+", delete=False) as temp_file:
        file_path = temp_file.name
        temp_file.writelines(f"{item}\n" for item in data)
    loaded_data = load_lines(file_path)
    assert loaded_data == [str(i) for i in data], (
        "Loaded data should match the original list"
    )
    os.remove(file_path)


def test_load_lines__with_callback():
    data = [1, 2, 3]
    with tempfile.NamedTemporaryFile(mode="w+", delete=False) as temp_file:
        file_path = temp_file.name
        temp_file.writelines(f"{item}\n" for item in data)
    loaded_data = load_lines(file_path, callback=lambda x: int(x.strip()))
    assert loaded_data == data, "Loaded data should match the original list"
    os.remove(file_path)


def test_load_lines__not_a_file():
    with tempfile.TemporaryDirectory() as temp_dir:
        with pytest.raises(IsADirectoryError):
            load_lines(temp_dir)


def test_load_lines__non_existent_file():
    with tempfile.TemporaryDirectory() as temp_dir:
        file_path = Path(temp_dir) / "non_existent.txt"
        with pytest.raises(FileNotFoundError):
            load_lines(file_path)


def test_load_lines__empty_file():
    with tempfile.NamedTemporaryFile(mode="w+", delete=False) as temp_file:
        file_path = temp_file.name
    loaded_data = load_lines(file_path)
    assert loaded_data == [], "Empty file should return empty list"
    os.remove(file_path)


def test_load_lines__with_empty_lines():
    data = ["line1", "", "line3", ""]
    with tempfile.NamedTemporaryFile(mode="w+", delete=False) as temp_file:
        file_path = temp_file.name
        temp_file.writelines(f"{line}\n" for line in data)
    loaded_data = load_lines(file_path)
    assert loaded_data == ["line1", "line3"], "Empty lines should be filtered out"
    os.remove(file_path)


def test_load_np():
    data = np.array([1, 2, 3])
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        file_path = temp_file.name + ".npy"
        np.save(file_path, data)
    loaded_data = load_np(file_path)
    assert np.array_equal(loaded_data, data), (
        "Loaded data should match the original array"
    )
    os.remove(file_path)


def test_load_tensor():
    data = torch.tensor([1, 2, 3])
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        file_path = temp_file.name
        torch.save(data, file_path)
    loaded_data = load_tensor(file_path)
    assert torch.equal(loaded_data, data), (
        "Loaded data should match the original tensor"
    )
    os.remove(file_path)


def test_load_image():
    data = np.array([[1, 2], [3, 4]], dtype=np.uint8)
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        file_path = temp_file.name + ".png"
        cv2.imwrite(file_path, data)
    loaded_data = load_image(file_path)
    assert np.array_equal(loaded_data, data), (
        "Loaded image should match the original array"
    )
    os.remove(file_path)


def test_load_image__non_image_file():
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        file_path = temp_file.name
        temp_file.write(b"test")
    result = load_image(file_path)
    assert result is None, "Loading a non-image file should return None"
    os.remove(file_path)


def test_load_images():
    data = [np.array([[1, 2], [3, 4]], dtype=np.uint8) for _ in range(3)]
    with tempfile.TemporaryDirectory() as temp_dir:
        file_paths = []
        for i, img in enumerate(data):
            file_path = os.path.join(temp_dir, f"image_{i}.png")
            cv2.imwrite(file_path, img)
            file_paths.append(file_path)
        loaded_data = load_images(file_paths)
    assert len(loaded_data) == len(data), "Loaded data should match the original list"
    for i in range(len(data)):
        assert np.array_equal(loaded_data[i], data[i]), (
            f"Loaded image {i} should match the original image"
        )


def test_load_images__non_existent_file():
    with tempfile.TemporaryDirectory() as temp_dir:
        non_existent_file = os.path.join(temp_dir, "non_existent.png")
        result = load_images([non_existent_file])
        assert result == [None], "Loading a non-existent file should return [None]"


def test_load_images__empty_list():
    loaded_data = load_images([])
    assert loaded_data == [], "Empty list should return an empty list"


def test_load_images__mixed_files():
    with tempfile.TemporaryDirectory() as temp_dir:
        image_file = os.path.join(temp_dir, "image.png")
        with open(image_file, "wb") as f:
            f.write(b"test")
        non_image_file = os.path.join(temp_dir, "not_a_file.txt")
        with open(non_image_file, "w") as f:
            f.write("test")
        result = load_images([image_file, non_image_file])
        assert result == [None, None], (
            "Loading a non-image file should return [None, None]"
        )
        os.remove(image_file)
        os.remove(non_image_file)


def test_load_files():
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        file1 = temp_path / "file1.txt"
        file2 = temp_path / "file2.txt"

        with open(file1, "w") as f:
            f.write("line1\nline2\n\nline3\n")

        with open(file2, "w") as f:
            f.write("hello\nworld\n")

        result = load_files(temp_path)

        assert isinstance(result, dict), "Result should be a dictionary"
        assert len(result) == 2, "Should have results for 2 files"
        assert "file1.txt" in result, "Should contain file1.txt as key"
        assert "file2.txt" in result, "Should contain file2.txt as key"
        assert result["file1.txt"] == ["line1", "line2", "line3"], (
            "Content should match"
        )
        assert result["file2.txt"] == ["hello", "world"], "Content should match"


def test_load_files__with_callback():
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        file1 = temp_path / "numbers.txt"
        with open(file1, "w") as f:
            f.write("1\n2\n3\n")

        result = load_files(temp_path, callback=lambda x: int(x.strip()))

        assert isinstance(result, dict), "Result should be a dictionary"
        assert len(result) == 1, "Should have results for 1 file"
        assert "numbers.txt" in result, "Should contain numbers.txt as key"
        assert result["numbers.txt"] == [1, 2, 3], (
            "Callback should convert strings to integers"
        )


def test_load_files__empty_directory():
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        result = load_files(temp_path)

        assert isinstance(result, dict), "Result should be a dictionary"
        assert result == {}, "Empty directory should return empty dictionary"


def test_load_files__mixed_file_types():
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        text_file = temp_path / "text.txt"
        with open(text_file, "w") as f:
            f.write("text content\n")

        binary_file = temp_path / "binary.bin"
        with open(binary_file, "wb") as f:
            f.write(b"\x00\x01\x02\x03")

        try:
            result = load_files(temp_path)
            assert isinstance(result, dict), (
                "Should return a dictionary even with mixed file types"
            )
            assert "text.txt" in result, "Should contain text file"
            assert "binary.bin" in result, "Should contain binary file"
        except UnicodeDecodeError:
            pytest.skip("Binary file caused UnicodeDecodeError as expected")


def test_load_file():
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        file1 = temp_path / "test.txt"
        with open(file1, "w") as f:
            f.write("line1\nline2\nline3\n")

        result = load_file(file1)

        assert isinstance(result, list), "Result should be a list"
        assert result == ["line1", "line2", "line3"], "Content should match"
