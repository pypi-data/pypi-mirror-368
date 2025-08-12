# MiniCNN

**MiniCNN** is a minimal, well-documented Python package with beginner-friendly 
**Convolutional Neural Network (CNN)** models using PyTorch.  
Great for **learning**, **tutorials**, and **fast prototyping**.

## Installation

pip install MiniCNN


## Usage

import torch

from MiniCNN import SimpleCNN, TinyCNN

Example: Create a SimpleCNN model for MNIST (10 classes)

model = SimpleCNN(num_classes=10) print(model)

Random input (batch=1, channel=1, size=28x28)

x = torch.randn(1, 1, 28, 28) y = model(x) print(y.shape)  # torch.Size()


## Features
- **SimpleCNN**: Standard small CNN, 2 conv layers + 2 FC layers.
- **TinyCNN**: Extremely small model for quick tests.


## Requirements
- Python 3.8+
- PyTorch >= 2.0.0


## License
MIT License
