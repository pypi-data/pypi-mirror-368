
from typing import List, Tuple
from rdkit import Chem

from abc import abstractmethod, ABC


class MolHandler:

    VALENCE_BASED="valence_based"
    ATOMIC_NUMBERS_BASED="atomic_based"

    def __calculate_per_atom_valence(self,atom):
        """
        A method to calculate the remaining valence electrion for an atom
        input: rdkit atom
        output: remaining valance (scaler)
        """
        periodic_table = Chem.GetPeriodicTable()

        atomic_num = atom.GetAtomicNum()
        # Skip dummy atoms
        if atomic_num == 0:
            return None

        # Get possible valences for this atom type
        possible_valences = periodic_table.GetValenceList(atomic_num)
        if not possible_valences:
            return None

        # The standard valence is typically the first in the list
        standard_valence = possible_valences[0]

        # Calculate current bond order sum (including hydrogens)
        bond_order_sum = sum(bond.GetBondTypeAsDouble() for bond in atom.GetBonds())
        bond_order_sum += atom.GetTotalNumHs()  # Add explicit+implicit hydrogens

        # Calculate remaining valence electrons
        remaining_valence = standard_valence - bond_order_sum + atom.GetFormalCharge()
        if remaining_valence<0:
            raise ValueError(f"The remaining valence ({remaining_valence}) cannot be negative! ")
        
        return remaining_valence
    
    def calculate_valences(self,mol):
        """
        A method to calculate the atomic valences of the rdkit mol object and return it as a dict(atom_id,valence)
        input: rdkit mol
        output: remaining valences of all atoms (dict(atom_id,valence)) 
        """
        try:
            atomic_valences = {}
            
            for atom in mol.GetAtoms():
                remaining_valence = self.__calculate_per_atom_valence(atom)
                if remaining_valence is not None:
                    atomic_valences[atom.GetIdx()] = {'symbol':atom.GetSymbol(),'valence':remaining_valence}
                    
            return atomic_valences
        
        except Exception as e:
            raise ValueError(f"Error processing molecule: {str(e)}")
        
    def find_connection_atoms(self,mol: Chem.Mol,method:str):
        """
        A method to determine the connection atoms (points) in an rdkit molecule
        """
        if not mol:
            raise ValueError("mol is not provided!")

        connection_points={}
        if method == "valence_based":
            # Calculate the atomic valences
            remaining_valences=self.calculate_valences(mol)
            # Filter the atoms with positive valences (potential connection points)
            connection_points= {key: value for key, value in remaining_valences.items() if value['valence'] > 0}
        elif method == "atomic_based":
            """Identify all connection points (dummy atoms) in a molecule."""
            #! not complete 
            for atom in mol.GetAtoms():
                if atom.GetAtomicNum() == 0:  # Dummy atom (*)
                    for neighbor in atom.GetNeighbors():
                        connection_points.append(
                            (atom.GetIdx(), neighbor.GetIdx())
                        )
        else:
            raise ValueError("Unknown method for connection points identification")
        

        return connection_points
    
    def __add_connection_points(self,mol:Chem.Mol,connection_points):
        # Create an editable molecule
        emol = Chem.RWMol(mol)
        # Get atom indices with positive valence (connection points)
        connection_atom_indices = {idx for idx, valence in connection_points if valence > 0}
        
        # Sort indices in reverse order to avoid index shifting issues
        for atom_idx in sorted(connection_atom_indices, reverse=True):
            if atom_idx >= emol.GetNumAtoms():
                continue  # Skip invalid indices
                
            # Get the atom object
            atom = emol.GetAtomWithIdx(atom_idx)
            # original_symbol = atom.GetSymbol()

            # Create a new atom to represent the connection point
            new_atom = Chem.Atom(0)  # Wildcard atom
            new_atom.SetProp("atomLabel", "*")

            # new_atom.SetProp("atomLabel", f"{original_symbol}*")
            # Copy important properties from original atom
            # new_atom.SetFormalCharge(atom.GetFormalCharge())
            # new_atom.SetIsAromatic(atom.GetIsAromatic())
            # Add the new atom to the molecule
            new_atom_idx = emol.AddAtom(new_atom)
            # Create a bond between the dummy atom and the target atom
            # emol.AddBond(new_atom_idx, atom_idx, Chem.BondType.SINGLE)
            # Re-order the atom indices
            emol=self.reorder_mol_indices(emol,new_atom_idx,atom_idx)
            # new_atom.SetFormalCharge(atom.GetFormalCharge())
            # new_atom.SetIsotope(atom.GetIdx() + 1)  # Optional: track original atom index
            
            # Insert the * before the connection atom
            # emol.ReplaceAtom(atom_idx, new_atom)
            
            
        return emol
    
    def mark_connection_atoms(self,mol:Chem.Mol,connection_atoms)->Chem.Mol:
        """Mark connection points in an RDKit Mol object."""
        for atom_idx, atom_props in connection_atoms.items():
            atom = mol.GetAtomWithIdx(atom_idx)
            atom.SetProp("ELIGIBLE_ATOMTYPE_TO_CONNECT", f"{str(atom_idx)} {str(atom_props['symbol'])}") # Store as an atom property
        
        return mol

    
    @staticmethod
    def reorder_mol_indices(mol:Chem.Mol,old_index,new_neighboring_index):
        # Get the current atom order
        original_order = list(range(mol.GetNumAtoms()))

        # Modify the order to place the new atom after the target atom
        # Remove the new atom index and re-insert it after atom_idx
        original_order.remove(old_index)
        insertion_index = original_order.index(new_neighboring_index) + 1
        reordered_order = original_order[:insertion_index] + [old_index] + original_order[insertion_index:]

        # Renumber atoms in the molecule
        reordered_mol  = Chem.RenumberAtoms(mol, reordered_order)
        emol = Chem.RWMol(reordered_mol)


        return emol
            
    def mol_to_smiles(self,mol: Chem.Mol, connection_points: List[Tuple[int, int]]=None)->str:            
        """Marks connection points in a SMILES string with asterisks (*)."""
        # Create molecule object
        if mol is None:
            raise ValueError("Invalid SMILES string")
        
        if connection_points: # If it requires adding connection points to the final smile
            # Add connection points to the mol
            emol=self.__add_connection_points(mol,connection_points)
            for atom in emol.GetAtoms():
                print(atom.GetSymbol())
            # Convert back to SMILES
            smiles = Chem.MolToSmiles(emol)
            # Clean up the output (replace isotopic markers with plain *)
            smiles = smiles.replace('[0]', '*')
        else: # If no connection points addition is required
            smiles=Chem.MolToSmiles(mol)
            
        
        return smiles
    
    
    def _set_sybyl_atom_types(self,mol:Chem.Mol):
        for atom in mol.GetAtoms():
            if not atom.HasProp("SYBYL_ATOM_TYPE"):
                atom.SetProp("SYBYL_ATOM_TYPE",self._get_sybyl_atom_type(atom))
        
        return mol


    def _smart_atomic_match(self,atom, smarts):
        idx = atom.GetIdx()
        return any(idx in m for m in atom.GetOwningMol().GetSubstructMatches(MolFromSmarts(smarts)))

    
    def _get_sybyl_atom_type(self,atom):
        """Get SYBYL atom type for a given atom."""
        # define groups for atom types
        atom_group_types = "[NX3,NX2]([!O,!S])!@C(!@[NX3,NX2]([!O,!S]))!@[NX3,NX2]([!O,!S])"  # strict
    
        sybyl_atom_type=None
        
        # Get atomic attributes 
        atom_symbol = atom.GetSymbol()
        atomic_number = atom.GetAtomicNum()
        atom_hybridization = min(atom.GetHybridization() - 1 ,3)

        atom_degree = atom.GetDegree()
        atom_is_aromatic = atom.GetIsAromatic()
        
        if atomic_number == 6: # Carbon (C)
            if atom_is_aromatic:
                sybyl_atom_type="C.ar"
            elif atom_degree == 3 and self._smart_atomic_match(atom, atom_group_types):
                sybyl_atom_type = "C.cat"
            else:
                sybyl_atom_type = f"{atom_symbol}.{atom_hybridization}"
            
        elif atomic_number == 7: # Nitrogen (N)
            if atom_is_aromatic:
                sybyl_atom_type = "N.ar"
            elif self._smart_atomic_match(atom, "C(=[O,S])-N"):
                sybyl_atom_type = "N.am"
            elif atom_degree == 3 and self._smart_atomic_match(atom, "[$(N!-*),$([NX3H1]-*!-*)]") | self._smart_atomic_match(atom, atom_group_types):
                sybyl_atom_type = "N.pl3"
            elif atom_degree == 4 or atom_hybridization == 3 and atom.GetFormalCharge():
                sybyl_atom_type = "N.4"
            else:
                sybyl_atom_type = f"{atom_symbol}.{atom_hybridization}"
        elif atomic_number == 8: # Oxygen (O)
            if atom_degree == 1 and self._smart_atomic_match(atom, "[CX3](=O)[OX1H0-]"):
                sybyl_atom_type = "O.co2"
            elif atom_degree == 2 and not atom_is_aromatic:  # Aromatic Os are sp2
                sybyl_atom_type = "O.3"
            else:
                sybyl_atom_type = "O.2"
            
        elif atomic_number == 16: # Sulphor (S)
            if atom_degree == 3 and self._smart_atomic_match(atom, "[$([#16X3]=[OX1]),$([#16X3+][OX1-])]"):
                sybyl_atom_type = "S.O"
            elif self._smart_atomic_match(atom, "S(=,-[OX1;+0,-1])(=,-[OX1;+0,-1])(-[#6])-[#6]"):
                sybyl_atom_type = "S.o2"
            else:
                sybyl_atom_type = f"{atom_symbol}.{atom_hybridization}" 
        elif atomic_number == 15: # Phosphorus (P)
            sybyl_atom_type = f"{atom_symbol}.{atom_hybridization}" 
                
        return atom_symbol if sybyl_atom_type is None else sybyl_atom_type

    

    def _add_mol_props(self,mol:Chem.Mol, mol_prop:str)->None:
        "A method to add custom properties to the Mol object"
        if mol is None:
            raise ValueError("Molecule is None")
        
        if mol.GetNumAtoms() == 0:
            return mol
        
        if mol_prop == "SIMILAR_FRAGMENTS":
            mol.SetProp("SIMILAR_FRAGMENTS", "")  # Empty if unused
            
        elif mol_prop == "ATOM_NUMBER ELIGIBLE_ATOMTYPE_TO_CONNECT":
            mol=self._set_sybyl_atom_types(mol)
            
            eligible_atoms_to_connect_info=""
            for atom in mol.GetAtoms():
                if atom.HasProp("ELIGIBLE_ATOMTYPE_TO_CONNECT"):
                    eligible_atoms_to_connect_info+= f"{atom.GetIdx()} {atom.GetProp('SYBYL_ATOM_TYPE')}"+"\n"
                    
            # Set the property at the molecule level 
            mol.SetProp(
                f"ATOM_NUMBER ELIGIBLE_ATOMTYPE_TO_CONNECT",
                eligible_atoms_to_connect_info
            )
            
        elif mol_prop == "MAX-NUMBER-Of-CONTACTS ATOMTYPES":
            mol=self._set_sybyl_atom_types(mol)
            
            max_num_contacts_and_atom_types=""
            for atom in mol.GetAtoms():
                pass
            
            mol.SetProp("MAX-NUMBER-Of-CONTACTS ATOMTYPES",
                        max_num_contacts_and_atom_types)
            
        elif mol_prop == "BRANCH @atom-number eligible-atmtype-to-connect":
            branch_atom_num_eligible_atomtype_to_connect=""
            for atom in mol.GetAtoms():
                if atom.HasProp("ELIGIBLE_ATOMTYPE_TO_CONNECT"):
                    branch_atom_num_eligible_atomtype_to_connect+=f"{atom.GetIdx()} {1}" # must replace 1 with the eligible-atmtype-to-connect ()
            
            mol.SetProp("BRANCH @atom-number eligible-atmtype-to-connect",
                        branch_atom_num_eligible_atomtype_to_connect)
            
        elif mol_prop == "ATOMTYPES":
            mol=self._set_sybyl_atom_types(mol)
            atom_types=""
            for atom in mol.GetAtoms():
                try:
                    atom_types+= f"{atom.GetProp('SYBYL_ATOM_TYPE')}"+"\n"
                except Exception as e:
                    print(f"An exception occured while trying to collect atom types: {e}")
                    
            # Set the property at the molecule level (for SDF metadata)
            mol.SetProp(f"ATOMTYPES",atom_types)
            
        return mol
    
   
    @staticmethod
    def _add_file_name_prefix(file_path: str, prefix: str) -> str:
        """
        Adds a prefix to filename if not already present.
        Args:
            file_path: Absolute path to the file
            prefix: Prefix to add 
        Returns:
            Modified file path if prefix was needed, original otherwise
        """
        dir_name, file_name = os.path.split(file_path)
        
        # Skip if prefix already exists
        if file_name.startswith(prefix):
            return file_path
            
        return os.path.join(dir_name, f"{prefix}{file_name}")
    
    
    def to_sdf(self,mol: Chem.Mol, output_file_path: str,mol_type:str, custom_mol_props:List[str]):
        """Write a molecule to SDF with connection point metadata."""
        # Pre-process the file-name based on the mol_type
        if mol_type == "rigid" or mol_type == "brick":
            output_file_path = self._add_file_name_prefix(output_file_path, "r-")
        elif mol_type == "linker":
            output_file_path = self._add_file_name_prefix(output_file_path, "l-")
        else:
            raise TypeError(f'Unknown mol type: {mol_type}. Acceptable mol types: rigid, brick, linker')


        # Add global Mol properties requested by the user
        for section in custom_mol_props:
            mol=self._add_mol_props(mol,section)
        
        # Write the molecule to the sdf file
        sdf_writer = Chem.SDWriter(output_file_path)
        sdf_writer.write(mol)
        sdf_writer.close()

        

        
if __name__=="__main__":
    from chem_handlers.smiles_handler import SmilesHandler,SmilesHandlingStrategyWithRDKIT
    
    smiles_handler=SmilesHandler(smiles_handling_strategy=SmilesHandlingStrategyWithRDKIT())
    
    test_smile="CC1(C)[CH]N2C(=O)[CH][C@H]2S1"
    test_mol=smiles_handler.smiles_to_mol(test_smile,sanitize=False)
    mol_handler=MolHandler()
    valences=mol_handler.calculate_valences(test_mol)
    con_points=mol_handler.find_connection_atoms(test_mol,method="valence_based")
    mol_with_con_atoms=mol_handler.mark_connection_atoms(test_mol,connection_atoms=con_points)
    mol_handler.mol_to_sdf(mol_with_con_atoms,"mol_in_sdf.sdf")
    pass
    

    


