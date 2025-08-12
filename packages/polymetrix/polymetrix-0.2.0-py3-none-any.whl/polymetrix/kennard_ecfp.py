# import numpy as np
# import pandas as pd
# from polymetrix.datasets import GlassTempDataset
# from polymetrix.data_loader import load_tg_dataset
# from mofdscribe.splitters.splitters import LOCOCV, KennardStoneSplitter
# from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
# from sklearn.metrics import mean_squared_error, mean_absolute_error
# from rdkit import Chem
# from rdkit.Chem import AllChem, DataStructs
# from joblib import Parallel, delayed  # Added for parallel processing
# import json

# def psmiles_to_ecfp(psmiles_str, radius=2, nBits=2048):
#     mol = Chem.MolFromSmiles(psmiles_str)
#     if mol is None:
#         return np.zeros((nBits,), dtype=int)
#     ecfp = AllChem.GetMorganFingerprintAsBitVect(mol, radius, nBits=nBits)
#     arr = np.zeros((nBits,), dtype=int)
#     DataStructs.ConvertToNumpyArray(ecfp, arr)
#     return arr

# # Load dataset and prepare features
# df = load_tg_dataset('PolymerTg.csv')
# dataset = GlassTempDataset(df=df)
# psmiles_list = dataset._psmiles
# ecfp_features = np.array([psmiles_to_ecfp(ps) for ps in psmiles_list])
# ecfp_columns = [f"ecfp_{i}" for i in range(ecfp_features.shape[1])]
# ecfp_df = pd.DataFrame(ecfp_features, columns=ecfp_columns, index=dataset._df.index)
# dataset._df = pd.concat([dataset._df, ecfp_df], axis=1)
# all_labels = dataset.get_labels(idx=range(len(dataset)))

# # Initialize splitter and regressor
# kennard = KennardStoneSplitter(
#     ds=dataset,
#     feature_names=ecfp_columns,
#     scale=True,
#     centrality_measure="mean",
#     metric="euclidean"
# )

# k = 5
# splits = list(kennard.k_fold(k=k))  # Precompute all splits

# def process_fold(fold_idx, train_idx, test_idx):
#     """Process one fold with its train/test indices"""
#     X_train = ecfp_features[train_idx]
#     y_train = all_labels[train_idx].ravel()
#     X_test = ecfp_features[test_idx]
#     y_test = all_labels[test_idx].ravel()
    
#     model = GradientBoostingRegressor(random_state=42)
#     model.fit(X_train, y_train)
#     preds = model.predict(X_test)
    
#     return (
#         mean_absolute_error(y_test, preds),
#         np.sqrt(mean_squared_error(y_test, preds))
#     )

# # Parallel execution across all available cores
# results = Parallel(n_jobs=-1, verbose=11)(
#     delayed(process_fold)(fold_idx, train_idx, test_idx)
#     for fold_idx, (train_idx, test_idx) in enumerate(splits)
# )

# # Unpack results
# mae_values, rmse_values = zip(*results)

# # Calculate statistics
# final_mae = np.mean(mae_values)
# final_mae_std = np.std(mae_values)

# print(f"\nFinal MAE: {final_mae:.2f} ± {final_mae_std:.2f}")

# # Save results
# with open('kennard.json', 'w') as f:
#     json.dump({
#         'mean_mae': float(final_mae),
#         'std_mae': float(final_mae_std)
#     }, f)



import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from polymetrix.datasets import CuratedGlassTempDataset
from polymetrix.splitters.splitters import TgSplitter
from mofdscribe.splitters.splitters import KennardStoneSplitter, LOCOCV
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error

# Import necessary modules
from polymetrix.datasets import CuratedGlassTempDataset

version = "v1"
url = "https://sandbox.zenodo.org/records/167351/files/PolymerTg_14_02_2025.csv?download=1"

# Load the dataset
dataset = CuratedGlassTempDataset(version=version, url=url)

# # consider 1000 data points
# dataset = dataset.get_subset(range(100))


# Get dataset size
print(f"Dataset contains {len(dataset)} entries")

# Access available data fields
print("\nAvailable features:", dataset.available_features)
print("Available labels:", dataset.available_labels)
print("Metadata fields:", dataset.meta_info)

features = dataset.get_features(idx=range(len(dataset)))
print(f'features', features)
print(f'features', features.shape)
labels = dataset.get_labels(idx=range(len(dataset)))
print(f'labels', labels)
print(f'labels', labels.shape)

# Ensure feature_names match the columns in your dataset
feature_names = dataset.available_features  # Use the list directly
print(f'feature_names', feature_names)

kennard = KennardStoneSplitter(
    ds=dataset,
    feature_names=feature_names,  # Features used for distance calculation
    scale=True,  # Recommended to scale features before sampling
    centrality_measure="mean",  # Initial point selection method
    metric="dice"  # Distance metric
)

gbr = GradientBoostingRegressor(random_state=42)
# Perform 5-fold cross-validation
k = 5
fold_metrics = []

for fold, (train_idx, test_idx) in enumerate(kennard.k_fold(k=k)):
    # Get splits based on Kennard-Stone ordering
    X_train = features[train_idx]
    print(f'X_train', X_train.shape)
    y_train = labels[train_idx]
    X_test = features[test_idx]
    y_test = labels[test_idx]
    
    # Train and predict (same as before)
    gbr.fit(X_train, y_train.ravel())
    preds = gbr.predict(X_test)
    
    # Calculate metrics
    mae = mean_absolute_error(y_test, preds)
    rmse = np.sqrt(mean_squared_error(y_test, preds))
    fold_metrics.append(mae)
    print(f"Fold {fold+1} MAE: {mae:.2f}")

# Calculate overall performance (same as before)
print(f"\nMean MAE: {np.mean(fold_metrics):.2f} ± {np.std(fold_metrics):.2f}")

# Save results in json format
import json
with open('kennard_ecfp_plus_feat.json', 'w') as f:
    json.dump({
        'mean_mae': float(np.mean(fold_metrics)),
        'std_mae': float(np.std(fold_metrics))
    }, f)
