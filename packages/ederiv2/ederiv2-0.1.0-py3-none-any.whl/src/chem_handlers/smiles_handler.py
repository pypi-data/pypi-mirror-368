from abc import abstractmethod
from typing import List, Tuple
from rdkit import Chem
from rdkit.Chem import rdMolDescriptors 
from abc import ABC
from rdkit.Chem import AllChem
# Import RDKit's drawing module
from rdkit.Chem import Draw
import warnings

class SmilesHandlingStrategyAbstract(ABC):
    @abstractmethod
    def smiles_to_image(self)->None:
        raise NotImplementedError

    @abstractmethod
    def smiles_to_mol(self):
        raise NotImplementedError
    
    @abstractmethod
    def smiles_to_molecular_formula(self)->str:
        raise NotImplementedError

    @abstractmethod
    def smiles_to_sdf(self)->None:
        raise NotImplementedError
    
    

class SmilesHandlingStrategyWithRDKIT(SmilesHandlingStrategyAbstract):

    def smiles_to_mol(self, smiles: str, sanitize: bool = True, removeHs:bool=False) :
        try:
            params = Chem.SmilesParserParams()
            params.sanitize = sanitize
            params.removeHs = removeHs  
            
            # First try with specified sanitization
            mol = Chem.MolFromSmiles(smiles, params)
            if mol is None:
                print("The returned molecule is None!")
                
            if not removeHs:
                mol = Chem.AddHs(mol, explicitOnly=True, addCoords=True)
               
            return mol
        except Exception:
            return None
    
    def smiles_to_image(self, smiles: str, output_image_path: str) -> None:
        # Convert the SMILES string to a molecule
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            warnings.warn("Invalid SMILES string provided. Did not generate image.")
            return
        # Compute 2D coordinates for visualization
        AllChem.Compute2DCoords(mol)
        
        # Generate and save the image to the specified file path
        Draw.MolToFile(mol, output_image_path)
    
    def smiles_to_molecular_formula(self,smiles:str)->str:
        # Convert SMILES to RDKit Mol object
        mol = Chem.MolFromSmiles(smiles) 
        if mol is None:
            return "Invalid SMILES"
        # Calculate molecular formula
        formula = Chem.rdMolDescriptors.CalcMolFormula(mol)
        return formula

    # TODO: Needs to be fixed
    def smiles_to_sdf(self, smiles:str, output_file:str, add_hs=True, generate_3d=True, conformers=True)->None:
        """
        Convert a SMILES string to an SDF file.
        """
        if smiles is None:
            raise ValueError("Invalid SMILES string")

        # Create molecule from SMILES
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            raise ValueError("None molecule!")

        # Find connection points (dummy atoms marked with '*' in SMILES)
        connection_points = []
        for atom in mol.GetAtoms():
            if atom.GetSymbol() == '*':
                connection_points.append(atom.GetIdx())

        # Add hydrogens if requested
        if add_hs:
            mol = Chem.AddHs(mol)
        
        # Generate 3D coordinates if requested
        if generate_3d:
            AllChem.EmbedMolecule(mol)
            try:
                AllChem.MMFFOptimizeMolecule(mol)
            except:
                AllChem.UFFOptimizeMolecule(mol)
        
        # Add connection points as properties
        if connection_points:
            mol.SetProp("CONNECTION_POINTS", ",".join(map(str, connection_points)))
        
        # For each connection point, add specific property
        for idx in connection_points:
            if idx < mol.GetNumAtoms():  # Ensure index is valid after H addition
                mol.SetProp(f"CONNECTION_{idx}", "1")
        
        # Write to SDF file
        writer = Chem.SDWriter(output_file)
        writer.write(mol)
        writer.close()
        
        return connection_points

    def is_smiles_in_list(self, smiles: str, smiles_list: list) -> bool:
        """
        Check if the canonical form of the given SMILES is present in the list of SMILES.
        """
        try:
            query_mol = Chem.MolFromSmiles(smiles)
            if query_mol is None:
                return False
            query_canonical = Chem.MolToSmiles(query_mol, canonical=True)
            canonical_list = []
            for s in smiles_list:
                mol = Chem.MolFromSmiles(s)
                if mol is not None:
                    canonical_list.append(Chem.MolToSmiles(mol, canonical=True))
            return query_canonical in canonical_list
        except Exception:
            return False
        
    def is_single_molecule(self, smiles: str) -> bool:
        """
        Returns True if the SMILES string represents a single molecule (no dot-separated fragments).
        """
        if not isinstance(smiles, str):
            print("Invalid SMILES. Input SMILES must be a string.")
            return False
        if smiles is None:
            print("Smailes is None.")
            return False
        # Remove whitespace and check for dot separator
        return '.' not in smiles.strip()


class SmilesHandler:
    def __init__(self, smiles_handling_strategy:SmilesHandlingStrategyAbstract=None):
        self._smiles_handling_strategy=smiles_handling_strategy

    def set_smiles_handling_strategy(self,smiles_handling_strategy:SmilesHandlingStrategyAbstract)->None:
        self._smiles_handling_strategy=smiles_handling_strategy

    def smiles_to_molecular_formula(self,smiles:str)->str:
        return self._smiles_handling_strategy.smiles_to_molecular_formula(smiles)

    def smiles_to_mol(self,smiles:str,sanitize:bool=False,removeHs:bool=False): 
        return self._smiles_handling_strategy.smiles_to_mol(smiles,sanitize,removeHs)
    
    def smiles_to_image(self,smiles:str,image_path:str)->None:
        return self._smiles_handling_strategy.smiles_to_image(smiles,image_path)

    def smiles_to_sdf(self, smiles:str, output_file:str, add_hs=True, generate_3d=True, conformers=True)->None:
        return self._smiles_handling_strategy.smiles_to_sdf(smiles,output_file,add_hs=True, generate_3d=True, conformers=True)
        
    def is_smiles_in_list(self, smiles: str, smiles_list: list) -> bool:
        return self._smiles_handling_strategy.is_smiles_in_list(smiles, smiles_list)
    
    def is_single_molecule(self, smiles: str) -> bool:
        return self._smiles_handling_strategy.is_single_molecule(smiles)
    
    


if __name__=="__main__":
    rdkit_smiles_handling_strategy=SmilesHandlingStrategyWithRDKIT()
    smiles_handler=SmilesHandler(smiles_handling_strategy=rdkit_smiles_handling_strategy)
    # Test molecular formula generator part
    orig_test_smile="N[C@@H](C=O)C1=CCC=CC1"
    orig_test_smile_mol_formula=smiles_handler.smiles_to_molecular_formula(orig_test_smile)
    pred_test_smile="NC(C=O)C1=CCC=CC1"
    pred_test_smile_mol_formula=smiles_handler.smiles_to_molecular_formula(orig_test_smile)
    print(f"""
        +----------------------+---------------------+
        | SMILES               | Molecular Formula   |
        +----------------------+---------------------+
        | {orig_test_smile:<20} | {orig_test_smile_mol_formula:<19} |
        | {pred_test_smile:<20} | {pred_test_smile_mol_formula:<19} |
        +----------------------+---------------------+
        """)
    
    # Test smiles to SDF method
    test_smiles="C1CC(*)NC(*)C1"
    # smiles_handler.smiles_to_sdf(test_smiles,"test.sdf")
    
    # Test smiles to mol conversion
    mol=smiles_handler.smiles_to_mol(orig_test_smile)
    for atom in mol.GetAtoms():
        print(atom.GetSymbol())
        
    pass
    
    

