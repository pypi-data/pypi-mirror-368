
from abc import ABC, abstractmethod
import copy
from itertools import permutations
import pandas as pd
from rdkit import Chem
from multiprocessing import Pool, cpu_count
import pickle
import os
from functools import partial
from tqdm import tqdm  # For better progress bars

from src.chem_handlers.smiles_handler import SmilesHandlingStrategyAbstract



class RDKitMolDFSActionGenerator:
    BOND_TYPE_MAP = {
        Chem.rdchem.BondType.SINGLE: 'single',
        Chem.rdchem.BondType.DOUBLE: 'double',
        Chem.rdchem.BondType.TRIPLE: 'triple',
        Chem.rdchem.BondType.AROMATIC: 'aromatic'
    }
    SPECIAL_ACTIONS = {'start': '<START>', 'end': '<END>', 'pad': '<PAD>'}
    
    def __init__(self):
        self.element_counters = {}  # To track counts per element type
        self.atom_ids = {}         # To map atom indices to their identifiers

    def _get_bond_type_str(self, bond):
        return self.BOND_TYPE_MAP.get(bond.GetBondType(), 'unknown')
    
    def _get_atom_identifier(self, atom_idx, atom_sym):
        """Returns atom identifier like C1, O2 based on element-specific counter"""
        if atom_idx in self.atom_ids:
            return self.atom_ids[atom_idx]
            
        if atom_sym not in self.element_counters:
            self.element_counters[atom_sym] = 0
        self.element_counters[atom_sym] += 1
        atom_id = f"{atom_sym}{self.element_counters[atom_sym]}"
        self.atom_ids[atom_idx] = atom_id
        return atom_id
    
    def _format_bond_action(self, bond, atom1_idx, atom2_idx, atom1_sym, atom2_sym, format='short'):
        bond_type = self._get_bond_type_str(bond)
        atom1_id = self._get_atom_identifier(atom1_idx, atom1_sym)
        atom2_id = self._get_atom_identifier(atom2_idx, atom2_sym)
        
        if format == 'long':
            return f"Add {bond_type} bond between {atom1_id} and {atom2_id}"
        return f"add_{bond_type}_bond_{atom1_id}_{atom2_id}"

    def _format_atom_action(self, atom_idx, atom_sym, format='short'):
        atom_id = self._get_atom_identifier(atom_idx, atom_sym)
        if format == 'long':
            return f"Add {atom_id}"
        return f"add_atom_{atom_id}"

    def _reset_counters(self):
        """Reset the element counters and atom IDs before each new traversal"""
        self.element_counters = {}
        self.atom_ids = {}
        
    def _actions_postprocessor(self, actions):
        """
        Reorders actions to ensure atoms are added before bonds involving them.
        Uses class's atom tracking system and BOND_TYPE_MAP.
        """
        processed_actions = []
        pending_bonds = []
        self._reset_counters()  # Clear any previous state

        for action in actions:
            if action in self.SPECIAL_ACTIONS.values():
                processed_actions.append(action)
                continue

            # Atom addition
            if action.startswith('add_atom_'):
                atom_id = action.split('_')[-1]
                element = ''.join(filter(str.isalpha, atom_id))
                num = ''.join(filter(str.isdigit, atom_id))
                
                # Update class's tracking system
                if element not in self.element_counters:
                    self.element_counters[element] = 0
                self.element_counters[element] = max(self.element_counters[element], int(num or 0))
                
                processed_actions.append(action)
                
                # Process pending bonds that might now be valid
                new_pending = []
                for bond in pending_bonds:
                    a1, a2 = self._extract_atoms_from_bond_action(bond)
                    if (a1 in self.atom_ids or a1 == atom_id) and \
                    (a2 in self.atom_ids or a2 == atom_id):
                        processed_actions.append(bond)
                    else:
                        new_pending.append(bond)
                pending_bonds = new_pending

            # Bond creation - now using BOND_TYPE_MAP values
            elif any(action.startswith(f'add_{bt}_bond_') 
                for bt in self.BOND_TYPE_MAP.values()):
                a1, a2 = self._extract_atoms_from_bond_action(action)
                if (a1 in self.atom_ids or any(act.endswith(a1) for act in processed_actions if act.startswith('add_atom_'))) and \
                (a2 in self.atom_ids or any(act.endswith(a2) for act in processed_actions if act.startswith('add_atom_'))):
                    processed_actions.append(action)
                else:
                    pending_bonds.append(action)
            else:
                raise ValueError(f"Unknown action: {action}")

        return processed_actions + pending_bonds
        
    @staticmethod
    def _extract_atoms_from_bond_action(bond_action):
        """Extract atom IDs from a bond action using class's naming convention"""
        parts = bond_action.split('_')
        # Handles both short and long formats:
        # 'add_single_bond_C1_O1' -> ['C1', 'O1']
        # 'Add single bond between C1 and O1' -> ['C1', 'O1']
        if bond_action.startswith('Add'):
            return parts[-3], parts[-1]  # For long format
        return parts[-2], parts[-1]     # For short format

        
    def _actions_postprocessor(self, actions):
        """
        Reorders actions to ensure atoms are added before bonds involving them.
        Uses class's atom tracking system and BOND_TYPE_MAP.
        """
        processed_actions = []
        pending_bonds = []
        self._reset_counters()  # Clear any previous state

        for action in actions:
            if action in self.SPECIAL_ACTIONS.values():
                processed_actions.append(action)
                continue

            # Atom addition
            if action.startswith('add_atom_'):
                atom_id = action.split('_')[-1]
                element = ''.join(filter(str.isalpha, atom_id))
                num = ''.join(filter(str.isdigit, atom_id))
                
                # Update class's tracking system
                if element not in self.element_counters:
                    self.element_counters[element] = 0
                self.element_counters[element] = max(self.element_counters[element], int(num or 0))
                
                processed_actions.append(action)
                
                # Process pending bonds that might now be valid
                new_pending = []
                for bond in pending_bonds:
                    a1, a2 = self._extract_atoms_from_bond_action(bond)
                    if (a1 in self.atom_ids or a1 == atom_id) and \
                    (a2 in self.atom_ids or a2 == atom_id):
                        processed_actions.append(bond)
                    else:
                        new_pending.append(bond)
                pending_bonds = new_pending

            # Bond creation - now using BOND_TYPE_MAP values
            elif any(action.startswith(f'add_{bt}_bond_') 
                for bt in self.BOND_TYPE_MAP.values()):
                a1, a2 = self._extract_atoms_from_bond_action(action)
                if (a1 in self.atom_ids or any(act.endswith(a1) for act in processed_actions if act.startswith('add_atom_'))) and \
                (a2 in self.atom_ids or any(act.endswith(a2) for act in processed_actions if act.startswith('add_atom_'))):
                    processed_actions.append(action)
                else:
                    pending_bonds.append(action)
            else:
                raise ValueError(f"Unknown action: {action}")

        return processed_actions + pending_bonds
        
    @staticmethod
    def _extract_atoms_from_bond_action(bond_action):
        """Extract atom IDs from a bond action using class's naming convention"""
        parts = bond_action.split('_')
        # Handles both short and long formats:
        # 'add_single_bond_C1_O1' -> ['C1', 'O1']
        # 'Add single bond between C1 and O1' -> ['C1', 'O1']
        if bond_action.startswith('Add'):
            return parts[-3], parts[-1]  # For long format
        return parts[-2], parts[-1]     # For short format


    def _dfs_traversal(self, mol, start_atom_idx, visited_atoms, visited_bonds, actions, action_format, include_atoms, include_bonds):
        """Core DFS traversal logic used by public methods"""
        atom = mol.GetAtomWithIdx(start_atom_idx)
        atom_sym = atom.GetSymbol()
        
        # Add atom action if requested (only if not already visited)
        if include_atoms and start_atom_idx not in visited_atoms:
            actions.append(self._format_atom_action(
                start_atom_idx, atom_sym, action_format
            ))
        
        visited_atoms.add(start_atom_idx)
        
        # Always traverse neighbors, regardless of include_bonds flag
        neighbors = []
        for bond in atom.GetBonds():
            nbr = bond.GetOtherAtom(atom)
            nbr_idx = nbr.GetIdx()
            if nbr_idx not in visited_atoms:
                neighbors.append((bond, nbr_idx, nbr.GetSymbol()))
        
        # Process neighbors
        for bond, nbr_idx, nbr_sym in neighbors:
            # Add bond action if requested
            if include_bonds:
                bond_idx = bond.GetIdx()
                if bond_idx not in visited_bonds:
                    actions.append(self._format_bond_action(
                        bond, start_atom_idx, nbr_idx,
                        atom_sym, nbr_sym,
                        action_format
                    ))
                    visited_bonds.add(bond_idx)
            
            # Continue DFS traversal
            self._dfs_traversal(mol, nbr_idx, visited_atoms, visited_bonds, actions, action_format, include_atoms, include_bonds)

    def single_dfs_actions(self, mol, start_atom_idx=0, action_format='short', include_atoms=True, include_bonds=True):
        """
        Single deterministic DFS traversal
        """
        self._reset_counters()  # Reset counters before starting
        actions = []
        actions.append(self.SPECIAL_ACTIONS['start'])
        self._dfs_traversal(mol, start_atom_idx, set(), set(), actions, action_format, include_atoms, include_bonds)
        actions= self._actions_postprocessor(actions)
        actions= self._actions_postprocessor(actions)
        actions.append(self.SPECIAL_ACTIONS['end'])
        return actions

    def all_dfs_actions(self, mol, action_format='short', include_atoms=True, include_bonds=True):
        """
        Generate all possible construction sequences via DFS traversals.
        Uses a transformed molecule where bonds become atoms for exhaustive bond exploration.
        """
        all_sequences = set()

        # ===== Step 1: Precompute Atom IDs (for bond naming) =====
        atom_ids = {}
        element_counters = {}
        for atom in mol.GetAtoms():
            atom_idx = atom.GetIdx()
            atom_sym = atom.GetSymbol()
            if atom_sym not in element_counters:
                element_counters[atom_sym] = 0
            element_counters[atom_sym] += 1
            atom_ids[atom_idx] = f"{atom_sym}{element_counters[atom_sym]}"

        # ===== Step 2: Create Transformed Molecule =====
        new_mol = self._create_bond_transformed_molecule(mol, atom_ids, action_format)

        # ===== Step 3: Perform DFS on the New Molecule =====
        def explore_new_paths(current_atom_idx, visited_atoms, current_actions):
            """
            Recursive DFS on the new molecule (where atoms represent bonds in the original molecule).
            """
            new_atom = new_mol.GetAtomWithIdx(current_atom_idx)
            
            if not new_atom.HasProp("bond_action"):
                raise ValueError(f"Atom {current_atom_idx} is missing the 'bond_action' property.")

            bond_action = new_atom.GetProp("bond_action")
            new_actions = current_actions.copy()
            new_actions.append(bond_action)

            # Mark as visited
            new_visited = visited_atoms.copy()
            new_visited.add(current_atom_idx)

            # Explore neighbors
            has_unvisited = False
            for neighbor in new_atom.GetNeighbors():
                neighbor_idx = neighbor.GetIdx()
                if neighbor_idx not in new_visited:
                    has_unvisited = True
                    explore_new_paths(neighbor_idx, new_visited, new_actions)

            # Base case: no more unvisited neighbors
            if not has_unvisited:
                all_sequences.add(tuple(new_actions))

        # Start DFS from each "atom" (bond) in the new molecule
        for start_atom_idx in range(new_mol.GetNumAtoms()):
            explore_new_paths(
                current_atom_idx=start_atom_idx,
                visited_atoms=set(),
                current_actions=[self.SPECIAL_ACTIONS['start']],
            )

        # ===== Step 4: Post-Processing =====
        # Add END token
        return [list(seq) + [self.SPECIAL_ACTIONS['end']] for seq in all_sequences]

    def _create_bond_transformed_molecule(self, mol, atom_ids, action_format):
        """
        Private method to create a molecule where bonds become atoms.
        
        Parameters:
            mol: Original RDKit molecule
            atom_ids: Dictionary mapping atom indices to their IDs (e.g., {0: 'C1', 1: 'O1'})
            action_format: 'short' or 'long' action format
        
        Returns:
            RDKit molecule where each atom represents a bond from the original molecule
        """
        from rdkit import Chem
        from rdkit.Chem import rdchem

        # Initialize a new molecule
        new_mol = Chem.RWMol()

        # Map original bond indices to new atom indices
        bond_to_atom_idx = {}

        # Add all bonds as atoms in the new molecule
        for bond in mol.GetBonds():
            bond_idx = bond.GetIdx()
            bond_type = self.BOND_TYPE_MAP.get(bond.GetBondType(), 'unknown')
            atom1_idx = bond.GetBeginAtomIdx()
            atom2_idx = bond.GetEndAtomIdx()
            atom1_id = atom_ids[atom1_idx]
            atom2_id = atom_ids[atom2_idx]

            # Create a new "atom" representing the bond
            new_atom = Chem.Atom(0)  # Dummy atom (type doesn't matter)
            new_atom_idx = new_mol.AddAtom(new_atom)
            bond_to_atom_idx[bond_idx] = new_atom_idx

            # Store the bond descriptor as a property
            if action_format == 'long':
                bond_descriptor = f"Add {bond_type} bond between {atom1_id} and {atom2_id}"
            else:
                bond_descriptor = f"add_{bond_type}_bond_{atom1_id}_{atom2_id}"
            new_mol.GetAtomWithIdx(new_atom_idx).SetProp("bond_action", bond_descriptor)

        # Connect atoms in new molecule if their bonds share an atom in original
        for bond1 in mol.GetBonds():
            for bond2 in mol.GetBonds():
                if bond1.GetIdx() >= bond2.GetIdx():
                    continue  # Avoid duplicates

                # Check if bonds share a common atom
                bond1_atoms = {bond1.GetBeginAtomIdx(), bond1.GetEndAtomIdx()}
                bond2_atoms = {bond2.GetBeginAtomIdx(), bond2.GetEndAtomIdx()}
                if bond1_atoms & bond2_atoms:  # Intersection
                    new_mol.AddBond(
                        bond_to_atom_idx[bond1.GetIdx()],
                        bond_to_atom_idx[bond2.GetIdx()],
                        rdchem.BondType.SINGLE,
                    )

        return new_mol


