# import pandas as pd
# import numpy as np
# from datetime import datetime
# from sklearn.metrics import mean_absolute_error
# from pysr import PySRRegressor
# from sklearn.model_selection import train_test_split
# import os
# import json
# import shutil
# import glob
# import traceback

# class SymbolicRegressionBoosting:
#     def __init__(self, base_features=None, output_dir="boosting_results"):
#         self.base_features = base_features.copy() if base_features else []
#         self.available_features = self.base_features.copy()
#         self.output_dir = output_dir
#         self.boosted_models = []
        
#         # Create output directory if it doesn't exist
#         os.makedirs(output_dir, exist_ok=True)

#     def create_pysr_model(self):
#         model_params = {
#             'binary_operators': ["+", "*", "-", "/"],
#             'unary_operators': ["exp", "square", "log10", "cube"],
#             'extra_sympy_mappings': {"inv": lambda x: 1 / x, "sqrt": lambda x: x**0.5},
#             'loss': "loss(prediction, target) = abs(prediction - target)",
#             'niterations': 1,
#             'early_stop_condition': "stop_if(loss, complexity) = loss < 20 && complexity < 10",
#         }
#         return PySRRegressor(**model_params)

#     def organize_hall_of_fame_files(self):
#         round_dir = os.path.join(self.output_dir, "round_1")
#         os.makedirs(round_dir, exist_ok=True)
        
#         # Look for hall of fame files in current directory
#         pattern = "hall_of_fame_*.csv"
#         hall_of_fame_files = glob.glob(pattern)
        
#         for file in hall_of_fame_files:
#             if os.path.exists(file):
#                 dest_file = os.path.join(round_dir, file)
#                 dest_pkl = os.path.join(round_dir, f"{os.path.splitext(file)[0]}.pkl")
                
#                 shutil.move(file, dest_file)
                
#                 pkl_file = f"{os.path.splitext(file)[0]}.pkl"
#                 if os.path.exists(pkl_file):
#                     shutil.move(pkl_file, dest_pkl)

#     def save_predictions(self, train_pred, valid_pred, test_pred, y_train, y_valid, y_test, train_mae, valid_mae, test_mae):
#         round_dir = os.path.join(self.output_dir, "round_1")
        
#         predictions = {
#             'train_predictions': train_pred.tolist(),
#             'valid_predictions': valid_pred.tolist(),
#             'test_predictions': test_pred.tolist(),
#             'train_mae': float(train_mae),
#             'valid_mae': float(valid_mae),
#             'test_mae': float(test_mae)
#         }
        
#         with open(os.path.join(round_dir, "predictions.json"), 'w') as f:
#             json.dump(predictions, f)

#     def extract_features_from_equation(self, equation):
#         equation_str = str(equation)
#         return {feature for feature in self.available_features if feature in equation_str}

#     def save_round_summary(self, model_info):
#         round_dir = os.path.join(self.output_dir, "round_1")
#         summary = {
#             "round": 1,
#             "timestamp": datetime.now().isoformat(),
#             "equation": str(model_info['equation']),
#             "train_mae": float(model_info['train_mae']),
#             "valid_mae": float(model_info['valid_mae']),
#             "test_mae": float(model_info['test_mae']),
#             "used_features": list(model_info['used_features'])
#         }
        
#         with open(os.path.join(round_dir, "round_summary.json"), 'w') as f:
#             json.dump(summary, f, indent=4)

#     def fit(self, X_train, y_train, X_valid, y_valid, X_test, y_test):
#         print("\nStarting model fitting process")
#         print(f"Training data shape: {X_train.shape}")
#         print(f"Validation data shape: {X_valid.shape}")
#         print(f"Test data shape: {X_test.shape}")
        
#         try:
#             # Create and fit model
#             model = self.create_pysr_model()
#             X_train_subset = X_train[self.available_features]
#             model.fit(X_train_subset, y_train)
            
#             # Organize files
#             self.organize_hall_of_fame_files()
            
#             # Load the best model
#             round_dir = os.path.join(self.output_dir, "round_1")
#             pkl_files = glob.glob(os.path.join(round_dir, "hall_of_fame_*.pkl"))
#             if not pkl_files:
#                 raise ValueError("No PKL files found")
            
