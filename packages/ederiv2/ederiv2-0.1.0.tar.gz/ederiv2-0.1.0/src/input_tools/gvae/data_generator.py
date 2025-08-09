import os
import logging
import pandas as pd
import torch
from torch.utils.data import Dataset
from rdkit import Chem
from itertools import permutations
import os
import logging
import pandas as pd
from rdkit import Chem
from typing import List, Optional, Tuple, Set
import torch.nn.functional as F

from graph_maker import DGLGraphMaker, GraphMakerAbstract  # Assuming this is your DGLGraphMaker class


class MoleculeGraphDataset(Dataset):
    def __init__(self, graphs, valid_smiles, edge_index):
        self._graphs = graphs
        self._valid_smiles = valid_smiles
        self._edge_index = edge_index
        
    def __len__(self):
        return len(self._graphs)
    
    def __add__(self, other):
        return super().__add__(other)

    def __getitem__(self, idx):
        if isinstance(idx, int):
            return self._graphs[idx], self._valid_smiles[idx], self._edge_index[idx]
        elif isinstance(idx, slice):
            return [
                (self._graphs[i], self._valid_smiles[i], self._edge_index[i])
                for i in range(*idx.indices(len(self)))
            ]
        else:
            raise TypeError("Index must be int or slice.")
        
    def __iadd__(self, other):
        """Appends 'other' to the list in-place (like +=)."""
        if isinstance(other, (list, tuple)):
            self.items.extend(other)
        else:
            self.items.append(other)
        return self  # Must return self for +=

        