class ActionGeneratorAbstract(ABC):
    @abstractmethod
    def generate(self):
        pass



class SmilesDatasetActionGenerator:
    def __init__(self, rdkit_action_generator: RDKitMolDFSActionGenerator):
        self._rdkit_action_generator = rdkit_action_generator
        self._actions = []
    
    def _process_single_smiles(self, smile, dfs_kwargs, dfs_type, h_flag):
        """Process a single SMILES string (worker function for parallel processing)"""
        mol = Chem.MolFromSmiles(smile)
        if mol is None:
            return None
            
        if h_flag: 
            mol = Chem.AddHs(mol, explicitOnly=True, addCoords=True) # Only consider the explicit Hs
        if h_flag: 
            mol = Chem.AddHs(mol, explicitOnly=True, addCoords=True) # Only consider the explicit Hs
            
        try:
            if dfs_type == 'single':
                return self._rdkit_action_generator.single_dfs_actions(mol, 0, **dfs_kwargs)
            else:
                return self._rdkit_action_generator.all_dfs_actions(mol, **dfs_kwargs)
        except Exception as e:
            print(f"Error processing {smile}: {str(e)}")
            return None

    def generate(self, smiles_dataset: list, dfs_kwargs, dfs_type: str, h_flag: bool = False, 
                 cache_file: str = None, n_jobs: int = -1):
        """
        Generate actions with parallel processing and optional caching.

        Args:
            smiles_dataset: List of SMILES strings to process.
            dfs_kwargs: Arguments for DFS traversal.
            dfs_type: Type of DFS ('single' or 'all').
            h_flag: Whether to include explicit hydrogens.
            cache_file: Path to save/load cached results.
            n_jobs: Number of parallel jobs (-1 for all cores).

        Returns:
            Dictionary containing both actions and corresponding SMILES.
        """
        # Attempt to load cached data if available
        if cache_file and os.path.exists(cache_file):
            print(f"Loading cached data from {cache_file}")
            with open(cache_file, 'rb') as f:
                cached_data = pickle.load(f)
                if self._is_cache_valid(cached_data, smiles_dataset, dfs_kwargs, dfs_type, h_flag):
                    print("Cached data matches the inputs. Using cached results.")
                    self._actions = cached_data.get('actions', [])
                    return cached_data
                print("Cached data does not match the inputs. Regenerating actions.")

        print('Generating actions dataset...')
        n_jobs = self._determine_job_count(n_jobs)
        process_fn = partial(self._process_single_smiles, dfs_kwargs=dfs_kwargs, dfs_type=dfs_type, h_flag=h_flag)

        # Process SMILES in parallel
        with Pool(n_jobs) as pool:
            results = list(tqdm(pool.imap(process_fn, smiles_dataset), total=len(smiles_dataset), desc="Processing SMILES"))

        # Compile results
        result_dict = self._compile_results(smiles_dataset, results, dfs_kwargs, dfs_type, h_flag)
        self._actions = result_dict['actions']

        # Save to cache if requested
        if cache_file:
            self._save_to_cache(cache_file, result_dict)

        return result_dict

    def _is_cache_valid(self, cached_data, smiles_dataset, dfs_kwargs, dfs_type, h_flag):
        """Check if cached data matches the current inputs."""
        return (
            cached_data.get('dfs_kwargs') == dfs_kwargs and
            cached_data.get('dfs_type') == dfs_type and
            cached_data.get('h_flag') == h_flag and
            set(cached_data.get('smiles', [])) == set(smiles_dataset)
        )

    def _determine_job_count(self, n_jobs):
        """Determine the number of jobs to use for parallel processing."""
        return cpu_count() if n_jobs == -1 else min(n_jobs, cpu_count())

    def _compile_results(self, smiles_dataset, results, dfs_kwargs, dfs_type, h_flag):
        """Compile results into a dictionary."""
        return {
            'actions': [res for res in results if res is not None],
            'smiles': [smiles for smiles, res in zip(smiles_dataset, results) if res is not None],
            'dfs_kwargs': dfs_kwargs,
            'dfs_type': dfs_type,
            'h_flag': h_flag
        }

    def _save_to_cache(self, cache_file, result_dict):
        """Save results to a cache file."""
        print(f"Saving cache to {cache_file}")
        with open(cache_file, 'wb') as f:
            pickle.dump(result_dict, f)
    
    
                


