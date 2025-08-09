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
backbone_flexibility_index
sidechain_length
sidechain_heavy_atom_count
sidechain_branch_count
sidechain_electronegative_count
sp3_count
sp2_count
+
results from CalcMolDescriptors()
```

## Functions

### processing
```process_polymer_smiles(smiles)```

### calculate_features
```
calculate_backbone_features(smiles)
calculate_sidechain_features(smiles)
calculate_extra_features(smiles)
calculate_descriptors(smiles)
```

### analyze
```analyze_polymers(smiles_list, extra_features=True, rdkit_descriptors=True, n_jobs=-1)```