#             latest_pkl = max(pkl_files, key=os.path.getctime)
#             loaded_model = PySRRegressor.from_file(latest_pkl)
#             best_equation = str(loaded_model.sympy())
            
#             # Make predictions
#             X_valid_subset = X_valid[self.available_features]
#             X_test_subset = X_test[self.available_features]
            
#             train_pred = loaded_model.predict(X_train_subset)
#             valid_pred = loaded_model.predict(X_valid_subset)
#             test_pred = loaded_model.predict(X_test_subset)
            
#             # Calculate metrics
#             train_mae = mean_absolute_error(y_train, train_pred)
#             valid_mae = mean_absolute_error(y_valid, valid_pred)
#             test_mae = mean_absolute_error(y_test, test_pred)
            
#             # Save predictions
#             self.save_predictions(train_pred, valid_pred, test_pred, 
#                                 y_train, y_valid, y_test,
#                                 train_mae, valid_mae, test_mae)
            
#             # Extract features and create model info
#             used_features = self.extract_features_from_equation(best_equation)
#             model_info = {
#                 'model': loaded_model,
#                 'equation': best_equation,
#                 'used_features': used_features,
#                 'train_mae': train_mae,
#                 'valid_mae': valid_mae,
#                 'test_mae': test_mae
#             }
            
#             self.boosted_models.append(model_info)
#             self.save_round_summary(model_info)
            
#             # Print results
#             print("\nModel Results:")
#             print(f"Best Equation: {best_equation}")
#             print(f"Train MAE: {train_mae:.4f}")
#             print(f"Valid MAE: {valid_mae:.4f}")
#             print(f"Test MAE: {test_mae:.4f}")
#             print(f"Features used: {sorted(used_features)}")
            
#         except Exception as e:
#             print(f"Error in model fitting: {str(e)}")
#             print(f"Traceback:\n{traceback.format_exc()}")

# def main():
#     # Define paths for datasets
#     train_data_path = "/home/ta45woj/PolyMetriX/src/polymetrix/sym_datasets/Polymer_Tg_new_featurizers_20_09_2024.csv"
#     test_data_path = "/home/ta45woj/PolyMetriX/src/polymetrix/sym_datasets/uncommon_mdpi_trained_set_unique.csv"
    
#     # Load datasets
#     train_df = pd.read_csv(train_data_path)
#     test_df = pd.read_csv(test_data_path)
    
#     features = [
#         "sp2_carbon_count_fullpolymerfeaturizer",
#         "num_rotatable_bonds_fullpolymerfeaturizer",
#         "num_aromatic_rings_fullpolymerfeaturizer",
#         "bridging_rings_count_fullpolymerfeaturizer",
#         "balaban_j_index_fullpolymerfeaturizer",
#         "slogp_vsa1_fullpolymerfeaturizer",
#         "num_atoms_backbonefeaturizer",
#         "num_aliphatic_heterocycles_fullpolymerfeaturizer",
#         "fp_density_morgan1_fullpolymerfeaturizer",
#         "numsidechainfeaturizer",
#         "num_atoms_sidechainfeaturizer_mean",
#         # "num_rings_fullpolymerfeaturizer",
#     ]
    
#     # Split data
#     X_train = train_df[features]
#     y_train = train_df["Exp_Tg(K)"]
#     X_test = test_df[features]
#     y_test = test_df["Exp_Tg(K)"]

#     # Create validation split
#     X_train_final, X_valid, y_train_final, y_valid = train_test_split(
#         X_train, y_train, test_size=0.1, random_state=42
#     )

#     # Create and fit model
#     model = SymbolicRegressionBoosting(base_features=features)
#     model.fit(X_train_final, y_train_final, X_valid, y_valid, X_test, y_test)

# if __name__ == "__main__":
#     main()



import pandas as pd
import numpy as np
from datetime import datetime
from sklearn.metrics import mean_absolute_error
from pysr import PySRRegressor
from sklearn.model_selection import train_test_split
import os
import json
import shutil
import glob
import traceback

