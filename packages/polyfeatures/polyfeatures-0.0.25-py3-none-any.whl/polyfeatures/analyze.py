from rdkit import Chem
from rdkit import Chem
import pandas as pd
from rdkit import Chem
from rdkit.Chem import Lipinski
import networkx as nx
from joblib import Parallel, delayed
from tqdm.auto import tqdm
import multiprocessing

from polyfeatures.calculate_features import calculate_backbone_features, calculate_sidechain_features, calculate_extra_features, calculate_descriptors

def analyze_polymers(smiles_list, extra_features=True, rdkit_descriptors=True, n_jobs=-1):
    if n_jobs == -1:
        n_jobs = multiprocessing.cpu_count()
    
    backbone_results = Parallel(n_jobs=n_jobs)(
        delayed(calculate_backbone_features)(smiles) for smiles in tqdm(smiles_list)
    )
    
    sidechain_results = Parallel(n_jobs=n_jobs)(
        delayed(calculate_sidechain_features)(smiles) for smiles in tqdm(smiles_list)
    )

    if extra_features == True:
        extra_results = Parallel(n_jobs=n_jobs)(
            delayed(calculate_extra_features)(smiles) for smiles in tqdm(smiles_list)
        )

    if rdkit_descriptors == True:
        descriptors = Parallel(n_jobs=n_jobs)(
            delayed(calculate_descriptors)(smiles) for smiles in tqdm(smiles_list)
        )

    backbone_results = pd.DataFrame(backbone_results).set_index('SMILES')
    sidechain_results = pd.DataFrame(sidechain_results).set_index('SMILES')
    extra_results = pd.DataFrame(extra_results).set_index('SMILES') if extra_features == True else None
    descriptors = pd.DataFrame(descriptors).set_index('SMILES') if rdkit_descriptors == True else None
    
    x = pd.concat([backbone_results, sidechain_results], axis=1)

    if extra_features == True and rdkit_descriptors == True:
        y = pd.concat([x, extra_results], axis=1)
        return pd.concat([y, descriptors], axis=1)
    elif extra_features == True and rdkit_descriptors == False:
        return pd.concat([x, extra_results], axis=1)
    elif extra_features == False and rdkit_descriptors == True:
        return pd.concat([x, descriptors], axis=1)
    else:
        return x