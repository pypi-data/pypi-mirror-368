from rdkit import Chem
from rdkit import Chem
import pandas as pd
from rdkit import Chem
from rdkit.Chem import Lipinski
import networkx as nx
from joblib import Parallel, delayed
from tqdm.auto import tqdm
import multiprocessing

def process_polymer_smiles(smiles):
    """Remove [*] atoms and identify backbone connection points."""
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return None, []
    
    star_neighbors = []
    editable_mol = Chem.RWMol(mol)
    atoms_to_remove = []
    
    for atom in mol.GetAtoms():
        if atom.GetAtomicNum() == 0:  # Star atoms have atomic number 0
            for neighbor in atom.GetNeighbors():
                star_neighbors.append(neighbor.GetIdx())
            atoms_to_remove.append(atom.GetIdx())
    
    for idx in sorted(atoms_to_remove, reverse=True):
        editable_mol.RemoveAtom(idx)
    
    # Adjust indices of neighbors after removal
    adjusted_neighbors = []
    for orig_idx in star_neighbors:
        adjustment = sum(1 for removed_idx in atoms_to_remove if removed_idx < orig_idx)
        adjusted_neighbors.append(orig_idx - adjustment)
    
    return editable_mol.GetMol(), list(set(adjusted_neighbors))