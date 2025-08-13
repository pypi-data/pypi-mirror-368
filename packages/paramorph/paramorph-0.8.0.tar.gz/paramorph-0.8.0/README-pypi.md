# Paramorph Client Library

Paramorph is a client library that provides automated hyperparameter tuning for neural network training. It integrates seamlessly with Hugging Face Transformers and other PyTorch-based training frameworks to dynamically adjust learning rates, weight decay, and other hyperparameters during training.

## Features

- **Automated Hyperparameter Tuning**: Dynamically adjusts learning rates, weight decay, and other optimizer parameters
- **Hugging Face Integration**: Built-in support for Hugging Face Transformers with minimal code changes
- **Multi-Agent Architecture**: Uses specialized agents for different parameter groups (embeddings, attention, linear layers, convolutions)
- **Real-time Monitoring**: Integrates with Weights & Biases for experiment tracking
- **Flexible Configuration**: Easy-to-use YAML configuration system

## Installation

### Prerequisites

- Python 3.10+
- PyTorch
- Hugging Face Transformers (for HF integration)
- [Optional] Weights & Biases account and API key (for experiment tracking and logging)

### Setup

Paramorph depends on the `libinephany` package, which provides core utilities and data models. Installation instructions differ based on your use case:

Ensure that python3.12 and make is installed:

#### Ubuntu / Debian
```commandline
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install python3.12
```

#### MacOS with brew
```commandline
brew install python@3.12
```

#### For Developers (Monorepo)
If you're working within the Inephany monorepo, the `libinephany` package is already available and will be installed into the venv created for this package when you run `make install-dev`.

#### For Clients (Standalone Installation)
Both `libinephany` and `paramorph` are available on PyPI and can be installed directly:

# Optional but recommended
```bash
python -m pip install --upgrade pip
```

# Install paramorph (libinephany will be installed as a depencency)
```bash
python -m pip install paramorph
```

For development installations with additional dependencies:

```bash
pip install libinephany[dev] paramorph[dev]
```

Then generate an API key in the portal and export it:
```commandline
export PARAMORPH_API_KEY=YOUR_API_KEY
```

### Getting Help

- Check the example scripts in the repository
- Review the configuration file format
- Ensure all dependencies are installed correctly
- Verify your model architecture matches the agent module mapping

## License

This package is licensed under the Apache License, Version 2.0. See the LICENSE file for details.
