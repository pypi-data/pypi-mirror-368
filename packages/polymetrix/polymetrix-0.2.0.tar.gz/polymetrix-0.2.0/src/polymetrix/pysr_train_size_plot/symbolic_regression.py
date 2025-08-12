# import pandas as pd
# import numpy as np
# import os
# import json
# from datetime import datetime
# from sklearn.model_selection import train_test_split
# from sklearn.metrics import mean_absolute_error
# from pysr import PySRRegressor


# class SimpleSymbolicRegression:
#     def __init__(self, features, base_dir="symbolic_regression_results"):
#         """Initialize the symbolic regression model"""
#         self.features = features
#         self.base_dir = base_dir
#         self.model = None
#         self.equation = None
        
#         # Create base directory if it doesn't exist
#         os.makedirs(base_dir, exist_ok=True)
        
#     def create_model(self):
#         """Create and configure the PySR model"""
#         model_params = {
#             'binary_operators': ["+", "*", "-", "/"],
#             'unary_operators': ["exp", "square", "log10", "cube"],
#             'loss': "loss(prediction, target) = abs(prediction - target)",
#             'niterations': 20,
#             'early_stop_condition': "stop_if(loss, complexity) = loss < 20 && complexity < 10",
#         }
        
#         return PySRRegressor(**model_params)
    
#     def fit_for_size(self, train_size, X_train, y_train, X_valid, y_valid, X_test, y_test):
#         """Fit model for a specific training size"""
#         print(f"\nTraining model with {train_size} samples...")
        
#         # Create directory for this training size
#         output_dir = os.path.join(self.base_dir, f"train_size_{train_size}")
#         os.makedirs(output_dir, exist_ok=True)
        
#         try:
#             # Sample training data if needed
#             if train_size < len(X_train):
#                 sample_indices = np.random.choice(len(X_train), size=train_size, replace=False)
#                 X_train_subset = X_train.iloc[sample_indices]
#                 y_train_subset = y_train.iloc[sample_indices]
#             else:
#                 X_train_subset = X_train
#                 y_train_subset = y_train
            
#             # Create and fit model
#             self.model = self.create_model()
#             self.model.fit(X_train_subset[self.features], y_train_subset)
            
#             # Get best equation
#             self.equation = str(self.model.sympy())
#             print(f"Best equation found: {self.equation}")
            
#             # Make predictions
#             train_pred = self.model.predict(X_train_subset[self.features])
#             valid_pred = self.model.predict(X_valid[self.features])
#             test_pred = self.model.predict(X_test[self.features])
            
#             # Calculate metrics
#             metrics = {
#                 'train_size': train_size,
#                 'train_mae': mean_absolute_error(y_train_subset, train_pred),
#                 'valid_mae': mean_absolute_error(y_valid, valid_pred),
#                 'test_mae': mean_absolute_error(y_test, test_pred)
#             }
            
#             # Save results
#             self.save_results(output_dir, metrics, train_pred, valid_pred, test_pred,
#                             y_train_subset, y_valid, y_test)
            
#             return metrics
            
#         except Exception as e:
#             print(f"Error in model fitting for size {train_size}: {str(e)}")
#             raise
    
#     def save_results(self, output_dir, metrics, train_pred, valid_pred, test_pred,
#                     y_train, y_valid, y_test):
#         """Save model results and predictions for a specific training size"""
#         results = {
#             'timestamp': datetime.now().isoformat(),
#             'equation': self.equation,
#             'metrics': metrics,
#             'features_used': self.features
#         }
        
#         # Save results as JSON
#         with open(os.path.join(output_dir, 'results.json'), 'w') as f:
#             json.dump(results, f, indent=4)
        
#         # Save predictions
#         predictions = {
#             'train': pd.DataFrame({
#                 'true_values': y_train,
#                 'predictions': train_pred,
#                 'mae': abs(y_train - train_pred)
#             }),
#             'valid': pd.DataFrame({
#                 'true_values': y_valid,
#                 'predictions': valid_pred,
#                 'mae': abs(y_valid - valid_pred)
#             }),
#             'test': pd.DataFrame({
#                 'true_values': y_test,
#                 'predictions': test_pred,
#                 'mae': abs(y_test - test_pred)
#             })
#         }
        
#         for name, df in predictions.items():
#             df.to_csv(os.path.join(output_dir, f'{name}_predictions.csv'),
#                      index=False)


# def main():
#     # Define paths for datasets
#     train_data_path = "/home/kunchapus/projects/PolyMetriX/src/polymetrix/sym_datasets/Polymer_Tg_new_featurizers_20_09_2024.csv"
#     test_data_path = "/home/kunchapus/projects/PolyMetriX/src/polymetrix/sym_datasets/mdpi_no_leakage_12_12_24_featurizers.csv"
    
