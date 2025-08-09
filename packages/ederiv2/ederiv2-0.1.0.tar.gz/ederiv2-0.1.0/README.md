# eDeriv2

A molecular graph generation and analysis toolkit using Graph Neural Networks for drug discovery and molecular design.

## Overview

eDeriv2 is a comprehensive Python package for molecular graph generation, analysis, and machine learning applications in chemistry and drug discovery. It provides state-of-the-art Graph Neural Network (GNN) models for molecular representation learning, graph generation, and molecular property prediction.

## Features

- **Molecular Graph Generation**: Advanced GNN-based models for generating molecular graphs
- **Graph Neural Networks**: Implementation of various GNN architectures (GVAE, GAE, EGATConv)
- **Molecular Analysis**: Tools for molecular property prediction and analysis
- **RDKit Integration**: Seamless integration with RDKit for molecular operations
- **DGL Support**: Built on Deep Graph Library (DGL) for efficient graph operations
- **PyTorch Backend**: Full PyTorch support for deep learning models
- **Visualization**: Built-in visualization tools for molecular graphs and results

## Installation

### From PyPI (Recommended)

```bash
pip install ederiv2
```

### From Source

```bash
# Clone the repository
git clone https://github.com/yourusername/eDeriv2.git
cd eDeriv2

# Install in development mode
pip install -e .
```

### Dependencies

The package requires the following key dependencies:
- Python >= 3.8
- PyTorch >= 1.9.0
- DGL >= 1.0.0
- RDKit >= 2022.9.1
- NumPy >= 1.21.0
- Pandas >= 1.3.0

For a complete list of dependencies, see `requirements.txt`.

## Quick Start

### Basic Usage

```python
import torch
from src.graph_handler import DGLGraphHandler
from src.gvae_models import GVAE

# Initialize a GVAE model
model = GVAE(
    node_feat_dim=13,
    edge_feat_dim=4,
    hidden_dim=64,
    latent_dim=32,
    node_classes=13,
    edge_classes=4
)

# Create a graph handler
handler = DGLGraphHandler()

# Your molecular data processing here
# ...
```

### Molecular Graph Generation

```python
from src.graph_maker import DGLGraphMaker
from rdkit import Chem

# Create a graph maker
graph_maker = DGLGraphMaker()

# Convert SMILES to graph
smiles = "CCO"
mol = Chem.MolFromSmiles(smiles)
graph = graph_maker.create(mol, "rdkit_mol")
```

### Training a Model

```python
from src.nn_tools.trainers import GVAETrainer

# Initialize trainer
trainer = GVAETrainer(model, device='cuda')

# Train the model
trainer.train(train_dataloader, val_dataloader, epochs=100)
```

## Project Structure

```
eDeriv2/
├── src/                          # Main package source
│   ├── chem_handlers/           # Chemical data handling
│   ├── input_tools/             # Input processing tools
│   ├── nn_tools/                # Neural network utilities
│   ├── optm_tools/              # Optimization tools
│   ├── output_tools/            # Output and visualization
│   └── sys_tools/               # System utilities
├── assets/                      # Data assets
├── outputs/                     # Output files
├── training_plots/              # Training visualizations
├── setup.py                     # Package setup
├── pyproject.toml              # Modern Python packaging
├── requirements.txt            # Dependencies
└── README.md                   # This file
```

## Models

### GVAE (Graph Variational Autoencoder)
- **File**: `gvae_v1.py`, `gvae_v2.py`
- **Description**: Graph Variational Autoencoder for molecular graph generation
- **Features**: Encoder-decoder architecture with variational inference

### GAE (Graph Autoencoder)
- **File**: `gae.py`
- **Description**: Graph Autoencoder for graph representation learning
- **Features**: Simple autoencoder architecture for graphs

### EGATConv (Edge-aware Graph Attention)
- **File**: `graph_encoder.py`
- **Description**: Edge-aware Graph Attention Convolution
- **Features**: Attention mechanism for both nodes and edges

## Examples

### Molecular Property Prediction

```python
from src.models import MolecularPropertyPredictor

# Initialize predictor
predictor = MolecularPropertyPredictor(model_path="path/to/model.pth")

# Predict properties
properties = predictor.predict(smiles_list)
```

### Graph Visualization

```python
from src.utils import plot_molecules_and_fragments

# Visualize molecular graphs
plot_molecules_and_fragments(molecules, fragments, output_path="output.png")
```

## Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Development Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/eDeriv2.git
cd eDeriv2

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Citation

If you use eDeriv2 in your research, please cite:

```bibtex
@software{ederiv2,
  title={eDeriv2: A molecular graph generation and analysis toolkit},
  author={eDeriv2 Team},
  year={2024},
  url={https://github.com/yourusername/eDeriv2}
}
```

## Support

- **Documentation**: [https://github.com/yourusername/eDeriv2#readme](https://github.com/yourusername/eDeriv2#readme)
- **Issues**: [https://github.com/yourusername/eDeriv2/issues](https://github.com/yourusername/eDeriv2/issues)
- **Discussions**: [https://github.com/yourusername/eDeriv2/discussions](https://github.com/yourusername/eDeriv2/discussions)

## Acknowledgments

- [RDKit](https://www.rdkit.org/) for molecular informatics
- [DGL](https://www.dgl.ai/) for deep graph library
- [PyTorch](https://pytorch.org/) for deep learning framework