class SymbolicRegressionBoosting:
    def __init__(self, base_features=None, output_dir="boosting_results"):
        self.base_features = base_features.copy() if base_features else []
        self.available_features = self.base_features.copy()
        self.output_dir = output_dir
        self.boosted_models = []
        os.makedirs(output_dir, exist_ok=True)

    def create_pysr_model(self, random_seed):
        model_params = {
            'binary_operators': ["+", "*", "-", "/"],
            'unary_operators': ["exp", "square", "log10", "cube"],
            'extra_sympy_mappings': {"inv": lambda x: 1 / x, "sqrt": lambda x: x**0.5},
            'loss': "loss(prediction, target) = abs(prediction - target)",
            'niterations': 1000,
            'early_stop_condition': "stop_if(loss, complexity) = loss < 20 && complexity < 10",
            'random_state': random_seed  # Added random seed
        }
        return PySRRegressor(**model_params)

    def organize_hall_of_fame_files(self, seed):
        round_dir = os.path.join(self.output_dir, f"seed_{seed}")
        os.makedirs(round_dir, exist_ok=True)
        
        pattern = "hall_of_fame_*.csv"
        hall_of_fame_files = glob.glob(pattern)
        
        for file in hall_of_fame_files:
            if os.path.exists(file):
                dest_file = os.path.join(round_dir, file)
                dest_pkl = os.path.join(round_dir, f"{os.path.splitext(file)[0]}.pkl")
                
                shutil.move(file, dest_file)
                
                pkl_file = f"{os.path.splitext(file)[0]}.pkl"
                if os.path.exists(pkl_file):
                    shutil.move(pkl_file, dest_pkl)

    def save_predictions(self, train_pred, valid_pred, test_pred, train_mae, valid_mae, test_mae, seed):
        round_dir = os.path.join(self.output_dir, f"seed_{seed}")
        
        predictions = {
            'train_predictions': train_pred.tolist(),
            'valid_predictions': valid_pred.tolist(),
            'test_predictions': test_pred.tolist(),
            'train_mae': float(train_mae),
            'valid_mae': float(valid_mae),
            'test_mae': float(test_mae)
        }
        
        with open(os.path.join(round_dir, "predictions.json"), 'w') as f:
            json.dump(predictions, f)

    def extract_features_from_equation(self, equation):
        equation_str = str(equation)
        return {feature for feature in self.available_features if feature in equation_str}

    def save_round_summary(self, model_info, seed):
        round_dir = os.path.join(self.output_dir, f"seed_{seed}")
        summary = {
            "seed": seed,
            "timestamp": datetime.now().isoformat(),
            "equation": str(model_info['equation']),
            "train_mae": float(model_info['train_mae']),
            "valid_mae": float(model_info['valid_mae']),
            "test_mae": float(model_info['test_mae']),
            "used_features": list(model_info['used_features'])
        }
        
        with open(os.path.join(round_dir, "round_summary.json"), 'w') as f:
            json.dump(summary, f, indent=4)

    def fit_single_seed(self, X_train, y_train, X_valid, y_valid, X_test, y_test, seed):
        print(f"\nFitting model with seed {seed}")
        try:
            model = self.create_pysr_model(seed)
            X_train_subset = X_train[self.available_features]
            model.fit(X_train_subset, y_train)
            
            self.organize_hall_of_fame_files(seed)
            
            round_dir = os.path.join(self.output_dir, f"seed_{seed}")
            pkl_files = glob.glob(os.path.join(round_dir, "hall_of_fame_*.pkl"))
            if not pkl_files:
                raise ValueError(f"No PKL files found for seed {seed}")
            
            latest_pkl = max(pkl_files, key=os.path.getctime)
            loaded_model = PySRRegressor.from_file(latest_pkl)
            best_equation = str(loaded_model.sympy())
            
            X_valid_subset = X_valid[self.available_features]
            X_test_subset = X_test[self.available_features]
            
            train_pred = loaded_model.predict(X_train_subset)
            valid_pred = loaded_model.predict(X_valid_subset)
            test_pred = loaded_model.predict(X_test_subset)
            
            train_mae = mean_absolute_error(y_train, train_pred)
            valid_mae = mean_absolute_error(y_valid, valid_pred)
            test_mae = mean_absolute_error(y_test, test_pred)
            
            self.save_predictions(train_pred, valid_pred, test_pred,
                                train_mae, valid_mae, test_mae, seed)
            
            used_features = self.extract_features_from_equation(best_equation)
            model_info = {
                'model': loaded_model,
                'equation': best_equation,
                'used_features': used_features,
                'train_mae': train_mae,
                'valid_mae': valid_mae,
                'test_mae': test_mae
            }
            
            self.save_round_summary(model_info, seed)
            
            print(f"\nResults for seed {seed}:")
            print(f"Best Equation: {best_equation}")
            print(f"Train MAE: {train_mae:.4f}")
            print(f"Valid MAE: {valid_mae:.4f}")
            print(f"Test MAE: {test_mae:.4f}")
            
            return model_info
            
        except Exception as e:
            print(f"Error in model fitting for seed {seed}: {str(e)}")
            print(f"Traceback:\n{traceback.format_exc()}")
            return None

