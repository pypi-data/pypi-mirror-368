# NCALab

NCALab makes it easy to create Neural Cellular Automata (NCA) implementations for various downstream tasks, such as image segmentation, classification and synthesis.


![docs](https://github.com/MECLabTUDA/NCAlab/actions/workflows/docs.yml/badge.svg)
![python-package](https://github.com/MECLabTUDA/NCAlab/actions/workflows/python-package.yml/badge.svg)
![manuscript](https://github.com/MECLabTUDA/NCAlab/actions/workflows/draft-pdf.yml/badge.svg)

![NCALab Logo](artwork/ncalab_logo.png)


## Features

Features of NCALab include:
  * Easy training and evaluation of NCA models
  * Cascaded multi-scale training
  * Tensorboard integration with default presets
  * Training with k-fold cross-validation
  * Convenience features: Fixing random seeds, selecting compute devices, data processing


## Getting started

Perhaps the best way of getting started with NCALab is to take a look at the provided usage example tasks, starting with the Growing Emoji task.

### Usage Example Tasks

So far, the following example tasks are implemented in NCALab:

  * Image Generation:
    * Growing NCA for emoji generation
      * Training and evaluation
      * Fine-tuning of a pre-trained emoji generator
      * Hyperparameter search
  * Image Classification:
    * Self-classifying MNIST digits
    * MedMNIST image classification (PathMNIST, BloodMNIST, DermaMNIST)
  * Image Segmentation:
    * Endoscopic polyp segmentation (Kvasir-SEG, public)


You can find those example tasks inside the `tasks/` directory and its subfolders.


### Growing Lizard Example

A good starting point to get started with NCAs is the famous Growing Lizard emoji example.


```bash
uv run tasks/growing_emoji/train_growing_emoji.py
```


Run this script to generate a GIF of the trained model's prediction:

```bash
uv run tasks/growing_emoji/eval_growing_emoji.py
```

![Animation of a growing lizard emoji](artwork/growing_emoji.gif)


### Installation

Run

```bash
pip install ncalab
```

to install the latest release or

```bash
pip install git+https://github.com/MECLabTUDA/NCALab
```

for the most recent commit of NCALab.
We recommend to install NCALab in a virtual environment.


## Tensorboard integration

We recommend you to monitor your training progress in Tensorboard.
To launch tensorboard, run

```bash
uv run tensorboard --logdir=runs
```

in a separate terminal.
Once it is running, it should show you the URL the tensorboard server is running on, which is [localhost:6006](https://localhost:6006) by default.
Alternatively, you may use the tensorboard integration of your IDE.


# For Developers

Type checking:

```bash
uv run mypy ncalab
```

Static code analysis:

```bash
uv run ruff check ncalab
```

Testing:

```bash
uv run pytest
```


# How to Cite

Coming soon.