#     # Define features to use
#     features = [
#         "num_rotatable_bonds_fullpolymerfeaturizer",
#         "sp2_carbon_count_fullpolymerfeaturizer",
#         "balaban_j_index_fullpolymerfeaturizer",
#         "num_hbond_acceptors_fullpolymerfeaturizer",
#         "molecular_weight_fullpolymerfeaturizer",
#         "num_rings_fullpolymerfeaturizer",
#         "num_hbond_donors_fullpolymerfeaturizer",
#         "num_atoms_sidechainfeaturizer_sum"
#     ]
    
#     try:
#         # Load datasets
#         train_df = pd.read_csv(train_data_path)
#         test_df = pd.read_csv(test_data_path)
#         print(f"Training data shape: {train_df.shape}")
#         print(f"Test data shape: {test_df.shape}")
        
#         # Split data into features and target
#         X_train = train_df[features]
#         y_train = train_df["Exp_Tg(K)"]
#         X_test = test_df[features]
#         y_test = test_df["Exp_Tg(K)"]
        
#         # Create train/validation split
#         X_train_final, X_valid, y_train_final, y_valid = train_test_split(
#             X_train, y_train, test_size=0.1, random_state=42
#         )
        
#         # Define training sizes
#         train_sizes = [50] #100, 300, 500, 1000, 2000, 3000, 4000, 5000, 6000, len(X_train_final)
        
#         # Create model
#         model = SimpleSymbolicRegression(features)
        
#         # Store all results
#         all_results = []
        
#         # Train for each size
#         for size in train_sizes:
#             print(f"\n{'='*50}")
#             print(f"Training with {size} samples")
#             metrics = model.fit_for_size(size, X_train_final, y_train_final, 
#                                        X_valid, y_valid, X_test, y_test)
#             all_results.append(metrics)
        
#         # Save summary of all results
#         summary_df = pd.DataFrame(all_results)
#         summary_df.to_csv(os.path.join(model.base_dir, 'training_size_summary.csv'), index=False)
        
#         # Print final summary
#         print("\nTraining Size Results Summary:")
#         print(summary_df.to_string(index=False))
        
#     except Exception as e:
#         print(f"Error in main execution: {str(e)}")
#         raise

# if __name__ == "__main__":
#     main()




import pandas as pd
import numpy as np
import os
import json
from datetime import datetime
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error
from pysr import PySRRegressor


class SimpleSymbolicRegression:
    def __init__(self, features, base_dir="symbolic_regression_results", seeds=[42, 43, 45]):
        """Initialize the symbolic regression model"""
        self.features = features
        self.base_dir = base_dir
        self.model = None
        self.equation = None
        self.seeds = seeds
        
        # Create base directory if it doesn't exist
        os.makedirs(base_dir, exist_ok=True)
        
    def create_model(self):
        """Create and configure the PySR model"""
        model_params = {
            'binary_operators': ["+", "*", "-", "/"],
            'unary_operators': ["exp", "square", "log10", "cube"],
            'loss': "loss(prediction, target) = abs(prediction - target)",
            'niterations': 2000,
            'early_stop_condition': "stop_if(loss, complexity) = loss < 20 && complexity < 10",
        }
        
        return PySRRegressor(**model_params)
    
    def fit_for_size_and_seed(self, train_size, seed, X_train, y_train, X_valid, y_valid, X_test, y_test):
        """Fit model for a specific training size and random seed"""
        print(f"\nTraining model with {train_size} samples (seed {seed})...")
        
        # Create directory for this training size and seed
        output_dir = os.path.join(self.base_dir, f"train_size_{train_size}", f"seed_{seed}")
        os.makedirs(output_dir, exist_ok=True)
        
        try:
            # Set random seed for reproducibility
            np.random.seed(seed)
            
            # Sample training data if needed
            if train_size < len(X_train):
                sample_indices = np.random.choice(len(X_train), size=train_size, replace=False)
                X_train_subset = X_train.iloc[sample_indices]
                y_train_subset = y_train.iloc[sample_indices]
            else:
                X_train_subset = X_train
                y_train_subset = y_train
            
            # Create and fit model
            self.model = self.create_model()
            self.model.fit(X_train_subset[self.features], y_train_subset)
            
            # Get best equation
            self.equation = str(self.model.sympy())
            print(f"Best equation found: {self.equation}")
            
            # Make predictions
            train_pred = self.model.predict(X_train_subset[self.features])
            valid_pred = self.model.predict(X_valid[self.features])
            test_pred = self.model.predict(X_test[self.features])
            
            # Calculate metrics
            metrics = {
                'train_size': train_size,
                'seed': seed,
                'train_mae': mean_absolute_error(y_train_subset, train_pred),
                'valid_mae': mean_absolute_error(y_valid, valid_pred),
                'test_mae': mean_absolute_error(y_test, test_pred)
            }
            
            # Save results
            self.save_results(output_dir, metrics, train_pred, valid_pred, test_pred,
                            y_train_subset, y_valid, y_test)
            
            return metrics
            
        except Exception as e:
            print(f"Error in model fitting for size {train_size}, seed {seed}: {str(e)}")
            raise
    
    def fit_for_size(self, train_size, X_train, y_train, X_valid, y_valid, X_test, y_test):
        """Fit model for a specific training size across multiple seeds"""
        all_seed_metrics = []
        
        for seed in self.seeds:
            metrics = self.fit_for_size_and_seed(
                train_size, seed, X_train, y_train, X_valid, y_valid, X_test, y_test
            )
            all_seed_metrics.append(metrics)
        
        # Calculate aggregate statistics
        test_maes = [m['test_mae'] for m in all_seed_metrics]
        aggregate_metrics = {
            'train_size': train_size,
            'mean_test_mae': np.mean(test_maes),
            'std_test_mae': np.std(test_maes),
            'individual_runs': all_seed_metrics
        }
        
        # Save aggregate results
        output_dir = os.path.join(self.base_dir, f"train_size_{train_size}")
        with open(os.path.join(output_dir, 'aggregate_results.json'), 'w') as f:
            json.dump(aggregate_metrics, f, indent=4)
        
        return aggregate_metrics
    
    def save_results(self, output_dir, metrics, train_pred, valid_pred, test_pred,
                    y_train, y_valid, y_test):
        """Save model results and predictions for a specific training size and seed"""
        results = {
            'timestamp': datetime.now().isoformat(),
            'equation': self.equation,
            'metrics': metrics,
            'features_used': self.features
        }
        
        # Save results as JSON
        with open(os.path.join(output_dir, 'results.json'), 'w') as f:
            json.dump(results, f, indent=4)
        
        # Save predictions
        predictions = {
            'train': pd.DataFrame({
                'true_values': y_train,
                'predictions': train_pred,
                'mae': abs(y_train - train_pred)
            }),
            'valid': pd.DataFrame({
                'true_values': y_valid,
                'predictions': valid_pred,
                'mae': abs(y_valid - valid_pred)
            }),
            'test': pd.DataFrame({
                'true_values': y_test,
                'predictions': test_pred,
                'mae': abs(y_test - test_pred)
            })
        }
        
        for name, df in predictions.items():
            df.to_csv(os.path.join(output_dir, f'{name}_predictions.csv'),
                     index=False)