class MoleculeDataGenerator:
    def __init__(self, base_path: str, dataset_filenames: List[str], graph_maker:DGLGraphMaker):
        
        self._validate_constructor_args(base_path, dataset_filenames)
        self._base_path = base_path
        self._dataset_filenames = dataset_filenames
        self._graph_maker = graph_maker
        self._valid_atoms: Optional[List[str]] = None

    def _validate_constructor_args(self, base_path: str, filenames: List[str]):
        """Validate all constructor arguments."""
        if not os.path.isdir(base_path):
            raise FileNotFoundError(f"Base path does not exist: {base_path}")
        
        invalid_files = self._find_invalid_extensions(filenames, '.pkl')
        if invalid_files:
            raise ValueError(
                f"Found {len(invalid_files)} files without .pkl extension: {invalid_files}"
            )
            
    @property
    def valid_atoms(self):
        return self._valid_atoms

    @staticmethod
    def _find_invalid_extensions(file_list: List[str], required_ext: str) -> List[str]:
        """Identify files without the required extension."""
        required_ext = required_ext.lower()
        return [
            f for f in file_list 
            if os.path.splitext(f)[1].lower() != required_ext
        ]


    def load_datasets(self) -> pd.DataFrame:
        datasets = []
        for filename in self._dataset_filenames:
            file_path = os.path.join(self._base_path, filename)
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Dataset file not found: {file_path}")
            datasets.append(pd.read_pickle(file_path))
        
        return pd.concat(datasets, ignore_index=True)


    def populate_valid_atoms(self, smiles_list: List[str], add_h:bool=False) -> None:
        """Extract unique atom symbols from SMILES strings.
        
        Args:
            smiles_list: List of SMILES strings to analyze
        """
        valid_atom_numbers=[]
        valid_atom_symbols = []
        for s in smiles_list:
            mol = Chem.MolFromSmiles(s)
            if add_h:
                mol = Chem.AddHs(mol)
            for atom in mol.GetAtoms():
                atomic_num = atom.GetAtomicNum()
                if atomic_num not in valid_atom_numbers:
                    valid_atom_symbols.append(atom.GetSymbol())
                    valid_atom_numbers.append(atomic_num)
                    
        
        logging.info(f"Detected {len(valid_atom_numbers)} valid atoms")
        logging.info(f"List of valid Atoms: {valid_atom_symbols}")
        logging.info(f"List of valid Atomic Number: {valid_atom_numbers}")
        
        self._valid_atoms = valid_atom_symbols
        return self._valid_atoms


    def _one_hot_encode_node_features(self, features):
        atom_to_idx = {atom: idx for idx, atom in enumerate(self._valid_atoms)}
        indices = [atom_to_idx.get(int(f.item()), 0) for f in features]
        return F.one_hot(torch.tensor(indices), num_classes=len(self._valid_atoms)).float()


    def _one_hot_encode_edge_features(self, features):
        features = features.long().squeeze(1)
        one_hot = F.one_hot(features, num_classes=5).float()
        return one_hot


    def _one_hot_encode_edge_exist_feature(self, edge_index, num_nodes):
        # Create all possible edge combinations (including self-edges)
        all_possible_edges = torch.cartesian_prod(torch.arange(num_nodes), 
                                                torch.arange(num_nodes)).T
        
        # Convert existing edges to set for faster lookup
        existing_edges = set(zip(edge_index[0].tolist(), edge_index[1].tolist()))
        
        # Initialize one-hot matrix (all edges non-existent by default)
        one_hot = torch.zeros(num_nodes * num_nodes, 2)
        one_hot[:, 1] = 1  # Default to [0, 1]
        
        # Mark existing edges
        for i, (src, dst) in enumerate(zip(all_possible_edges[0], all_possible_edges[1])):
            if (src.item(), dst.item()) in existing_edges:
                one_hot[i] = torch.tensor([1, 0])
        
        return one_hot


    def generate(self, max_samples: Optional[int] = None) -> 'MoleculeGraphDataset':
        """Generate molecule graph dataset from SMILES strings or loaded data.
        
        Args:
            max_samples: Maximum number of samples to include
            
        Returns:
            Initialized MoleculeGraphDataset instance
        """
        df = self.load_datasets()
        
        smiles_list = df['fragments'].tolist()
        
        # Populate valid atoms
        if not self._valid_atoms:
            self.populate_valid_atoms(smiles_list, add_h=False)
            
        # Reset atom_types
        self._graph_maker.set_atom_types(self._valid_atoms)
        
        # Filter valid SMILES
        valid_smiles = [smi for smi in smiles_list if len(smi) > 1]

        # Filter the smiles if needed
        if max_samples:
            if max_samples > len(valid_smiles):
                print(f"Warning: max_samples ({max_samples}) is larger than available samples ({len(valid_smiles)}). Using all {len(valid_smiles)} samples.")
            valid_smiles = valid_smiles[:min(max_samples, len(valid_smiles))]
            
        # Convert smiles to graphs
        graphs=[]
        edge_index=[]
        for smiles in valid_smiles:
            g = self._graph_maker.create(input_format='smiles', input_data=smiles)
            # Get edge indices as tensors
            src, dst = g.edges()
            
            graphs.append(g)
            edge_index.append(torch.stack([src, dst]) )  # Shape: [2, num_edges]
 

        return MoleculeGraphDataset(graphs, valid_smiles, edge_index)

    @property
    def valid_atoms(self) -> List[str]:
        """Get list of detected valid atoms."""
        if self._valid_atoms is None:
            raise ValueError("Valid atoms not populated - call generate() first")
        return self._valid_atoms


    @property
    def dataset_files(self) -> List[str]:
        """Get list of validated dataset filenames."""
        return self._dataset_filenames


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Instantiate a graph maker
    bond_types=['NONE', 'SINGLE', 'DOUBLE', 'TRIPLE', 'AROMATIC']
    graph_maker=DGLGraphMaker(bond_types=bond_types)
    # Example usage
    # base_path="/home/meisam/GitHub_codes/eDeriv2/assets/datasets/"
    base_path = "/home/magesh/eDeriv/graph_variation/"
    dataset_filenames=["graph_emolfrag_all_dude_data.pkl", "graph_emolfrag_test_pen_data.pkl",
                       "graph_emolfrag_train_non_pen_data.pkl"]
    generator = MoleculeDataGenerator(base_path, dataset_filenames, graph_maker)
    dataset=generator.generate(max_samples=100)
    device='cuda' if torch.cuda.is_available() else 'cpu'
    for input_graph, smi, edge_index in dataset:
        input_graph = input_graph.to(device)
        input_node_feats = input_graph.ndata['x'].float()
        input_edge_feats = input_graph.edata['e'].float()
    
    