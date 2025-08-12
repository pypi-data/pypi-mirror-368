import pandas as pd
import numpy as np
import os
import json
import shutil
import glob
from datetime import datetime
from concurrent.futures import ProcessPoolExecutor
from sklearn.metrics import mean_absolute_error
from pysr import PySRRegressor
from sklearn.model_selection import train_test_split
import pickle
import traceback

class SymbolicRegressionBoosting:
    def __init__(self, n_boosting_rounds=3, start_round=1, base_features=None, output_dir="boosting_results"):
        """Modified initialization to store training and test data"""
        self.n_boosting_rounds = n_boosting_rounds
        self.start_round = start_round
        self.boosted_models = []
        self.used_features = set()
        self.base_features = base_features.copy() if base_features else []
        self.available_features = base_features.copy() if base_features else []
        self.feature_history = []
        self.results_history = []
        self.output_dir = output_dir
        
        # Store references to training and test data
        self.y_train = None
        self.y_test = None
        
        # Load previous rounds' data if starting from round > 1
        if start_round > 1:
            self.load_previous_rounds_data(start_round - 1)

        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)

        # Optimize CPU usage
        self.n_cores = os.cpu_count()
        # self.n_processes = 48

        print(f"Initializing SymbolicRegressionBoosting:")
        print(f"Starting from round: {start_round}")
        print(f"Total boosting rounds: {n_boosting_rounds}")
        # print(f"Using {self.n_processes} CPU cores")
        print(f"Output directory: {self.output_dir}")
        
    
    def load_previous_rounds_data(self, last_round):
        """Load models and predictions from previous rounds"""
        print(f"\nLoading data from previous {last_round} rounds...")
        
        self.previous_predictions_train = []
        self.previous_predictions_test = []
        
        for round_num in range(1, last_round + 1):
            round_dir = os.path.join(self.output_dir, f"round_{round_num}")
            
            # Load model
            pkl_files = glob.glob(os.path.join(round_dir, "hall_of_fame_*.pkl"))
            if not pkl_files:
                raise ValueError(f"No PKL files found for round {round_num}")
            
            latest_pkl = max(pkl_files, key=os.path.getctime)
            loaded_model = PySRRegressor.from_file(latest_pkl)
            
            # Load predictions
            predictions_file = os.path.join(round_dir, "predictions.json")
            with open(predictions_file, 'r') as f:
                predictions = json.load(f)
            
            # Store loaded data
            model_info = {
                'model': loaded_model,
                'equation': str(loaded_model.sympy()),
                'used_features': self.extract_features_from_equation(str(loaded_model.sympy())),
                'train_mae': predictions['train_mae'],
                'test_mae': predictions['test_mae']
            }
            
            self.boosted_models.append(model_info)
            self.previous_predictions_train.append(np.array(predictions['train_predictions']))
            self.previous_predictions_test.append(np.array(predictions['test_predictions']))
            
            # Update feature pools
            self.used_features.update(model_info['used_features'])
            self.available_features = list(set(self.base_features) - self.used_features)
            
            print(f"Loaded round {round_num}:")
            print(f"Equation: {model_info['equation']}")
            print(f"Features used: {sorted(model_info['used_features'])}")
            print(f"MAE (train/test): {model_info['train_mae']:.4f}/{model_info['test_mae']:.4f}")
            
        
    def save_round_predictions(self, round_num, train_pred, test_pred, train_mae, test_mae):
        """Save predictions and metrics for a round, including CSV files with ground truth"""
        round_dir = os.path.join(self.output_dir, f"round_{round_num}")
        
        # Save the original predictions.json
        predictions = {
            'train_predictions': train_pred.tolist(),
            'test_predictions': test_pred.tolist(),
            'train_mae': float(train_mae),
            'test_mae': float(test_mae)
        }
        
        with open(os.path.join(round_dir, "predictions.json"), 'w') as f:
            json.dump(predictions, f)
        
        # Save training data and predictions to CSV
        train_df = pd.DataFrame({
            'ground_truth': self.y_train,
            'prediction': train_pred,
            'cumulative_prediction': self.predictions_train + train_pred
        })
        train_df.to_csv(os.path.join(round_dir, f"train_{round_num}.csv"), index=False)
        
        # Save test data and predictions to CSV
        test_df = pd.DataFrame({
            'ground_truth': self.y_test,
            'prediction': test_pred,
            'cumulative_prediction': self.predictions_test + test_pred
        })
        test_df.to_csv(os.path.join(round_dir, f"test_{round_num}.csv"), index=False)
    

    def create_pysr_model(self, round_num):
        # Create round directory
        round_dir = os.path.join(self.output_dir, f"round_{round_num}")
        os.makedirs(round_dir, exist_ok=True)

        model_params = {
            'binary_operators': ["+", "*", "-", "/"],
            'unary_operators': ["exp", "square","log10", "cube"],
            'extra_sympy_mappings': {"inv": lambda x: 1 / x, "sqrt": lambda x: x**0.5},
            'loss': "loss(prediction, target) = abs(prediction - target)",
            'niterations': 20000,
            'early_stop_condition': "stop_if(loss, complexity) = loss < 20 && complexity < 10",
        }

        print(f"Creating PySR model for round {round_num} with parameters:")
        for param, value in model_params.items():
            if param not in ['extra_sympy_mappings']:
                print(f"{param}: {value}")

        return PySRRegressor(**model_params)

    def organize_hall_of_fame_files(self, round_num):
        """Organize hall of fame files into the appropriate round directory"""
        round_dir = os.path.join(self.output_dir, f"round_{round_num}")
        
        # Look for hall of fame files in the current directory
        pattern = "hall_of_fame_*.csv"
        hall_of_fame_files = glob.glob(pattern)
        
        for file in hall_of_fame_files:
            if os.path.exists(file):
                # Define destination paths
                dest_file = os.path.join(round_dir, file)
                dest_backup = os.path.join(round_dir, f"{file}.bkup")
                dest_pkl = os.path.join(round_dir, f"{os.path.splitext(file)[0]}.pkl")
                
                # Move the CSV file
                shutil.move(file, dest_file)
                print(f"Moved {file} to {dest_file}")
                
                # Create backup
                shutil.copy2(dest_file, dest_backup)
                print(f"Created backup at {dest_backup}")
                
                # Handle pickle file if it exists
                pkl_file = f"{os.path.splitext(file)[0]}.pkl"
                if os.path.exists(pkl_file):
                    shutil.move(pkl_file, dest_pkl)
                    print(f"Moved {pkl_file} to {dest_pkl}")

    def save_round_summary(self, round_num, model_info):
        round_dir = os.path.join(self.output_dir, f"round_{round_num}")
        summary = {
            "round": round_num,
            "timestamp": datetime.now().isoformat(),
            "equation": str(model_info['equation']),
            "test_mae": float(model_info['test_mae']),
            "used_features": list(model_info['used_features']),
            "available_features": list(self.available_features)
        }
        
        with open(os.path.join(round_dir, "round_summary.json"), 'w') as f:
            json.dump(summary, f, indent=4)

    def extract_features_from_equation(self, equation):
        if not equation:
            return set()
        
        equation_str = str(equation)
        used_features = {feature for feature in self.available_features if feature in equation_str}
        
        print(f"Extracted features from equation: {used_features}")
        return used_features

    def update_feature_pools(self, new_used_features, round_number):
        print(f"Updating feature pools for round {round_number}")
        print(f"Features used in this round: {sorted(new_used_features)}")
        
        self.feature_history.append({
            'round': round_number,
            'features_used': new_used_features,
            'n_features_before': len(self.available_features)
        })
        
        self.used_features.update(new_used_features)
        self.available_features = list(set(self.available_features) - new_used_features)
        
        print(f"Total features used so far: {len(self.used_features)}")
        print(f"Remaining available features: {len(self.available_features)}")
        
        self.feature_history[-1]['n_features_after'] = len(self.available_features)

    def get_cumulative_equation(self, current_round):
        equation = " + ".join(str(model['equation']) for model in self.boosted_models[:current_round + 1])
        print(f"Generated cumulative equation up to round {current_round}")
        return equation

    def parallel_predict(self, model_info, X):
        model = model_info['model']
        used_features = model_info['used_features']
        X_subset = X[list(used_features)]
        try:
            return model.predict(X_subset)
        except Exception as e:
            print(f"Error in prediction: {str(e)}")
            return np.zeros(len(X))

    def predict(self, X):
        print(f"Making predictions for {len(X)} samples")
        predictions = np.zeros(len(X))
        
        with ProcessPoolExecutor(max_workers=self.n_processes) as executor:
            futures = []
            for model_info in self.boosted_models:
                future = executor.submit(self.parallel_predict, model_info, X)
                futures.append(future)
            
            for future in futures:
                try:
                    predictions += future.result()
                except Exception as e:
                    print(f"Error in parallel prediction: {str(e)}")
        
        print("Predictions completed")
        return predictions
    
    
    def check_for_existing_round(self, round_num):
        """Check if a round has already been run"""
        round_dir = os.path.join(self.output_dir, f"round_{round_num}")
        predictions_file = os.path.join(round_dir, "predictions.json")
        pkl_files = glob.glob(os.path.join(round_dir, "hall_of_fame_*.pkl"))
        
        if os.path.exists(round_dir) and os.path.exists(predictions_file) and pkl_files:
            raise ValueError(f"Round {round_num} has already been completed. Found existing files in {round_dir}")

    def check_mae_improvement(self, current_mae, previous_mae, min_improvement=0.001):
        """Check if MAE improvement meets minimum threshold"""
        if previous_mae is None:
            return True
        
        improvement = (previous_mae - current_mae) / previous_mae
        return improvement >= min_improvement
    
    def regenerate_round_files(self, round_num, X_train, y_train, X_test, y_test):
        self.y_train = y_train
        self.y_test = y_test
        """Regenerate files from PKL"""
        try:
            print(f"\nRegenerating files for round {round_num}")
            round_dir = os.path.join(self.output_dir, f"round_{round_num}")
            
            # Get cumulative predictions from previous rounds
            if round_num > 1:
                self.predictions_train = np.sum(self.previous_predictions_train, axis=0)
                self.predictions_test = np.sum(self.previous_predictions_test, axis=0)
            else:
                self.predictions_train = np.zeros_like(y_train, dtype=float)
                self.predictions_test = np.zeros_like(y_test, dtype=float)
            
            # Find PKL file
            pkl_files = glob.glob(os.path.join(round_dir, "hall_of_fame_*.pkl"))
            if not pkl_files:
                print(f"No PKL files found in {round_dir}")
                return False
                
            # Load model from PKL
            latest_pkl = max(pkl_files, key=os.path.getctime)
            loaded_model = PySRRegressor.from_file(latest_pkl)
            best_equation = str(loaded_model.sympy())
            print(f"Best equation found: {best_equation}")

            # Get features exactly like in the fit function
            X_train_round = X_train[self.available_features]
            X_test_round = X_test[self.available_features]
                
            # Make predictions using the same data subset as original training
            round_pred_train = loaded_model.predict(X_train_round)
            round_pred_test = loaded_model.predict(X_test_round)
            
            # Calculate MAEs using cumulative predictions
            train_mae = mean_absolute_error(y_train, self.predictions_train + round_pred_train)
            test_mae = mean_absolute_error(y_test, self.predictions_test + round_pred_test)
            
            # Save predictions.json
            self.save_round_predictions(round_num, round_pred_train, round_pred_test, train_mae, test_mae)
            
            # Extract features used in equation
            new_used_features = self.extract_features_from_equation(best_equation)
            
            # Create and save model info
            model_info = {
                'model': loaded_model,
                'equation': best_equation,
                'used_features': new_used_features,
                'train_mae': train_mae,
                'test_mae': test_mae,
                'round_predictions': {
                    'train': round_pred_train,
                    'test': round_pred_test
                }
            }
            
            # Add to boosted_models and update features
            self.boosted_models.append(model_info)
            self.update_feature_pools(new_used_features, round_num)
            
            # Save round summary
            self.save_round_summary(round_num, model_info)
            
            # Save results CSV
            self.save_results_csv()
            
            return True
                
        except Exception as e:
            print(f"Error regenerating files: {str(e)}")
            print(f"Traceback:\n{traceback.format_exc()}")
            return False
    
    
    def fit(self, X_train, y_train, X_test, y_test):
        """Modified fit function with early stopping and round checking"""
        self.y_train = y_train
        self.y_test = y_test
        # Check if round already exists
        self.check_for_existing_round(self.start_round)
        
        print("\n" + "="*80)
        print("Starting model fitting process")
        print(f"Training data shape: {X_train.shape}")
        print(f"Test data shape: {X_test.shape}")
        print(f"Starting from round: {self.start_round}")
        print("="*80 + "\n")

        # Check for PKL-only scenario
        round_dir = os.path.join(self.output_dir, f"round_{self.start_round}")
        predictions_file = os.path.join(round_dir, "predictions.json")
        pkl_files = glob.glob(os.path.join(round_dir, "hall_of_fame_*.pkl"))
        
        if os.path.exists(round_dir) and pkl_files and not os.path.exists(predictions_file):
            print(f"Found hall_of_fame files but missing other files in round {self.start_round}")
            print("Attempting to regenerate files...")
            if self.regenerate_round_files(self.start_round, X_train, y_train, X_test, y_test):
                print("Successfully regenerated all files!")
                return
            print("Failed to regenerate files")
            return
        
        # Initialize predictions arrays
        if self.start_round == 1:
            self.predictions_train = np.zeros_like(y_train, dtype=float)
            self.predictions_test = np.zeros_like(y_test, dtype=float)
        else:
            # Load cumulative predictions from previous rounds
            self.predictions_train = np.sum(self.previous_predictions_train, axis=0)
            self.predictions_test = np.sum(self.previous_predictions_test, axis=0)
        
        # Initial targets - if starting from round > 1, use residuals from previous rounds
        current_y_train = y_train - self.predictions_train
        current_y_test = y_test - self.predictions_test
        
        tracked_samples = range(min(5, len(y_train)))
        previous_mae = None if self.start_round == 1 else self.boosted_models[-1]['test_mae']

        # Rest of your original fit function remains exactly the same
        for round in range(self.start_round - 1, self.n_boosting_rounds):
            round_num = round + 1
            print(f"\n{'='*50}")
            print(f"Starting Boosting Round {round_num}/{self.n_boosting_rounds}")
            
            if round_num > 1:
                print(f"\nPrevious round MAE: {previous_mae:.4f}")
            
            if not self.available_features:
                print("\nNo more features available for boosting")
                break
                
            try:
                # Print round information
                if round_num == 1:
                    print("\nROUND 1:")
                    print("Target = Original Tg values")
                    print(f"Target range: {current_y_train.min():.2f} to {current_y_train.max():.2f}")
                else:
                    print(f"\nROUND {round_num}:")
                    print("Target = Residuals from previous round")
                    print(f"Previous round predictions stored: {len(self.boosted_models)}")
                    print(f"Current target range: {current_y_train.min():.2f} to {current_y_train.max():.2f}")
                    
                    for i in tracked_samples:
                        print(f"\nSample {i+1}:")
                        print(f"Original Tg: {y_train.iloc[i]:.2f}")
                        print(f"Cumulative prediction: {self.predictions_train[i]:.2f}")
                        print(f"Current residual: {current_y_train.iloc[i]:.2f}")
                
                # Create and fit model for this round
                print(f"\nFitting model for round {round_num}")
                print(f"Available features: {len(self.available_features)}")
                
                model = self.create_pysr_model(round_num)
                X_train_round = X_train[self.available_features]
                X_test_round = X_test[self.available_features]
                
                model.fit(X_train_round, current_y_train)
                
                # Organize hall of fame files
                self.organize_hall_of_fame_files(round_num)
                
                # Load equation and model from PKL
                best_equation, loaded_model = self.load_equations_from_pkl(round_num)
                if best_equation is None or loaded_model is None:
                    print(f"Failed to load model/equation for round {round_num}")
                    continue
                
                # Make predictions
                print(f"\nMaking predictions using loaded model...")
                try:
                    round_pred_train = loaded_model.predict(X_train_round)
                    round_pred_test = loaded_model.predict(X_test_round)
                    
                    # Save round predictions
                    train_mae = mean_absolute_error(y_train, self.predictions_train + round_pred_train)
                    test_mae = mean_absolute_error(y_test, self.predictions_test + round_pred_test)
                    
                    # Check for MAE improvement
                    if not self.check_mae_improvement(test_mae, previous_mae):
                        print(f"\nEarly stopping: MAE improvement less than minimum threshold")
                        print(f"Current MAE: {test_mae:.4f}")
                        print(f"Previous MAE: {previous_mae:.4f}")
                        break
                    
                    self.save_round_predictions(round_num, round_pred_train, round_pred_test, train_mae, test_mae)
                    
                    # Update cumulative predictions
                    self.predictions_train += round_pred_train
                    self.predictions_test += round_pred_test
                    
                    # Calculate new residuals
                    current_y_train = y_train - self.predictions_train
                    current_y_test = y_test - self.predictions_test
                    
                    # Extract features and update pools
                    new_used_features = self.extract_features_from_equation(best_equation)
                    self.update_feature_pools(new_used_features, round_num)
                    
                    # Store model information
                    model_info = {
                        'model': loaded_model,
                        'equation': best_equation,
                        'used_features': new_used_features,
                        'train_mae': train_mae,
                        'test_mae': test_mae,
                        'round_predictions': {
                            'train': round_pred_train,
                            'test': round_pred_test
                        }
                    }
                    
                    self.boosted_models.append(model_info)
                    self.save_round_summary(round_num, model_info)
                    
                    # Store results
                    self.results_history.append({
                        'Algorithm': f'SyRBo Stage {round_num}',
                        'Equation': best_equation,
                        'Train_MAE': train_mae,
                        'Test_MAE': test_mae,
                        'Prediction_Equation': self.get_cumulative_equation(round)
                    })
                    
                    # Print round statistics
                    print(f"\nRound {round_num} Statistics:")
                    print(f"Train MAE: {train_mae:.4f}")
                    print(f"Test MAE: {test_mae:.4f}")
                    print(f"Predictions - Train: [{round_pred_train.min():.2f}, {round_pred_train.max():.2f}]")
                    print(f"Predictions - Test: [{round_pred_test.min():.2f}, {round_pred_test.max():.2f}]")
                    print(f"Remaining features: {len(self.available_features)}")
                    
                    # Update previous_mae for next round
                    previous_mae = test_mae
                    
                except Exception as e:
                    print(f"Error in predictions: {str(e)}")
                    continue
                
            except Exception as e:
                print(f"\nError in round {round_num}: {str(e)}")
                print(f"Traceback:\n{traceback.format_exc()}")
                break
        
        print("\n" + "="*80)
        print("Model fitting completed")
        print(f"Rounds completed: {len(self.boosted_models)}")
        
        if self.boosted_models:
            print("\nFinal Metrics:")
            print(f"Train MAE: {train_mae:.4f}")
            print(f"Test MAE: {test_mae:.4f}")
            print("\nFeatures Used Per Round:")
            for i, model in enumerate(self.boosted_models, 1):
                print(f"Round {i}: {sorted(model['used_features'])}")
        
        print("="*80 + "\n")
        self.save_results_csv()


    def save_results_csv(self, filename=None):
        if filename is None:
            filename = os.path.join(self.output_dir, "test_results.csv")
        
        try:
            # Create detailed results similar to txt file
            results_data = []
            for i, model_info in enumerate(self.boosted_models, 1):
                results_data.append({
                    'Stage': i,
                    'Equation': str(model_info['equation']),
                    'Test_MAE': float(model_info['test_mae']),
                    'Train_MAE': float(model_info['train_mae']),
                    'Features_Used': sorted(model_info['used_features']),
                    'Cumulative_Equation': self.get_cumulative_equation(i-1)
                })
            
            pd.DataFrame(results_data).to_csv(filename, index=False)
            print(f"Results successfully saved to {filename}")
        except Exception as e:
            print(f"Error saving results to CSV: {str(e)}")

    def load_equations_from_pkl(self, round_num):
        """Load model and equations from PKL file using PySRRegressor.from_file()"""
        try:
            # Get the round directory
            round_dir = os.path.join(self.output_dir, f"round_{round_num}")
            if not os.path.exists(round_dir):
                print(f"Round directory not found: {round_dir}")
                return None, None
                
            # Find all PKL files in the round directory
            pkl_files = glob.glob(os.path.join(round_dir, "hall_of_fame_*.pkl"))
            
            if not pkl_files:
                print(f"No PKL files found in {round_dir}")
                return None, None
                
            # Use the most recent PKL file
            latest_pkl = max(pkl_files, key=os.path.getctime)
            print(f"Loading model from: {latest_pkl}")
            
            # Load model using from_file
            loaded_model = PySRRegressor.from_file(latest_pkl)
            print("Model loaded successfully")
            
            # Get equation using sympy()
            best_equation = str(loaded_model.sympy())
            print(f"Best equation found: {best_equation}")
            
            return best_equation, loaded_model
                
        except Exception as e:
            print(f"Error loading model from PKL: {str(e)}")
            print(f"Traceback:\n{traceback.format_exc()}")
            return None, None
    
    
    
