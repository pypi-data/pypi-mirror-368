from analyze import analyze_polymers
import numpy as np

smiles = ["*NC(C)C(=O)NCC(=O)NCC(*)=O", "*Oc1ccc(C(C)(C)c2ccc(Oc3ccc(C(=O)c4cccc(C(=O)c5ccc(*)cc5)c4)cc3)cc2)cc1"]  # e.g., a repeating unit

features = analyze_polymers(smiles, extra_features=True, rdkit_descriptors=False)

print(features)