def main():
    # Define paths for datasets
    train_data_path = "/home/ta45woj/PolyMetriX/src/polymetrix/sym_datasets/Polymer_Tg_new_featurizers_20_09_2024.csv"
    test_data_path = "/home/ta45woj/PolyMetriX/src/polymetrix/sym_datasets/mdpi_no_leakage_12_12_24_featurizers.csv"
    
    # Define features to use
    features = [
        "num_rotatable_bonds_fullpolymerfeaturizer",
        "sp2_carbon_count_fullpolymerfeaturizer",
        "balaban_j_index_fullpolymerfeaturizer",
        "num_hbond_acceptors_fullpolymerfeaturizer",
        "molecular_weight_fullpolymerfeaturizer",
        "num_hbond_donors_fullpolymerfeaturizer",
        "num_atoms_sidechainfeaturizer_sum",
        # "num_rings_fullpolymerfeaturizer"
    ]
    
    try:
        # Load datasets
        train_df = pd.read_csv(train_data_path)
        test_df = pd.read_csv(test_data_path)
        print(f"Training data shape: {train_df.shape}")
        print(f"Test data shape: {test_df.shape}")
        
        # Split data into features and target
        X_train = train_df[features]
        y_train = train_df["Exp_Tg(K)"]
        X_test = test_df[features]
        y_test = test_df["Exp_Tg(K)"]
        
        # Create train/validation split with fixed random state
        X_train_final, X_valid, y_train_final, y_valid = train_test_split(
            X_train, y_train, test_size=0.1, random_state=42
        )
        
        # Define training sizes
        train_sizes = [100] #50, 100, 300, 500, 1000, 2000, 3000, 4000, 5000, 6000, len(X_train_final)
        
        # Create model with specified seeds
        model = SimpleSymbolicRegression(features, seeds=[40])  # 42, 43, 44
        
        # Store all results
        all_results = []
        
        # Train for each size
        for size in train_sizes:
            print(f"\n{'='*50}")
            print(f"Training with {size} samples across {len(model.seeds)} random seeds {model.seeds}")
            metrics = model.fit_for_size(size, X_train_final, y_train_final, 
                                       X_valid, y_valid, X_test, y_test)
            all_results.append(metrics)
        
        # Create summary DataFrame
        summary_df = pd.DataFrame([{
            'train_size': r['train_size'],
            'mean_test_mae': r['mean_test_mae'],
            'std_test_mae': r['std_test_mae']
        } for r in all_results])
        
        # Save summary of all results
        summary_df.to_csv(os.path.join(model.base_dir, 'training_size_summary.csv'), index=False)
        
        # Print final summary
        print("\nTraining Size Results Summary:")
        print(summary_df.to_string(index=False))
        
    except Exception as e:
        print(f"Error in main execution: {str(e)}")
        raise

if __name__ == "__main__":
    main()