def main():
    # Set all relevant thread environment variables
    os.environ["OMP_NUM_THREADS"] = "48"
    os.environ["MKL_NUM_THREADS"] = "48"
    os.environ["OPENBLAS_NUM_THREADS"] = "48"
    os.environ["NUMEXPR_NUM_THREADS"] = "48"

    print("Starting main execution")
    print(f"CPU Configuration:")
    print(f"Total CPU cores: {os.cpu_count()}")
    print(f"OpenMP threads: {os.environ.get('OMP_NUM_THREADS')}")
    print(f"MKL threads: {os.environ.get('MKL_NUM_THREADS')}")

    # Define paths for both training and test datasets
    train_data_path = "/home/ta45woj/PolyMetriX/src/polymetrix/sym_datasets/Polymer_Tg_new_featurizers_20_09_2024.csv"
    test_data_path = "/home/ta45woj/PolyMetriX/src/polymetrix/sym_datasets/uncommon_mdpi_trained_set.csv"
    
    print(f"Loading training data from: {train_data_path}")
    print(f"Loading test data from: {test_data_path}")
    
    try:
        # Load both datasets
        train_df = pd.read_csv(train_data_path)
        test_df = pd.read_csv(test_data_path)
        print(f"Training data loaded successfully. Shape: {train_df.shape}")
        print(f"Test data loaded successfully. Shape: {test_df.shape}")
    except Exception as e:
        print(f"Error loading data: {str(e)}")
        return
    
    features = [
        "sp2_carbon_count_fullpolymerfeaturizer",
        "num_rotatable_bonds_fullpolymerfeaturizer",
        "num_rings_fullpolymerfeaturizer",
        "num_aromatic_rings_fullpolymerfeaturizer",
        "bridging_rings_count_fullpolymerfeaturizer",
        "balaban_j_index_fullpolymerfeaturizer",
        "slogp_vsa1_fullpolymerfeaturizer",
        "num_atoms_backbonefeaturizer",
        "num_aliphatic_heterocycles_fullpolymerfeaturizer",
        "fp_density_morgan1_fullpolymerfeaturizer",
        "max_ring_size_fullpolymerfeaturizer",
        "fraction_bicyclic_rings_fullpolymerfeaturizer",
        "molecular_weight_fullpolymerfeaturizer",
        "num_non_aromatic_rings_fullpolymerfeaturizer",
        "double_bonds_fullpolymerfeaturizer"
    ]
    print(f"\nNumber of features: {len(features)}")
    print("Features list: " + ", ".join(features))

    # Split the data into features and target
    X_train = train_df[features]
    y_train = train_df["Exp_Tg(K)"]
    X_test = test_df[features]
    y_test = test_df["Exp_Tg(K)"]

    print(f"\nTraining set size: {len(X_train)}")
    print(f"Test set size: {len(X_test)}")

    # Print statistics about the datasets
    print("\nTraining Data Statistics:")
    print(f"Tg range: [{y_train.min():.2f}, {y_train.max():.2f}]")
    print(f"Tg mean: {y_train.mean():.2f}")
    print(f"Tg std: {y_train.std():.2f}")
    
    print("\nTest Data Statistics:")
    print(f"Tg range: [{y_test.min():.2f}, {y_test.max():.2f}]")
    print(f"Tg mean: {y_test.mean():.2f}")
    print(f"Tg std: {y_test.std():.2f}")

    n_rounds = 7  # Set number of rounds
    start_round = 7  # Set starting round

    # Create initial model instance to handle file checks
    boosting_model = SymbolicRegressionBoosting(
        n_boosting_rounds=n_rounds,
        start_round=start_round,
        base_features=features
    )

    # Check if this round has already been run
    round_dir = os.path.join("boosting_results", f"round_{start_round}")
    if os.path.exists(round_dir):
        predictions_file = os.path.join(round_dir, "predictions.json")
        pkl_files = glob.glob(os.path.join(round_dir, "hall_of_fame_*.pkl"))
        if os.path.exists(predictions_file) and pkl_files:
            print(f"\nError: Round {start_round} has already been completed.")
            print(f"Found existing directory with required files: {round_dir}")
            print("To rerun this round, please delete or rename the existing directory first.")
            return
    
    # Check if we have all necessary files for previous rounds when running rounds > 1
    if start_round > 1:
        print("\nChecking for previous rounds' data...")
        for prev_round in range(1, start_round):
            prev_round_dir = os.path.join("boosting_results", f"round_{prev_round}")
            prev_predictions = os.path.join(prev_round_dir, "predictions.json")
            prev_pkl = glob.glob(os.path.join(prev_round_dir, "hall_of_fame_*.pkl"))
            
            # Check for PKL only scenario
            if prev_pkl and not os.path.exists(prev_predictions):
                print(f"\nFound PKL but missing files in round {prev_round}, attempting to generate...")
                if not boosting_model.check_round_files(prev_round, X_train, y_train, X_test, y_test):
                    print(f"\nError: Failed to generate required files for round {prev_round}")
                    return
                print(f"Successfully generated missing files for round {prev_round}")
            
            # Normal check
            if not (os.path.exists(prev_round_dir) and os.path.exists(prev_predictions) and prev_pkl):
                print(f"\nError: Missing required data from round {prev_round}")
                print(f"Please run round {prev_round} first.")
                return
        print("All previous rounds' data found!")
    
    print("\nStarting model training")
    boosting_model.fit(X_train, y_train, X_test, y_test)
    print("Model training completed")
    boosting_model.save_results_csv()

    # Save detailed results to text file
    output_file = "symbolic_regression_boosting_results.txt"
    try:
        with open(output_file, "w") as f:
            f.write("Symbolic Regression Boosting Results\n")
            f.write("===================================\n\n")
            f.write("Dataset Information:\n")
            f.write(f"Training samples: {len(X_train)}\n")
            f.write(f"Test samples: {len(X_test)}\n")
            f.write(f"Features used: {len(features)}\n\n")
            
            for i, model_info in enumerate(boosting_model.boosted_models, 1):
                f.write(f"\nStage {i}:\n")
                f.write(f"Equation: {model_info['equation']}\n")
                f.write(f"Test MAE: {model_info['test_mae']:.4f}\n")
                f.write(f"Features used: {sorted(model_info['used_features'])}\n")
                f.write("\nCumulative equation up to this stage:\n")
                f.write(boosting_model.get_cumulative_equation(i-1))
                f.write("\n")
        print(f"Detailed results saved to {output_file}")
    except IOError as e:
        print(f"Error writing to file {output_file}: {str(e)}")

    print("Program execution completed successfully")
    return boosting_model

if __name__ == "__main__":
    main()