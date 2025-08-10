<h1 align="center">Video Understanding Toolkit</h1>

<p align="center">
  <a href="https://github.com/kage1020/vut">
    <img src="https://img.shields.io/github/stars/kage1020/vut" alt="Stars" />
  </a>
  <a href="https://github.com/kage1020/vut/blob/main/LICENSE">
    <img src="https://img.shields.io/github/license/kage1020/vut" alt="License" />
  </a>
  <a href="https://pypi.org/project/vut/">
    <img src="https://img.shields.io/pypi/v/vut" alt="Latest Release" />
  </a>
  <a href="https://codecov.io/gh/kage1020/vut" >
   <img src="https://codecov.io/gh/kage1020/vut/graph/badge.svg?token=XWNCMG995B"/>
  </a>
  <a href="https://deepwiki.com/kage1020/vut">
    <img src="https://deepwiki.com/badge.svg" alt="Ask DeepWiki">
  </a>
</p>


This repository provides a collection of tools and utilities for video understanding tasks, including video classification, action recognition, and more. The toolkit is designed to be modular and extensible, allowing researchers and developers to easily integrate new models and datasets.

## Features

TODO: Implement the features and tools in the toolkit.

## Installation

You can install the toolkit using pip:

```bash
pip install vut
```

By default, **no dependencies** are installed. This is suitable for code snippet usage or minimal environments.

If you want to use all features with all dependencies, install with:

```bash
pip install vut[full]
```

This will install all dependencies required for full functionality.

## Usage

TODO: Provide usage examples and documentation for the various features and tools in the toolkit.

## Tools & Utilities

In addition to the main toolkit, we provide some useful tools and utilities:

### Matplotlib Colormap Visualization
We've created an interactive web application for visualizing matplotlib colormaps. This tool helps you explore and choose the right colormap for your data visualization needs.

🌈 **Visit the site**: [matplotlib-colormap.streamlit.app](https://matplotlib-colormap.streamlit.app/)

This visualization tool provides:
- Interactive preview of all matplotlib colormaps
- Easy comparison between different colormaps
- Information about colormap properties and use cases
- Export capabilities for your selected colormaps

## Development

This toolkit requires package management tool [uv](https://docs.astral.sh/uv). You first need to install it:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.local/bin/env
```

Then, you can install the toolkit using the following command:

```bash
git clone https://github.com/kage1020/vut.git
cd vut
uv venv
source .venv/bin/activate
uv sync --all
```

`uv sync --all` command will install all the optional dependencies specified in the `pyproject.toml` file, including those for full functionality like PyTorch, NumPy, OpenCV, and more.

This will install all the required dependencies and set up the development environment.

## License

The core functionality of this toolkit is licensed under the [MIT License](LICENSE).

However, the models included in the `vut/models` directory may be subject to different licenses:

- Each model implementation in the `vut/models` directory includes its own licensing information.
- Please refer to the [models README](vut/models/README.md) for specific license details of each model.

When using this toolkit, especially when incorporating the provided models, please make sure to comply with the respective licenses.

## Contributing

We welcome contributions to the toolkit!
