# Neutrophils Maturation Classifier App

![alt text](./doc/screenshot.png "Screenshot")

A minimal 3D neutrophil maturation classification app with convolution neural network.

## Overview

This application allows for the automated classification of neutrophils at different maturation stages using a 3D convolutional neural network. It's designed to assist researchers and clinicians in analyzing 3D neutrophil morphology with geometric and CNN embedded features.

**Note**: GPU runtime only available on Linux.

## Features

- 3D visualization of neutrophil isosurfaces
- Real-time classification of neutrophil maturation stages
- Support for TIFF image input
- Batch processing capabilities

## Requirements

- Python 3.9 or higher
- CUDA-compatible GPU (recommended for GPU acceleration)

## Installation

### Simple Installation (Recommended)
```bash
pip install neutrophils-classifier
```

### Run the App
```bash
neutrophil-classifier
```

## For Developers

### Development Setup
1. Set up the conda environment:
```bash
git clone git@github.com:bpi-oxford/Neutrophils-Classifier-App.git
cd Neutrophils-Classifier-App
git submodule update --init --recursive
mamba env create -f env-minimal.yaml
mamba activate neutrophils-minimal
```

2. Install in editable mode:
```bash
pip install -e .
```

3. Run the application:
```bash
neutrophil-classifier
```

### Building and Publishing

See [`BUILD_GUIDE.md`](BUILD_GUIDE.md) for detailed build and publish instructions.