from rdkit import Chem
from rdkit.Chem import rdmolops
import pandas as pd

from src.chem_handlers.mol_handler import MolHandler

class MolTranslator:
    def __init__(self):
        self.atom_map = {}
        self.mol = Chem.RWMol()
        self.atom_count = 0

    def reset(self):
        self.atom_map = {}
        self.mol = Chem.RWMol()
        self.atom_count = 0

    def parse_token(self, token):
        """
        Example token: 'add_aromatic_bond_C2_C3'
        Extracts: bond_type = 'aromatic', atom1 = 'C2', atom2 = 'C3'
        """
        if not token.startswith("add_"):
            return None

        parts = token.split("_")
        bond_type = parts[1]  
        atom1 = parts[3]
        atom2 = parts[4]
        return bond_type, atom1, atom2

    def _add_atom(self, atom_label):
        
        if atom_label not in self.atom_map:
            atom_symbol = ''.join([c for c in atom_label if c.isalpha()])

            atom = Chem.Atom(atom_symbol)
            idx = self.mol.AddAtom(atom)
            self.atom_map[atom_label] = idx
            self.atom_count += 1
        
    def _update_radicals(self):
        mol = self.mol

        expected_valence = {
            'C': 4,
            'N': 3,
            'O': 2,
            'H': 1,
        }

        for atom in mol.GetAtoms():
            symbol = atom.GetSymbol()
            if symbol == "H":
                continue

            idx = atom.GetIdx()
            total_bonds = sum([b.GetBondTypeAsDouble() for b in atom.GetBonds()])
            expl_H = sum(1 for n in atom.GetNeighbors() if n.GetSymbol() == "H")

            try:
                atom.CalcImplicitValence()
                impl_H = atom.GetNumImplicitHs()
            except:
                impl_H = 0

            valence = expected_valence.get(symbol, 0)
            radical_electrons = valence - total_bonds - impl_H
            # print(f"Total bonds for atom idx: {idx}, symbol: {symbol}, expl_H: {expl_H}, impl_H: {impl_H}, bonds: {total_bonds}, valence: {valence}, re: {radical_electrons}")

            # print(f"print {symbol} radical electorm, {radical_electrons}")
            if radical_electrons > 0 and expl_H > 0:
                atom.SetNumRadicalElectrons(int(radical_electrons))



    def _add_bond(self, bond_type, atom1_label, atom2_label):
        # if "H" in atom1_label or "H" in atom2_label:
        #     return

        self._add_atom(atom1_label)
        self._add_atom(atom2_label)
        idx1 = self.atom_map[atom1_label]
        idx2 = self.atom_map[atom2_label]

        bond_dict = {
            "single": Chem.BondType.SINGLE,
            "double": Chem.BondType.DOUBLE,
            "triple": Chem.BondType.TRIPLE,
            "aromatic": Chem.BondType.AROMATIC
        }

        bond_enum = bond_dict.get(bond_type.lower())
        if bond_enum is None:
            raise ValueError(f"Unsupported bond type: {bond_type}")

        if self.mol.GetBondBetweenAtoms(idx1, idx2) is None:
            self.mol.AddBond(idx1, idx2, bond_enum)
        
        # Sanitize and then update radicals
        mol = self.mol.GetMol()
        try:
            # Chem.SanitizeMol(mol, sanitizeOps=Chem.SanitizeFlags.SANITIZE_PROPERTIES)
            # print("molecule getting sanitized")
            Chem.SanitizeMol(mol)
        except Exception:
            pass
            
        self._update_radicals()

    @staticmethod
    def _assign_explicit_hydrogens(mol):
        """
        Iterate over atoms in a molecule and set the number of explicit hydrogens
        based on how many H atoms are directly bonded to each atom.
        This assumes H atoms are already added as separate atoms.
        """
        rw_mol = Chem.RWMol(mol)  # Make it editable

        for atom in rw_mol.GetAtoms():
            if atom.GetAtomicNum() == 1:
                continue  # skip hydrogen atoms

            # Count the number of hydrogen neighbors
            h_count = 0
            for neighbor in atom.GetNeighbors():
                if neighbor.GetAtomicNum() == 1:
                    h_count += 1

            # Set the number of explicit Hs
            atom.SetNumExplicitHs(h_count)
            # if h_count>0:
            #     atom.SetNumRadicalElectrons(1)

            # Optional: Prevent RDKit from adding implicit Hs
            # atom.SetNoImplicit(True)

        return rw_mol.GetMol()


    def build_molecule(self, instruction_list):
        self.reset()
        for token in instruction_list:
            if token in ["<START>", "<END>"]:
                continue
            parsed = self.parse_token(token)
            if parsed:
                bond_type, atom1, atom2 = parsed
                self._add_bond(bond_type, atom1, atom2)

        
        mol = self.mol.GetMol()
        Chem.SanitizeMol(mol)
        # self._print_atom_hydrogen_info(mol)
        valences=MolHandler().calculate_valences(mol)
        # print(valences)
        # mol = Chem.RemoveHs(mol, implicitOnly=False)
        # mol = Chem.AddHs(mol)
        Chem.SanitizeMol(mol)
        return mol
    
    @staticmethod
    def _print_atom_hydrogen_info(mol):
        """
        Print hydrogen-related properties for all atoms in the molecule.
        """
        print(f"{'Idx':>3} {'Symbol':>6} {'Expl_H':>7} {'Impl_H':>7} {'Total_H':>8} {'Radicals':>9}")
        print("-" * 45)

        for atom in mol.GetAtoms():
            idx = atom.GetIdx()
            symbol = atom.GetSymbol()
            expl_h = atom.GetNumExplicitHs()
            impl_h = atom.GetNumImplicitHs()
            total_h = atom.GetTotalNumHs()
            radicals = atom.GetNumRadicalElectrons()

            print(f"{idx:>3} {symbol:>6} {expl_h:>7} {impl_h:>7} {total_h:>8} {radicals:>9}")


    def to_smiles(self, instruction_list):
        try:
            mol = self.build_molecule(instruction_list)
            return Chem.MolToSmiles(mol)
        except Exception as e:
            print(f'Exception occured during molecule reconstruction from the instructions:{e}')


def apply_translator_to_df(df, instruction_col="actions"):
    translator = MolTranslator()
    df["recons_smiles"] = df[instruction_col].apply(translator.to_smiles)
    return df
    

if __name__ == "__main__":

    instructions = ['<START>', 'add_single_bond_C1_C2', 
                    'add_single_bond_C1_C3', 'add_double_bond_C3_O1', 
                    'add_single_bond_C1_H1', '<END>']
    

    translator = MolTranslator()
    smiles = translator.to_smiles(instructions)
    print("SMILES:", smiles)  # Should print: c1ccccc1 or equivalent
    