def main():
    # Define paths for datasets
    train_data_path = "/home/ta45woj/PolyMetriX/src/polymetrix/sym_datasets/Polymer_Tg_new_featurizers_20_09_2024.csv"
    test_data_path = "/home/ta45woj/PolyMetriX/src/polymetrix/sym_datasets/uncommon_mdpi_trained_set_unique.csv"
    
    # Load datasets
    train_df = pd.read_csv(train_data_path)
    test_df = pd.read_csv(test_data_path)
    
    features = [
        "sp2_carbon_count_fullpolymerfeaturizer",
        "num_rotatable_bonds_fullpolymerfeaturizer",
        "num_aromatic_rings_fullpolymerfeaturizer",
        "bridging_rings_count_fullpolymerfeaturizer",
        "balaban_j_index_fullpolymerfeaturizer",
        "slogp_vsa1_fullpolymerfeaturizer",
        "num_atoms_backbonefeaturizer",
        "num_aliphatic_heterocycles_fullpolymerfeaturizer",
        "fp_density_morgan1_fullpolymerfeaturizer",
        "numsidechainfeaturizer",
        "num_atoms_sidechainfeaturizer_mean",
    ]
    
    # Split data
    X_full = train_df[features]
    y_full = train_df["Exp_Tg(K)"]
    X_test = test_df[features]
    y_test = test_df["Exp_Tg(K)"]
    
    # Run multiple seeds
    n_seeds = 5  # Number of different seeds to try
    seeds = range(42, 42 + n_seeds)  # Generate seeds starting from 42
    
    results = []
    train_maes = []
    valid_maes = []
    test_maes = []
    
    for seed in seeds:
        # Create train/validation split with current seed
        X_train, X_valid, y_train, y_valid = train_test_split(
            X_full, y_full, test_size=0.1, random_state=42  # Keep this seed fixed
        )
        
        # Create and fit model with current seed
        model = SymbolicRegressionBoosting(base_features=features)
        result = model.fit_single_seed(X_train, y_train, X_valid, y_valid, X_test, y_test, seed)
        
        if result is not None:
            results.append(result)
            train_maes.append(result['train_mae'])
            valid_maes.append(result['valid_mae'])
            test_maes.append(result['test_mae'])
    
    # Calculate statistics
    train_mean = np.mean(train_maes)
    train_std = np.std(train_maes)
    valid_mean = np.mean(valid_maes)
    valid_std = np.std(valid_maes)
    test_mean = np.mean(test_maes)
    test_std = np.std(test_maes)
    
    print("\nFinal Results Across All Seeds:")
    print(f"Train MAE: {train_mean:.2f} ± {train_std:.2f}")
    print(f"Valid MAE: {valid_mean:.2f} ± {valid_std:.2f}")
    print(f"Test MAE: {test_mean:.2f} ± {test_std:.2f}")
    
    # Save overall results
    overall_results = {
        "n_seeds": n_seeds,
        "seeds": list(seeds),
        "train_mae_mean": float(train_mean),
        "train_mae_std": float(train_std),
        "valid_mae_mean": float(valid_mean),
        "valid_mae_std": float(valid_std),
        "test_mae_mean": float(test_mean),
        "test_mae_std": float(test_std),
        "individual_results": [
            {
                "seed": seed,
                "train_mae": float(mae_train),
                "valid_mae": float(mae_valid),
                "test_mae": float(mae_test),
                "equation": str(result['equation'])
            }
            for seed, mae_train, mae_valid, mae_test, result in 
            zip(seeds, train_maes, valid_maes, test_maes, results)
        ]
    }
    
    with open("overall_results.json", 'w') as f:
        json.dump(overall_results, f, indent=4)

if __name__ == "__main__":
    main()