if __name__=="__main__":



    # Test rdkit mol action generator
    Indole_smiles = "c1ccc2[nH]ccc2c1"  # Indole
    co2_smiles="O=C=O"
    benzene_smiles="c1ccccc1"
    ts1="C[CH]C=O"
    ts2='c1ccc2[nH]ccc2c1'
    ts3='Nc1ccc(S(=O)(=O)c2ccc(N)cc2)cc1'
    ts4='CO/N=C(\\C=O)c1csc(N)n1'
    ts5="[CH3]"
    target_smile=ts5
    
    mol = Chem.MolFromSmiles(target_smile)
    recon_smile=Chem.MolToSmiles(mol)

    mol = Chem.AddHs(mol,explicitOnly=True, addCoords=True)
    recon_smile_from_mol_with_H = Chem.MolToSmiles(mol, allHsExplicit=True)


    recon_smile=Chem.MolToSmiles(mol)

    mol = Chem.AddHs(mol,explicitOnly=True, addCoords=True)
    recon_smile_from_mol_with_H = Chem.MolToSmiles(mol, allHsExplicit=True)


    rdkit_mol_action_generator = RDKitMolDFSActionGenerator()
    start_atom_idx=1
    
    atom_sequence = rdkit_mol_action_generator.single_dfs_actions(mol,start_atom_idx, include_bonds=False)
    print(f"Atom sequences of actions for {target_smile} starting from atom id {start_atom_idx}:\n {atom_sequence}\n")
    
    # Get only bond creation sequence
    bond_sequence = rdkit_mol_action_generator.single_dfs_actions(mol,start_atom_idx, include_atoms=False)
    print(f"Bond sequences of actions for {target_smile} starting from atom id {start_atom_idx}:\n {bond_sequence}\n")

    # Get both (default)
    full_sequence = rdkit_mol_action_generator.single_dfs_actions(mol,start_atom_idx, start_atom_idx)
    print(f"Full atom_bond sequences of actions for {target_smile} starting from atom id {start_atom_idx}:\n {full_sequence}\n")

    # Get all possible DFS sequences with only atoms
    all_atom_bond_sequences = rdkit_mol_action_generator.all_dfs_actions(mol, include_bonds=True, include_atoms=False)
    print(f"All possible atom_bond sequences of actions ({len(all_atom_bond_sequences)}) for {target_smile}:\n {all_atom_bond_sequences}\n")
    
    """ Generate list of actions for the smiles dataset """
    
    BASE_PATH = "/home/meisam/GitHub_codes/eDeriv2/assets/datasets/"
    # BASE_PATH = "/home/magesh/eDeriv/graph_variation/"
    
    dataset_filenames=['graph_emolfrag_train_non_pen_data.pkl','graph_emolfrag_all_dude_data.pkl',
                       'graph_emolfrag_test_pen_data.pkl']
    
    df_train = pd.read_pickle(BASE_PATH + 'graph_emolfrag_train_non_pen_data.pkl')
    df_train_dude = pd.read_pickle(BASE_PATH + 'graph_emolfrag_all_dude_data.pkl')
    df_test = pd.read_pickle(BASE_PATH + 'graph_emolfrag_test_pen_data.pkl')

    final = [df_train, df_train_dude, df_test]
    df_final = pd.concat(final)
    frag_smiles = df_final['fragments'].tolist()
    frag_smiles = [x for x in frag_smiles if len(x) > 1]
    h_flag=False
    smiles_dataset_action_gen=SmilesDatasetActionGenerator(frag_smiles, rdkit_mol_action_generator)
    dfs_kwargs={'action_format': 'short','include_atoms': False,'include_bonds': True}
    dataset_actions=smiles_dataset_action_gen.generate(dfs_kwargs,cache_file='smiles_actions.pkl', dfs_type='single')
    print(f'The action dataset was made and it includes {len(dataset_actions)} number of data')
        
