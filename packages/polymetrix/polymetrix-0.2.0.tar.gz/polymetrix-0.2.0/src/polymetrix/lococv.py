import numpy as np
import pandas as pd
from polymetrix.datasets import GlassTempDataset
from polymetrix.data_loader import load_tg_dataset
from mofdscribe.splitters.splitters import LOCOCV
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error

from rdkit import Chem
from rdkit.Chem import AllChem, DataStructs

def psmiles_to_ecfp(psmiles_str, radius=2, nBits=2048):
    mol = Chem.MolFromSmiles(psmiles_str)
    if mol is None:
        return np.zeros((nBits,), dtype=int)
    ecfp = AllChem.GetMorganFingerprintAsBitVect(mol, radius, nBits=nBits)
    arr = np.zeros((nBits,), dtype=int)
    DataStructs.ConvertToNumpyArray(ecfp, arr)
    return arr

df = load_tg_dataset('PolymerTg.csv')
dataset = GlassTempDataset(df=df)
print("Dataset details:")
print(dataset)

# Access the list of PSMILES strings
psmiles_list = dataset._psmiles
print("\nPSMILES strings:")
print(psmiles_list)

# Convert each PSMILES string to its corresponding ECFP vector
ecfp_features = [psmiles_to_ecfp(ps) for ps in psmiles_list]
ecfp_features = np.array(ecfp_features)
print("\nECFP features shape:", ecfp_features.shape)

# Create a DataFrame for the ECFP features with one column per bit
ecfp_columns = [f"ecfp_{i}" for i in range(ecfp_features.shape[1])]
ecfp_df = pd.DataFrame(ecfp_features, columns=ecfp_columns, index=dataset._df.index)

# Append the ECFP features to the original dataset's DataFrame
dataset._df = pd.concat([dataset._df, ecfp_df], axis=1)

# Retrieve target labels from the dataset
num_entries = len(dataset)
all_labels = dataset.get_labels(idx=range(num_entries))
print("Labels shape:", all_labels.shape)

# Initialize LOCOCV with the new ECFP column names (a valid feature subset)
loco = LOCOCV(
    ds=dataset,
    feature_names=ecfp_columns,  # Use the new ECFP features for clustering
    n_pca_components="mle",      # Automatic PCA selection if desired
    random_state=42,
    scaled=True
)

# Initialize the regressor – here, a RandomForestRegressor is used
regressor = GradientBoostingRegressor(random_state=42)

# Perform 5-fold LOCOCV evaluation
k = 5
fold_metrics = []

print("\nStarting 5-fold LOCOCV evaluation:")
for fold, (train_idx, test_idx) in enumerate(loco.k_fold(k=k)):
    
    print(f"\nFold {fold+1}:")
    # Use the computed ECFP features for training and testing
    X_train = ecfp_features[train_idx]
    y_train = all_labels[train_idx]
    X_test = ecfp_features[test_idx]
    y_test = all_labels[test_idx]
    
    regressor.fit(X_train, y_train.ravel())
    preds = regressor.predict(X_test)
    
    mae = mean_absolute_error(y_test, preds)
    rmse = np.sqrt(mean_squared_error(y_test, preds))
    fold_metrics.append(mae)
    print(f"Fold {fold+1} MAE: {mae:.2f}  |  RMSE: {rmse:.2f}")

mean_mae = np.mean(fold_metrics)
std_mae = np.std(fold_metrics)
print(f"\nOverall Mean MAE: {mean_mae:.2f} ± {std_mae:.2f}")

# save overall mean mae and std mae in json file
import json
data = {}
data['mean_mae'] = mean_mae
data['std_mae'] = std_mae

with open('LOCOCV.json', 'w') as outfile:
    json.dump(data, outfile)

