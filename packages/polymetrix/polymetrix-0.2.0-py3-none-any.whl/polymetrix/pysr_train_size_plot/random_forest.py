import pandas as pd
import numpy as np
import json
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from rdkit import Chem
from rdkit.Chem import AllChem


def calculate_morgan_fingerprints(smiles_list, radius=2, nBits=2048):
    """Calculate Morgan fingerprints for a list of SMILES strings"""
    fingerprints = []
    for smiles in smiles_list:
        mol = Chem.MolFromSmiles(smiles)
        if mol is not None:
            fingerprint = AllChem.GetMorganFingerprintAsBitVect(mol, radius, nBits=nBits)
            fingerprints.append(list(fingerprint.ToBitString()))
        else:
            print(f"Warning: Could not process SMILES: {smiles}")
    return np.array(fingerprints, dtype=int)


def run_experiment(seed, X_train_full, y_train_full, test_data, train_size):
    """Run a single experiment with specific training size"""
    np.random.seed(seed)
    
    # Sample training data if needed
    if train_size < len(X_train_full):
        indices = np.random.choice(len(X_train_full), size=train_size, replace=False)
        X_train_subset = X_train_full.iloc[indices]
        y_train_subset = y_train_full.iloc[indices]
    else:
        X_train_subset = X_train_full.copy()
        y_train_subset = y_train_full.copy()

    # Calculate Morgan fingerprints
    X_fp = calculate_morgan_fingerprints(X_train_subset['PSMILES'].values)
    X_test_fp = calculate_morgan_fingerprints(test_data['PSMILES'].values)
    
    # Split into training and validation
    X_train, X_val, y_train, y_val = train_test_split(X_fp, y_train_subset, test_size=0.1, random_state=42)
    
    # Train model
    rf_model = RandomForestRegressor(random_state=seed, n_estimators=100)
    rf_model.fit(X_train, y_train)
    
    # Make predictions
    y_val_pred = rf_model.predict(X_val)
    y_test_pred = rf_model.predict(X_test_fp)
    
    # Calculate metrics
    val_metrics = {
        'val_rmse': float(np.sqrt(mean_squared_error(y_val, y_val_pred))),
        'val_mae': float(mean_absolute_error(y_val, y_val_pred)),
        'val_r2': float(r2_score(y_val, y_val_pred))
    }
    
    test_metrics = {
        'test_rmse': float(np.sqrt(mean_squared_error(test_data['Exp_Tg(K)'], y_test_pred))),
        'test_mae': float(mean_absolute_error(test_data['Exp_Tg(K)'], y_test_pred)),
        'test_r2': float(r2_score(test_data['Exp_Tg(K)'], y_test_pred))
    }
    
    return val_metrics, test_metrics


def main():
    # Load datasets
    train_data_path = '/home/ta45woj/PolyMetriX/src/polymetrix/sym_datasets/Polymer_Tg_new_featurizers_20_09_2024.csv'
    test_data_path = '/home/ta45woj/PolyMetriX/src/polymetrix/sym_datasets/mdpi_no_leakage_12_12_24_featurizers.csv'
    
    print("Loading datasets...")
    train_df = pd.read_csv(train_data_path)
    test_df = pd.read_csv(test_data_path)
    
    print(f"Original training data size: {len(train_df)}")
    print(f"Test data size: {len(test_df)}")
    
    # Create initial train/validation split
    X_train, X_valid, y_train, y_valid = train_test_split(
        train_df, train_df['Exp_Tg(K)'], 
        test_size=0.1, 
        random_state=42
    )
    
    max_train_size = len(X_train)
    print(f"\nAfter validation split:")
    print(f"Available training set size: {max_train_size}")
    print(f"Validation set size: {len(X_valid)}")
    
    # Define training sizes
    train_sizes = [50, 100, 300, 500, 1000, 2000, 3000, 4000, 5000, 6000, max_train_size] #100, 300, 500, 1000, 2000, 3000, 4000, 5000, 6000, max_train_size
    train_sizes = [size for size in train_sizes if size <= max_train_size]
    
    print(f"\nTraining sizes to be used: {train_sizes}")
    
    seeds = [42, 43, 44]  # Multiple seeds for robust results
    
    # Store results
    results = {
        'experiment_details': {
            'original_dataset_size': len(train_df),
            'final_training_set_size': len(X_train),
            'validation_set_size': len(X_valid),
            'test_set_size': len(test_df),
            'validation_split': 0.1,
            'random_seeds': seeds  # Changed from single value to list of seeds
        },
        'results': []
    }
    
    # Run experiments
    for train_size in train_sizes:
        print(f"\nRunning experiments with training size: {train_size}")
        
        size_results = {
            'train_size': train_size,
            'seeds': []
        }
        
        for seed in seeds:
            print(f"  Seed {seed}")
            val_metrics, test_metrics = run_experiment(seed, X_train, y_train, test_df, train_size)
            
            seed_results = {
                'seed': seed,
                'validation_metrics': val_metrics,
                'test_metrics': test_metrics
            }
            size_results['seeds'].append(seed_results)
            
            print(f"    Validation MAE: {val_metrics['val_mae']:.2f} K")
            print(f"    Test MAE: {test_metrics['test_mae']:.2f} K")
            print(f"    Test R2: {test_metrics['test_r2']:.3f}")
        
        # Calculate aggregated metrics
        test_maes = [run['test_metrics']['test_mae'] for run in size_results['seeds']]
        test_r2s = [run['test_metrics']['test_r2'] for run in size_results['seeds']]
        
        size_results['aggregated_metrics'] = {
            'mean_test_mae': float(np.mean(test_maes)),
            'std_test_mae': float(np.std(test_maes)),
            'mean_test_r2': float(np.mean(test_r2s)),
            'std_test_r2': float(np.std(test_r2s))
        }
        
        results['results'].append(size_results)
    
    # Save results
    output_file = '/home/ta45woj/PolyMetriX/src/polymetrix/pysr_train_size_plot/rf_training_size_results.json'
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {output_file}")
    
    # Print summary
    print("\nFinal Summary:")
    print("Training Size | Test MAE | Test R2")
    print("-" * 40)
    for result in results['results']:
        size = result['train_size']
        mae = result['aggregated_metrics']['mean_test_mae']
        r2 = result['aggregated_metrics']['mean_test_r2']
        print(f"{size:12d} | {mae:8.2f} | {r2:7.3f}")


if __name__ == "__main__":
    main()