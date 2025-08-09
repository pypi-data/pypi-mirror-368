# PolyFeatures: Polymer Featurizer

## Installation
```
pip install polyfeatures
```

## Example Usage
```
from analyze_features import analyze_polymers

smiles = ["*Oc1ccc(C=NN=Cc2ccc(Oc3ccc(C(c4ccc(*)cc4)(C(F)(F)F)C(F)(F)F)cc3)cc2)cc1", "*Oc1ccc(C(C)(C)c2ccc(Oc3ccc(C(=O)c4cccc(C(=O)c5ccc(*)cc5)c4)cc3)cc2)cc1"]  # e.g., a repeating unit

features = analyze_polymers(smiles)

print(features)
```

## Supported Features
```
backbone_length
backbone_aromatic_fraction
backbone_heavy_atom_count
backbone_electronegative_count
sidechain_length
sidechain_heavy_atom_count
sidechain_branch_count
sidechain_electronegative_count
num_hbond_donors
no_atom_count
```
