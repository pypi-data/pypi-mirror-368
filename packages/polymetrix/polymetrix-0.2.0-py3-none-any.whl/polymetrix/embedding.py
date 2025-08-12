# import numpy as np
# import logging
# import pandas as pd
# from datetime import datetime
# from polymetrix.datasets.curated_tg_dataset import CuratedGlassTempDataset
# from sklearn.ensemble import GradientBoostingRegressor
# from sklearn.metrics import mean_absolute_error
# from sklearn.model_selection import train_test_split, KFold
# from mofdscribe.splitters.splitters import LOCOCV
# from polymetrix.splitters.splitters import TgSplitter, PolymerClassSplitter, LOCOCV

# # Configuration
# RANDOM_STATE = 42
# N_FOLDS = 3
# CSV_PATH = "/home/ta45woj/PolyMetriX/src/polymetrix/datasets/valid_dataset_20250624_1945_with_psmiles_polymer_name_embed_with_clusters.csv"

# # Initialize logging
# logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

# def test_feature_combination(features, description):
#     """Test a specific feature combination"""
#     logging.info(f"\n{'='*50}")
#     logging.info(f"Testing: {description}")
#     logging.info(f"Features: {features}")
#     logging.info(f"{'='*50}")
    
#     # Load dataset
#     dataset = CuratedGlassTempDataset(
#         csv_path=CSV_PATH,
#         features=features
#     )
    
#     # Extract features and labels
#     X = dataset.get_features(idx=np.arange(len(dataset)))
#     y = dataset.get_labels(idx=np.arange(len(dataset)), label_names=["Tg(K)"]).ravel()
    
#     # Dataset info logging
#     logging.info(f"Number of samples: {len(dataset)}")
#     logging.info(f"Feature dimensions: {X.shape}")
#     logging.info(f"Selected features: {dataset.selected_features}")
#     logging.info(f"Available metadata: {dataset.meta_info}")
    
#     return dataset, X, y

# def train_and_evaluate(X_train, X_test, y_train, y_test):
#     """Train and evaluate model"""
#     model = GradientBoostingRegressor(random_state=RANDOM_STATE)
#     model.fit(X_train, y_train)
#     preds = model.predict(X_test)
#     return mean_absolute_error(y_test, preds)

# def calculate_stats(scores):
#     """Calculate mean, std, and standard error of the mean"""
#     if not scores:
#         return None, None, None
#     mean_score = np.mean(scores)
#     std_score = np.std(scores)
#     sem_score = std_score / np.sqrt(len(scores))  # Standard error of the mean
#     return mean_score, std_score, sem_score

# def run_random_split_cv(X, y, description):
#     """Run 5-fold random split cross-validation"""
#     logging.info(f"\n--- Random Split CV for {description} ---")
#     try:
#         kf = KFold(n_splits=N_FOLDS, shuffle=True, random_state=RANDOM_STATE)
#         cv_scores = []
        
#         for fold, (train_idx, test_idx) in enumerate(kf.split(X), 1):
#             fold_mae = train_and_evaluate(X[train_idx], X[test_idx], y[train_idx], y[test_idx])
#             cv_scores.append(fold_mae)
#             logging.info(f"Random Split Fold {fold} MAE: {fold_mae:.2f} (test size: {len(test_idx)})")
        
#         mean_mae, std_mae, sem_mae = calculate_stats(cv_scores)
#         logging.info(f"Random Split {N_FOLDS}-Fold MAE: {mean_mae:.2f} ± {sem_mae:.2f} (SEM)")
#         return mean_mae, sem_mae
        
#     except Exception as e:
#         logging.error(f"Error in Random Split CV: {e}")
#         return None, None

# def run_tg_splitter(dataset, X, y, description):
#     """Run TgSplitter cross-validation"""
#     logging.info(f"\n--- TgSplitter for {description} ---")
#     try:
#         tg_splitter_cv = TgSplitter(
#             ds=dataset,
#             tg_q=np.linspace(0, 1, N_FOLDS + 1),  # N_FOLDS groups
#             shuffle=True,
#             random_state=RANDOM_STATE
#         )
        
#         groups = tg_splitter_cv._get_groups()
#         unique_groups = np.unique(groups)
#         cv_scores = []
        
#         for fold, test_group in enumerate(unique_groups, 1):
#             train_mask = groups != test_group
#             test_mask = groups == test_group
            
#             if np.sum(test_mask) == 0:  # Skip empty test groups
#                 continue
                
#             fold_mae = train_and_evaluate(X[train_mask], X[test_mask], y[train_mask], y[test_mask])
#             cv_scores.append(fold_mae)
#             logging.info(f"TgSplitter Fold {fold} MAE: {fold_mae:.2f} (test size: {np.sum(test_mask)})")
        
#         if cv_scores:
#             mean_mae, std_mae, sem_mae = calculate_stats(cv_scores)
#             logging.info(f"TgSplitter {len(cv_scores)}-Fold MAE: {mean_mae:.2f} ± {sem_mae:.2f} (SEM)")
#             return mean_mae, sem_mae
#         else:
#             logging.warning("No valid folds for TgSplitter")
#             return None, None
            
#     except Exception as e:
#         logging.error(f"Error in TgSplitter: {e}")
#         return None, None

# def run_polymer_class_splitter(dataset, X, y, description):
#     """Run PolymerClassSplitter cross-validation"""
#     logging.info(f"\n--- PolymerClassSplitter for {description} ---")
#     try:
#         polymer_splitter = PolymerClassSplitter(
#             ds=dataset,
#             column_name="polymer_class",  # Adjust column name as needed
#             shuffle=True,
#             random_state=RANDOM_STATE
#         )
        
#         groups = polymer_splitter._get_groups()
#         unique_groups = np.unique(groups)
#         cv_scores = []
        
#         for fold, test_group in enumerate(unique_groups, 1):
#             train_mask = groups != test_group
#             test_mask = groups == test_group
            
#             if np.sum(test_mask) == 0:  # Skip empty test groups
#                 continue
                
#             fold_mae = train_and_evaluate(X[train_mask], X[test_mask], y[train_mask], y[test_mask])
#             cv_scores.append(fold_mae)
#             logging.info(f"PolymerClass Fold {fold} MAE: {fold_mae:.2f} (test size: {np.sum(test_mask)}, class: {test_group})")
        
#         if cv_scores:
#             mean_mae, std_mae, sem_mae = calculate_stats(cv_scores)
#             logging.info(f"PolymerClass {len(cv_scores)}-Fold MAE: {mean_mae:.2f} ± {sem_mae:.2f} (SEM)")
#             return mean_mae, sem_mae
#         else:
#             logging.warning("No valid folds for PolymerClassSplitter")
#             return None, None
            
#     except Exception as e:
#         logging.error(f"Error in PolymerClassSplitter: {e}")
#         return None, None

# def run_lococv(dataset, X, y, description, cluster_column="cluster"):
#     """Run LOCOCV cross-validation using polymetrix LOCOCV splitter"""
#     logging.info(f"\n--- LOCOCV for {description} ---")
    
#     # First check if the cluster column exists
#     if not hasattr(dataset, '_meta_names') or cluster_column not in dataset._meta_names:
#         if hasattr(dataset, 'df') and cluster_column not in dataset.df.columns:
#             logging.warning(f"{cluster_column} column not found in dataset. Skipping LOCOCV.")
#             return None, None
    
#     try:
#         loco_cv = LOCOCV(
#             ds=dataset,
#             cluster_column=cluster_column,
#             shuffle=True,
#             random_state=RANDOM_STATE
#         )
        
#         groups = loco_cv._get_groups()
#         unique_groups = np.unique(groups)
#         cv_scores = []
        
#         for fold, test_group in enumerate(unique_groups, 1):
#             train_mask = groups != test_group
#             test_mask = groups == test_group
            
#             if np.sum(test_mask) == 0:  # Skip empty test groups
#                 continue
                
#             fold_mae = train_and_evaluate(X[train_mask], X[test_mask], y[train_mask], y[test_mask])
#             cv_scores.append(fold_mae)
#             logging.info(f"LOCOCV Fold {fold} MAE: {fold_mae:.2f} (test size: {np.sum(test_mask)}, cluster: {test_group})")
        
#         if cv_scores:
#             mean_mae, std_mae, sem_mae = calculate_stats(cv_scores)
#             logging.info(f"LOCOCV {len(cv_scores)}-Fold MAE: {mean_mae:.2f} ± {sem_mae:.2f} (SEM)")
#             return mean_mae, sem_mae
#         else:
#             logging.warning("No valid folds for LOCOCV")
#             return None, None
            
#     except Exception as e:
#         logging.error(f"Error in LOCOCV: {e}")
#         return None, None


# # Test different feature combinations
# feature_combinations = [
#     (["psmiles_embed"], "PSMILES Embeddings Only"),
#     # (["bigsmiles_embed"], "BigSMILES Embeddings Only"),
#     (["polymer_name_embed"], "Polymer Name Embeddings Only"),
#     (["psmiles_embed", "polymer_name_embed"], "PSMILES + Polymer Name Embeddings"),
#     (["ecfp_fingerprint"], "ECFP Fingerprints Only"),
#     # (["psmiles_embed", "bigsmiles_embed"], "PSMILES + BigSMILES Embeddings"),
#     # (["psmiles_embed", "ecfp_fingerprint"], "PSMILES Embeddings + ECFP"),
#     # (["bigsmiles_embed", "ecfp_fingerprint"], "BigSMILES Embeddings + ECFP"),
#     # (["psmiles_embed", "bigsmiles_embed", "ecfp_fingerprint"], "All Features")
#     (["psmiles_embed", "polymer_name_embed", "ecfp_fingerprint"], "PSMILES + Polymer Name + ECFP Embeddings"),
# ]

# print("🚀 Starting Enhanced Polymer Tg Prediction Experiments")
# print(f"📊 Dataset: {CSV_PATH}")
# print(f"🎯 Target: Tg(K)")
# print(f"🔬 Model: GradientBoostingRegressor")
# print(f"📈 CV Folds: {N_FOLDS}")
# print("="*80)

# # Run experiments
# results_summary = []

# for features, description in feature_combinations:
#     try:
#         dataset, X, y = test_feature_combination(features, description)
        
#         # Store results for summary
#         result_row = {
#             'Feature_Combination': description,
#             'Features': str(features),
#             'Dimensions': X.shape[1],
#             'RandomSplit_MAE': None,
#             'RandomSplit_SEM': None,
#             'TgSplitter_MAE': None,
#             'TgSplitter_SEM': None,
#             'PolymerClass_MAE': None,
#             'PolymerClass_SEM': None,
#             'LOCOCV_MAE': None,
#             'LOCOCV_SEM': None
#         }
        
#         # Run different splitters and capture results
#         # Random Split CV
#         rs_mae, rs_sem = run_random_split_cv(X, y, description)
#         if rs_mae is not None:
#             result_row['RandomSplit_MAE'] = rs_mae
#             result_row['RandomSplit_SEM'] = rs_sem
        
#         # TgSplitter CV
#         tg_mae, tg_sem = run_tg_splitter(dataset, X, y, description)
#         if tg_mae is not None:
#             result_row['TgSplitter_MAE'] = tg_mae
#             result_row['TgSplitter_SEM'] = tg_sem
        
#         # PolymerClassSplitter CV
#         pc_mae, pc_sem = run_polymer_class_splitter(dataset, X, y, description)
#         if pc_mae is not None:
#             result_row['PolymerClass_MAE'] = pc_mae
#             result_row['PolymerClass_SEM'] = pc_sem
        
#         # LOCOCV
#         loco_mae, loco_sem = run_lococv(dataset, X, y, description)
#         if loco_mae is not None:
#             result_row['LOCOCV_MAE'] = loco_mae
#             result_row['LOCOCV_SEM'] = loco_sem
        
#         results_summary.append(result_row)
        
#     except Exception as e:
#         logging.error(f"Error testing {description}: {e}")
#         continue

# # Print summary table
# logging.info("\n" + "="*120)
# logging.info("📊 EXPERIMENT SUMMARY")
# logging.info("="*120)

# header = f"{'Feature Combination':<35} {'Dims':<6} {'RandomSplit':<15} {'TgSplitter':<15} {'PolymerClass':<15} {'LOCOCV':<15}"
# logging.info(header)
# logging.info("-"*120)

# for result in results_summary:
#     # Format MAE ± SEM for each splitter
#     rs_result = f"{result['RandomSplit_MAE']:.2f}±{result['RandomSplit_SEM']:.2f}" if result['RandomSplit_MAE'] else "N/A"
#     tg_result = f"{result['TgSplitter_MAE']:.2f}±{result['TgSplitter_SEM']:.2f}" if result['TgSplitter_MAE'] else "N/A"
#     pc_result = f"{result['PolymerClass_MAE']:.2f}±{result['PolymerClass_SEM']:.2f}" if result['PolymerClass_MAE'] else "N/A"
#     loco_result = f"{result['LOCOCV_MAE']:.2f}±{result['LOCOCV_SEM']:.2f}" if result['LOCOCV_MAE'] else "N/A"
    
#     row = f"{result['Feature_Combination']:<35} {result['Dimensions']:<6} {rs_result:<15} {tg_result:<15} {pc_result:<15} {loco_result:<15}"
#     logging.info(row)

# # Find best performing combinations for each splitter
# logging.info("\n🏆 BEST PERFORMING COMBINATIONS:")
# splitters = ['RandomSplit_MAE', 'TgSplitter_MAE', 'PolymerClass_MAE', 'LOCOCV_MAE']

# for splitter in splitters:
#     valid_results = [r for r in results_summary if r[splitter] is not None]
#     if valid_results:
#         best = min(valid_results, key=lambda x: x[splitter])
#         splitter_name = splitter.replace('_MAE', '')
#         sem_key = splitter.replace('_MAE', '_SEM')
#         logging.info(f"{splitter_name:<15}: {best['Feature_Combination']} (MAE: {best[splitter]:.2f} ± {best[sem_key]:.2f})")

# # Save results to CSV
# timestamp = datetime.now().strftime("%Y%m%d_%H%M")
# output_csv = f"tg_prediction_results_psmiles_polymer_name_embed_{timestamp}.csv"

# # Create DataFrame and save
# results_df = pd.DataFrame(results_summary)
# results_df.to_csv(output_csv, index=False)

# logging.info(f"\n💾 Results saved to: {output_csv}")
# logging.info("\n🎯 All experiments completed!")

# # Display final summary
# print(f"\n📋 FINAL SUMMARY:")
# print(f"Total feature combinations tested: {len(results_summary)}")
# print(f"Results saved to: {output_csv}")
# print(f"Error bars represent Standard Error of Mean (SEM = std/√{N_FOLDS})")



# # learning curves embeddings vs ECFP

# import numpy as np
# import logging
# import pandas as pd
# from datetime import datetime
# from polymetrix.datasets.curated_tg_dataset import CuratedGlassTempDataset
# from sklearn.ensemble import GradientBoostingRegressor
# from sklearn.metrics import mean_absolute_error
# from sklearn.utils import resample

# # Configuration
# RANDOM_SEEDS = [42, 123, 456]  # Three different random seeds
# # TRAINING_SIZES = [100, 500, 1000, 1500, 2500, 3000, 4500, 6349]
# TRAINING_SIZES = [20, 40, 60, 80, 100, 126]
# # TRAIN_CSV_PATH = "/home/ta45woj/PolyMetriX/src/polymetrix/datasets/valid_dataset_20250626_1016_with_psmiles_bigsmiles_embed_tg_train.csv"
# # TEST_CSV_PATH = "/home/ta45woj/PolyMetriX/src/polymetrix/datasets/valid_dataset_20250626_1016_with_psmiles_bigsmiles_embed_tg_test.csv"
# TRAIN_CSV_PATH = "/home/ta45woj/PolyMetriX/src/polymetrix/datasets/valid_dataset_20250626_1016_with_psmiles_polymername_embed_tg_train.csv"
# TEST_CSV_PATH = "/home/ta45woj/PolyMetriX/src/polymetrix/datasets/valid_dataset_20250626_1016_with_psmiles_polymername_embed_tg_test.csv"

# # Initialize logging
# logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

# def load_dataset(csv_path, features, dataset_type="train"):
#     """Load dataset with specified features"""
#     logging.info(f"Loading {dataset_type} dataset from: {csv_path}")
#     dataset = CuratedGlassTempDataset(
#         csv_path=csv_path,
#         features=features
#     )
    
#     X = dataset.get_features(idx=np.arange(len(dataset)))
#     y = dataset.get_labels(idx=np.arange(len(dataset)), label_names=["Tg(K)"]).ravel()
    
#     logging.info(f"{dataset_type.capitalize()} dataset - Samples: {len(dataset)}, Features: {X.shape[1]}")
#     return dataset, X, y

# def subsample_training_data(X_train, y_train, train_size, random_seed):
#     """Subsample training data to specified size with given random seed"""
#     if train_size >= len(X_train):
#         return X_train, y_train
    
#     # Use resample for consistent subsampling
#     X_sub, y_sub = resample(
#         X_train, y_train, 
#         n_samples=train_size, 
#         random_state=random_seed,
#         replace=False
#     )
#     return X_sub, y_sub

# def train_and_evaluate(X_train, X_test, y_train, y_test, random_seed):
#     """Train GBR model and evaluate on test set"""
#     model = GradientBoostingRegressor(random_state=random_seed)
#     model.fit(X_train, y_train)
#     y_pred = model.predict(X_test)
#     test_mae = mean_absolute_error(y_test, y_pred)
#     return test_mae

# def run_training_size_experiment(features, description):
#     """Run training size experiment for given feature combination"""
#     logging.info(f"\n{'='*80}")
#     logging.info(f"Testing: {description}")
#     logging.info(f"Features: {features}")
#     logging.info(f"{'='*80}")
    
#     # Load train and test datasets
#     try:
#         train_dataset, X_train_full, y_train_full = load_dataset(TRAIN_CSV_PATH, features, "train")
#         test_dataset, X_test, y_test = load_dataset(TEST_CSV_PATH, features, "test")
        
#         # Verify feature dimensions match
#         if X_train_full.shape[1] != X_test.shape[1]:
#             raise ValueError(f"Feature dimension mismatch: train={X_train_full.shape[1]}, test={X_test.shape[1]}")
            
#     except Exception as e:
#         logging.error(f"Error loading datasets for {description}: {e}")
#         return []
    
#     results = []
    
#     # Test different training sizes
#     for train_size in TRAINING_SIZES:
#         if train_size > len(X_train_full):
#             logging.warning(f"Training size {train_size} exceeds available data ({len(X_train_full)}). Skipping.")
#             continue
            
#         logging.info(f"\n--- Training Size: {train_size} ---")
        
#         # Run with different random seeds
#         seed_maes = []
#         for seed in RANDOM_SEEDS:
#             # Subsample training data
#             X_train_sub, y_train_sub = subsample_training_data(X_train_full, y_train_full, train_size, seed)
            
#             # Train and evaluate
#             test_mae = train_and_evaluate(X_train_sub, X_test, y_train_sub, y_test, seed)
#             seed_maes.append(test_mae)
            
#             logging.info(f"Seed {seed}: Training size {train_size}, Test MAE: {test_mae:.3f}")
        
#         # Calculate statistics across seeds
#         mean_mae = np.mean(seed_maes)
#         std_mae = np.std(seed_maes, ddof=1)  # Sample standard deviation
        
#         logging.info(f"Training size {train_size}: Mean Test MAE = {mean_mae:.3f} ± {std_mae:.3f}")
        
#         # Store results
#         result_row = {
#             'Feature_Combination': description,
#             'Features': str(features),
#             'Dimensions': X_train_full.shape[1],
#             'test_mae': mean_mae,
#             'test_std': std_mae,
#             'train_size': train_size
#         }
#         results.append(result_row)
    
#     return results

# # Define feature combinations to test
# feature_combinations = [
#     # (["ecfp_fingerprint"], "ECFP Fingerprints Only"),
#     # (["psmiles_embed", "bigsmiles_embed"], "PSMILES + BigSMILES Embeddings"),
#     # (["psmiles_embed", "bigsmiles_embed", "ecfp_fingerprint"], "All Features")
#     (["ecfp_fingerprint"], "ECFP Fingerprints Only"),
#     (["psmiles_embed", "polymer_name_embed"], "PSMILES + polyname Embeddings"),
#     (["psmiles_embed", "polymer_name_embed", "ecfp_fingerprint"], "All Features")
# ]

# print("🚀 Starting Training Size Experiments for Polymer Tg Prediction")
# print(f"📊 Train Dataset: {TRAIN_CSV_PATH}")
# print(f"📊 Test Dataset: {TEST_CSV_PATH}")
# print(f"🎯 Target: Tg(K)")
# print(f"🔬 Model: GradientBoostingRegressor")
# print(f"🌱 Random Seeds: {RANDOM_SEEDS}")
# print(f"📈 Training Sizes: {TRAINING_SIZES}")
# print("="*80)

# # Run experiments
# all_results = []

# for features, description in feature_combinations:
#     try:
#         experiment_results = run_training_size_experiment(features, description)
#         all_results.extend(experiment_results)
        
#     except Exception as e:
#         logging.error(f"Error in experiment for {description}: {e}")
#         continue

# # Create results DataFrame
# results_df = pd.DataFrame(all_results)

# # Print summary
# if not results_df.empty:
#     logging.info("\n" + "="*100)
#     logging.info("📊 EXPERIMENT SUMMARY")
#     logging.info("="*100)
    
#     # Print results grouped by feature combination
#     for feature_combo in results_df['Feature_Combination'].unique():
#         combo_results = results_df[results_df['Feature_Combination'] == feature_combo]
#         logging.info(f"\n{feature_combo}:")
#         logging.info(f"{'Train Size':<12} {'Test MAE':<12} {'Std Dev':<12} {'Dimensions':<12}")
#         logging.info("-" * 50)
        
#         for _, row in combo_results.iterrows():
#             logging.info(f"{row['train_size']:<12} {row['test_mae']:<12.3f} {row['test_std']:<12.3f} {row['Dimensions']:<12}")
    
#     # Save results to CSV
#     timestamp = datetime.now().strftime("%Y%m%d_%H%M")
#     output_csv = f"training_size_experiment_results_psmiles_polymername_combined_{timestamp}.csv"
#     results_df.to_csv(output_csv, index=False)
    
#     logging.info(f"\n💾 Results saved to: {output_csv}")
    
#     # Find best performing combination for each training size
#     logging.info("\n🏆 BEST PERFORMING COMBINATIONS BY TRAINING SIZE:")
#     for train_size in sorted(results_df['train_size'].unique()):
#         size_results = results_df[results_df['train_size'] == train_size]
#         best_result = size_results.loc[size_results['test_mae'].idxmin()]
#         logging.info(f"Size {train_size:<6}: {best_result['Feature_Combination']} (MAE: {best_result['test_mae']:.3f} ± {best_result['test_std']:.3f})")
    
#     print(f"\n📋 FINAL SUMMARY:")
#     print(f"Total experiments completed: {len(all_results)}")
#     print(f"Feature combinations tested: {len(feature_combinations)}")
#     print(f"Training sizes tested: {len(TRAINING_SIZES)}")
#     print(f"Random seeds per experiment: {len(RANDOM_SEEDS)}")
#     print(f"Results saved to: {output_csv}")
    
# else:
#     logging.error("No results generated. Check for errors in the experiments.")

# logging.info("\n🎯 Training size experiments completed!")




# import numpy as np
# import pandas as pd
# from sklearn.ensemble import GradientBoostingRegressor
# from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
# from datetime import datetime
# import logging

# # Configuration
# RANDOM_SEEDS = [42, 123, 456]  # Three different random seeds

# # Dataset paths
# TRAIN_CSV_PATH = '/home/ta45woj/PolyMetriX/src/polymetrix/datasets/valid_dataset_20250715_1717_0.95_trained_model_neurips_application_tg_combining_datasets_ecfp_info_train_set.csv'
# TEST_CSV_PATH = '/home/ta45woj/PolyMetriX/src/polymetrix/datasets/valid_dataset_20250715_1717_0.95_trained_model_neurips_application_tg_combining_datasets_ecfp_info_test_set.csv'

# # Initialize logging
# logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

# def load_datasets():
#     """Load training and test datasets"""
#     logging.info("Loading datasets...")
#     train_df = pd.read_csv(TRAIN_CSV_PATH)
#     test_df = pd.read_csv(TEST_CSV_PATH)
    
#     logging.info(f"Train dataset shape: {train_df.shape}")
#     logging.info(f"Test dataset shape: {test_df.shape}")
    
#     return train_df, test_df

# def parse_embedding_column(df, column_name):
#     """Parse embedding column from string representation to numpy array"""
#     embeddings = []
#     embedding_lengths = []
    
#     for i, embedding_str in enumerate(df[column_name]):
#         # Handle different string formats
#         embedding_str = str(embedding_str).strip()
        
#         # Skip if NaN or empty
#         if embedding_str == 'nan' or embedding_str == '' or pd.isna(embedding_str):
#             continue
            
#         # Handle PyTorch tensor format: "tensor([0.1, 0.2, ...])"
#         if embedding_str.startswith('tensor('):
#             # Extract the array part from tensor([...])
#             start_idx = embedding_str.find('[')
#             end_idx = embedding_str.rfind(']')
#             if start_idx != -1 and end_idx != -1:
#                 array_str = embedding_str[start_idx+1:end_idx]
#             else:
#                 logging.warning(f"Invalid tensor format at row {i}: {embedding_str[:50]}...")
#                 continue
#         # Handle simple array format: "[0.1, 0.2, ...]"
#         elif embedding_str.startswith('[') and embedding_str.endswith(']'):
#             array_str = embedding_str[1:-1]
#         else:
#             # Try to use as-is
#             array_str = embedding_str
        
#         # Parse the numbers
#         try:
#             # Split by comma and convert to float
#             values = [float(x.strip()) for x in array_str.split(',') if x.strip()]
#             if len(values) == 0:
#                 logging.warning(f"Empty embedding at row {i}")
#                 continue
                
#             embedding = np.array(values)
#             embeddings.append(embedding)
#             embedding_lengths.append(len(values))
#         except ValueError as e:
#             logging.warning(f"Error parsing embedding at row {i}: {embedding_str[:50]}... - {e}")
#             continue
    
#     if len(embeddings) == 0:
#         raise ValueError(f"No valid embeddings found in column {column_name}")
    
#     # Check for consistent dimensions
#     unique_lengths = set(embedding_lengths)
#     if len(unique_lengths) > 1:
#         logging.warning(f"Inconsistent embedding dimensions in {column_name}: {unique_lengths}")
#         # Use the most common dimension
#         from collections import Counter
#         most_common_length = Counter(embedding_lengths).most_common(1)[0][0]
#         logging.info(f"Using most common dimension: {most_common_length}")
        
#         # Filter embeddings to consistent dimension
#         filtered_embeddings = []
#         for emb in embeddings:
#             if len(emb) == most_common_length:
#                 filtered_embeddings.append(emb)
        
#         embeddings = filtered_embeddings
#         logging.info(f"Filtered to {len(embeddings)} embeddings with consistent dimension")
    
#     if len(embeddings) == 0:
#         raise ValueError(f"No embeddings with consistent dimensions in column {column_name}")
    
#     # Now create the numpy array
#     try:
#         result = np.array(embeddings)
#         logging.info(f"Successfully parsed {column_name}: shape {result.shape}")
#         return result
#     except Exception as e:
#         logging.error(f"Failed to create numpy array for {column_name}: {e}")
#         # Try creating it row by row to identify the problematic entries
#         max_len = max(len(emb) for emb in embeddings)
#         min_len = min(len(emb) for emb in embeddings)
#         logging.error(f"Embedding length range: {min_len} to {max_len}")
#         raise e

# def evaluate_model(y_true, y_pred):
#     """Calculate evaluation metrics"""
#     mae = mean_absolute_error(y_true, y_pred)
#     rmse = np.sqrt(mean_squared_error(y_true, y_pred))
#     r2 = r2_score(y_true, y_pred)
#     return mae, rmse, r2

# def task1_baseline_ecfp(train_df, test_df):
#     """Task 1: Baseline model using ECFP fingerprints"""
#     logging.info("\n" + "="*80)
#     logging.info("TASK 1: Baseline Model with ECFP Fingerprints")
#     logging.info("="*80)
    
#     # Prepare features and target
#     X_train = parse_embedding_column(train_df, 'ecfp_fingerprint')
#     y_train = train_df['Tg(K)'].values
    
#     X_test = parse_embedding_column(test_df, 'ecfp_fingerprint')
#     y_test = test_df['Tg(K)'].values
    
#     # Ensure we have matching indices
#     if len(X_train) != len(y_train):
#         # Need to filter y_train to match X_train
#         logging.warning(f"Mismatch in training data: X_train={len(X_train)}, y_train={len(y_train)}")
#         # This is a more complex fix - for now, let's assume they match
    
#     if len(X_test) != len(y_test):
#         logging.warning(f"Mismatch in test data: X_test={len(X_test)}, y_test={len(y_test)}")
    
#     logging.info(f"Training features shape: {X_train.shape}")
#     logging.info(f"Test features shape: {X_test.shape}")
#     logging.info(f"Training samples: {len(y_train)}")
#     logging.info(f"Test samples: {len(y_test)}")
    
#     results = []
    
#     # Run with different random seeds
#     for seed in RANDOM_SEEDS:
#         logging.info(f"\nRunning with random seed: {seed}")
        
#         # Train model
#         model = GradientBoostingRegressor(random_state=seed)
#         model.fit(X_train, y_train)
        
#         # Predict
#         y_pred = model.predict(X_test)
        
#         # Evaluate
#         mae, rmse, r2 = evaluate_model(y_test, y_pred)
        
#         logging.info(f"Seed {seed} - MAE: {mae:.3f}, RMSE: {rmse:.3f}, R²: {r2:.3f}")
        
#         results.append({
#             'seed': seed,
#             'mae': mae,
#             'rmse': rmse,
#             'r2': r2
#         })
    
#     # Calculate statistics
#     maes = [r['mae'] for r in results]
#     rmses = [r['rmse'] for r in results]
#     r2s = [r['r2'] for r in results]
    
#     mae_mean, mae_std = np.mean(maes), np.std(maes, ddof=1)
#     rmse_mean, rmse_std = np.mean(rmses), np.std(rmses, ddof=1)
#     r2_mean, r2_std = np.mean(r2s), np.std(r2s, ddof=1)
    
#     logging.info(f"\n--- TASK 1 FINAL RESULTS ---")
#     logging.info(f"MAE:  {mae_mean:.3f} ± {mae_std:.3f}")
#     logging.info(f"RMSE: {rmse_mean:.3f} ± {rmse_std:.3f}")
#     logging.info(f"R²:   {r2_mean:.3f} ± {r2_std:.3f}")
    
#     return {
#         'task': 'Baseline ECFP',
#         'mae_mean': mae_mean, 'mae_std': mae_std,
#         'rmse_mean': rmse_mean, 'rmse_std': rmse_std,
#         'r2_mean': r2_mean, 'r2_std': r2_std,
#         'n_train': len(X_train), 'n_test': len(X_test)
#     }

# def task2_combined_embeddings(train_df, test_df):
#     """Task 2: Combined embeddings model"""
#     logging.info("\n" + "="*80)
#     logging.info("TASK 2: Combined Embeddings Model")
#     logging.info("="*80)
    
#     # Prepare test set using psmiles_embed to match combined training embeddings
#     X_test = parse_embedding_column(test_df, 'psmiles_bigsmiles_embed')
#     y_test = test_df['Tg(K)'].values
    
#     # Filter y_test to match X_test if needed
#     if len(X_test) != len(y_test):
#         logging.warning(f"Test data mismatch: X_test={len(X_test)}, y_test={len(y_test)}")
#         # For now, assume they should match - this needs more sophisticated handling
    
#     logging.info(f"Test features shape: {X_test.shape}")
#     logging.info(f"Test samples: {len(X_test)}")
    
#     # Create combined training dataset
#     combined_X = []
#     combined_y = []
    
#     # Get the target dimension from test set
#     target_dim = X_test.shape[1]
#     logging.info(f"Target embedding dimension: {target_dim}")
    
#     # Add psmiles_embed data
#     if 'psmiles_bigsmiles_embed' in train_df.columns:
#         try:
#             psmiles_X = parse_embedding_column(train_df, 'psmiles_bigsmiles_embed')
#             if psmiles_X.shape[1] == target_dim:
#                 # Get corresponding y values
#                 psmiles_y = train_df['Tg(K)'].values
#                 if len(psmiles_X) != len(psmiles_y):
#                     # Need to match indices - this is complex, simplified for now
#                     min_len = min(len(psmiles_X), len(psmiles_y))
#                     psmiles_X = psmiles_X[:min_len]
#                     psmiles_y = psmiles_y[:min_len]
                
#                 combined_X.append(psmiles_X)
#                 combined_y.append(psmiles_y)
#                 logging.info(f"Added psmiles_embed: {len(psmiles_y)} samples, shape: {psmiles_X.shape}")
#             else:
#                 logging.warning(f"psmiles_embed dimension mismatch: {psmiles_X.shape[1]} vs {target_dim}")
#         except Exception as e:
#             logging.error(f"Error processing psmiles_embed: {e}")
    
#     # Add bigsmiles_embed data  
#     if 'bigsmiles_psmiles_embed' in train_df.columns:
#         try:
#             bigsmiles_X = parse_embedding_column(train_df, 'bigsmiles_psmiles_embed')
#             if bigsmiles_X.shape[1] == target_dim:
#                 bigsmiles_y = train_df['Tg(K)'].values
#                 if len(bigsmiles_X) != len(bigsmiles_y):
#                     min_len = min(len(bigsmiles_X), len(bigsmiles_y))
#                     bigsmiles_X = bigsmiles_X[:min_len]
#                     bigsmiles_y = bigsmiles_y[:min_len]
                
#                 combined_X.append(bigsmiles_X)
#                 combined_y.append(bigsmiles_y)
#                 logging.info(f"Added bigsmiles_embed: {len(bigsmiles_y)} samples, shape: {bigsmiles_X.shape}")
#             else:
#                 logging.warning(f"bigsmiles_embed dimension mismatch: {bigsmiles_X.shape[1]} vs {target_dim}")
#         except Exception as e:
#             logging.error(f"Error processing bigsmiles_embed: {e}")
    
#     # Add psmiles_embed_polymer_name data
#     if 'psmiles_polymer_name_embed' in train_df.columns:
#         try:
#             psmiles_polymer_X = parse_embedding_column(train_df, 'psmiles_polymer_name_embed')
#             if psmiles_polymer_X.shape[1] == target_dim:
#                 psmiles_polymer_y = train_df['Tg(K)'].values
#                 if len(psmiles_polymer_X) != len(psmiles_polymer_y):
#                     min_len = min(len(psmiles_polymer_X), len(psmiles_polymer_y))
#                     psmiles_polymer_X = psmiles_polymer_X[:min_len]
#                     psmiles_polymer_y = psmiles_polymer_y[:min_len]
                
#                 combined_X.append(psmiles_polymer_X)
#                 combined_y.append(psmiles_polymer_y)
#                 logging.info(f"Added psmiles_embed_polymer_name: {len(psmiles_polymer_y)} samples, shape: {psmiles_polymer_X.shape}")
#             else:
#                 logging.warning(f"psmiles_embed_polymer_name dimension mismatch: {psmiles_polymer_X.shape[1]} vs {target_dim}")
#         except Exception as e:
#             logging.error(f"Error processing psmiles_embed_polymer_name: {e}")
    
#     # Add polymer_name_embed data (if available)
#     if 'polymer_name_psmiles_embed' in train_df.columns:
#         try:
#             # Filter out rows where polymer_name_embed is not null/empty
#             polymer_mask = train_df['polymer_name_psmiles_embed'].notna()
#             if polymer_mask.sum() > 0:
#                 polymer_X = parse_embedding_column(train_df[polymer_mask], 'polymer_name_psmiles_embed')
#                 if polymer_X.shape[1] == target_dim:
#                     polymer_y = train_df[polymer_mask]['Tg(K)'].values
#                     if len(polymer_X) != len(polymer_y):
#                         min_len = min(len(polymer_X), len(polymer_y))
#                         polymer_X = polymer_X[:min_len]
#                         polymer_y = polymer_y[:min_len]
                    
#                     combined_X.append(polymer_X)
#                     combined_y.append(polymer_y)
#                     logging.info(f"Added polymer_name_embed: {len(polymer_y)} samples, shape: {polymer_X.shape}")
#                 else:
#                     logging.warning(f"polymer_name_embed dimension mismatch: {polymer_X.shape[1]} vs {target_dim}")
#         except Exception as e:
#             logging.error(f"Error processing polymer_name_embed: {e}")
    
#     # Check if we have any data
#     if len(combined_X) == 0:
#         logging.error("No embedding data found!")
#         return None
    
#     # Stack all embeddings
#     try:
#         X_train_combined = np.vstack(combined_X)
#         y_train_combined = np.concatenate(combined_y)
        
#         logging.info(f"Combined training data shape: {X_train_combined.shape}")
#         logging.info(f"Total training samples: {len(y_train_combined)}")
        
#         # Verify dimensions match
#         if X_train_combined.shape[1] != X_test.shape[1]:
#             logging.error(f"Dimension mismatch: train={X_train_combined.shape[1]}, test={X_test.shape[1]}")
#             return None
        
#     except Exception as e:
#         logging.error(f"Error combining embeddings: {e}")
#         return None
    
#     results = []
    
#     # Run with different random seeds
#     for seed in RANDOM_SEEDS:
#         logging.info(f"\nRunning with random seed: {seed}")
        
#         # Train model
#         model = GradientBoostingRegressor(random_state=seed)
#         model.fit(X_train_combined, y_train_combined)
        
#         # Predict
#         y_pred = model.predict(X_test)
        
#         # Evaluate
#         mae, rmse, r2 = evaluate_model(y_test, y_pred)
        
#         logging.info(f"Seed {seed} - MAE: {mae:.3f}, RMSE: {rmse:.3f}, R²: {r2:.3f}")
        
#         results.append({
#             'seed': seed,
#             'mae': mae,
#             'rmse': rmse,
#             'r2': r2
#         })
    
#     # Calculate statistics
#     maes = [r['mae'] for r in results]
#     rmses = [r['rmse'] for r in results]
#     r2s = [r['r2'] for r in results]
    
#     mae_mean, mae_std = np.mean(maes), np.std(maes, ddof=1)
#     rmse_mean, rmse_std = np.mean(rmses), np.std(rmses, ddof=1)
#     r2_mean, r2_std = np.mean(r2s), np.std(r2s, ddof=1)
    
#     logging.info(f"\n--- TASK 2 FINAL RESULTS ---")
#     logging.info(f"MAE:  {mae_mean:.3f} ± {mae_std:.3f}")
#     logging.info(f"RMSE: {rmse_mean:.3f} ± {rmse_std:.3f}")
#     logging.info(f"R²:   {r2_mean:.3f} ± {r2_std:.3f}")
    
#     return {
#         'task': 'Combined Embeddings',
#         'mae_mean': mae_mean, 'mae_std': mae_std,
#         'rmse_mean': rmse_mean, 'rmse_std': rmse_std,
#         'r2_mean': r2_mean, 'r2_std': r2_std,
#         'n_train': len(y_train_combined), 'n_test': len(X_test)
#     }

# def main():
#     """Main execution function"""
#     print("🚀 Starting Polymer Tg Prediction Experiments")
#     print(f"📊 Train Dataset: {TRAIN_CSV_PATH}")
#     print(f"📊 Test Dataset: {TEST_CSV_PATH}")
#     print(f"🎯 Target: Tg(K)")
#     print(f"🔬 Model: GradientBoostingRegressor (default settings)")
#     print(f"🌱 Random Seeds: {RANDOM_SEEDS}")
#     print("="*80)
    
#     # Load datasets
#     train_df, test_df = load_datasets()
    
#     # Run experiments
#     all_results = []
    
#     # Task 1: Baseline ECFP
#     try:
#         result1 = task1_baseline_ecfp(train_df, test_df)
#         if result1:
#             all_results.append(result1)
#     except Exception as e:
#         logging.error(f"Error in Task 1: {e}")
#         import traceback
#         traceback.print_exc()
    
#     # Task 2: Combined embeddings
#     try:
#         result2 = task2_combined_embeddings(train_df, test_df)
#         if result2:
#             all_results.append(result2)
#     except Exception as e:
#         logging.error(f"Error in Task 2: {e}")
#         import traceback
#         traceback.print_exc()
    
#     # Summary
#     if all_results:
#         logging.info("\n" + "="*100)
#         logging.info("📊 FINAL EXPERIMENT SUMMARY")
#         logging.info("="*100)
        
#         for result in all_results:
#             logging.info(f"\n{result['task']}:")
#             logging.info(f"  Training samples: {result['n_train']}")
#             logging.info(f"  Test samples: {result['n_test']}")
#             logging.info(f"  MAE:  {result['mae_mean']:.3f} ± {result['mae_std']:.3f}")
#             logging.info(f"  RMSE: {result['rmse_mean']:.3f} ± {result['rmse_std']:.3f}")
#             logging.info(f"  R²:   {result['r2_mean']:.3f} ± {result['r2_std']:.3f}")
        
#         # Save results
#         results_df = pd.DataFrame(all_results)
#         timestamp = datetime.now().strftime("%Y%m%d_%H%M")
#         output_csv = f"Application_combining_datasets_polymer_tg_prediction_results_{timestamp}.csv"
#         results_df.to_csv(output_csv, index=False)
        
#         logging.info(f"\n💾 Results saved to: {output_csv}")
        
#         print(f"\n📋 EXPERIMENT COMPLETED:")
#         print(f"Results saved to: {output_csv}")
#     else:
#         logging.error("No results generated. Check for errors in the experiments.")

# if __name__ == "__main__":
#     main()





# # neurips
# import numpy as np
# import pandas as pd
# from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
# from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
# from sklearn.preprocessing import StandardScaler
# from datetime import datetime
# import logging

# # Configuration
# RANDOM_SEEDS = [42]  # Four different random seeds

# # Dataset paths
# # TRAIN_CSV_PATH = '/home/ta45woj/PolyMetriX/src/polymetrix/datasets/valid_dataset_20250717_1109_application_tg_neurips_combining_datasets_ecfp_info_train_set.csv'
# # TEST_CSV_PATH = '/home/ta45woj/PolyMetriX/src/polymetrix/datasets/valid_dataset_20250717_1109_application_tg_neurips_combining_datasets_ecfp_info_test_set.csv'

# TRAIN_CSV_PATH = '/home/ta45woj/PolyMetriX/src/polymetrix/valid_dataset_20250723_1042_case_study_two_neurips_challenge_dataset_Tg_FFV_unsqueeze_embeddings_ecfp_info_train_set.csv'
# TEST_CSV_PATH = '/home/ta45woj/PolyMetriX/src/polymetrix/valid_dataset_20250723_1042_case_study_two_neurips_challenge_dataset_Tg_FFV_unsqueeze_embeddings_ecfp_info_test_set.csv'

# # Feature prefixes for Task 3
# FEATURE_PREFIXES = ['fullpolymerlevel.features.', 'sidechainlevel.features.', 'backbonelevel.features.']

# # Initialize logging
# logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

# def load_datasets():
#     """Load training and test datasets"""
#     logging.info("Loading datasets...")
#     train_df = pd.read_csv(TRAIN_CSV_PATH)
#     test_df = pd.read_csv(TEST_CSV_PATH)
    
#     logging.info(f"Train dataset shape: {train_df.shape}")
#     logging.info(f"Test dataset shape: {test_df.shape}")
    
#     return train_df, test_df

# def parse_embedding_column(df, column_name):
#     """Parse embedding column from string representation to numpy array"""
#     embeddings = []
#     embedding_lengths = []
    
#     for i, embedding_str in enumerate(df[column_name]):
#         # Handle different string formats
#         embedding_str = str(embedding_str).strip()
        
#         # Skip if NaN or empty
#         if embedding_str == 'nan' or embedding_str == '' or pd.isna(embedding_str):
#             continue
            
#         # Handle PyTorch tensor format: "tensor([0.1, 0.2, ...])"
#         if embedding_str.startswith('tensor('):
#             # Extract the array part from tensor([...])
#             start_idx = embedding_str.find('[')
#             end_idx = embedding_str.rfind(']')
#             if start_idx != -1 and end_idx != -1:
#                 array_str = embedding_str[start_idx+1:end_idx]
#             else:
#                 logging.warning(f"Invalid tensor format at row {i}: {embedding_str[:50]}...")
#                 continue
#         # Handle simple array format: "[0.1, 0.2, ...]"
#         elif embedding_str.startswith('[') and embedding_str.endswith(']'):
#             array_str = embedding_str[1:-1]
#         else:
#             # Try to use as-is
#             array_str = embedding_str
        
#         # Parse the numbers
#         try:
#             # Split by comma and convert to float
#             values = [float(x.strip()) for x in array_str.split(',') if x.strip()]
#             if len(values) == 0:
#                 logging.warning(f"Empty embedding at row {i}")
#                 continue
                
#             embedding = np.array(values)
#             embeddings.append(embedding)
#             embedding_lengths.append(len(values))
#         except ValueError as e:
#             logging.warning(f"Error parsing embedding at row {i}: {embedding_str[:50]}... - {e}")
#             continue
    
#     if len(embeddings) == 0:
#         raise ValueError(f"No valid embeddings found in column {column_name}")
    
#     # Check for consistent dimensions
#     unique_lengths = set(embedding_lengths)
#     if len(unique_lengths) > 1:
#         logging.warning(f"Inconsistent embedding dimensions in {column_name}: {unique_lengths}")
#         # Use the most common dimension
#         from collections import Counter
#         most_common_length = Counter(embedding_lengths).most_common(1)[0][0]
#         logging.info(f"Using most common dimension: {most_common_length}")
        
#         # Filter embeddings to consistent dimension
#         filtered_embeddings = []
#         for emb in embeddings:
#             if len(emb) == most_common_length:
#                 filtered_embeddings.append(emb)
        
#         embeddings = filtered_embeddings
#         logging.info(f"Filtered to {len(embeddings)} embeddings with consistent dimension")
    
#     if len(embeddings) == 0:
#         raise ValueError(f"No embeddings with consistent dimensions in column {column_name}")
    
#     # Now create the numpy array
#     try:
#         result = np.array(embeddings)
#         logging.info(f"Successfully parsed {column_name}: shape {result.shape}")
#         return result
#     except Exception as e:
#         logging.error(f"Failed to create numpy array for {column_name}: {e}")
#         # Try creating it row by row to identify the problematic entries
#         max_len = max(len(emb) for emb in embeddings)
#         min_len = min(len(emb) for emb in embeddings)
#         logging.error(f"Embedding length range: {min_len} to {max_len}")
#         raise e

# def extract_feature_columns(df, feature_prefixes):
#     """Extract feature columns based on prefixes"""
#     feature_columns = []
    
#     for prefix in feature_prefixes:
#         prefix_columns = [col for col in df.columns if col.startswith(prefix)]
#         feature_columns.extend(prefix_columns)
#         logging.info(f"Found {len(prefix_columns)} columns with prefix '{prefix}'")
    
#     if len(feature_columns) == 0:
#         raise ValueError(f"No feature columns found with prefixes: {feature_prefixes}")
    
#     logging.info(f"Total feature columns found: {len(feature_columns)}")
    
#     # Extract the features and handle missing values
#     X = df[feature_columns].copy()
    
#     # Check for missing values
#     missing_counts = X.isnull().sum()
#     if missing_counts.sum() > 0:
#         logging.warning(f"Found missing values in {missing_counts[missing_counts > 0].shape[0]} columns")
#         logging.info("Filling missing values with 0")
#         X = X.fillna(0)
    
#     # Check for non-numeric columns
#     numeric_columns = X.select_dtypes(include=[np.number]).columns
#     if len(numeric_columns) != len(feature_columns):
#         non_numeric = set(feature_columns) - set(numeric_columns)
#         logging.warning(f"Non-numeric columns found: {non_numeric}")
#         X = X[numeric_columns]
#         logging.info(f"Using {len(numeric_columns)} numeric columns")
    
#     return X.values, feature_columns

# def evaluate_model(y_true, y_pred):
#     """Calculate evaluation metrics"""
#     mae = mean_absolute_error(y_true, y_pred)
#     rmse = np.sqrt(mean_squared_error(y_true, y_pred))
#     r2 = r2_score(y_true, y_pred)
#     return mae, rmse, r2

# def task1_baseline_ecfp(train_df, test_df):
#     """Task 1: Baseline model using ECFP fingerprints"""
#     logging.info("\n" + "="*80)
#     logging.info("TASK 1: Baseline Model with ECFP Fingerprints")
#     logging.info("="*80)
    
#     # Prepare features and target
#     X_train = parse_embedding_column(train_df, 'ecfp_fingerprint')
#     y_train = train_df['Tg(K)'].values
    
#     X_test = parse_embedding_column(test_df, 'ecfp_fingerprint')
#     y_test = test_df['Tg(K)'].values
    
#     # Ensure we have matching indices
#     if len(X_train) != len(y_train):
#         # Need to filter y_train to match X_train
#         logging.warning(f"Mismatch in training data: X_train={len(X_train)}, y_train={len(y_train)}")
#         # This is a more complex fix - for now, let's assume they match
    
#     if len(X_test) != len(y_test):
#         logging.warning(f"Mismatch in test data: X_test={len(X_test)}, y_test={len(y_test)}")
    
#     logging.info(f"Training features shape: {X_train.shape}")
#     logging.info(f"Test features shape: {X_test.shape}")
#     logging.info(f"Training samples: {len(y_train)}")
#     logging.info(f"Test samples: {len(y_test)}")
    
#     results = []
    
#     # Run with different random seeds
#     for seed in RANDOM_SEEDS:
#         logging.info(f"\nRunning with random seed: {seed}")
        
#         # Train model
#         model = GradientBoostingRegressor(random_state=seed)
#         model.fit(X_train, y_train)
        
#         # Predict
#         y_pred = model.predict(X_test)
        
#         # Evaluate
#         mae, rmse, r2 = evaluate_model(y_test, y_pred)
        
#         logging.info(f"Seed {seed} - MAE: {mae:.3f}, RMSE: {rmse:.3f}, R²: {r2:.3f}")
        
#         results.append({
#             'seed': seed,
#             'mae': mae,
#             'rmse': rmse,
#             'r2': r2
#         })
    
#     # Calculate statistics
#     maes = [r['mae'] for r in results]
#     rmses = [r['rmse'] for r in results]
#     r2s = [r['r2'] for r in results]
    
#     mae_mean, mae_std = np.mean(maes), np.std(maes, ddof=1)
#     rmse_mean, rmse_std = np.mean(rmses), np.std(rmses, ddof=1)
#     r2_mean, r2_std = np.mean(r2s), np.std(r2s, ddof=1)
    
#     logging.info(f"\n--- TASK 1 FINAL RESULTS ---")
#     logging.info(f"MAE:  {mae_mean:.3f} ± {mae_std:.3f}")
#     logging.info(f"RMSE: {rmse_mean:.3f} ± {rmse_std:.3f}")
#     logging.info(f"R²:   {r2_mean:.3f} ± {r2_std:.3f}")
    
#     return {
#         'task': 'Baseline ECFP',
#         'mae_mean': mae_mean, 'mae_std': mae_std,
#         'rmse_mean': rmse_mean, 'rmse_std': rmse_std,
#         'r2_mean': r2_mean, 'r2_std': r2_std,
#         'n_train': len(X_train), 'n_test': len(X_test)
#     }

# def task2_combined_embeddings(train_df, test_df):
#     """Task 2: Combined embeddings model"""
#     logging.info("\n" + "="*80)
#     logging.info("TASK 2: Combined Embeddings Model")
#     logging.info("="*80)
    
#     # Prepare test set using psmiles_embed to match combined training embeddings
#     X_test = parse_embedding_column(test_df, 'psmiles_bigsmiles_embed')
#     y_test = test_df['Tg(K)'].values
    
#     # Filter y_test to match X_test if needed
#     if len(X_test) != len(y_test):
#         logging.warning(f"Test data mismatch: X_test={len(X_test)}, y_test={len(y_test)}")
#         # For now, assume they should match - this needs more sophisticated handling
    
#     logging.info(f"Test features shape: {X_test.shape}")
#     logging.info(f"Test samples: {len(X_test)}")
    
#     # Create combined training dataset
#     combined_X = []
#     combined_y = []
    
#     # Get the target dimension from test set
#     target_dim = X_test.shape[1]
#     logging.info(f"Target embedding dimension: {target_dim}")
    
#     # Add psmiles_embed data
#     if 'psmiles_bigsmiles_embed' in train_df.columns:
#         try:
#             psmiles_X = parse_embedding_column(train_df, 'psmiles_bigsmiles_embed')
#             if psmiles_X.shape[1] == target_dim:
#                 # Get corresponding y values
#                 psmiles_y = train_df['Tg(K)'].values
#                 if len(psmiles_X) != len(psmiles_y):
#                     # Need to match indices - this is complex, simplified for now
#                     min_len = min(len(psmiles_X), len(psmiles_y))
#                     psmiles_X = psmiles_X[:min_len]
#                     psmiles_y = psmiles_y[:min_len]
                
#                 combined_X.append(psmiles_X)
#                 combined_y.append(psmiles_y)
#                 logging.info(f"Added psmiles_embed: {len(psmiles_y)} samples, shape: {psmiles_X.shape}")
#             else:
#                 logging.warning(f"psmiles_embed dimension mismatch: {psmiles_X.shape[1]} vs {target_dim}")
#         except Exception as e:
#             logging.error(f"Error processing psmiles_embed: {e}")
    
#     # Add bigsmiles_embed data  
#     if 'bigsmiles_psmiles_embed' in train_df.columns:
#         try:
#             bigsmiles_X = parse_embedding_column(train_df, 'bigsmiles_psmiles_embed')
#             if bigsmiles_X.shape[1] == target_dim:
#                 bigsmiles_y = train_df['Tg(K)'].values
#                 if len(bigsmiles_X) != len(bigsmiles_y):
#                     min_len = min(len(bigsmiles_X), len(bigsmiles_y))
#                     bigsmiles_X = bigsmiles_X[:min_len]
#                     bigsmiles_y = bigsmiles_y[:min_len]
                
#                 combined_X.append(bigsmiles_X)
#                 combined_y.append(bigsmiles_y)
#                 logging.info(f"Added bigsmiles_embed: {len(bigsmiles_y)} samples, shape: {bigsmiles_X.shape}")
#             else:
#                 logging.warning(f"bigsmiles_embed dimension mismatch: {bigsmiles_X.shape[1]} vs {target_dim}")
#         except Exception as e:
#             logging.error(f"Error processing bigsmiles_embed: {e}")
    
#     # Add psmiles_embed_polymer_name data
#     if 'psmiles_polymer_name_embed' in train_df.columns:
#         try:
#             psmiles_polymer_X = parse_embedding_column(train_df, 'psmiles_polymer_name_embed')
#             if psmiles_polymer_X.shape[1] == target_dim:
#                 psmiles_polymer_y = train_df['Tg(K)'].values
#                 if len(psmiles_polymer_X) != len(psmiles_polymer_y):
#                     min_len = min(len(psmiles_polymer_X), len(psmiles_polymer_y))
#                     psmiles_polymer_X = psmiles_polymer_X[:min_len]
#                     psmiles_polymer_y = psmiles_polymer_y[:min_len]
                
#                 combined_X.append(psmiles_polymer_X)
#                 combined_y.append(psmiles_polymer_y)
#                 logging.info(f"Added psmiles_embed_polymer_name: {len(psmiles_polymer_y)} samples, shape: {psmiles_polymer_X.shape}")
#             else:
#                 logging.warning(f"psmiles_embed_polymer_name dimension mismatch: {psmiles_polymer_X.shape[1]} vs {target_dim}")
#         except Exception as e:
#             logging.error(f"Error processing psmiles_embed_polymer_name: {e}")
    
#     # Add polymer_name_embed data (if available)
#     if 'polymer_name_psmiles_embed' in train_df.columns:
#         try:
#             # Filter out rows where polymer_name_embed is not null/empty
#             polymer_mask = train_df['polymer_name_psmiles_embed'].notna()
#             if polymer_mask.sum() > 0:
#                 polymer_X = parse_embedding_column(train_df[polymer_mask], 'polymer_name_psmiles_embed')
#                 if polymer_X.shape[1] == target_dim:
#                     polymer_y = train_df[polymer_mask]['Tg(K)'].values
#                     if len(polymer_X) != len(polymer_y):
#                         min_len = min(len(polymer_X), len(polymer_y))
#                         polymer_X = polymer_X[:min_len]
#                         polymer_y = polymer_y[:min_len]
                    
#                     combined_X.append(polymer_X)
#                     combined_y.append(polymer_y)
#                     logging.info(f"Added polymer_name_embed: {len(polymer_y)} samples, shape: {polymer_X.shape}")
#                 else:
#                     logging.warning(f"polymer_name_embed dimension mismatch: {polymer_X.shape[1]} vs {target_dim}")
#         except Exception as e:
#             logging.error(f"Error processing polymer_name_embed: {e}")
    
#     # Check if we have any data
#     if len(combined_X) == 0:
#         logging.error("No embedding data found!")
#         return None
    
#     # Stack all embeddings
#     try:
#         X_train_combined = np.vstack(combined_X)
#         y_train_combined = np.concatenate(combined_y)
        
#         logging.info(f"Combined training data shape: {X_train_combined.shape}")
#         logging.info(f"Total training samples: {len(y_train_combined)}")
        
#         # Verify dimensions match
#         if X_train_combined.shape[1] != X_test.shape[1]:
#             logging.error(f"Dimension mismatch: train={X_train_combined.shape[1]}, test={X_test.shape[1]}")
#             return None
        
#     except Exception as e:
#         logging.error(f"Error combining embeddings: {e}")
#         return None
    
#     results = []
    
#     # Run with different random seeds
#     for seed in RANDOM_SEEDS:
#         logging.info(f"\nRunning with random seed: {seed}")
        
#         # Train model
#         model = GradientBoostingRegressor(random_state=seed)
#         model.fit(X_train_combined, y_train_combined)
        
#         # Predict
#         y_pred = model.predict(X_test)
        
#         # Evaluate
#         mae, rmse, r2 = evaluate_model(y_test, y_pred)
        
#         logging.info(f"Seed {seed} - MAE: {mae:.3f}, RMSE: {rmse:.3f}, R²: {r2:.3f}")
        
#         results.append({
#             'seed': seed,
#             'mae': mae,
#             'rmse': rmse,
#             'r2': r2
#         })
    
#     # Calculate statistics
#     maes = [r['mae'] for r in results]
#     rmses = [r['rmse'] for r in results]
#     r2s = [r['r2'] for r in results]
    
#     mae_mean, mae_std = np.mean(maes), np.std(maes, ddof=1)
#     rmse_mean, rmse_std = np.mean(rmses), np.std(rmses, ddof=1)
#     r2_mean, r2_std = np.mean(r2s), np.std(r2s, ddof=1)
    
#     logging.info(f"\n--- TASK 2 FINAL RESULTS ---")
#     logging.info(f"MAE:  {mae_mean:.3f} ± {mae_std:.3f}")
#     logging.info(f"RMSE: {rmse_mean:.3f} ± {rmse_std:.3f}")
#     logging.info(f"R²:   {r2_mean:.3f} ± {r2_std:.3f}")
    
#     return {
#         'task': 'Combined Embeddings',
#         'mae_mean': mae_mean, 'mae_std': mae_std,
#         'rmse_mean': rmse_mean, 'rmse_std': rmse_std,
#         'r2_mean': r2_mean, 'r2_std': r2_std,
#         'n_train': len(y_train_combined), 'n_test': len(X_test)
#     }

# def task3_feature_based_model(train_df, test_df):
#     """Task 3: Feature-based model using polymer level features"""
#     logging.info("\n" + "="*80)
#     logging.info("TASK 3: Feature-based Model with Polymer Level Features")
#     logging.info("="*80)
    
#     # Extract feature columns
#     try:
#         X_train, feature_columns = extract_feature_columns(train_df, FEATURE_PREFIXES)
#         X_test, _ = extract_feature_columns(test_df, FEATURE_PREFIXES)
        
#         # Get target values
#         y_train = train_df['Tg(K)'].values
#         y_test = test_df['Tg(K)'].values
        
#         logging.info(f"Training features shape: {X_train.shape}")
#         logging.info(f"Test features shape: {X_test.shape}")
#         logging.info(f"Training samples: {len(y_train)}")
#         logging.info(f"Test samples: {len(y_test)}")
        
#         # Check for dimension mismatch
#         if X_train.shape[1] != X_test.shape[1]:
#             logging.error(f"Feature dimension mismatch: train={X_train.shape[1]}, test={X_test.shape[1]}")
#             return None
        
#         # Check for consistent sample sizes
#         if len(X_train) != len(y_train):
#             logging.warning(f"Sample size mismatch in training: X={len(X_train)}, y={len(y_train)}")
#             min_len = min(len(X_train), len(y_train))
#             X_train = X_train[:min_len]
#             y_train = y_train[:min_len]
#             logging.info(f"Adjusted to {min_len} training samples")
        
#         if len(X_test) != len(y_test):
#             logging.warning(f"Sample size mismatch in test: X={len(X_test)}, y={len(y_test)}")
#             min_len = min(len(X_test), len(y_test))
#             X_test = X_test[:min_len]
#             y_test = y_test[:min_len]
#             logging.info(f"Adjusted to {min_len} test samples")
        
#         # Feature scaling (important for feature-based models)
#         scaler = StandardScaler()
#         X_train_scaled = scaler.fit_transform(X_train)
#         X_test_scaled = scaler.transform(X_test)
        
#         logging.info("Features scaled using StandardScaler")
        
#         # Log feature statistics
#         logging.info(f"Feature range after scaling - Train: [{X_train_scaled.min():.3f}, {X_train_scaled.max():.3f}]")
#         logging.info(f"Feature range after scaling - Test: [{X_test_scaled.min():.3f}, {X_test_scaled.max():.3f}]")
        
#         # Breakdown by feature prefix
#         prefix_counts = {}
#         for prefix in FEATURE_PREFIXES:
#             count = sum(1 for col in feature_columns if col.startswith(prefix))
#             prefix_counts[prefix] = count
#             logging.info(f"{prefix}: {count} features")
        
#         results = []
        
#         # Run with different random seeds
#         for seed in RANDOM_SEEDS:
#             logging.info(f"\nRunning with random seed: {seed}")
            
#             # Train model
#             model = GradientBoostingRegressor(random_state=seed)
#             model.fit(X_train_scaled, y_train)
            
#             # Predict
#             y_pred = model.predict(X_test_scaled)
            
#             # Evaluate
#             mae, rmse, r2 = evaluate_model(y_test, y_pred)
            
#             logging.info(f"Seed {seed} - MAE: {mae:.3f}, RMSE: {rmse:.3f}, R²: {r2:.3f}")
            
#             results.append({
#                 'seed': seed,
#                 'mae': mae,
#                 'rmse': rmse,
#                 'r2': r2
#             })
        
#         # Calculate statistics
#         maes = [r['mae'] for r in results]
#         rmses = [r['rmse'] for r in results]
#         r2s = [r['r2'] for r in results]
        
#         mae_mean, mae_std = np.mean(maes), np.std(maes, ddof=1)
#         rmse_mean, rmse_std = np.mean(rmses), np.std(rmses, ddof=1)
#         r2_mean, r2_std = np.mean(r2s), np.std(r2s, ddof=1)
        
#         logging.info(f"\n--- TASK 3 FINAL RESULTS ---")
#         logging.info(f"Total features used: {len(feature_columns)}")
#         for prefix, count in prefix_counts.items():
#             logging.info(f"  {prefix}: {count} features")
#         logging.info(f"MAE:  {mae_mean:.3f} ± {mae_std:.3f}")
#         logging.info(f"RMSE: {rmse_mean:.3f} ± {rmse_std:.3f}")
#         logging.info(f"R²:   {r2_mean:.3f} ± {r2_std:.3f}")
        
#         return {
#             'task': 'Feature-based Model',
#             'mae_mean': mae_mean, 'mae_std': mae_std,
#             'rmse_mean': rmse_mean, 'rmse_std': rmse_std,
#             'r2_mean': r2_mean, 'r2_std': r2_std,
#             'n_train': len(y_train), 'n_test': len(y_test),
#             'n_features': len(feature_columns),
#             'feature_breakdown': prefix_counts
#         }
        
#     except Exception as e:
#         logging.error(f"Error in Task 3: {e}")
#         import traceback
#         traceback.print_exc()
#         return None

# def main():
#     """Main execution function"""
#     print("🚀 Starting Polymer Tg Prediction Experiments")
#     print(f"📊 Train Dataset: {TRAIN_CSV_PATH}")
#     print(f"📊 Test Dataset: {TEST_CSV_PATH}")
#     print(f"🎯 Target: Tg(K)")
#     print(f"🔬 Model: GradientBoostingRegressor (default settings)")
#     print(f"🌱 Random Seeds: {RANDOM_SEEDS}")
#     print(f"🔧 Feature Prefixes: {FEATURE_PREFIXES}")
#     print("="*80)
    
#     # Load datasets
#     train_df, test_df = load_datasets()
    
#     # Run experiments
#     all_results = []
    
#     # Task 1: Baseline ECFP
#     try:
#         result1 = task1_baseline_ecfp(train_df, test_df)
#         if result1:
#             all_results.append(result1)
#     except Exception as e:
#         logging.error(f"Error in Task 1: {e}")
#         import traceback
#         traceback.print_exc()
    
#     # Task 2: Combined embeddings
#     try:
#         result2 = task2_combined_embeddings(train_df, test_df)
#         if result2:
#             all_results.append(result2)
#     except Exception as e:
#         logging.error(f"Error in Task 2: {e}")
#         import traceback
#         traceback.print_exc()
    
#     # Task 3: Feature-based model
#     try:
#         result3 = task3_feature_based_model(train_df, test_df)
#         if result3:
#             all_results.append(result3)
#     except Exception as e:
#         logging.error(f"Error in Task 3: {e}")
#         import traceback
#         traceback.print_exc()
    
#     # Summary
#     if all_results:
#         logging.info("\n" + "="*100)
#         logging.info("📊 FINAL EXPERIMENT SUMMARY")
#         logging.info("="*100)
        
#         for result in all_results:
#             logging.info(f"\n{result['task']}:")
#             logging.info(f"  Training samples: {result['n_train']}")
#             logging.info(f"  Test samples: {result['n_test']}")
#             if 'n_features' in result:
#                 logging.info(f"  Features used: {result['n_features']}")
#             if 'feature_breakdown' in result:
#                 for prefix, count in result['feature_breakdown'].items():
#                     logging.info(f"    {prefix}: {count}")
#             logging.info(f"  MAE:  {result['mae_mean']:.3f} ± {result['mae_std']:.3f}")
#             logging.info(f"  RMSE: {result['rmse_mean']:.3f} ± {result['rmse_std']:.3f}")
#             logging.info(f"  R²:   {result['r2_mean']:.3f} ± {result['r2_std']:.3f}")
        
#         # Save results
#         results_df = pd.DataFrame(all_results)
#         timestamp = datetime.now().strftime("%Y%m%d_%H%M")
#         output_csv = f"case_study_two_Application_Neurips_combining_datasets_{timestamp}.csv"
#         results_df.to_csv(output_csv, index=False)
        
#         logging.info(f"\n💾 Results saved to: {output_csv}")
        
#         print(f"\n📋 EXPERIMENT COMPLETED:")
#         print(f"Results saved to: {output_csv}")
        
#         # Performance comparison
#         if len(all_results) > 1:
#             logging.info("\n🏆 PERFORMANCE COMPARISON (R² Score):")
#             sorted_results = sorted(all_results, key=lambda x: x['r2_mean'], reverse=True)
#             for i, result in enumerate(sorted_results, 1):
#                 logging.info(f"  {i}. {result['task']}: R² = {result['r2_mean']:.3f} ± {result['r2_std']:.3f}")
            
#             logging.info("\n🎯 PERFORMANCE COMPARISON (MAE - Lower is Better):")
#             sorted_mae = sorted(all_results, key=lambda x: x['mae_mean'])
#             for i, result in enumerate(sorted_mae, 1):
#                 logging.info(f"  {i}. {result['task']}: MAE = {result['mae_mean']:.3f} ± {result['mae_std']:.3f}")
#     else:
#         logging.error("No results generated. Check for errors in the experiments.")

# if __name__ == "__main__":
#     main()




# neurips - Multi-Property Version
import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler
from datetime import datetime
import logging

# Configuration
RANDOM_SEEDS = [42, 44, 45, 46]  # Four different random seeds

# Dataset paths
TRAIN_CSV_PATH = '/home/ta45woj/PolyMetriX/src/polymetrix/valid_dataset_20250723_1042_case_study_two_neurips_challenge_dataset_Tg_FFV_unsqueeze_embeddings_ecfp_info_train_set_Tc.csv'
TEST_CSV_PATH = '/home/ta45woj/PolyMetriX/src/polymetrix/valid_dataset_20250723_1042_case_study_two_neurips_challenge_dataset_Tg_FFV_unsqueeze_embeddings_ecfp_info_test_set_Tc.csv'

# Target properties to predict
# TARGET_PROPERTIES = ['Tg(K)', 'FFV', 'Tc', 'Density', 'Rg']
TARGET_PROPERTIES = ['Tc']

# Feature prefixes for Task 3
FEATURE_PREFIXES = ['fullpolymerlevel.features.', 'sidechainlevel.features.', 'backbonelevel.features.']

# Initialize logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

def load_datasets():
    """Load training and test datasets"""
    logging.info("Loading datasets...")
    train_df = pd.read_csv(TRAIN_CSV_PATH)
    test_df = pd.read_csv(TEST_CSV_PATH)
    
    logging.info(f"Train dataset shape: {train_df.shape}")
    logging.info(f"Test dataset shape: {test_df.shape}")
    
    return train_df, test_df

def filter_nan_values(train_df, test_df, target_property):
    """Filter out NaN values for the specified target property"""
    logging.info(f"Filtering NaN values for property: {target_property}")
    
    # Check if property exists in both datasets
    if target_property not in train_df.columns:
        logging.error(f"Property {target_property} not found in training dataset")
        return None, None
    if target_property not in test_df.columns:
        logging.error(f"Property {target_property} not found in test dataset")
        return None, None
    
    # Filter training data
    train_mask = train_df[target_property].notna()
    train_filtered = train_df[train_mask].copy()
    
    # Filter test data
    test_mask = test_df[target_property].notna()
    test_filtered = test_df[test_mask].copy()
    
    logging.info(f"Training data: {len(train_df)} → {len(train_filtered)} samples (removed {len(train_df) - len(train_filtered)} NaN)")
    logging.info(f"Test data: {len(test_df)} → {len(test_filtered)} samples (removed {len(test_df) - len(test_filtered)} NaN)")
    
    if len(train_filtered) == 0:
        logging.error(f"No valid training samples for property {target_property}")
        return None, None
    if len(test_filtered) == 0:
        logging.error(f"No valid test samples for property {target_property}")
        return None, None
    
    return train_filtered, test_filtered

def parse_embedding_column(df, column_name):
    """Parse embedding column from string representation to numpy array"""
    embeddings = []
    embedding_lengths = []
    valid_indices = []
    
    for i, embedding_str in enumerate(df[column_name]):
        # Handle different string formats
        embedding_str = str(embedding_str).strip()
        
        # Skip if NaN or empty
        if embedding_str == 'nan' or embedding_str == '' or pd.isna(embedding_str):
            continue
            
        # Handle PyTorch tensor format: "tensor([0.1, 0.2, ...])"
        if embedding_str.startswith('tensor('):
            # Extract the array part from tensor([...])
            start_idx = embedding_str.find('[')
            end_idx = embedding_str.rfind(']')
            if start_idx != -1 and end_idx != -1:
                array_str = embedding_str[start_idx+1:end_idx]
            else:
                logging.warning(f"Invalid tensor format at row {i}: {embedding_str[:50]}...")
                continue
        # Handle simple array format: "[0.1, 0.2, ...]"
        elif embedding_str.startswith('[') and embedding_str.endswith(']'):
            array_str = embedding_str[1:-1]
        else:
            # Try to use as-is
            array_str = embedding_str
        
        # Parse the numbers
        try:
            # Split by comma and convert to float
            values = [float(x.strip()) for x in array_str.split(',') if x.strip()]
            if len(values) == 0:
                logging.warning(f"Empty embedding at row {i}")
                continue
                
            embedding = np.array(values)
            embeddings.append(embedding)
            embedding_lengths.append(len(values))
            valid_indices.append(i)
        except ValueError as e:
            logging.warning(f"Error parsing embedding at row {i}: {embedding_str[:50]}... - {e}")
            continue
    
    if len(embeddings) == 0:
        raise ValueError(f"No valid embeddings found in column {column_name}")
    
    # Check for consistent dimensions
    unique_lengths = set(embedding_lengths)
    if len(unique_lengths) > 1:
        logging.warning(f"Inconsistent embedding dimensions in {column_name}: {unique_lengths}")
        # Use the most common dimension
        from collections import Counter
        most_common_length = Counter(embedding_lengths).most_common(1)[0][0]
        logging.info(f"Using most common dimension: {most_common_length}")
        
        # Filter embeddings to consistent dimension
        filtered_embeddings = []
        filtered_indices = []
        for emb, idx in zip(embeddings, valid_indices):
            if len(emb) == most_common_length:
                filtered_embeddings.append(emb)
                filtered_indices.append(idx)
        
        embeddings = filtered_embeddings
        valid_indices = filtered_indices
        logging.info(f"Filtered to {len(embeddings)} embeddings with consistent dimension")
    
    if len(embeddings) == 0:
        raise ValueError(f"No embeddings with consistent dimensions in column {column_name}")
    
    # Now create the numpy array
    try:
        result = np.array(embeddings)
        logging.info(f"Successfully parsed {column_name}: shape {result.shape}")
        return result, valid_indices
    except Exception as e:
        logging.error(f"Failed to create numpy array for {column_name}: {e}")
        # Try creating it row by row to identify the problematic entries
        max_len = max(len(emb) for emb in embeddings)
        min_len = min(len(emb) for emb in embeddings)
        logging.error(f"Embedding length range: {min_len} to {max_len}")
        raise e

def extract_feature_columns(df, feature_prefixes):
    """Extract feature columns based on prefixes"""
    feature_columns = []
    
    for prefix in feature_prefixes:
        prefix_columns = [col for col in df.columns if col.startswith(prefix)]
        feature_columns.extend(prefix_columns)
        logging.info(f"Found {len(prefix_columns)} columns with prefix '{prefix}'")
    
    if len(feature_columns) == 0:
        raise ValueError(f"No feature columns found with prefixes: {feature_prefixes}")
    
    logging.info(f"Total feature columns found: {len(feature_columns)}")
    
    # Extract the features and handle missing values
    X = df[feature_columns].copy()
    
    # Check for missing values
    missing_counts = X.isnull().sum()
    if missing_counts.sum() > 0:
        logging.warning(f"Found missing values in {missing_counts[missing_counts > 0].shape[0]} columns")
        logging.info("Filling missing values with 0")
        X = X.fillna(0)
    
    # Check for non-numeric columns
    numeric_columns = X.select_dtypes(include=[np.number]).columns
    if len(numeric_columns) != len(feature_columns):
        non_numeric = set(feature_columns) - set(numeric_columns)
        logging.warning(f"Non-numeric columns found: {non_numeric}")
        X = X[numeric_columns]
        logging.info(f"Using {len(numeric_columns)} numeric columns")
    
    return X.values, feature_columns

def evaluate_model(y_true, y_pred):
    """Calculate evaluation metrics"""
    mae = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    r2 = r2_score(y_true, y_pred)
    return mae, rmse, r2

def task1_baseline_ecfp(train_df, test_df, target_property):
    """Task 1: Baseline model using ECFP fingerprints"""
    logging.info(f"\n--- TASK 1: Baseline Model with ECFP Fingerprints for {target_property} ---")
    
    # Prepare features and target
    try:
        X_train, train_indices = parse_embedding_column(train_df, 'ecfp_fingerprint')
        y_train = train_df.iloc[train_indices][target_property].values
        
        X_test, test_indices = parse_embedding_column(test_df, 'ecfp_fingerprint')
        y_test = test_df.iloc[test_indices][target_property].values
    except Exception as e:
        logging.error(f"Error parsing embeddings for {target_property}: {e}")
        return None
    
    logging.info(f"Training features shape: {X_train.shape}")
    logging.info(f"Test features shape: {X_test.shape}")
    logging.info(f"Training samples: {len(y_train)}")
    logging.info(f"Test samples: {len(y_test)}")
    
    results = []
    
    # Run with different random seeds
    for seed in RANDOM_SEEDS:
        logging.info(f"Running with random seed: {seed}")
        
        # Train model
        model = GradientBoostingRegressor(random_state=seed)
        model.fit(X_train, y_train)
        
        # Predict
        y_pred = model.predict(X_test)
        
        # Evaluate
        mae, rmse, r2 = evaluate_model(y_test, y_pred)
        
        logging.info(f"Seed {seed} - MAE: {mae:.3f}, RMSE: {rmse:.3f}, R²: {r2:.3f}")
        
        results.append({
            'seed': seed,
            'mae': mae,
            'rmse': rmse,
            'r2': r2
        })
    
    # Calculate statistics
    maes = [r['mae'] for r in results]
    rmses = [r['rmse'] for r in results]
    r2s = [r['r2'] for r in results]
    
    mae_mean, mae_std = np.mean(maes), np.std(maes, ddof=1) if len(maes) > 1 else 0
    rmse_mean, rmse_std = np.mean(rmses), np.std(rmses, ddof=1) if len(rmses) > 1 else 0
    r2_mean, r2_std = np.mean(r2s), np.std(r2s, ddof=1) if len(r2s) > 1 else 0
    
    logging.info(f"TASK 1 FINAL RESULTS for {target_property}:")
    logging.info(f"MAE:  {mae_mean:.3f} ± {mae_std:.3f}")
    logging.info(f"RMSE: {rmse_mean:.3f} ± {rmse_std:.3f}")
    logging.info(f"R²:   {r2_mean:.3f} ± {r2_std:.3f}")
    
    return {
        'task': 'Baseline ECFP',
        'property': target_property,
        'mae_mean': mae_mean, 'mae_std': mae_std,
        'rmse_mean': rmse_mean, 'rmse_std': rmse_std,
        'r2_mean': r2_mean, 'r2_std': r2_std,
        'n_train': len(X_train), 'n_test': len(X_test)
    }

def task2_combined_embeddings(train_df, test_df, target_property):
    """Task 2: Combined embeddings model"""
    logging.info(f"\n--- TASK 2: Combined Embeddings Model for {target_property} ---")
    
    # Prepare test set using psmiles_embed to match combined training embeddings
    try:
        X_test, test_indices = parse_embedding_column(test_df, 'psmiles_bigsmiles_embed')
        y_test = test_df.iloc[test_indices][target_property].values
    except Exception as e:
        logging.error(f"Error parsing test embeddings for {target_property}: {e}")
        return None
    
    logging.info(f"Test features shape: {X_test.shape}")
    logging.info(f"Test samples: {len(X_test)}")
    
    # Create combined training dataset
    combined_X = []
    combined_y = []
    
    # Get the target dimension from test set
    target_dim = X_test.shape[1]
    logging.info(f"Target embedding dimension: {target_dim}")
    
    # List of embedding columns to try
    embedding_columns = [
        'psmiles_bigsmiles_embed',
        # 'bigsmiles_psmiles_embed', 
        # 'psmiles_polymer_name_embed',
        # 'polymer_name_psmiles_embed'
    ]
    
    for col_name in embedding_columns:
        if col_name in train_df.columns:
            try:
                embed_X, embed_indices = parse_embedding_column(train_df, col_name)
                if embed_X.shape[1] == target_dim:
                    embed_y = train_df.iloc[embed_indices][target_property].values
                    
                    combined_X.append(embed_X)
                    combined_y.append(embed_y)
                    logging.info(f"Added {col_name}: {len(embed_y)} samples, shape: {embed_X.shape}")
                else:
                    logging.warning(f"{col_name} dimension mismatch: {embed_X.shape[1]} vs {target_dim}")
            except Exception as e:
                logging.error(f"Error processing {col_name}: {e}")
    
    # Check if we have any data
    if len(combined_X) == 0:
        logging.error("No embedding data found!")
        return None
    
    # Stack all embeddings
    try:
        X_train_combined = np.vstack(combined_X)
        y_train_combined = np.concatenate(combined_y)
        
        logging.info(f"Combined training data shape: {X_train_combined.shape}")
        logging.info(f"Total training samples: {len(y_train_combined)}")
        
        # Verify dimensions match
        if X_train_combined.shape[1] != X_test.shape[1]:
            logging.error(f"Dimension mismatch: train={X_train_combined.shape[1]}, test={X_test.shape[1]}")
            return None
        
    except Exception as e:
        logging.error(f"Error combining embeddings: {e}")
        return None
    
    results = []
    
    # Run with different random seeds
    for seed in RANDOM_SEEDS:
        logging.info(f"Running with random seed: {seed}")
        
        # Train model
        model = GradientBoostingRegressor(random_state=seed)
        model.fit(X_train_combined, y_train_combined)
        
        # Predict
        y_pred = model.predict(X_test)
        
        # Evaluate
        mae, rmse, r2 = evaluate_model(y_test, y_pred)
        
        logging.info(f"Seed {seed} - MAE: {mae:.3f}, RMSE: {rmse:.3f}, R²: {r2:.3f}")
        
        results.append({
            'seed': seed,
            'mae': mae,
            'rmse': rmse,
            'r2': r2
        })
    
    # Calculate statistics
    maes = [r['mae'] for r in results]
    rmses = [r['rmse'] for r in results]
    r2s = [r['r2'] for r in results]
    
    mae_mean, mae_std = np.mean(maes), np.std(maes, ddof=1) if len(maes) > 1 else 0
    rmse_mean, rmse_std = np.mean(rmses), np.std(rmses, ddof=1) if len(rmses) > 1 else 0
    r2_mean, r2_std = np.mean(r2s), np.std(r2s, ddof=1) if len(r2s) > 1 else 0
    
    logging.info(f"TASK 2 FINAL RESULTS for {target_property}:")
    logging.info(f"MAE:  {mae_mean:.3f} ± {mae_std:.3f}")
    logging.info(f"RMSE: {rmse_mean:.3f} ± {rmse_std:.3f}")
    logging.info(f"R²:   {r2_mean:.3f} ± {r2_std:.3f}")
    
    return {
        'task': 'Combined Embeddings',
        'property': target_property,
        'mae_mean': mae_mean, 'mae_std': mae_std,
        'rmse_mean': rmse_mean, 'rmse_std': rmse_std,
        'r2_mean': r2_mean, 'r2_std': r2_std,
        'n_train': len(y_train_combined), 'n_test': len(X_test)
    }

# def task3_feature_based_model(train_df, test_df, target_property):
#     """Task 3: Feature-based model using polymer level features"""
#     logging.info(f"\n--- TASK 3: Feature-based Model with Polymer Level Features for {target_property} ---")
    
#     # Extract feature columns
#     try:
#         X_train, feature_columns = extract_feature_columns(train_df, FEATURE_PREFIXES)
#         X_test, _ = extract_feature_columns(test_df, FEATURE_PREFIXES)
        
#         # Get target values
#         y_train = train_df[target_property].values
#         y_test = test_df[target_property].values
        
#         logging.info(f"Training features shape: {X_train.shape}")
#         logging.info(f"Test features shape: {X_test.shape}")
#         logging.info(f"Training samples: {len(y_train)}")
#         logging.info(f"Test samples: {len(y_test)}")
        
#         # Check for dimension mismatch
#         if X_train.shape[1] != X_test.shape[1]:
#             logging.error(f"Feature dimension mismatch: train={X_train.shape[1]}, test={X_test.shape[1]}")
#             return None
        
#         # Check for consistent sample sizes
#         if len(X_train) != len(y_train):
#             logging.warning(f"Sample size mismatch in training: X={len(X_train)}, y={len(y_train)}")
#             min_len = min(len(X_train), len(y_train))
#             X_train = X_train[:min_len]
#             y_train = y_train[:min_len]
#             logging.info(f"Adjusted to {min_len} training samples")
        
#         if len(X_test) != len(y_test):
#             logging.warning(f"Sample size mismatch in test: X={len(X_test)}, y={len(y_test)}")
#             min_len = min(len(X_test), len(y_test))
#             X_test = X_test[:min_len]
#             y_test = y_test[:min_len]
#             logging.info(f"Adjusted to {min_len} test samples")
        
#         # Feature scaling (important for feature-based models)
#         scaler = StandardScaler()
#         X_train_scaled = scaler.fit_transform(X_train)
#         X_test_scaled = scaler.transform(X_test)
        
#         logging.info("Features scaled using StandardScaler")
        
#         # Log feature statistics
#         logging.info(f"Feature range after scaling - Train: [{X_train_scaled.min():.3f}, {X_train_scaled.max():.3f}]")
#         logging.info(f"Feature range after scaling - Test: [{X_test_scaled.min():.3f}, {X_test_scaled.max():.3f}]")
        
#         # Breakdown by feature prefix
#         prefix_counts = {}
#         for prefix in FEATURE_PREFIXES:
#             count = sum(1 for col in feature_columns if col.startswith(prefix))
#             prefix_counts[prefix] = count
#             logging.info(f"{prefix}: {count} features")
        
#         results = []
        
#         # Run with different random seeds
#         for seed in RANDOM_SEEDS:
#             logging.info(f"Running with random seed: {seed}")
            
#             # Train model
#             model = GradientBoostingRegressor(random_state=seed)
#             model.fit(X_train_scaled, y_train)
            
#             # Predict
#             y_pred = model.predict(X_test_scaled)
            
#             # Evaluate
#             mae, rmse, r2 = evaluate_model(y_test, y_pred)
            
#             logging.info(f"Seed {seed} - MAE: {mae:.3f}, RMSE: {rmse:.3f}, R²: {r2:.3f}")
            
#             results.append({
#                 'seed': seed,
#                 'mae': mae,
#                 'rmse': rmse,
#                 'r2': r2
#             })
        
#         # Calculate statistics
#         maes = [r['mae'] for r in results]
#         rmses = [r['rmse'] for r in results]
#         r2s = [r['r2'] for r in results]
        
#         mae_mean, mae_std = np.mean(maes), np.std(maes, ddof=1) if len(maes) > 1 else 0
#         rmse_mean, rmse_std = np.mean(rmses), np.std(rmses, ddof=1) if len(rmses) > 1 else 0
#         r2_mean, r2_std = np.mean(r2s), np.std(r2s, ddof=1) if len(r2s) > 1 else 0
        
#         logging.info(f"TASK 3 FINAL RESULTS for {target_property}:")
#         logging.info(f"Total features used: {len(feature_columns)}")
#         for prefix, count in prefix_counts.items():
#             logging.info(f"  {prefix}: {count} features")
#         logging.info(f"MAE:  {mae_mean:.3f} ± {mae_std:.3f}")
#         logging.info(f"RMSE: {rmse_mean:.3f} ± {rmse_std:.3f}")
#         logging.info(f"R²:   {r2_mean:.3f} ± {r2_std:.3f}")
        
#         return {
#             'task': 'Feature-based Model',
#             'property': target_property,
#             'mae_mean': mae_mean, 'mae_std': mae_std,
#             'rmse_mean': rmse_mean, 'rmse_std': rmse_std,
#             'r2_mean': r2_mean, 'r2_std': r2_std,
#             'n_train': len(y_train), 'n_test': len(y_test),
#             'n_features': len(feature_columns),
#             'feature_breakdown': prefix_counts
#         }
        
#     except Exception as e:
#         logging.error(f"Error in Task 3 for {target_property}: {e}")
#         import traceback
#         traceback.print_exc()
#         return None

def run_experiments_for_property(train_df, test_df, target_property):
    """Run all three tasks for a specific target property"""
    logging.info(f"\n{'='*100}")
    logging.info(f"🎯 STARTING EXPERIMENTS FOR PROPERTY: {target_property}")
    logging.info(f"{'='*100}")
    
    # Filter datasets for this property
    train_filtered, test_filtered = filter_nan_values(train_df, test_df, target_property)
    
    if train_filtered is None or test_filtered is None:
        logging.error(f"Cannot proceed with {target_property} due to filtering issues")
        return []
    
    property_results = []
    
    # Task 1: Baseline ECFP
    try:
        result1 = task1_baseline_ecfp(train_filtered, test_filtered, target_property)
        if result1:
            property_results.append(result1)
    except Exception as e:
        logging.error(f"Error in Task 1 for {target_property}: {e}")
        import traceback
        traceback.print_exc()
    
    # Task 2: Combined embeddings
    try:
        result2 = task2_combined_embeddings(train_filtered, test_filtered, target_property)
        if result2:
            property_results.append(result2)
    except Exception as e:
        logging.error(f"Error in Task 2 for {target_property}: {e}")
        import traceback
        traceback.print_exc()
    
    # Task 3: Feature-based model
    try:
        result3 = task3_feature_based_model(train_filtered, test_filtered, target_property)
        if result3:
            property_results.append(result3)
    except Exception as e:
        logging.error(f"Error in Task 3 for {target_property}: {e}")
        import traceback
        traceback.print_exc()
    
    return property_results

def main():
    """Main execution function"""
    print("🚀 Starting Multi-Property Polymer Prediction Experiments")
    print(f"📊 Train Dataset: {TRAIN_CSV_PATH}")
    print(f"📊 Test Dataset: {TEST_CSV_PATH}")
    print(f"🎯 Target Properties: {TARGET_PROPERTIES}")
    print(f"🔬 Model: GradientBoostingRegressor (default settings)")
    print(f"🌱 Random Seeds: {RANDOM_SEEDS}")
    print(f"🔧 Feature Prefixes: {FEATURE_PREFIXES}")
    print("="*100)
    
    # Load datasets
    train_df, test_df = load_datasets()
    
    # Check which properties are available
    available_properties = []
    for prop in TARGET_PROPERTIES:
        if prop in train_df.columns and prop in test_df.columns:
            available_properties.append(prop)
            logging.info(f"✅ Property {prop} found in both datasets")
        else:
            logging.warning(f"❌ Property {prop} missing from datasets")
    
    if not available_properties:
        logging.error("No target properties available in datasets!")
        return
    
    logging.info(f"Will run experiments for {len(available_properties)} properties: {available_properties}")
    
    # Run experiments for each property
    all_results = []
    
    for target_property in available_properties:
        property_results = run_experiments_for_property(train_df, test_df, target_property)
        all_results.extend(property_results)
    
    # Summary
    if all_results:
        logging.info("\n" + "="*120)
        logging.info("📊 FINAL MULTI-PROPERTY EXPERIMENT SUMMARY")
        logging.info("="*120)
        
        # Group results by property
        results_by_property = {}
        for result in all_results:
            prop = result['property']
            if prop not in results_by_property:
                results_by_property[prop] = []
            results_by_property[prop].append(result)
        
        # Display results grouped by property
        for prop, prop_results in results_by_property.items():
            logging.info(f"\n🎯 RESULTS FOR {prop}:")
            logging.info("-" * 80)
            
            for result in prop_results:
                logging.info(f"\n{result['task']}:")
                logging.info(f"  Training samples: {result['n_train']}")
                logging.info(f"  Test samples: {result['n_test']}")
                if 'n_features' in result:
                    logging.info(f"  Features used: {result['n_features']}")
                if 'feature_breakdown' in result:
                    for prefix, count in result['feature_breakdown'].items():
                        logging.info(f"    {prefix}: {count}")
                logging.info(f"  MAE:  {result['mae_mean']:.3f} ± {result['mae_std']:.3f}")
                logging.info(f"  RMSE: {result['rmse_mean']:.3f} ± {result['rmse_std']:.3f}")
                logging.info(f"  R²:   {result['r2_mean']:.3f} ± {result['r2_std']:.3f}")
            
            # Best performance for this property
            if len(prop_results) > 1:
                best_r2 = max(prop_results, key=lambda x: x['r2_mean'])
                best_mae = min(prop_results, key=lambda x: x['mae_mean'])
                
                logging.info(f"\n🏆 BEST FOR {prop}:")
                logging.info(f"  Highest R²: {best_r2['task']} - R² = {best_r2['r2_mean']:.3f} ± {best_r2['r2_std']:.3f}")
                logging.info(f"  Lowest MAE: {best_mae['task']} - MAE = {best_mae['mae_mean']:.3f} ± {best_mae['mae_std']:.3f}")
        
        # Save results
        results_df = pd.DataFrame(all_results)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        output_csv = f"multi_property_neurips_results_{timestamp}.csv"
        results_df.to_csv(output_csv, index=False)
        
        logging.info(f"\n💾 Results saved to: {output_csv}")
        
        print(f"\n📋 MULTI-PROPERTY EXPERIMENT COMPLETED:")
        print(f"Results saved to: {output_csv}")
        print(f"Properties analyzed: {list(results_by_property.keys())}")
        
        # Overall performance comparison
        logging.info("\n🌟 OVERALL PERFORMANCE COMPARISON:")
        logging.info("-" * 80)
        
        # Best performing method per property
        for prop, prop_results in results_by_property.items():
            if len(prop_results) > 1:
                best_overall = max(prop_results, key=lambda x: x['r2_mean'])
                logging.info(f"{prop}: {best_overall['task']} (R² = {best_overall['r2_mean']:.3f})")
            elif len(prop_results) == 1:
                logging.info(f"{prop}: {prop_results[0]['task']} (R² = {prop_results[0]['r2_mean']:.3f})")
        
        # Task performance across all properties
        task_performance = {}
        for result in all_results:
            task = result['task']
            if task not in task_performance:
                task_performance[task] = {'r2_scores': [], 'mae_scores': []}
            task_performance[task]['r2_scores'].append(result['r2_mean'])
            task_performance[task]['mae_scores'].append(result['mae_mean'])
        
        logging.info("\n📈 AVERAGE PERFORMANCE ACROSS ALL PROPERTIES:")
        for task, scores in task_performance.items():
            avg_r2 = np.mean(scores['r2_scores'])
            avg_mae = np.mean(scores['mae_scores'])
            logging.info(f"{task}: Avg R² = {avg_r2:.3f}, Avg MAE = {avg_mae:.3f}")
        
    else:
        logging.error("No results generated. Check for errors in the experiments.")

if __name__ == "__main__":
    main()






# # neurips
# import numpy as np
# import pandas as pd
# from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
# from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
# from sklearn.preprocessing import StandardScaler
# from datetime import datetime
# import logging

# # Configuration
# RANDOM_SEEDS = [42, 43, 44, 45]  # Three different random seeds

# # Dataset paths
# TRAIN_CSV_PATH = '/home/ta45woj/PolyMetriX/src/polymetrix/datasets/valid_dataset_20250715_1717_0.95_trained_model_neurips_application_tg_combining_datasets_ecfp_info_train_set.csv'
# TEST_CSV_PATH = '/home/ta45woj/PolyMetriX/src/polymetrix/datasets/valid_dataset_20250715_1717_0.95_trained_model_neurips_application_tg_combining_datasets_ecfp_info_test_set.csv'

# # Feature prefixes for Task 3
# FEATURE_PREFIXES = ['fullpolymerlevel.features.', 'sidechainlevel.features.', 'backbonelevel.features.']

# # Initialize logging
# logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

# def load_datasets():
#     """Load training and test datasets"""
#     logging.info("Loading datasets...")
#     train_df = pd.read_csv(TRAIN_CSV_PATH)
#     test_df = pd.read_csv(TEST_CSV_PATH)
    
#     logging.info(f"Train dataset shape: {train_df.shape}")
#     logging.info(f"Test dataset shape: {test_df.shape}")
    
#     return train_df, test_df

# def parse_embedding_column(df, column_name):
#     """Parse embedding column from string representation to numpy array"""
#     embeddings = []
#     embedding_lengths = []
    
#     for i, embedding_str in enumerate(df[column_name]):
#         # Handle different string formats
#         embedding_str = str(embedding_str).strip()
        
#         # Skip if NaN or empty
#         if embedding_str == 'nan' or embedding_str == '' or pd.isna(embedding_str):
#             continue
            
#         # Handle PyTorch tensor format: "tensor([0.1, 0.2, ...])"
#         if embedding_str.startswith('tensor('):
#             # Extract the array part from tensor([...])
#             start_idx = embedding_str.find('[')
#             end_idx = embedding_str.rfind(']')
#             if start_idx != -1 and end_idx != -1:
#                 array_str = embedding_str[start_idx+1:end_idx]
#             else:
#                 logging.warning(f"Invalid tensor format at row {i}: {embedding_str[:50]}...")
#                 continue
#         # Handle simple array format: "[0.1, 0.2, ...]"
#         elif embedding_str.startswith('[') and embedding_str.endswith(']'):
#             array_str = embedding_str[1:-1]
#         else:
#             # Try to use as-is
#             array_str = embedding_str
        
#         # Parse the numbers
#         try:
#             # Split by comma and convert to float
#             values = [float(x.strip()) for x in array_str.split(',') if x.strip()]
#             if len(values) == 0:
#                 logging.warning(f"Empty embedding at row {i}")
#                 continue
                
#             embedding = np.array(values)
#             embeddings.append(embedding)
#             embedding_lengths.append(len(values))
#         except ValueError as e:
#             logging.warning(f"Error parsing embedding at row {i}: {embedding_str[:50]}... - {e}")
#             continue
    
#     if len(embeddings) == 0:
#         raise ValueError(f"No valid embeddings found in column {column_name}")
    
#     # Check for consistent dimensions
#     unique_lengths = set(embedding_lengths)
#     if len(unique_lengths) > 1:
#         logging.warning(f"Inconsistent embedding dimensions in {column_name}: {unique_lengths}")
#         # Use the most common dimension
#         from collections import Counter
#         most_common_length = Counter(embedding_lengths).most_common(1)[0][0]
#         logging.info(f"Using most common dimension: {most_common_length}")
        
#         # Filter embeddings to consistent dimension
#         filtered_embeddings = []
#         for emb in embeddings:
#             if len(emb) == most_common_length:
#                 filtered_embeddings.append(emb)
        
#         embeddings = filtered_embeddings
#         logging.info(f"Filtered to {len(embeddings)} embeddings with consistent dimension")
    
#     if len(embeddings) == 0:
#         raise ValueError(f"No embeddings with consistent dimensions in column {column_name}")
    
#     # Now create the numpy array
#     try:
#         result = np.array(embeddings)
#         logging.info(f"Successfully parsed {column_name}: shape {result.shape}")
#         return result
#     except Exception as e:
#         logging.error(f"Failed to create numpy array for {column_name}: {e}")
#         # Try creating it row by row to identify the problematic entries
#         max_len = max(len(emb) for emb in embeddings)
#         min_len = min(len(emb) for emb in embeddings)
#         logging.error(f"Embedding length range: {min_len} to {max_len}")
#         raise e

# def extract_feature_columns(df, feature_prefixes):
#     """Extract feature columns based on prefixes"""
#     feature_columns = []
    
#     for prefix in feature_prefixes:
#         prefix_columns = [col for col in df.columns if col.startswith(prefix)]
#         feature_columns.extend(prefix_columns)
#         logging.info(f"Found {len(prefix_columns)} columns with prefix '{prefix}'")
    
#     if len(feature_columns) == 0:
#         raise ValueError(f"No feature columns found with prefixes: {feature_prefixes}")
    
#     logging.info(f"Total feature columns found: {len(feature_columns)}")
    
#     # Extract the features and handle missing values
#     X = df[feature_columns].copy()
    
#     # Check for missing values
#     missing_counts = X.isnull().sum()
#     if missing_counts.sum() > 0:
#         logging.warning(f"Found missing values in {missing_counts[missing_counts > 0].shape[0]} columns")
#         logging.info("Filling missing values with 0")
#         X = X.fillna(0)
    
#     # Check for non-numeric columns
#     numeric_columns = X.select_dtypes(include=[np.number]).columns
#     if len(numeric_columns) != len(feature_columns):
#         non_numeric = set(feature_columns) - set(numeric_columns)
#         logging.warning(f"Non-numeric columns found: {non_numeric}")
#         X = X[numeric_columns]
#         logging.info(f"Using {len(numeric_columns)} numeric columns")
    
#     return X.values, feature_columns

# def evaluate_model(y_true, y_pred):
#     """Calculate evaluation metrics"""
#     mae = mean_absolute_error(y_true, y_pred)
#     rmse = np.sqrt(mean_squared_error(y_true, y_pred))
#     r2 = r2_score(y_true, y_pred)
#     return mae, rmse, r2

# def task1_baseline_ecfp(train_df, test_df):
#     """Task 1: Baseline model using ECFP fingerprints"""
#     logging.info("\n" + "="*80)
#     logging.info("TASK 1: Baseline Model with ECFP Fingerprints")
#     logging.info("="*80)
    
#     # Prepare features and target
#     X_train = parse_embedding_column(train_df, 'ecfp_fingerprint')
#     y_train = train_df['Tg(K)'].values
    
#     X_test = parse_embedding_column(test_df, 'ecfp_fingerprint')
#     y_test = test_df['Tg(K)'].values
    
#     # Ensure we have matching indices
#     if len(X_train) != len(y_train):
#         logging.warning(f"Mismatch in training data: X_train={len(X_train)}, y_train={len(y_train)}")
    
#     if len(X_test) != len(y_test):
#         logging.warning(f"Mismatch in test data: X_test={len(X_test)}, y_test={len(y_test)}")
    
#     logging.info(f"Training features shape: {X_train.shape}")
#     logging.info(f"Test features shape: {X_test.shape}")
#     logging.info(f"Training samples: {len(y_train)}")
#     logging.info(f"Test samples: {len(y_test)}")
    
#     results = []
    
#     # Run with different random seeds
#     for seed in RANDOM_SEEDS:
#         logging.info(f"\nRunning with random seed: {seed}")
        
#         # Train model
#         model = GradientBoostingRegressor(random_state=seed)
#         model.fit(X_train, y_train)
        
#         # Predict
#         y_pred = model.predict(X_test)
        
#         # Evaluate
#         mae, rmse, r2 = evaluate_model(y_test, y_pred)
        
#         logging.info(f"Seed {seed} - MAE: {mae:.3f}, RMSE: {rmse:.3f}, R²: {r2:.3f}")
        
#         results.append({
#             'seed': seed,
#             'mae': mae,
#             'rmse': rmse,
#             'r2': r2
#         })
    
#     # Calculate statistics
#     maes = [r['mae'] for r in results]
#     rmses = [r['rmse'] for r in results]
#     r2s = [r['r2'] for r in results]
    
#     mae_mean, mae_std = np.mean(maes), np.std(maes, ddof=1)
#     rmse_mean, rmse_std = np.mean(rmses), np.std(rmses, ddof=1)
#     r2_mean, r2_std = np.mean(r2s), np.std(r2s, ddof=1)
    
#     logging.info(f"\n--- TASK 1 FINAL RESULTS ---")
#     logging.info(f"MAE:  {mae_mean:.3f} ± {mae_std:.3f}")
#     logging.info(f"RMSE: {rmse_mean:.3f} ± {rmse_std:.3f}")
#     logging.info(f"R²:   {r2_mean:.3f} ± {r2_std:.3f}")
    
#     return {
#         'task': 'Baseline ECFP',
#         'mae_mean': mae_mean, 'mae_std': mae_std,
#         'rmse_mean': rmse_mean, 'rmse_std': rmse_std,
#         'r2_mean': r2_mean, 'r2_std': r2_std,
#         'n_train': len(X_train), 'n_test': len(X_test)
#     }

# def task2_combined_embeddings(train_df, test_df):
#     """Task 2: Combined embeddings model"""
#     logging.info("\n" + "="*80)
#     logging.info("TASK 2: Combined Embeddings Model")
#     logging.info("="*80)
    
#     # Prepare test set using psmiles_embed to match combined training embeddings
#     X_test = parse_embedding_column(test_df, 'psmiles_bigsmiles_embed')
#     y_test = test_df['Tg(K)'].values
    
#     # Filter y_test to match X_test if needed
#     if len(X_test) != len(y_test):
#         logging.warning(f"Test data mismatch: X_test={len(X_test)}, y_test={len(y_test)}")
#         # For now, assume they should match - this needs more sophisticated handling
    
#     logging.info(f"Test features shape: {X_test.shape}")
#     logging.info(f"Test samples: {len(X_test)}")
    
#     # Create combined training dataset
#     combined_X = []
#     combined_y = []
    
#     # Get the target dimension from test set
#     target_dim = X_test.shape[1]
#     logging.info(f"Target embedding dimension: {target_dim}")
    
#     # Add psmiles_embed data
#     if 'psmiles_bigsmiles_embed' in train_df.columns:
#         try:
#             psmiles_X = parse_embedding_column(train_df, 'psmiles_bigsmiles_embed')
#             if psmiles_X.shape[1] == target_dim:
#                 # Get corresponding y values
#                 psmiles_y = train_df['Tg(K)'].values
#                 if len(psmiles_X) != len(psmiles_y):
#                     min_len = min(len(psmiles_X), len(psmiles_y))
#                     psmiles_X = psmiles_X[:min_len]
#                     psmiles_y = psmiles_y[:min_len]
                
#                 combined_X.append(psmiles_X)
#                 combined_y.append(psmiles_y)
#                 logging.info(f"Added psmiles_embed: {len(psmiles_y)} samples, shape: {psmiles_X.shape}")
#             else:
#                 logging.warning(f"psmiles_embed dimension mismatch: {psmiles_X.shape[1]} vs {target_dim}")
#         except Exception as e:
#             logging.error(f"Error processing psmiles_embed: {e}")
    
#     # Add bigsmiles_embed data  
#     if 'bigsmiles_psmiles_embed' in train_df.columns:
#         try:
#             bigsmiles_X = parse_embedding_column(train_df, 'bigsmiles_psmiles_embed')
#             if bigsmiles_X.shape[1] == target_dim:
#                 bigsmiles_y = train_df['Tg(K)'].values
#                 if len(bigsmiles_X) != len(bigsmiles_y):
#                     min_len = min(len(bigsmiles_X), len(bigsmiles_y))
#                     bigsmiles_X = bigsmiles_X[:min_len]
#                     bigsmiles_y = bigsmiles_y[:min_len]
                
#                 combined_X.append(bigsmiles_X)
#                 combined_y.append(bigsmiles_y)
#                 logging.info(f"Added bigsmiles_embed: {len(bigsmiles_y)} samples, shape: {bigsmiles_X.shape}")
#             else:
#                 logging.warning(f"bigsmiles_embed dimension mismatch: {bigsmiles_X.shape[1]} vs {target_dim}")
#         except Exception as e:
#             logging.error(f"Error processing bigsmiles_embed: {e}")
    
#     # Add psmiles_embed_polymer_name data
#     if 'psmiles_polymer_name_embed' in train_df.columns:
#         try:
#             psmiles_polymer_X = parse_embedding_column(train_df, 'psmiles_polymer_name_embed')
#             if psmiles_polymer_X.shape[1] == target_dim:
#                 psmiles_polymer_y = train_df['Tg(K)'].values
#                 if len(psmiles_polymer_X) != len(psmiles_polymer_y):
#                     min_len = min(len(psmiles_polymer_X), len(psmiles_polymer_y))
#                     psmiles_polymer_X = psmiles_polymer_X[:min_len]
#                     psmiles_polymer_y = psmiles_polymer_y[:min_len]
                
#                 combined_X.append(psmiles_polymer_X)
#                 combined_y.append(psmiles_polymer_y)
#                 logging.info(f"Added psmiles_embed_polymer_name: {len(psmiles_polymer_y)} samples, shape: {psmiles_polymer_X.shape}")
#             else:
#                 logging.warning(f"psmiles_embed_polymer_name dimension mismatch: {psmiles_polymer_X.shape[1]} vs {target_dim}")
#         except Exception as e:
#             logging.error(f"Error processing psmiles_embed_polymer_name: {e}")
    
#     # Add polymer_name_embed data (if available)
#     if 'polymer_name_psmiles_embed' in train_df.columns:
#         try:
#             # Filter out rows where polymer_name_embed is not null/empty
#             polymer_mask = train_df['polymer_name_psmiles_embed'].notna()
#             if polymer_mask.sum() > 0:
#                 polymer_X = parse_embedding_column(train_df[polymer_mask], 'polymer_name_psmiles_embed')
#                 if polymer_X.shape[1] == target_dim:
#                     polymer_y = train_df[polymer_mask]['Tg(K)'].values
#                     if len(polymer_X) != len(polymer_y):
#                         min_len = min(len(polymer_X), len(polymer_y))
#                         polymer_X = polymer_X[:min_len]
#                         polymer_y = polymer_y[:min_len]
                    
#                     combined_X.append(polymer_X)
#                     combined_y.append(polymer_y)
#                     logging.info(f"Added polymer_name_embed: {len(polymer_y)} samples, shape: {polymer_X.shape}")
#                 else:
#                     logging.warning(f"polymer_name_embed dimension mismatch: {polymer_X.shape[1]} vs {target_dim}")
#         except Exception as e:
#             logging.error(f"Error processing polymer_name_embed: {e}")
    
#     # Check if we have any data
#     if len(combined_X) == 0:
#         logging.error("No embedding data found!")
#         return None
    
#     # Stack all embeddings
#     try:
#         X_train_combined = np.vstack(combined_X)
#         y_train_combined = np.concatenate(combined_y)
        
#         logging.info(f"Combined training data shape: {X_train_combined.shape}")
#         logging.info(f"Total training samples: {len(y_train_combined)}")
        
#         # Verify dimensions match
#         if X_train_combined.shape[1] != X_test.shape[1]:
#             logging.error(f"Dimension mismatch: train={X_train_combined.shape[1]}, test={X_test.shape[1]}")
#             return None
        
#     except Exception as e:
#         logging.error(f"Error combining embeddings: {e}")
#         return None
    
#     results = []
    
#     # Run with different random seeds
#     for seed in RANDOM_SEEDS:
#         logging.info(f"\nRunning with random seed: {seed}")
        
#         # Train model
#         model = GradientBoostingRegressor(random_state=seed)
#         model.fit(X_train_combined, y_train_combined)
        
#         # Predict
#         y_pred = model.predict(X_test)
        
#         # Calculate individual MAE for each test point
#         individual_mae = np.abs(y_test - y_pred)
        
#         # Create a copy of test_df to store results
#         test_df_with_mae = test_df.copy()
#         test_df_with_mae['test_MAE'] = individual_mae
        
#         # Save the test DataFrame with MAE to a CSV file
#         timestamp = datetime.now().strftime("%Y%m%d_%H%M")
#         output_test_csv = f"task2_test_with_mae_{timestamp}_seed_{seed}.csv"
#         test_df_with_mae.to_csv(output_test_csv, index=False)
#         logging.info(f"Saved test data with individual MAE to: {output_test_csv}")
        
#         # Evaluate
#         mae, rmse, r2 = evaluate_model(y_test, y_pred)
        
#         logging.info(f"Seed {seed} - MAE: {mae:.3f}, RMSE: {rmse:.3f}, R²: {r2:.3f}")
        
#         results.append({
#             'seed': seed,
#             'mae': mae,
#             'rmse': rmse,
#             'r2': r2
#         })
    
#     # Calculate statistics
#     maes = [r['mae'] for r in results]
#     rmses = [r['rmse'] for r in results]
#     r2s = [r['r2'] for r in results]
    
#     mae_mean, mae_std = np.mean(maes), np.std(maes, ddof=1)
#     rmse_mean, rmse_std = np.mean(rmses), np.std(rmses, ddof=1)
#     r2_mean, r2_std = np.mean(r2s), np.std(r2s, ddof=1)
    
#     logging.info(f"\n--- TASK 2 FINAL RESULTS ---")
#     logging.info(f"MAE:  {mae_mean:.3f} ± {mae_std:.3f}")
#     logging.info(f"RMSE: {rmse_mean:.3f} ± {rmse_std:.3f}")
#     logging.info(f"R²:   {r2_mean:.3f} ± {r2_std:.3f}")
    
#     return {
#         'task': 'Combined Embeddings',
#         'mae_mean': mae_mean, 'mae_std': mae_std,
#         'rmse_mean': rmse_mean, 'rmse_std': rmse_std,
#         'r2_mean': r2_mean, 'r2_std': r2_std,
#         'n_train': len(y_train_combined), 'n_test': len(X_test)
#     }

# def task3_feature_based_model(train_df, test_df):
#     """Task 3: Feature-based model using polymer level features"""
#     logging.info("\n" + "="*80)
#     logging.info("TASK 3: Feature-based Model with Polymer Level Features")
#     logging.info("="*80)
    
#     # Extract feature columns
#     try:
#         X_train, feature_columns = extract_feature_columns(train_df, FEATURE_PREFIXES)
#         X_test, _ = extract_feature_columns(test_df, FEATURE_PREFIXES)
        
#         # Get target values
#         y_train = train_df['Tg(K)'].values
#         y_test = test_df['Tg(K)'].values
        
#         logging.info(f"Training features shape: {X_train.shape}")
#         logging.info(f"Test features shape: {X_test.shape}")
#         logging.info(f"Training samples: {len(y_train)}")
#         logging.info(f"Test samples: {len(y_test)}")
        
#         # Check for dimension mismatch
#         if X_train.shape[1] != X_test.shape[1]:
#             logging.error(f"Feature dimension mismatch: train={X_train.shape[1]}, test={X_test.shape[1]}")
#             return None
        
#         # Check for consistent sample sizes
#         if len(X_train) != len(y_train):
#             logging.warning(f"Sample size mismatch in training: X={len(X_train)}, y={len(y_train)}")
#             min_len = min(len(X_train), len(y_train))
#             X_train = X_train[:min_len]
#             y_train = y_train[:min_len]
#             logging.info(f"Adjusted to {min_len} training samples")
        
#         if len(X_test) != len(y_test):
#             logging.warning(f"Sample size mismatch in test: X={len(X_test)}, y={len(y_test)}")
#             min_len = min(len(X_test), len(y_test))
#             X_test = X_test[:min_len]
#             y_test = y_test[:min_len]
#             logging.info(f"Adjusted to {min_len} test samples")
        
#         # Feature scaling (important for feature-based models)
#         scaler = StandardScaler()
#         X_train_scaled = scaler.fit_transform(X_train)
#         X_test_scaled = scaler.transform(X_test)
        
#         logging.info("Features scaled using StandardScaler")
        
#         # Log feature statistics
#         logging.info(f"Feature range after scaling - Train: [{X_train_scaled.min():.3f}, {X_train_scaled.max():.3f}]")
#         logging.info(f"Feature range after scaling - Test: [{X_test_scaled.min():.3f}, {X_test_scaled.max():.3f}]")
        
#         # Breakdown by feature prefix
#         prefix_counts = {}
#         for prefix in FEATURE_PREFIXES:
#             count = sum(1 for col in feature_columns if col.startswith(prefix))
#             prefix_counts[prefix] = count
#             logging.info(f"{prefix}: {count} features")
        
#         results = []
        
#         # Run with different random seeds
#         for seed in RANDOM_SEEDS:
#             logging.info(f"\nRunning with random seed: {seed}")
            
#             # Train model
#             model = GradientBoostingRegressor(random_state=seed)
#             model.fit(X_train_scaled, y_train)
            
#             # Predict
#             y_pred = model.predict(X_test_scaled)
            
#             # Evaluate
#             mae, rmse, r2 = evaluate_model(y_test, y_pred)
            
#             logging.info(f"Seed {seed} - MAE: {mae:.3f}, RMSE: {rmse:.3f}, R²: {r2:.3f}")
            
#             results.append({
#                 'seed': seed,
#                 'mae': mae,
#                 'rmse': rmse,
#                 'r2': r2
#             })
        
#         # Calculate statistics
#         maes = [r['mae'] for r in results]
#         rmses = [r['rmse'] for r in results]
#         r2s = [r['r2'] for r in results]
        
#         mae_mean, mae_std = np.mean(maes), np.std(maes, ddof=1)
#         rmse_mean, rmse_std = np.mean(rmses), np.std(rmses, ddof=1)
#         r2_mean, r2_std = np.mean(r2s), np.std(r2s, ddof=1)
        
#         logging.info(f"\n--- TASK 3 FINAL RESULTS ---")
#         logging.info(f"Total features used: {len(feature_columns)}")
#         for prefix, count in prefix_counts.items():
#             logging.info(f"  {prefix}: {count} features")
#         logging.info(f"MAE:  {mae_mean:.3f} ± {mae_std:.3f}")
#         logging.info(f"RMSE: {rmse_mean:.3f} ± {rmse_std:.3f}")
#         logging.info(f"R²:   {r2_mean:.3f} ± {r2_std:.3f}")
        
#         return {
#             'task': 'Feature-based Model',
#             'mae_mean': mae_mean, 'mae_std': mae_std,
#             'rmse_mean': rmse_mean, 'rmse_std': rmse_std,
#             'r2_mean': r2_mean, 'r2_std': r2_std,
#             'n_train': len(y_train), 'n_test': len(y_test),
#             'n_features': len(feature_columns),
#             'feature_breakdown': prefix_counts
#         }
        
#     except Exception as e:
#         logging.error(f"Error in Task 3: {e}")
#         import traceback
#         traceback.print_exc()
#         return None

# def main():
#     """Main execution function"""
#     print("🚀 Starting Polymer Tg Prediction Experiments")
#     print(f"📊 Train Dataset: {TRAIN_CSV_PATH}")
#     print(f"📊 Test Dataset: {TEST_CSV_PATH}")
#     print(f"🎯 Target: Tg(K)")
#     print(f"🔬 Model: GradientBoostingRegressor (default settings)")
#     print(f"🌱 Random Seeds: {RANDOM_SEEDS}")
#     print(f"🔧 Feature Prefixes: {FEATURE_PREFIXES}")
#     print("="*80)
    
#     # Load datasets
#     train_df, test_df = load_datasets()
    
#     # Run experiments
#     all_results = []
    
#     # # Task 1: Baseline ECFP
#     # try:
#     #     result1 = task1_baseline_ecfp(train_df, test_df)
#     #     if result1:
#     #         all_results.append(result1)
#     # except Exception as e:
#     #     logging.error(f"Error in Task 1: {e}")
#     #     import traceback
#     #     traceback.print_exc()
    
#     # Task 2: Combined embeddings
#     try:
#         result2 = task2_combined_embeddings(train_df, test_df)
#         if result2:
#             all_results.append(result2)
#     except Exception as e:
#         logging.error(f"Error in Task 2: {e}")
#         import traceback
#         traceback.print_exc()
    
#     # # Task 3: Feature-based model
#     # try:
#     #     result3 = task3_feature_based_model(train_df, test_df)
#     #     if result3:
#     #         all_results.append(result3)
#     # except Exception as e:
#     #     logging.error(f"Error in Task 3: {e}")
#     #     import traceback
#     #     traceback.print_exc()
    
#     # Summary
#     if all_results:
#         logging.info("\n" + "="*100)
#         logging.info("📊 FINAL EXPERIMENT SUMMARY")
#         logging.info("="*100)
        
#         for result in all_results:
#             logging.info(f"\n{result['task']}:")
#             logging.info(f"  Training samples: {result['n_train']}")
#             logging.info(f"  Test samples: {result['n_test']}")
#             if 'n_features' in result:
#                 logging.info(f"  Features used: {result['n_features']}")
#             if 'feature_breakdown' in result:
#                 for prefix, count in result['feature_breakdown'].items():
#                     logging.info(f"    {prefix}: {count}")
#             logging.info(f"  MAE:  {result['mae_mean']:.3f} ± {result['mae_std']:.3f}")
#             logging.info(f"  RMSE: {result['rmse_mean']:.3f} ± {result['rmse_std']:.3f}")
#             logging.info(f"  R²:   {result['r2_mean']:.3f} ± {result['r2_std']:.3f}")
        
#         # Save results
#         results_df = pd.DataFrame(all_results)
#         timestamp = datetime.now().strftime("%Y%m%d_%H%M")
#         output_csv = f"Application_Neurips_combining_datasets_{timestamp}.csv"
#         results_df.to_csv(output_csv, index=False)
        
#         logging.info(f"\n💾 Results saved to: {output_csv}")
        
#         print(f"\n📋 EXPERIMENT COMPLETED:")
#         print(f"Results saved to: {output_csv}")
        
#         # Performance comparison
#         if len(all_results) > 1:
#             logging.info("\n🏆 PERFORMANCE COMPARISON (R² Score):")
#             sorted_results = sorted(all_results, key=lambda x: x['r2_mean'], reverse=True)
#             for i, result in enumerate(sorted_results, 1):
#                 logging.info(f"  {i}. {result['task']}: R² = {result['r2_mean']:.3f} ± {result['r2_std']:.3f}")
            
#             logging.info("\n🎯 PERFORMANCE COMPARISON (MAE - Lower is Better):")
#             sorted_mae = sorted(all_results, key=lambda x: x['mae_mean'])
#             for i, result in enumerate(sorted_mae, 1):
#                 logging.info(f"  {i}. {result['task']}: MAE = {result['mae_mean']:.3f} ± {result['mae_std']:.3f}")
#     else:
#         logging.error("No results generated. Check for errors in the experiments.")

# if __name__ == "__main__":
#     main()


# # neurips with classifiaction
# import numpy as np
# import pandas as pd
# from sklearn.ensemble import GradientBoostingRegressor
# from sklearn.linear_model import LogisticRegression
# from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
# from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report
# from sklearn.preprocessing import StandardScaler
# from datetime import datetime
# import logging

# # Configuration
# RANDOM_SEEDS = [42]  # Three different random seeds

# # Dataset paths
# TRAIN_CSV_PATH = '/home/ta45woj/PolyMetriX/src/polymetrix/datasets/valid_dataset_20250717_1109_application_tg_neurips_combining_datasets_ecfp_info_train_set_clusters.csv'
# TEST_CSV_PATH = '/home/ta45woj/PolyMetriX/src/polymetrix/datasets/valid_dataset_20250717_1109_application_tg_neurips_combining_datasets_ecfp_info_test_set_clusters.csv'
# # Feature prefixes for Task 3
# FEATURE_PREFIXES = ['fullpolymerlevel.features.', 'sidechainlevel.features.', 'backbonelevel.features.']

# # Initialize logging
# logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

# def load_datasets():
#     """Load training and test datasets"""
#     logging.info("Loading datasets...")
#     train_df = pd.read_csv(TRAIN_CSV_PATH)
#     test_df = pd.read_csv(TEST_CSV_PATH)
    
#     logging.info(f"Train dataset shape: {train_df.shape}")
#     logging.info(f"Test dataset shape: {test_df.shape}")
    
#     return train_df, test_df

# def parse_embedding_column(df, column_name):
#     """Parse embedding column from string representation to numpy array"""
#     embeddings = []
#     embedding_lengths = []
    
#     for i, embedding_str in enumerate(df[column_name]):
#         # Handle different string formats
#         embedding_str = str(embedding_str).strip()
        
#         # Skip if NaN or empty
#         if embedding_str == 'nan' or embedding_str == '' or pd.isna(embedding_str):
#             continue
            
#         # Handle PyTorch tensor format: "tensor([0.1, 0.2, ...])"
#         if embedding_str.startswith('tensor('):
#             # Extract the array part from tensor([...])
#             start_idx = embedding_str.find('[')
#             end_idx = embedding_str.rfind(']')
#             if start_idx != -1 and end_idx != -1:
#                 array_str = embedding_str[start_idx+1:end_idx]
#             else:
#                 logging.warning(f"Invalid tensor format at row {i}: {embedding_str[:50]}...")
#                 continue
#         # Handle simple array format: "[0.1, 0.2, ...]"
#         elif embedding_str.startswith('[') and embedding_str.endswith(']'):
#             array_str = embedding_str[1:-1]
#         else:
#             # Try to use as-is
#             array_str = embedding_str
        
#         # Parse the numbers
#         try:
#             # Split by comma and convert to float
#             values = [float(x.strip()) for x in array_str.split(',') if x.strip()]
#             if len(values) == 0:
#                 logging.warning(f"Empty embedding at row {i}")
#                 continue
                
#             embedding = np.array(values)
#             embeddings.append(embedding)
#             embedding_lengths.append(len(values))
#         except ValueError as e:
#             logging.warning(f"Error parsing embedding at row {i}: {embedding_str[:50]}... - {e}")
#             continue
    
#     if len(embeddings) == 0:
#         raise ValueError(f"No valid embeddings found in column {column_name}")
    
#     # Check for consistent dimensions
#     unique_lengths = set(embedding_lengths)
#     if len(unique_lengths) > 1:
#         logging.warning(f"Inconsistent embedding dimensions in {column_name}: {unique_lengths}")
#         # Use the most common dimension
#         from collections import Counter
#         most_common_length = Counter(embedding_lengths).most_common(1)[0][0]
#         logging.info(f"Using most common dimension: {most_common_length}")
        
#         # Filter embeddings to consistent dimension
#         filtered_embeddings = []
#         for emb in embeddings:
#             if len(emb) == most_common_length:
#                 filtered_embeddings.append(emb)
        
#         embeddings = filtered_embeddings
#         logging.info(f"Filtered to {len(embeddings)} embeddings with consistent dimension")
    
#     if len(embeddings) == 0:
#         raise ValueError(f"No embeddings with consistent dimensions in column {column_name}")
    
#     # Now create the numpy array
#     try:
#         result = np.array(embeddings)
#         logging.info(f"Successfully parsed {column_name}: shape {result.shape}")
#         return result
#     except Exception as e:
#         logging.error(f"Failed to create numpy array for {column_name}: {e}")
#         # Try creating it row by row to identify the problematic entries
#         max_len = max(len(emb) for emb in embeddings)
#         min_len = min(len(emb) for emb in embeddings)
#         logging.error(f"Embedding length range: {min_len} to {max_len}")
#         raise e

# def extract_feature_columns(df, feature_prefixes):
#     """Extract feature columns based on prefixes"""
#     feature_columns = []
    
#     for prefix in feature_prefixes:
#         prefix_columns = [col for col in df.columns if col.startswith(prefix)]
#         feature_columns.extend(prefix_columns)
#         logging.info(f"Found {len(prefix_columns)} columns with prefix '{prefix}'")
    
#     if len(feature_columns) == 0:
#         raise ValueError(f"No feature columns found with prefixes: {feature_prefixes}")
    
#     logging.info(f"Total feature columns found: {len(feature_columns)}")
    
#     # Extract the features and handle missing values
#     X = df[feature_columns].copy()
    
#     # Check for missing values
#     missing_counts = X.isnull().sum()
#     if missing_counts.sum() > 0:
#         logging.warning(f"Found missing values in {missing_counts[missing_counts > 0].shape[0]} columns")
#         logging.info("Filling missing values with 0")
#         X = X.fillna(0)
    
#     # Check for non-numeric columns
#     numeric_columns = X.select_dtypes(include=[np.number]).columns
#     if len(numeric_columns) != len(feature_columns):
#         non_numeric = set(feature_columns) - set(numeric_columns)
#         logging.warning(f"Non-numeric columns found: {non_numeric}")
#         X = X[numeric_columns]
#         logging.info(f"Using {len(numeric_columns)} numeric columns")
    
#     return X.values, feature_columns

# def evaluate_regression_model(y_true, y_pred):
#     """Calculate regression evaluation metrics"""
#     mae = mean_absolute_error(y_true, y_pred)
#     rmse = np.sqrt(mean_squared_error(y_true, y_pred))
#     r2 = r2_score(y_true, y_pred)
#     return mae, rmse, r2

# def evaluate_classification_model(y_true, y_pred):
#     """Calculate classification evaluation metrics"""
#     accuracy = accuracy_score(y_true, y_pred)
#     precision = precision_score(y_true, y_pred, average='weighted', zero_division=0)
#     recall = recall_score(y_true, y_pred, average='weighted', zero_division=0)
#     f1 = f1_score(y_true, y_pred, average='weighted', zero_division=0)
#     return accuracy, precision, recall, f1

# def task1_baseline_ecfp(train_df, test_df):
#     """Task 1: Baseline model using ECFP fingerprints for both regression and classification"""
#     logging.info("\n" + "="*80)
#     logging.info("TASK 1: Baseline Model with ECFP Fingerprints")
#     logging.info("="*80)
    
#     # Prepare features
#     X_train = parse_embedding_column(train_df, 'ecfp_fingerprint')
#     X_test = parse_embedding_column(test_df, 'ecfp_fingerprint')
    
#     # Regression targets
#     y_train_reg = train_df['Tg(K)'].values
#     y_test_reg = test_df['Tg(K)'].values
    
#     # Classification targets
#     y_train_cls = train_df['class_label'].values
#     y_test_cls = test_df['class_label'].values
    
#     # Ensure we have matching indices
#     if len(X_train) != len(y_train_reg):
#         logging.warning(f"Mismatch in training data: X_train={len(X_train)}, y_train={len(y_train_reg)}")
    
#     if len(X_test) != len(y_test_reg):
#         logging.warning(f"Mismatch in test data: X_test={len(X_test)}, y_test={len(y_test_reg)}")
    
#     logging.info(f"Training features shape: {X_train.shape}")
#     logging.info(f"Test features shape: {X_test.shape}")
#     logging.info(f"Training samples: {len(y_train_reg)}")
#     logging.info(f"Test samples: {len(y_test_reg)}")
    
#     regression_results = []
#     classification_results = []
    
#     # Run with different random seeds
#     for seed in RANDOM_SEEDS:
#         logging.info(f"\nRunning with random seed: {seed}")
        
#         # REGRESSION
#         logging.info("  Running regression...")
#         reg_model = GradientBoostingRegressor(random_state=seed)
#         reg_model.fit(X_train, y_train_reg)
#         y_pred_reg = reg_model.predict(X_test)
#         mae, rmse, r2 = evaluate_regression_model(y_test_reg, y_pred_reg)
        
#         logging.info(f"  Regression - MAE: {mae:.3f}, RMSE: {rmse:.3f}, R²: {r2:.3f}")
        
#         regression_results.append({
#             'seed': seed,
#             'mae': mae,
#             'rmse': rmse,
#             'r2': r2
#         })
        
#         # CLASSIFICATION
#         logging.info("  Running classification...")
#         cls_model = LogisticRegression(random_state=seed, max_iter=1000, class_weight='balanced')
#         cls_model.fit(X_train, y_train_cls)
#         y_pred_cls = cls_model.predict(X_test)
#         accuracy, precision, recall, f1 = evaluate_classification_model(y_test_cls, y_pred_cls)
        
#         logging.info(f"  Classification - Accuracy: {accuracy:.3f}, Precision: {precision:.3f}, Recall: {recall:.3f}, F1: {f1:.3f}")
        
#         classification_results.append({
#             'seed': seed,
#             'accuracy': accuracy,
#             'precision': precision,
#             'recall': recall,
#             'f1': f1
#         })
    
#     # Calculate regression statistics
#     reg_maes = [r['mae'] for r in regression_results]
#     reg_rmses = [r['rmse'] for r in regression_results]
#     reg_r2s = [r['r2'] for r in regression_results]
    
#     reg_mae_mean, reg_mae_std = np.mean(reg_maes), np.std(reg_maes, ddof=1)
#     reg_rmse_mean, reg_rmse_std = np.mean(reg_rmses), np.std(reg_rmses, ddof=1)
#     reg_r2_mean, reg_r2_std = np.mean(reg_r2s), np.std(reg_r2s, ddof=1)
    
#     # Calculate classification statistics
#     cls_accs = [r['accuracy'] for r in classification_results]
#     cls_precs = [r['precision'] for r in classification_results]
#     cls_recs = [r['recall'] for r in classification_results]
#     cls_f1s = [r['f1'] for r in classification_results]
    
#     cls_acc_mean, cls_acc_std = np.mean(cls_accs), np.std(cls_accs, ddof=1)
#     cls_prec_mean, cls_prec_std = np.mean(cls_precs), np.std(cls_precs, ddof=1)
#     cls_rec_mean, cls_rec_std = np.mean(cls_recs), np.std(cls_recs, ddof=1)
#     cls_f1_mean, cls_f1_std = np.mean(cls_f1s), np.std(cls_f1s, ddof=1)
    
#     logging.info(f"\n--- TASK 1 REGRESSION RESULTS ---")
#     logging.info(f"MAE:  {reg_mae_mean:.3f} ± {reg_mae_std:.3f}")
#     logging.info(f"RMSE: {reg_rmse_mean:.3f} ± {reg_rmse_std:.3f}")
#     logging.info(f"R²:   {reg_r2_mean:.3f} ± {reg_r2_std:.3f}")
    
#     logging.info(f"\n--- TASK 1 CLASSIFICATION RESULTS ---")
#     logging.info(f"Accuracy:  {cls_acc_mean:.3f} ± {cls_acc_std:.3f}")
#     logging.info(f"Precision: {cls_prec_mean:.3f} ± {cls_prec_std:.3f}")
#     logging.info(f"Recall:    {cls_rec_mean:.3f} ± {cls_rec_std:.3f}")
#     logging.info(f"F1:        {cls_f1_mean:.3f} ± {cls_f1_std:.3f}")
    
#     return [
#         {
#             'task': 'regression',
#             'features': 'Baseline ECFP',
#             'mae_mean': reg_mae_mean, 'mae_std': reg_mae_std,
#             'rmse_mean': reg_rmse_mean, 'rmse_std': reg_rmse_std,
#             'r2_mean': reg_r2_mean, 'r2_std': reg_r2_std,
#             'accuracy_mean': None, 'accuracy_std': None,
#             'precision_mean': None, 'precision_std': None,
#             'recall_mean': None, 'recall_std': None,
#             'f1_mean': None, 'f1_std': None,
#             'n_train': len(X_train), 'n_test': len(X_test)
#         },
#         {
#             'task': 'classification',
#             'features': 'Baseline ECFP',
#             'mae_mean': None, 'mae_std': None,
#             'rmse_mean': None, 'rmse_std': None,
#             'r2_mean': None, 'r2_std': None,
#             'accuracy_mean': cls_acc_mean, 'accuracy_std': cls_acc_std,
#             'precision_mean': cls_prec_mean, 'precision_std': cls_prec_std,
#             'recall_mean': cls_rec_mean, 'recall_std': cls_rec_std,
#             'f1_mean': cls_f1_mean, 'f1_std': cls_f1_std,
#             'n_train': len(X_train), 'n_test': len(X_test)
#         }
#     ]

# def task2_combined_embeddings(train_df, test_df):
#     """Task 2: Combined embeddings model for both regression and classification"""
#     logging.info("\n" + "="*80)
#     logging.info("TASK 2: Combined Embeddings Model")
#     logging.info("="*80)
    
#     # Prepare test set using psmiles_embed to match combined training embeddings
#     X_test = parse_embedding_column(test_df, 'psmiles_bigsmiles_embed')
#     y_test_reg = test_df['Tg(K)'].values
#     y_test_cls = test_df['class_label'].values
    
#     # Filter targets to match X_test if needed
#     if len(X_test) != len(y_test_reg):
#         logging.warning(f"Test data mismatch: X_test={len(X_test)}, y_test={len(y_test_reg)}")
    
#     logging.info(f"Test features shape: {X_test.shape}")
#     logging.info(f"Test samples: {len(X_test)}")
    
#     # Create combined training dataset
#     combined_X = []
#     combined_y_reg = []
#     combined_y_cls = []
    
#     # Get the target dimension from test set
#     target_dim = X_test.shape[1]
#     logging.info(f"Target embedding dimension: {target_dim}")
    
#     # Add psmiles_embed data
#     if 'psmiles_bigsmiles_embed' in train_df.columns:
#         try:
#             psmiles_X = parse_embedding_column(train_df, 'psmiles_bigsmiles_embed')
#             if psmiles_X.shape[1] == target_dim:
#                 # Get corresponding y values
#                 psmiles_y_reg = train_df['Tg(K)'].values
#                 psmiles_y_cls = train_df['class_label'].values
#                 if len(psmiles_X) != len(psmiles_y_reg):
#                     # Need to match indices - this is complex, simplified for now
#                     min_len = min(len(psmiles_X), len(psmiles_y_reg))
#                     psmiles_X = psmiles_X[:min_len]
#                     psmiles_y_reg = psmiles_y_reg[:min_len]
#                     psmiles_y_cls = psmiles_y_cls[:min_len]
                
#                 combined_X.append(psmiles_X)
#                 combined_y_reg.append(psmiles_y_reg)
#                 combined_y_cls.append(psmiles_y_cls)
#                 logging.info(f"Added psmiles_embed: {len(psmiles_y_reg)} samples, shape: {psmiles_X.shape}")
#             else:
#                 logging.warning(f"psmiles_embed dimension mismatch: {psmiles_X.shape[1]} vs {target_dim}")
#         except Exception as e:
#             logging.error(f"Error processing psmiles_embed: {e}")
    
#     # Add bigsmiles_embed data  
#     if 'bigsmiles_psmiles_embed' in train_df.columns:
#         try:
#             bigsmiles_X = parse_embedding_column(train_df, 'bigsmiles_psmiles_embed')
#             if bigsmiles_X.shape[1] == target_dim:
#                 bigsmiles_y_reg = train_df['Tg(K)'].values
#                 bigsmiles_y_cls = train_df['class_label'].values
#                 if len(bigsmiles_X) != len(bigsmiles_y_reg):
#                     min_len = min(len(bigsmiles_X), len(bigsmiles_y_reg))
#                     bigsmiles_X = bigsmiles_X[:min_len]
#                     bigsmiles_y_reg = bigsmiles_y_reg[:min_len]
#                     bigsmiles_y_cls = bigsmiles_y_cls[:min_len]
                
#                 combined_X.append(bigsmiles_X)
#                 combined_y_reg.append(bigsmiles_y_reg)
#                 combined_y_cls.append(bigsmiles_y_cls)
#                 logging.info(f"Added bigsmiles_embed: {len(bigsmiles_y_reg)} samples, shape: {bigsmiles_X.shape}")
#             else:
#                 logging.warning(f"bigsmiles_embed dimension mismatch: {bigsmiles_X.shape[1]} vs {target_dim}")
#         except Exception as e:
#             logging.error(f"Error processing bigsmiles_embed: {e}")
    
#     # Add psmiles_embed_polymer_name data
#     if 'psmiles_polymer_name_embed' in train_df.columns:
#         try:
#             psmiles_polymer_X = parse_embedding_column(train_df, 'psmiles_polymer_name_embed')
#             if psmiles_polymer_X.shape[1] == target_dim:
#                 psmiles_polymer_y_reg = train_df['Tg(K)'].values
#                 psmiles_polymer_y_cls = train_df['class_label'].values
#                 if len(psmiles_polymer_X) != len(psmiles_polymer_y_reg):
#                     min_len = min(len(psmiles_polymer_X), len(psmiles_polymer_y_reg))
#                     psmiles_polymer_X = psmiles_polymer_X[:min_len]
#                     psmiles_polymer_y_reg = psmiles_polymer_y_reg[:min_len]
#                     psmiles_polymer_y_cls = psmiles_polymer_y_cls[:min_len]
                
#                 combined_X.append(psmiles_polymer_X)
#                 combined_y_reg.append(psmiles_polymer_y_reg)
#                 combined_y_cls.append(psmiles_polymer_y_cls)
#                 logging.info(f"Added psmiles_embed_polymer_name: {len(psmiles_polymer_y_reg)} samples, shape: {psmiles_polymer_X.shape}")
#             else:
#                 logging.warning(f"psmiles_embed_polymer_name dimension mismatch: {psmiles_polymer_X.shape[1]} vs {target_dim}")
#         except Exception as e:
#             logging.error(f"Error processing psmiles_embed_polymer_name: {e}")
    
#     # Add polymer_name_embed data (if available)
#     if 'polymer_name_psmiles_embed' in train_df.columns:
#         try:
#             # Filter out rows where polymer_name_embed is not null/empty
#             polymer_mask = train_df['polymer_name_psmiles_embed'].notna()
#             if polymer_mask.sum() > 0:
#                 polymer_X = parse_embedding_column(train_df[polymer_mask], 'polymer_name_psmiles_embed')
#                 if polymer_X.shape[1] == target_dim:
#                     polymer_y_reg = train_df[polymer_mask]['Tg(K)'].values
#                     polymer_y_cls = train_df[polymer_mask]['class_label'].values
#                     if len(polymer_X) != len(polymer_y_reg):
#                         min_len = min(len(polymer_X), len(polymer_y_reg))
#                         polymer_X = polymer_X[:min_len]
#                         polymer_y_reg = polymer_y_reg[:min_len]
#                         polymer_y_cls = polymer_y_cls[:min_len]
                    
#                     combined_X.append(polymer_X)
#                     combined_y_reg.append(polymer_y_reg)
#                     combined_y_cls.append(polymer_y_cls)
#                     logging.info(f"Added polymer_name_embed: {len(polymer_y_reg)} samples, shape: {polymer_X.shape}")
#                 else:
#                     logging.warning(f"polymer_name_embed dimension mismatch: {polymer_X.shape[1]} vs {target_dim}")
#         except Exception as e:
#             logging.error(f"Error processing polymer_name_embed: {e}")
    
#     # Check if we have any data
#     if len(combined_X) == 0:
#         logging.error("No embedding data found!")
#         return None
    
#     # Stack all embeddings
#     try:
#         X_train_combined = np.vstack(combined_X)
#         y_train_combined_reg = np.concatenate(combined_y_reg)
#         y_train_combined_cls = np.concatenate(combined_y_cls)
        
#         logging.info(f"Combined training data shape: {X_train_combined.shape}")
#         logging.info(f"Total training samples: {len(y_train_combined_reg)}")
        
#         # Verify dimensions match
#         if X_train_combined.shape[1] != X_test.shape[1]:
#             logging.error(f"Dimension mismatch: train={X_train_combined.shape[1]}, test={X_test.shape[1]}")
#             return None
        
#     except Exception as e:
#         logging.error(f"Error combining embeddings: {e}")
#         return None
    
#     regression_results = []
#     classification_results = []
    
#     # Run with different random seeds
#     for seed in RANDOM_SEEDS:
#         logging.info(f"\nRunning with random seed: {seed}")
        
#         # REGRESSION
#         logging.info("  Running regression...")
#         reg_model = GradientBoostingRegressor(random_state=seed)
#         reg_model.fit(X_train_combined, y_train_combined_reg)
#         y_pred_reg = reg_model.predict(X_test)
#         mae, rmse, r2 = evaluate_regression_model(y_test_reg, y_pred_reg)
        
#         logging.info(f"  Regression - MAE: {mae:.3f}, RMSE: {rmse:.3f}, R²: {r2:.3f}")
        
#         regression_results.append({
#             'seed': seed,
#             'mae': mae,
#             'rmse': rmse,
#             'r2': r2
#         })
        
#         # CLASSIFICATION
#         logging.info("  Running classification...")
#         cls_model = LogisticRegression(random_state=seed, max_iter=1000)
#         cls_model.fit(X_train_combined, y_train_combined_cls)
#         y_pred_cls = cls_model.predict(X_test)
#         accuracy, precision, recall, f1 = evaluate_classification_model(y_test_cls, y_pred_cls)
        
#         logging.info(f"  Classification - Accuracy: {accuracy:.3f}, Precision: {precision:.3f}, Recall: {recall:.3f}, F1: {f1:.3f}")
        
#         classification_results.append({
#             'seed': seed,
#             'accuracy': accuracy,
#             'precision': precision,
#             'recall': recall,
#             'f1': f1
#         })
    
#     # Calculate regression statistics
#     reg_maes = [r['mae'] for r in regression_results]
#     reg_rmses = [r['rmse'] for r in regression_results]
#     reg_r2s = [r['r2'] for r in regression_results]
    
#     reg_mae_mean, reg_mae_std = np.mean(reg_maes), np.std(reg_maes, ddof=1)
#     reg_rmse_mean, reg_rmse_std = np.mean(reg_rmses), np.std(reg_rmses, ddof=1)
#     reg_r2_mean, reg_r2_std = np.mean(reg_r2s), np.std(reg_r2s, ddof=1)
    
#     # Calculate classification statistics
#     cls_accs = [r['accuracy'] for r in classification_results]
#     cls_precs = [r['precision'] for r in classification_results]
#     cls_recs = [r['recall'] for r in classification_results]
#     cls_f1s = [r['f1'] for r in classification_results]
    
#     cls_acc_mean, cls_acc_std = np.mean(cls_accs), np.std(cls_accs, ddof=1)
#     cls_prec_mean, cls_prec_std = np.mean(cls_precs), np.std(cls_precs, ddof=1)
#     cls_rec_mean, cls_rec_std = np.mean(cls_recs), np.std(cls_recs, ddof=1)
#     cls_f1_mean, cls_f1_std = np.mean(cls_f1s), np.std(cls_f1s, ddof=1)
    
#     logging.info(f"\n--- TASK 2 REGRESSION RESULTS ---")
#     logging.info(f"MAE:  {reg_mae_mean:.3f} ± {reg_mae_std:.3f}")
#     logging.info(f"RMSE: {reg_rmse_mean:.3f} ± {reg_rmse_std:.3f}")
#     logging.info(f"R²:   {reg_r2_mean:.3f} ± {reg_r2_std:.3f}")
    
#     logging.info(f"\n--- TASK 2 CLASSIFICATION RESULTS ---")
#     logging.info(f"Accuracy:  {cls_acc_mean:.3f} ± {cls_acc_std:.3f}")
#     logging.info(f"Precision: {cls_prec_mean:.3f} ± {cls_prec_std:.3f}")
#     logging.info(f"Recall:    {cls_rec_mean:.3f} ± {cls_rec_std:.3f}")
#     logging.info(f"F1:        {cls_f1_mean:.3f} ± {cls_f1_std:.3f}")
    
#     return [
#         {
#             'task': 'regression',
#             'features': 'Combined Embeddings',
#             'mae_mean': reg_mae_mean, 'mae_std': reg_mae_std,
#             'rmse_mean': reg_rmse_mean, 'rmse_std': reg_rmse_std,
#             'r2_mean': reg_r2_mean, 'r2_std': reg_r2_std,
#             'accuracy_mean': None, 'accuracy_std': None,
#             'precision_mean': None, 'precision_std': None,
#             'recall_mean': None, 'recall_std': None,
#             'f1_mean': None, 'f1_std': None,
#             'n_train': len(y_train_combined_reg), 'n_test': len(X_test)
#         },
#         {
#             'task': 'classification',
#             'features': 'Combined Embeddings',
#             'mae_mean': None, 'mae_std': None,
#             'rmse_mean': None, 'rmse_std': None,
#             'r2_mean': None, 'r2_std': None,
#             'accuracy_mean': cls_acc_mean, 'accuracy_std': cls_acc_std,
#             'precision_mean': cls_prec_mean, 'precision_std': cls_prec_std,
#             'recall_mean': cls_rec_mean, 'recall_std': cls_rec_std,
#             'f1_mean': cls_f1_mean, 'f1_std': cls_f1_std,
#             'n_train': len(y_train_combined_reg), 'n_test': len(X_test)
#         }
#     ]

# def task3_feature_based_model(train_df, test_df):
#     """Task 3: Feature-based model using polymer level features for both regression and classification"""
#     logging.info("\n" + "="*80)
#     logging.info("TASK 3: Feature-based Model with Polymer Level Features")
#     logging.info("="*80)
    
#     # Extract feature columns
#     try:
#         X_train, feature_columns = extract_feature_columns(train_df, FEATURE_PREFIXES)
#         X_test, _ = extract_feature_columns(test_df, FEATURE_PREFIXES)
        
#         # Get target values
#         y_train_reg = train_df['Tg(K)'].values
#         y_test_reg = test_df['Tg(K)'].values
#         y_train_cls = train_df['class_label'].values
#         y_test_cls = test_df['class_label'].values
        
#         logging.info(f"Training features shape: {X_train.shape}")
#         logging.info(f"Test features shape: {X_test.shape}")
#         logging.info(f"Training samples: {len(y_train_reg)}")
#         logging.info(f"Test samples: {len(y_test_reg)}")
        
#         # Check for dimension mismatch
#         if X_train.shape[1] != X_test.shape[1]:
#             logging.error(f"Feature dimension mismatch: train={X_train.shape[1]}, test={X_test.shape[1]}")
#             return None
        
#         # Check for consistent sample sizes
#         if len(X_train) != len(y_train_reg):
#             logging.warning(f"Sample size mismatch in training: X={len(X_train)}, y={len(y_train_reg)}")
#             min_len = min(len(X_train), len(y_train_reg))
#             X_train = X_train[:min_len]
#             y_train_reg = y_train_reg[:min_len]
#             y_train_cls = y_train_cls[:min_len]
#             logging.info(f"Adjusted to {min_len} training samples")
        
#         if len(X_test) != len(y_test_reg):
#             logging.warning(f"Sample size mismatch in test: X={len(X_test)}, y={len(y_test_reg)}")
#             min_len = min(len(X_test), len(y_test_reg))
#             X_test = X_test[:min_len]
#             y_test_reg = y_test_reg[:min_len]
#             y_test_cls = y_test_cls[:min_len]
#             logging.info(f"Adjusted to {min_len} test samples")
        
#         # Feature scaling (important for feature-based models)
#         scaler = StandardScaler()
#         X_train_scaled = scaler.fit_transform(X_train)
#         X_test_scaled = scaler.transform(X_test)
        
#         logging.info("Features scaled using StandardScaler")
        
#         # Log feature statistics
#         logging.info(f"Feature range after scaling - Train: [{X_train_scaled.min():.3f}, {X_train_scaled.max():.3f}]")
#         logging.info(f"Feature range after scaling - Test: [{X_test_scaled.min():.3f}, {X_test_scaled.max():.3f}]")
        
#         # Breakdown by feature prefix
#         prefix_counts = {}
#         for prefix in FEATURE_PREFIXES:
#             count = sum(1 for col in feature_columns if col.startswith(prefix))
#             prefix_counts[prefix] = count
#             logging.info(f"{prefix}: {count} features")
        
#         regression_results = []
#         classification_results = []
        
#         # Run with different random seeds
#         for seed in RANDOM_SEEDS:
#             logging.info(f"\nRunning with random seed: {seed}")
            
#             # REGRESSION
#             logging.info("  Running regression...")
#             reg_model = GradientBoostingRegressor(random_state=seed)
#             reg_model.fit(X_train_scaled, y_train_reg)
#             y_pred_reg = reg_model.predict(X_test_scaled)
#             mae, rmse, r2 = evaluate_regression_model(y_test_reg, y_pred_reg)
            
#             logging.info(f"  Regression - MAE: {mae:.3f}, RMSE: {rmse:.3f}, R²: {r2:.3f}")
            
#             regression_results.append({
#                 'seed': seed,
#                 'mae': mae,
#                 'rmse': rmse,
#                 'r2': r2
#             })
            
#             # CLASSIFICATION
#             logging.info("  Running classification...")
#             cls_model = LogisticRegression(random_state=seed, max_iter=1000)
#             cls_model.fit(X_train_scaled, y_train_cls)
#             y_pred_cls = cls_model.predict(X_test_scaled)
#             accuracy, precision, recall, f1 = evaluate_classification_model(y_test_cls, y_pred_cls)
            
#             logging.info(f"  Classification - Accuracy: {accuracy:.3f}, Precision: {precision:.3f}, Recall: {recall:.3f}, F1: {f1:.3f}")
            
#             classification_results.append({
#                 'seed': seed,
#                 'accuracy': accuracy,
#                 'precision': precision,
#                 'recall': recall,
#                 'f1': f1
#             })
        
#         # Calculate regression statistics
#         reg_maes = [r['mae'] for r in regression_results]
#         reg_rmses = [r['rmse'] for r in regression_results]
#         reg_r2s = [r['r2'] for r in regression_results]
        
#         reg_mae_mean, reg_mae_std = np.mean(reg_maes), np.std(reg_maes, ddof=1)
#         reg_rmse_mean, reg_rmse_std = np.mean(reg_rmses), np.std(reg_rmses, ddof=1)
#         reg_r2_mean, reg_r2_std = np.mean(reg_r2s), np.std(reg_r2s, ddof=1)
        
#         # Calculate classification statistics
#         cls_accs = [r['accuracy'] for r in classification_results]
#         cls_precs = [r['precision'] for r in classification_results]
#         cls_recs = [r['recall'] for r in classification_results]
#         cls_f1s = [r['f1'] for r in classification_results]
        
#         cls_acc_mean, cls_acc_std = np.mean(cls_accs), np.std(cls_accs, ddof=1)
#         cls_prec_mean, cls_prec_std = np.mean(cls_precs), np.std(cls_precs, ddof=1)
#         cls_rec_mean, cls_rec_std = np.mean(cls_recs), np.std(cls_recs, ddof=1)
#         cls_f1_mean, cls_f1_std = np.mean(cls_f1s), np.std(cls_f1s, ddof=1)
        
#         logging.info(f"\n--- TASK 3 REGRESSION RESULTS ---")
#         logging.info(f"Total features used: {len(feature_columns)}")
#         for prefix, count in prefix_counts.items():
#             logging.info(f"  {prefix}: {count} features")
#         logging.info(f"MAE:  {reg_mae_mean:.3f} ± {reg_mae_std:.3f}")
#         logging.info(f"RMSE: {reg_rmse_mean:.3f} ± {reg_rmse_std:.3f}")
#         logging.info(f"R²:   {reg_r2_mean:.3f} ± {reg_r2_std:.3f}")
        
#         logging.info(f"\n--- TASK 3 CLASSIFICATION RESULTS ---")
#         logging.info(f"Accuracy:  {cls_acc_mean:.3f} ± {cls_acc_std:.3f}")
#         logging.info(f"Precision: {cls_prec_mean:.3f} ± {cls_prec_std:.3f}")
#         logging.info(f"Recall:    {cls_rec_mean:.3f} ± {cls_rec_std:.3f}")
#         logging.info(f"F1:        {cls_f1_mean:.3f} ± {cls_f1_std:.3f}")
        
#         return [
#             {
#                 'task': 'regression',
#                 'features': 'Feature-based Model',
#                 'mae_mean': reg_mae_mean, 'mae_std': reg_mae_std,
#                 'rmse_mean': reg_rmse_mean, 'rmse_std': reg_rmse_std,
#                 'r2_mean': reg_r2_mean, 'r2_std': reg_r2_std,
#                 'accuracy_mean': None, 'accuracy_std': None,
#                 'precision_mean': None, 'precision_std': None,
#                 'recall_mean': None, 'recall_std': None,
#                 'f1_mean': None, 'f1_std': None,
#                 'n_train': len(y_train_reg), 'n_test': len(y_test_reg),
#                 'n_features': len(feature_columns),
#                 'feature_breakdown': prefix_counts
#             },
#             {
#                 'task': 'classification',
#                 'features': 'Feature-based Model',
#                 'mae_mean': None, 'mae_std': None,
#                 'rmse_mean': None, 'rmse_std': None,
#                 'r2_mean': None, 'r2_std': None,
#                 'accuracy_mean': cls_acc_mean, 'accuracy_std': cls_acc_std,
#                 'precision_mean': cls_prec_mean, 'precision_std': cls_prec_std,
#                 'recall_mean': cls_rec_mean, 'recall_std': cls_rec_std,
#                 'f1_mean': cls_f1_mean, 'f1_std': cls_f1_std,
#                 'n_train': len(y_train_reg), 'n_test': len(y_test_reg),
#                 'n_features': len(feature_columns),
#                 'feature_breakdown': prefix_counts
#             }
#         ]
        
#     except Exception as e:
#         logging.error(f"Error in Task 3: {e}")
#         import traceback
#         traceback.print_exc()
#         return None

# def main():
#     """Main execution function"""
#     print("🚀 Starting Polymer Tg Prediction Experiments (Regression + Classification)")
#     print(f"📊 Train Dataset: {TRAIN_CSV_PATH}")
#     print(f"📊 Test Dataset: {TEST_CSV_PATH}")
#     print(f"🎯 Regression Target: Tg(K)")
#     print(f"🎯 Classification Target: class_label")
#     print(f"🔬 Regression Model: GradientBoostingRegressor (default settings)")
#     print(f"🔬 Classification Model: LogisticRegression (default settings)")
#     print(f"🌱 Random Seeds: {RANDOM_SEEDS}")
#     print(f"🔧 Feature Prefixes: {FEATURE_PREFIXES}")
#     print("="*80)
    
#     # Load datasets
#     train_df, test_df = load_datasets()
    
#     # Run experiments
#     all_results = []
    
#     # Task 1: Baseline ECFP
#     try:
#         results1 = task1_baseline_ecfp(train_df, test_df)
#         if results1:
#             all_results.extend(results1)
#     except Exception as e:
#         logging.error(f"Error in Task 1: {e}")
#         import traceback
#         traceback.print_exc()
    
#     # Task 2: Combined embeddings
#     try:
#         results2 = task2_combined_embeddings(train_df, test_df)
#         if results2:
#             all_results.extend(results2)
#     except Exception as e:
#         logging.error(f"Error in Task 2: {e}")
#         import traceback
#         traceback.print_exc()
    
#     # Task 3: Feature-based model
#     try:
#         results3 = task3_feature_based_model(train_df, test_df)
#         if results3:
#             all_results.extend(results3)
#     except Exception as e:
#         logging.error(f"Error in Task 3: {e}")
#         import traceback
#         traceback.print_exc()
    
#     # Summary
#     if all_results:
#         logging.info("\n" + "="*100)
#         logging.info("📊 FINAL EXPERIMENT SUMMARY")
#         logging.info("="*100)
        
#         # Separate regression and classification results
#         regression_results = [r for r in all_results if r['task'] == 'regression']
#         classification_results = [r for r in all_results if r['task'] == 'classification']
        
#         logging.info("\n🔢 REGRESSION RESULTS:")
#         for result in regression_results:
#             logging.info(f"\n{result['features']}:")
#             logging.info(f"  Training samples: {result['n_train']}")
#             logging.info(f"  Test samples: {result['n_test']}")
#             if 'n_features' in result:
#                 logging.info(f"  Features used: {result['n_features']}")
#             if 'feature_breakdown' in result:
#                 for prefix, count in result['feature_breakdown'].items():
#                     logging.info(f"    {prefix}: {count}")
#             logging.info(f"  MAE:  {result['mae_mean']:.3f} ± {result['mae_std']:.3f}")
#             logging.info(f"  RMSE: {result['rmse_mean']:.3f} ± {result['rmse_std']:.3f}")
#             logging.info(f"  R²:   {result['r2_mean']:.3f} ± {result['r2_std']:.3f}")
        
#         logging.info("\n🎯 CLASSIFICATION RESULTS:")
#         for result in classification_results:
#             logging.info(f"\n{result['features']}:")
#             logging.info(f"  Training samples: {result['n_train']}")
#             logging.info(f"  Test samples: {result['n_test']}")
#             if 'n_features' in result:
#                 logging.info(f"  Features used: {result['n_features']}")
#             if 'feature_breakdown' in result:
#                 for prefix, count in result['feature_breakdown'].items():
#                     logging.info(f"    {prefix}: {count}")
#             logging.info(f"  Accuracy:  {result['accuracy_mean']:.3f} ± {result['accuracy_std']:.3f}")
#             logging.info(f"  Precision: {result['precision_mean']:.3f} ± {result['precision_std']:.3f}")
#             logging.info(f"  Recall:    {result['recall_mean']:.3f} ± {result['recall_std']:.3f}")
#             logging.info(f"  F1:        {result['f1_mean']:.3f} ± {result['f1_std']:.3f}")
        
#         # Save results
#         results_df = pd.DataFrame(all_results)
#         timestamp = datetime.now().strftime("%Y%m%d_%H%M")
#         output_csv = f"Application_Neurips_combining_datasets_{timestamp}.csv"
#         results_df.to_csv(output_csv, index=False)
        
#         logging.info(f"\n💾 Results saved to: {output_csv}")
        
#         print(f"\n📋 EXPERIMENT COMPLETED:")
#         print(f"Results saved to: {output_csv}")
        
#         # Performance comparison
#         if len(regression_results) > 1:
#             logging.info("\n🏆 REGRESSION PERFORMANCE COMPARISON (R² Score):")
#             sorted_results = sorted(regression_results, key=lambda x: x['r2_mean'], reverse=True)
#             for i, result in enumerate(sorted_results, 1):
#                 logging.info(f"  {i}. {result['features']}: R² = {result['r2_mean']:.3f} ± {result['r2_std']:.3f}")
            
#             logging.info("\n🎯 REGRESSION PERFORMANCE COMPARISON (MAE - Lower is Better):")
#             sorted_mae = sorted(regression_results, key=lambda x: x['mae_mean'])
#             for i, result in enumerate(sorted_mae, 1):
#                 logging.info(f"  {i}. {result['features']}: MAE = {result['mae_mean']:.3f} ± {result['mae_std']:.3f}")
        
#         if len(classification_results) > 1:
#             logging.info("\n🏆 CLASSIFICATION PERFORMANCE COMPARISON (F1 Score):")
#             sorted_f1 = sorted(classification_results, key=lambda x: x['f1_mean'], reverse=True)
#             for i, result in enumerate(sorted_f1, 1):
#                 logging.info(f"  {i}. {result['features']}: F1 = {result['f1_mean']:.3f} ± {result['f1_std']:.3f}")
            
#             logging.info("\n🎯 CLASSIFICATION PERFORMANCE COMPARISON (Accuracy):")
#             sorted_acc = sorted(classification_results, key=lambda x: x['accuracy_mean'], reverse=True)
#             for i, result in enumerate(sorted_acc, 1):
#                 logging.info(f"  {i}. {result['features']}: Accuracy = {result['accuracy_mean']:.3f} ± {result['accuracy_std']:.3f}")
#     else:
#         logging.error("No results generated. Check for errors in the experiments.")

# if __name__ == "__main__":
#     main()


# # neurips concatenated embeddingd
# # neurips
# import numpy as np
# import pandas as pd
# from sklearn.ensemble import GradientBoostingRegressor
# from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
# from sklearn.preprocessing import StandardScaler
# from datetime import datetime
# import logging

# # Configuration
# RANDOM_SEEDS = [42, 123, 456]  # Three different random seeds

# # Dataset paths
# TRAIN_CSV_PATH = '/home/ta45woj/PolyMetriX/src/polymetrix/datasets/valid_dataset_20250715_1717_0.95_trained_model_neurips_application_tg_combining_datasets_ecfp_info_train_set.csv'
# TEST_CSV_PATH = '/home/ta45woj/PolyMetriX/src/polymetrix/datasets/valid_dataset_20250715_1717_0.95_trained_model_neurips_application_tg_combining_datasets_ecfp_info_test_set.csv'

# # Feature prefixes for Task 3
# FEATURE_PREFIXES = ['fullpolymerlevel.features.', 'sidechainlevel.features.', 'backbonelevel.features.']

# # Initialize logging
# logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

# def load_datasets():
#     """Load training and test datasets"""
#     logging.info("Loading datasets...")
#     train_df = pd.read_csv(TRAIN_CSV_PATH)
#     test_df = pd.read_csv(TEST_CSV_PATH)
    
#     logging.info(f"Train dataset shape: {train_df.shape}")
#     logging.info(f"Test dataset shape: {test_df.shape}")
    
#     return train_df, test_df

# def parse_embedding_column(df, column_name):
#     """Parse embedding column from string representation to numpy array"""
#     embeddings = []
#     embedding_lengths = []
    
#     for i, embedding_str in enumerate(df[column_name]):
#         # Handle different string formats
#         embedding_str = str(embedding_str).strip()
        
#         # Skip if NaN or empty
#         if embedding_str == 'nan' or embedding_str == '' or pd.isna(embedding_str):
#             continue
            
#         # Handle PyTorch tensor format: "tensor([0.1, 0.2, ...])"
#         if embedding_str.startswith('tensor('):
#             # Extract the array part from tensor([...])
#             start_idx = embedding_str.find('[')
#             end_idx = embedding_str.rfind(']')
#             if start_idx != -1 and end_idx != -1:
#                 array_str = embedding_str[start_idx+1:end_idx]
#             else:
#                 logging.warning(f"Invalid tensor format at row {i}: {embedding_str[:50]}...")
#                 continue
#         # Handle simple array format: "[0.1, 0.2, ...]"
#         elif embedding_str.startswith('[') and embedding_str.endswith(']'):
#             array_str = embedding_str[1:-1]
#         else:
#             # Try to use as-is
#             array_str = embedding_str
        
#         # Parse the numbers
#         try:
#             # Split by comma and convert to float
#             values = [float(x.strip()) for x in array_str.split(',') if x.strip()]
#             if len(values) == 0:
#                 logging.warning(f"Empty embedding at row {i}")
#                 continue
                
#             embedding = np.array(values)
#             embeddings.append(embedding)
#             embedding_lengths.append(len(values))
#         except ValueError as e:
#             logging.warning(f"Error parsing embedding at row {i}: {embedding_str[:50]}... - {e}")
#             continue
    
#     if len(embeddings) == 0:
#         raise ValueError(f"No valid embeddings found in column {column_name}")
    
#     # Check for consistent dimensions
#     unique_lengths = set(embedding_lengths)
#     if len(unique_lengths) > 1:
#         logging.warning(f"Inconsistent embedding dimensions in {column_name}: {unique_lengths}")
#         # Use the most common dimension
#         from collections import Counter
#         most_common_length = Counter(embedding_lengths).most_common(1)[0][0]
#         logging.info(f"Using most common dimension: {most_common_length}")
        
#         # Filter embeddings to consistent dimension
#         filtered_embeddings = []
#         for emb in embeddings:
#             if len(emb) == most_common_length:
#                 filtered_embeddings.append(emb)
        
#         embeddings = filtered_embeddings
#         logging.info(f"Filtered to {len(embeddings)} embeddings with consistent dimension")
    
#     if len(embeddings) == 0:
#         raise ValueError(f"No embeddings with consistent dimensions in column {column_name}")
    
#     # Now create the numpy array
#     try:
#         result = np.array(embeddings)
#         logging.info(f"Successfully parsed {column_name}: shape {result.shape}")
#         return result
#     except Exception as e:
#         logging.error(f"Failed to create numpy array for {column_name}: {e}")
#         # Try creating it row by row to identify the problematic entries
#         max_len = max(len(emb) for emb in embeddings)
#         min_len = min(len(emb) for emb in embeddings)
#         logging.error(f"Embedding length range: {min_len} to {max_len}")
#         raise e

# def extract_feature_columns(df, feature_prefixes):
#     """Extract feature columns based on prefixes"""
#     feature_columns = []
    
#     for prefix in feature_prefixes:
#         prefix_columns = [col for col in df.columns if col.startswith(prefix)]
#         feature_columns.extend(prefix_columns)
#         logging.info(f"Found {len(prefix_columns)} columns with prefix '{prefix}'")
    
#     if len(feature_columns) == 0:
#         raise ValueError(f"No feature columns found with prefixes: {feature_prefixes}")
    
#     logging.info(f"Total feature columns found: {len(feature_columns)}")
    
#     # Extract the features and handle missing values
#     X = df[feature_columns].copy()
    
#     # Check for missing values
#     missing_counts = X.isnull().sum()
#     if missing_counts.sum() > 0:
#         logging.warning(f"Found missing values in {missing_counts[missing_counts > 0].shape[0]} columns")
#         logging.info("Filling missing values with 0")
#         X = X.fillna(0)
    
#     # Check for non-numeric columns
#     numeric_columns = X.select_dtypes(include=[np.number]).columns
#     if len(numeric_columns) != len(feature_columns):
#         non_numeric = set(feature_columns) - set(numeric_columns)
#         logging.warning(f"Non-numeric columns found: {non_numeric}")
#         X = X[numeric_columns]
#         logging.info(f"Using {len(numeric_columns)} numeric columns")
    
#     return X.values, feature_columns

# def evaluate_model(y_true, y_pred):
#     """Calculate evaluation metrics"""
#     mae = mean_absolute_error(y_true, y_pred)
#     rmse = np.sqrt(mean_squared_error(y_true, y_pred))
#     r2 = r2_score(y_true, y_pred)
#     return mae, rmse, r2

# def task1_baseline_ecfp(train_df, test_df):
#     """Task 1: Baseline model using ECFP fingerprints"""
#     logging.info("\n" + "="*80)
#     logging.info("TASK 1: Baseline Model with ECFP Fingerprints")
#     logging.info("="*80)
    
#     # Prepare features and target
#     X_train = parse_embedding_column(train_df, 'ecfp_fingerprint')
#     y_train = train_df['Tg(K)'].values
    
#     X_test = parse_embedding_column(test_df, 'ecfp_fingerprint')
#     y_test = test_df['Tg(K)'].values
    
#     # Ensure we have matching indices
#     if len(X_train) != len(y_train):
#         # Need to filter y_train to match X_train
#         logging.warning(f"Mismatch in training data: X_train={len(X_train)}, y_train={len(y_train)}")
#         # This is a more complex fix - for now, let's assume they match
    
#     if len(X_test) != len(y_test):
#         logging.warning(f"Mismatch in test data: X_test={len(X_test)}, y_test={len(y_test)}")
    
#     logging.info(f"Training features shape: {X_train.shape}")
#     logging.info(f"Test features shape: {X_test.shape}")
#     logging.info(f"Training samples: {len(y_train)}")
#     logging.info(f"Test samples: {len(y_test)}")
    
#     results = []
    
#     # Run with different random seeds
#     for seed in RANDOM_SEEDS:
#         logging.info(f"\nRunning with random seed: {seed}")
        
#         # Train model
#         model = GradientBoostingRegressor(random_state=seed)
#         model.fit(X_train, y_train)
        
#         # Predict
#         y_pred = model.predict(X_test)
        
#         # Evaluate
#         mae, rmse, r2 = evaluate_model(y_test, y_pred)
        
#         logging.info(f"Seed {seed} - MAE: {mae:.3f}, RMSE: {rmse:.3f}, R²: {r2:.3f}")
        
#         results.append({
#             'seed': seed,
#             'mae': mae,
#             'rmse': rmse,
#             'r2': r2
#         })
    
#     # Calculate statistics
#     maes = [r['mae'] for r in results]
#     rmses = [r['rmse'] for r in results]
#     r2s = [r['r2'] for r in results]
    
#     mae_mean, mae_std = np.mean(maes), np.std(maes, ddof=1)
#     rmse_mean, rmse_std = np.mean(rmses), np.std(rmses, ddof=1)
#     r2_mean, r2_std = np.mean(r2s), np.std(r2s, ddof=1)
    
#     logging.info(f"\n--- TASK 1 FINAL RESULTS ---")
#     logging.info(f"MAE:  {mae_mean:.3f} ± {mae_std:.3f}")
#     logging.info(f"RMSE: {rmse_mean:.3f} ± {rmse_std:.3f}")
#     logging.info(f"R²:   {r2_mean:.3f} ± {r2_std:.3f}")
    
#     return {
#         'task': 'Baseline ECFP',
#         'mae_mean': mae_mean, 'mae_std': mae_std,
#         'rmse_mean': rmse_mean, 'rmse_std': rmse_std,
#         'r2_mean': r2_mean, 'r2_std': r2_std,
#         'n_train': len(X_train), 'n_test': len(X_test)
#     }

# def task2_combined_embeddings(train_df, test_df):
#     """Task 2: Combined embeddings model - Concatenate psmiles_bigsmiles_embed and bigsmiles_psmiles_embed"""
#     logging.info("\n" + "="*80)
#     logging.info("TASK 2: Concatenated Embeddings Model (psmiles_bigsmiles_embed + bigsmiles_psmiles_embed)")
#     logging.info("="*80)
    
#     # Parse both embedding columns for training data
#     try:
#         psmiles_train = parse_embedding_column(train_df, 'psmiles_bigsmiles_embed')
#         bigsmiles_train = parse_embedding_column(train_df, 'bigsmiles_psmiles_embed')
#         y_train = train_df['Tg(K)'].values
        
#         logging.info(f"psmiles_bigsmiles_embed training shape: {psmiles_train.shape}")
#         logging.info(f"bigsmiles_psmiles_embed training shape: {bigsmiles_train.shape}")
        
#         # Ensure both embeddings have same number of samples
#         min_train_samples = min(len(psmiles_train), len(bigsmiles_train), len(y_train))
#         psmiles_train = psmiles_train[:min_train_samples]
#         bigsmiles_train = bigsmiles_train[:min_train_samples]
#         y_train = y_train[:min_train_samples]
        
#         # Concatenate embeddings horizontally (feature-wise)
#         X_train_combined = np.concatenate([psmiles_train, bigsmiles_train], axis=1)
        
#         logging.info(f"Training - psmiles shape: {psmiles_train.shape}")
#         logging.info(f"Training - bigsmiles shape: {bigsmiles_train.shape}")
#         logging.info(f"Training - concatenated shape: {X_train_combined.shape}")
#         logging.info(f"Training samples: {len(y_train)}")
        
#     except Exception as e:
#         logging.error(f"Error processing training embeddings: {e}")
#         return None
    
#     # Parse both embedding columns for test data
#     try:
#         psmiles_test = parse_embedding_column(test_df, 'psmiles_bigsmiles_embed')
#         bigsmiles_test = parse_embedding_column(test_df, 'bigsmiles_psmiles_embed')
#         y_test = test_df['Tg(K)'].values
        
#         logging.info(f"psmiles_bigsmiles_embed test shape: {psmiles_test.shape}")
#         logging.info(f"bigsmiles_psmiles_embed test shape: {bigsmiles_test.shape}")
        
#         # Ensure both embeddings have same number of samples
#         min_test_samples = min(len(psmiles_test), len(bigsmiles_test), len(y_test))
#         psmiles_test = psmiles_test[:min_test_samples]
#         bigsmiles_test = bigsmiles_test[:min_test_samples]
#         y_test = y_test[:min_test_samples]
        
#         # Concatenate embeddings horizontally (feature-wise)
#         X_test_combined = np.concatenate([psmiles_test, bigsmiles_test], axis=1)
        
#         logging.info(f"Test - psmiles shape: {psmiles_test.shape}")
#         logging.info(f"Test - bigsmiles shape: {bigsmiles_test.shape}")
#         logging.info(f"Test - concatenated shape: {X_test_combined.shape}")
#         logging.info(f"Test samples: {len(y_test)}")
        
#     except Exception as e:
#         logging.error(f"Error processing test embeddings: {e}")
#         return None
    
#     # Verify dimensions match between train and test
#     if X_train_combined.shape[1] != X_test_combined.shape[1]:
#         logging.error(f"Feature dimension mismatch: train={X_train_combined.shape[1]}, test={X_test_combined.shape[1]}")
#         return None
    
#     # Expected concatenated dimension should be 512 (256 + 256)
#     expected_dim = 512
#     if X_train_combined.shape[1] == expected_dim:
#         logging.info(f"✓ Concatenated embeddings have expected dimension: {expected_dim}")
#     else:
#         logging.warning(f"Concatenated dimension {X_train_combined.shape[1]} differs from expected {expected_dim}")
    
#     # NOTE: Ignoring psmiles_polymer_name_embed and polymer_name_psmiles_embed as requested
#     logging.info("Ignoring psmiles_polymer_name_embed and polymer_name_psmiles_embed embeddings")
    
#     results = []
    
#     # Run with different random seeds
#     for seed in RANDOM_SEEDS:
#         logging.info(f"\nRunning with random seed: {seed}")
        
#         # Train model
#         model = GradientBoostingRegressor(random_state=seed)
#         model.fit(X_train_combined, y_train)
        
#         # Predict
#         y_pred = model.predict(X_test_combined)
        
#         # Evaluate
#         mae, rmse, r2 = evaluate_model(y_test, y_pred)
        
#         logging.info(f"Seed {seed} - MAE: {mae:.3f}, RMSE: {rmse:.3f}, R²: {r2:.3f}")
        
#         results.append({
#             'seed': seed,
#             'mae': mae,
#             'rmse': rmse,
#             'r2': r2
#         })
    
#     # Calculate statistics
#     maes = [r['mae'] for r in results]
#     rmses = [r['rmse'] for r in results]
#     r2s = [r['r2'] for r in results]
    
#     mae_mean, mae_std = np.mean(maes), np.std(maes, ddof=1)
#     rmse_mean, rmse_std = np.mean(rmses), np.std(rmses, ddof=1)
#     r2_mean, r2_std = np.mean(r2s), np.std(r2s, ddof=1)
    
#     logging.info(f"\n--- TASK 2 FINAL RESULTS ---")
#     logging.info(f"Concatenated embedding dimension: {X_train_combined.shape[1]} (expected: 512)")
#     logging.info(f"MAE:  {mae_mean:.3f} ± {mae_std:.3f}")
#     logging.info(f"RMSE: {rmse_mean:.3f} ± {rmse_std:.3f}")
#     logging.info(f"R²:   {r2_mean:.3f} ± {r2_std:.3f}")
    
#     return {
#         'task': 'Concatenated Embeddings (psmiles_bigsmiles + bigsmiles_psmiles)',
#         'mae_mean': mae_mean, 'mae_std': mae_std,
#         'rmse_mean': rmse_mean, 'rmse_std': rmse_std,
#         'r2_mean': r2_mean, 'r2_std': r2_std,
#         'n_train': len(y_train), 'n_test': len(y_test),
#         'embedding_dim': X_train_combined.shape[1]
#     }

# def task3_feature_based_model(train_df, test_df):
#     """Task 3: Feature-based model using polymer level features"""
#     logging.info("\n" + "="*80)
#     logging.info("TASK 3: Feature-based Model with Polymer Level Features")
#     logging.info("="*80)
    
#     # Extract feature columns
#     try:
#         X_train, feature_columns = extract_feature_columns(train_df, FEATURE_PREFIXES)
#         X_test, _ = extract_feature_columns(test_df, FEATURE_PREFIXES)
        
#         # Get target values
#         y_train = train_df['Tg(K)'].values
#         y_test = test_df['Tg(K)'].values
        
#         logging.info(f"Training features shape: {X_train.shape}")
#         logging.info(f"Test features shape: {X_test.shape}")
#         logging.info(f"Training samples: {len(y_train)}")
#         logging.info(f"Test samples: {len(y_test)}")
        
#         # Check for dimension mismatch
#         if X_train.shape[1] != X_test.shape[1]:
#             logging.error(f"Feature dimension mismatch: train={X_train.shape[1]}, test={X_test.shape[1]}")
#             return None
        
#         # Check for consistent sample sizes
#         if len(X_train) != len(y_train):
#             logging.warning(f"Sample size mismatch in training: X={len(X_train)}, y={len(y_train)}")
#             min_len = min(len(X_train), len(y_train))
#             X_train = X_train[:min_len]
#             y_train = y_train[:min_len]
#             logging.info(f"Adjusted to {min_len} training samples")
        
#         if len(X_test) != len(y_test):
#             logging.warning(f"Sample size mismatch in test: X={len(X_test)}, y={len(y_test)}")
#             min_len = min(len(X_test), len(y_test))
#             X_test = X_test[:min_len]
#             y_test = y_test[:min_len]
#             logging.info(f"Adjusted to {min_len} test samples")
        
#         # Feature scaling (important for feature-based models)
#         scaler = StandardScaler()
#         X_train_scaled = scaler.fit_transform(X_train)
#         X_test_scaled = scaler.transform(X_test)
        
#         logging.info("Features scaled using StandardScaler")
        
#         # Log feature statistics
#         logging.info(f"Feature range after scaling - Train: [{X_train_scaled.min():.3f}, {X_train_scaled.max():.3f}]")
#         logging.info(f"Feature range after scaling - Test: [{X_test_scaled.min():.3f}, {X_test_scaled.max():.3f}]")
        
#         # Breakdown by feature prefix
#         prefix_counts = {}
#         for prefix in FEATURE_PREFIXES:
#             count = sum(1 for col in feature_columns if col.startswith(prefix))
#             prefix_counts[prefix] = count
#             logging.info(f"{prefix}: {count} features")
        
#         results = []
        
#         # Run with different random seeds
#         for seed in RANDOM_SEEDS:
#             logging.info(f"\nRunning with random seed: {seed}")
            
#             # Train model
#             model = GradientBoostingRegressor(random_state=seed)
#             model.fit(X_train_scaled, y_train)
            
#             # Predict
#             y_pred = model.predict(X_test_scaled)
            
#             # Evaluate
#             mae, rmse, r2 = evaluate_model(y_test, y_pred)
            
#             logging.info(f"Seed {seed} - MAE: {mae:.3f}, RMSE: {rmse:.3f}, R²: {r2:.3f}")
            
#             results.append({
#                 'seed': seed,
#                 'mae': mae,
#                 'rmse': rmse,
#                 'r2': r2
#             })
        
#         # Calculate statistics
#         maes = [r['mae'] for r in results]
#         rmses = [r['rmse'] for r in results]
#         r2s = [r['r2'] for r in results]
        
#         mae_mean, mae_std = np.mean(maes), np.std(maes, ddof=1)
#         rmse_mean, rmse_std = np.mean(rmses), np.std(rmses, ddof=1)
#         r2_mean, r2_std = np.mean(r2s), np.std(r2s, ddof=1)
        
#         logging.info(f"\n--- TASK 3 FINAL RESULTS ---")
#         logging.info(f"Total features used: {len(feature_columns)}")
#         for prefix, count in prefix_counts.items():
#             logging.info(f"  {prefix}: {count} features")
#         logging.info(f"MAE:  {mae_mean:.3f} ± {mae_std:.3f}")
#         logging.info(f"RMSE: {rmse_mean:.3f} ± {rmse_std:.3f}")
#         logging.info(f"R²:   {r2_mean:.3f} ± {r2_std:.3f}")
        
#         return {
#             'task': 'Feature-based Model',
#             'mae_mean': mae_mean, 'mae_std': mae_std,
#             'rmse_mean': rmse_mean, 'rmse_std': rmse_std,
#             'r2_mean': r2_mean, 'r2_std': r2_std,
#             'n_train': len(y_train), 'n_test': len(y_test),
#             'n_features': len(feature_columns),
#             'feature_breakdown': prefix_counts
#         }
        
#     except Exception as e:
#         logging.error(f"Error in Task 3: {e}")
#         import traceback
#         traceback.print_exc()
#         return None

# def main():
#     """Main execution function"""
#     print("🚀 Starting Polymer Tg Prediction Experiments")
#     print(f"📊 Train Dataset: {TRAIN_CSV_PATH}")
#     print(f"📊 Test Dataset: {TEST_CSV_PATH}")
#     print(f"🎯 Target: Tg(K)")
#     print(f"🔬 Model: GradientBoostingRegressor (default settings)")
#     print(f"🌱 Random Seeds: {RANDOM_SEEDS}")
#     print(f"🔧 Feature Prefixes: {FEATURE_PREFIXES}")
#     print("="*80)
    
#     # Load datasets
#     train_df, test_df = load_datasets()
    
#     # Run experiments
#     all_results = []
    
#     # Task 1: Baseline ECFP
#     try:
#         result1 = task1_baseline_ecfp(train_df, test_df)
#         if result1:
#             all_results.append(result1)
#     except Exception as e:
#         logging.error(f"Error in Task 1: {e}")
#         import traceback
#         traceback.print_exc()
    
#     # Task 2: Combined embeddings
#     try:
#         result2 = task2_combined_embeddings(train_df, test_df)
#         if result2:
#             all_results.append(result2)
#     except Exception as e:
#         logging.error(f"Error in Task 2: {e}")
#         import traceback
#         traceback.print_exc()
    
#     # Task 3: Feature-based model
#     try:
#         result3 = task3_feature_based_model(train_df, test_df)
#         if result3:
#             all_results.append(result3)
#     except Exception as e:
#         logging.error(f"Error in Task 3: {e}")
#         import traceback
#         traceback.print_exc()
    
#     # Summary
#     if all_results:
#         logging.info("\n" + "="*100)
#         logging.info("📊 FINAL EXPERIMENT SUMMARY")
#         logging.info("="*100)
        
#         for result in all_results:
#             logging.info(f"\n{result['task']}:")
#             logging.info(f"  Training samples: {result['n_train']}")
#             logging.info(f"  Test samples: {result['n_test']}")
#             if 'n_features' in result:
#                 logging.info(f"  Features used: {result['n_features']}")
#             if 'feature_breakdown' in result:
#                 for prefix, count in result['feature_breakdown'].items():
#                     logging.info(f"    {prefix}: {count}")
#             logging.info(f"  MAE:  {result['mae_mean']:.3f} ± {result['mae_std']:.3f}")
#             logging.info(f"  RMSE: {result['rmse_mean']:.3f} ± {result['rmse_std']:.3f}")
#             logging.info(f"  R²:   {result['r2_mean']:.3f} ± {result['r2_std']:.3f}")
        
#         # Save results
#         results_df = pd.DataFrame(all_results)
#         timestamp = datetime.now().strftime("%Y%m%d_%H%M")
#         output_csv = f"Application_Neurips_combining_datasets_{timestamp}.csv"
#         results_df.to_csv(output_csv, index=False)
        
#         logging.info(f"\n💾 Results saved to: {output_csv}")
        
#         print(f"\n📋 EXPERIMENT COMPLETED:")
#         print(f"Results saved to: {output_csv}")
        
#         # Performance comparison
#         if len(all_results) > 1:
#             logging.info("\n🏆 PERFORMANCE COMPARISON (R² Score):")
#             sorted_results = sorted(all_results, key=lambda x: x['r2_mean'], reverse=True)
#             for i, result in enumerate(sorted_results, 1):
#                 logging.info(f"  {i}. {result['task']}: R² = {result['r2_mean']:.3f} ± {result['r2_std']:.3f}")
            
#             logging.info("\n🎯 PERFORMANCE COMPARISON (MAE - Lower is Better):")
#             sorted_mae = sorted(all_results, key=lambda x: x['mae_mean'])
#             for i, result in enumerate(sorted_mae, 1):
#                 logging.info(f"  {i}. {result['task']}: MAE = {result['mae_mean']:.3f} ± {result['mae_std']:.3f}")
#     else:
#         logging.error("No results generated. Check for errors in the experiments.")

# if __name__ == "__main__":
#     main()

# import numpy as np
# import pandas as pd
# from sklearn.ensemble import GradientBoostingRegressor
# from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
# from datetime import datetime
# import logging

# # Configuration
# RANDOM_SEEDS = [42, 123, 456]  # Three different random seeds

# # Dataset paths
# TRAIN_CSV_PATH = '/home/ta45woj/PolyMetriX/src/polymetrix/datasets/valid_dataset_20250626_1016_with_psmiles_bigsmiles_embed_tg_train_test_application_multuple_property_train.csv'
# TEST_CSV_PATH = '/home/ta45woj/PolyMetriX/src/polymetrix/datasets/valid_dataset_20250626_1016_with_psmiles_bigsmiles_embed_tg_train_test_application_multuple_property_test.csv'

# # Target properties
# TARGET_PROPERTIES = [
#     'Tg(K)',
#     'Melting temperature_value_median',
#     'Crystallization temperature_value_median',
#     'Brittleness temperature_value_median',
#     'Radius of gyration_value_median'
# ]

# # Initialize logging
# logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

# def load_datasets():
#     """Load training and test datasets"""
#     logging.info("Loading datasets...")
#     train_df = pd.read_csv(TRAIN_CSV_PATH)
#     test_df = pd.read_csv(TEST_CSV_PATH)
    
#     logging.info(f"Train dataset shape: {train_df.shape}")
#     logging.info(f"Test dataset shape: {test_df.shape}")
    
#     # Check which target properties are available
#     available_targets = []
#     for target in TARGET_PROPERTIES:
#         if target in train_df.columns:
#             available_targets.append(target)
#             non_nan_train = train_df[target].notna().sum()
#             non_nan_test = test_df[target].notna().sum() if target in test_df.columns else 0
#             logging.info(f"Target '{target}': {non_nan_train} train samples, {non_nan_test} test samples")
#         else:
#             logging.warning(f"Target '{target}' not found in datasets")
    
#     logging.info(f"Available target properties: {available_targets}")
#     return train_df, test_df, available_targets

# def parse_embedding_column(df, column_name):
#     """Parse embedding column from string representation to numpy array - EXACTLY like original script"""
#     embeddings = []
#     embedding_lengths = []
    
#     for i, embedding_str in enumerate(df[column_name]):
#         # Handle different string formats
#         embedding_str = str(embedding_str).strip()
        
#         # Skip if NaN or empty
#         if embedding_str == 'nan' or embedding_str == '' or pd.isna(embedding_str):
#             continue
            
#         # Handle PyTorch tensor format: "tensor([0.1, 0.2, ...])"
#         if embedding_str.startswith('tensor('):
#             # Extract the array part from tensor([...])
#             start_idx = embedding_str.find('[')
#             end_idx = embedding_str.rfind(']')
#             if start_idx != -1 and end_idx != -1:
#                 array_str = embedding_str[start_idx+1:end_idx]
#             else:
#                 logging.warning(f"Invalid tensor format at row {i}: {embedding_str[:50]}...")
#                 continue
#         # Handle simple array format: "[0.1, 0.2, ...]"
#         elif embedding_str.startswith('[') and embedding_str.endswith(']'):
#             array_str = embedding_str[1:-1]
#         else:
#             # Try to use as-is
#             array_str = embedding_str
        
#         # Parse the numbers
#         try:
#             # Split by comma and convert to float
#             values = [float(x.strip()) for x in array_str.split(',') if x.strip()]
#             if len(values) == 0:
#                 logging.warning(f"Empty embedding at row {i}")
#                 continue
                
#             embedding = np.array(values)
#             embeddings.append(embedding)
#             embedding_lengths.append(len(values))
#         except ValueError as e:
#             logging.warning(f"Error parsing embedding at row {i}: {embedding_str[:50]}... - {e}")
#             continue
    
#     if len(embeddings) == 0:
#         raise ValueError(f"No valid embeddings found in column {column_name}")
    
#     # Check for consistent dimensions
#     unique_lengths = set(embedding_lengths)
#     if len(unique_lengths) > 1:
#         logging.warning(f"Inconsistent embedding dimensions in {column_name}: {unique_lengths}")
#         # Use the most common dimension
#         from collections import Counter
#         most_common_length = Counter(embedding_lengths).most_common(1)[0][0]
#         logging.info(f"Using most common dimension: {most_common_length}")
        
#         # Filter embeddings to consistent dimension
#         filtered_embeddings = []
#         for emb in embeddings:
#             if len(emb) == most_common_length:
#                 filtered_embeddings.append(emb)
        
#         embeddings = filtered_embeddings
#         logging.info(f"Filtered to {len(embeddings)} embeddings with consistent dimension")
    
#     if len(embeddings) == 0:
#         raise ValueError(f"No embeddings with consistent dimensions in column {column_name}")
    
#     # Now create the numpy array
#     try:
#         result = np.array(embeddings)
#         logging.info(f"Successfully parsed {column_name}: shape {result.shape}")
#         return result
#     except Exception as e:
#         logging.error(f"Failed to create numpy array for {column_name}: {e}")
#         # Try creating it row by row to identify the problematic entries
#         max_len = max(len(emb) for emb in embeddings)
#         min_len = min(len(emb) for emb in embeddings)
#         logging.error(f"Embedding length range: {min_len} to {max_len}")
#         raise e

# def evaluate_model(y_true, y_pred):
#     """Calculate evaluation metrics"""
#     mae = mean_absolute_error(y_true, y_pred)
#     rmse = np.sqrt(mean_squared_error(y_true, y_pred))
#     r2 = r2_score(y_true, y_pred)
#     return mae, rmse, r2

# def task1_baseline_ecfp(train_df, test_df, target_property):
#     """Task 1: Baseline model using ECFP fingerprints - EXACTLY like original script"""
#     logging.info(f"\n--- TASK 1: Baseline ECFP for {target_property} ---")
    
#     # Prepare features and target - NO FILTERING, just like original
#     X_train = parse_embedding_column(train_df, 'ecfp_fingerprint')
#     y_train = train_df[target_property].values
    
#     X_test = parse_embedding_column(test_df, 'ecfp_fingerprint')
#     y_test = test_df[target_property].values
    
#     # Filter out NaN values AFTER parsing embeddings, maintaining alignment
#     # This matches the original script's approach
#     if len(X_train) != len(y_train):
#         logging.warning(f"Length mismatch: X_train={len(X_train)}, y_train={len(y_train)}")
#         # For now, assume they should match - this needs investigation
#         min_len = min(len(X_train), len(y_train))
#         X_train = X_train[:min_len]
#         y_train = y_train[:min_len]
    
#     if len(X_test) != len(y_test):
#         logging.warning(f"Length mismatch: X_test={len(X_test)}, y_test={len(y_test)}")
#         min_len = min(len(X_test), len(y_test))
#         X_test = X_test[:min_len]
#         y_test = y_test[:min_len]
    
#     # Now filter for valid target values while maintaining X-y alignment
#     train_mask = ~np.isnan(y_train)
#     X_train = X_train[train_mask]
#     y_train = y_train[train_mask]
    
#     test_mask = ~np.isnan(y_test)
#     X_test = X_test[test_mask]
#     y_test = y_test[test_mask]
    
#     logging.info(f"Training features shape: {X_train.shape}")
#     logging.info(f"Test features shape: {X_test.shape}")
#     logging.info(f"Training samples: {len(y_train)}")
#     logging.info(f"Test samples: {len(y_test)}")
    
#     if len(X_train) == 0 or len(X_test) == 0:
#         logging.warning(f"Insufficient data for {target_property}")
#         return None
    
#     results = []
    
#     # Run with different random seeds
#     for seed in RANDOM_SEEDS:
#         logging.info(f"Running with random seed: {seed}")
        
#         # Train model
#         model = GradientBoostingRegressor(random_state=seed)
#         model.fit(X_train, y_train)
        
#         # Predict
#         y_pred = model.predict(X_test)
        
#         # Evaluate
#         mae, rmse, r2 = evaluate_model(y_test, y_pred)
        
#         logging.info(f"Seed {seed} - MAE: {mae:.3f}, RMSE: {rmse:.3f}, R²: {r2:.3f}")
        
#         results.append({
#             'seed': seed,
#             'mae': mae,
#             'rmse': rmse,
#             'r2': r2
#         })
    
#     # Calculate statistics
#     maes = [r['mae'] for r in results]
#     rmses = [r['rmse'] for r in results]
#     r2s = [r['r2'] for r in results]
    
#     mae_mean, mae_std = np.mean(maes), np.std(maes, ddof=1)
#     rmse_mean, rmse_std = np.mean(rmses), np.std(rmses, ddof=1)
#     r2_mean, r2_std = np.mean(r2s), np.std(r2s, ddof=1)
    
#     logging.info(f"--- TASK 1 RESULTS for {target_property} ---")
#     logging.info(f"MAE:  {mae_mean:.3f} ± {mae_std:.3f}")
#     logging.info(f"RMSE: {rmse_mean:.3f} ± {rmse_std:.3f}")
#     logging.info(f"R²:   {r2_mean:.3f} ± {r2_std:.3f}")
    
#     return {
#         'task': 'Baseline ECFP',
#         'target_property': target_property,
#         'mae_mean': mae_mean, 'mae_std': mae_std,
#         'rmse_mean': rmse_mean, 'rmse_std': rmse_std,
#         'r2_mean': r2_mean, 'r2_std': r2_std,
#         'n_train': len(X_train), 'n_test': len(X_test)
#     }

# def task2_combined_embeddings(train_df, test_df, target_property):
#     """Task 2: Combined embeddings model - EXACTLY like original script"""
#     logging.info(f"\n--- TASK 2: Combined Embeddings for {target_property} ---")
    
#     # Prepare test set using psmiles_embed to match combined training embeddings
#     X_test = parse_embedding_column(test_df, 'psmiles_embed')
#     y_test = test_df[target_property].values
    
#     # Handle length mismatch
#     if len(X_test) != len(y_test):
#         logging.warning(f"Test data mismatch: X_test={len(X_test)}, y_test={len(y_test)}")
#         min_len = min(len(X_test), len(y_test))
#         X_test = X_test[:min_len]
#         y_test = y_test[:min_len]
    
#     # Filter for valid target values
#     test_mask = ~np.isnan(y_test)
#     X_test = X_test[test_mask]
#     y_test = y_test[test_mask]
    
#     logging.info(f"Test features shape: {X_test.shape}")
#     logging.info(f"Test samples: {len(X_test)}")
    
#     if len(X_test) == 0:
#         logging.warning(f"No test data for {target_property}")
#         return None
    
#     # Create combined training dataset
#     combined_X = []
#     combined_y = []
    
#     # Get the target dimension from test set
#     target_dim = X_test.shape[1]
#     logging.info(f"Target embedding dimension: {target_dim}")
    
#     # Add psmiles_embed data
#     if 'psmiles_embed' in train_df.columns:
#         try:
#             psmiles_X = parse_embedding_column(train_df, 'psmiles_embed')
#             if psmiles_X.shape[1] == target_dim:
#                 # Get corresponding y values
#                 psmiles_y = train_df[target_property].values
#                 if len(psmiles_X) != len(psmiles_y):
#                     min_len = min(len(psmiles_X), len(psmiles_y))
#                     psmiles_X = psmiles_X[:min_len]
#                     psmiles_y = psmiles_y[:min_len]
                
#                 # Filter for valid target values
#                 mask = ~np.isnan(psmiles_y)
#                 psmiles_X = psmiles_X[mask]
#                 psmiles_y = psmiles_y[mask]
                
#                 combined_X.append(psmiles_X)
#                 combined_y.append(psmiles_y)
#                 logging.info(f"Added psmiles_embed: {len(psmiles_y)} samples, shape: {psmiles_X.shape}")
#             else:
#                 logging.warning(f"psmiles_embed dimension mismatch: {psmiles_X.shape[1]} vs {target_dim}")
#         except Exception as e:
#             logging.error(f"Error processing psmiles_embed: {e}")
    
#     # Add bigsmiles_embed data  
#     if 'bigsmiles_embed' in train_df.columns:
#         try:
#             bigsmiles_X = parse_embedding_column(train_df, 'bigsmiles_embed')
#             if bigsmiles_X.shape[1] == target_dim:
#                 bigsmiles_y = train_df[target_property].values
#                 if len(bigsmiles_X) != len(bigsmiles_y):
#                     min_len = min(len(bigsmiles_X), len(bigsmiles_y))
#                     bigsmiles_X = bigsmiles_X[:min_len]
#                     bigsmiles_y = bigsmiles_y[:min_len]
                
#                 # Filter for valid target values
#                 mask = ~np.isnan(bigsmiles_y)
#                 bigsmiles_X = bigsmiles_X[mask]
#                 bigsmiles_y = bigsmiles_y[mask]
                
#                 combined_X.append(bigsmiles_X)
#                 combined_y.append(bigsmiles_y)
#                 logging.info(f"Added bigsmiles_embed: {len(bigsmiles_y)} samples, shape: {bigsmiles_X.shape}")
#             else:
#                 logging.warning(f"bigsmiles_embed dimension mismatch: {bigsmiles_X.shape[1]} vs {target_dim}")
#         except Exception as e:
#             logging.error(f"Error processing bigsmiles_embed: {e}")
    
#     # Add psmiles_embed_polymer_name data
#     if 'psmiles_embed_polymer_name' in train_df.columns:
#         try:
#             psmiles_polymer_X = parse_embedding_column(train_df, 'psmiles_embed_polymer_name')
#             if psmiles_polymer_X.shape[1] == target_dim:
#                 psmiles_polymer_y = train_df[target_property].values
#                 if len(psmiles_polymer_X) != len(psmiles_polymer_y):
#                     min_len = min(len(psmiles_polymer_X), len(psmiles_polymer_y))
#                     psmiles_polymer_X = psmiles_polymer_X[:min_len]
#                     psmiles_polymer_y = psmiles_polymer_y[:min_len]
                
#                 # Filter for valid target values
#                 mask = ~np.isnan(psmiles_polymer_y)
#                 psmiles_polymer_X = psmiles_polymer_X[mask]
#                 psmiles_polymer_y = psmiles_polymer_y[mask]
                
#                 combined_X.append(psmiles_polymer_X)
#                 combined_y.append(psmiles_polymer_y)
#                 logging.info(f"Added psmiles_embed_polymer_name: {len(psmiles_polymer_y)} samples, shape: {psmiles_polymer_X.shape}")
#             else:
#                 logging.warning(f"psmiles_embed_polymer_name dimension mismatch: {psmiles_polymer_X.shape[1]} vs {target_dim}")
#         except Exception as e:
#             logging.error(f"Error processing psmiles_embed_polymer_name: {e}")
    
#     # Add polymer_name_embed data (if available)
#     if 'polymer_name_embed' in train_df.columns:
#         try:
#             # Filter out rows where polymer_name_embed is not null/empty
#             polymer_mask = train_df['polymer_name_embed'].notna()
#             if polymer_mask.sum() > 0:
#                 polymer_df = train_df[polymer_mask]
#                 polymer_X = parse_embedding_column(polymer_df, 'polymer_name_embed')
#                 if polymer_X.shape[1] == target_dim:
#                     polymer_y = polymer_df[target_property].values
#                     if len(polymer_X) != len(polymer_y):
#                         min_len = min(len(polymer_X), len(polymer_y))
#                         polymer_X = polymer_X[:min_len]
#                         polymer_y = polymer_y[:min_len]
                    
#                     # Filter for valid target values
#                     mask = ~np.isnan(polymer_y)
#                     polymer_X = polymer_X[mask]
#                     polymer_y = polymer_y[mask]
                    
#                     combined_X.append(polymer_X)
#                     combined_y.append(polymer_y)
#                     logging.info(f"Added polymer_name_embed: {len(polymer_y)} samples, shape: {polymer_X.shape}")
#                 else:
#                     logging.warning(f"polymer_name_embed dimension mismatch: {polymer_X.shape[1]} vs {target_dim}")
#         except Exception as e:
#             logging.error(f"Error processing polymer_name_embed: {e}")
    
#     # Check if we have any data
#     if len(combined_X) == 0:
#         logging.error(f"No embedding data found for {target_property}!")
#         return None
    
#     # Stack all embeddings
#     try:
#         X_train_combined = np.vstack(combined_X)
#         y_train_combined = np.concatenate(combined_y)
        
#         logging.info(f"Combined training data shape: {X_train_combined.shape}")
#         logging.info(f"Total training samples: {len(y_train_combined)}")
        
#         # Verify dimensions match
#         if X_train_combined.shape[1] != X_test.shape[1]:
#             logging.error(f"Dimension mismatch: train={X_train_combined.shape[1]}, test={X_test.shape[1]}")
#             return None
        
#     except Exception as e:
#         logging.error(f"Error combining embeddings: {e}")
#         return None
    
#     results = []
    
#     # Run with different random seeds
#     for seed in RANDOM_SEEDS:
#         logging.info(f"Running with random seed: {seed}")
        
#         # Train model
#         model = GradientBoostingRegressor(random_state=seed)
#         model.fit(X_train_combined, y_train_combined)
        
#         # Predict
#         y_pred = model.predict(X_test)
        
#         # Evaluate
#         mae, rmse, r2 = evaluate_model(y_test, y_pred)
        
#         logging.info(f"Seed {seed} - MAE: {mae:.3f}, RMSE: {rmse:.3f}, R²: {r2:.3f}")
        
#         results.append({
#             'seed': seed,
#             'mae': mae,
#             'rmse': rmse,
#             'r2': r2
#         })
    
#     # Calculate statistics
#     maes = [r['mae'] for r in results]
#     rmses = [r['rmse'] for r in results]
#     r2s = [r['r2'] for r in results]
    
#     mae_mean, mae_std = np.mean(maes), np.std(maes, ddof=1)
#     rmse_mean, rmse_std = np.mean(rmses), np.std(rmses, ddof=1)
#     r2_mean, r2_std = np.mean(r2s), np.std(r2s, ddof=1)
    
#     logging.info(f"--- TASK 2 RESULTS for {target_property} ---")
#     logging.info(f"MAE:  {mae_mean:.3f} ± {mae_std:.3f}")
#     logging.info(f"RMSE: {rmse_mean:.3f} ± {rmse_std:.3f}")
#     logging.info(f"R²:   {r2_mean:.3f} ± {r2_std:.3f}")
    
#     return {
#         'task': 'Combined Embeddings',
#         'target_property': target_property,
#         'mae_mean': mae_mean, 'mae_std': mae_std,
#         'rmse_mean': rmse_mean, 'rmse_std': rmse_std,
#         'r2_mean': r2_mean, 'r2_std': r2_std,
#         'n_train': len(y_train_combined), 'n_test': len(X_test)
#     }

# def main():
#     """Main execution function"""
#     print("🚀 Starting Multi-Property Polymer Prediction Experiments")
#     print(f"📊 Train Dataset: {TRAIN_CSV_PATH}")
#     print(f"📊 Test Dataset: {TEST_CSV_PATH}")
#     print(f"🎯 Target Properties: {TARGET_PROPERTIES}")
#     print(f"🔬 Model: GradientBoostingRegressor (default settings)")
#     print(f"🌱 Random Seeds: {RANDOM_SEEDS}")
#     print("="*80)
    
#     # Load datasets
#     train_df, test_df, available_targets = load_datasets()
    
#     # Run experiments for each target property
#     all_results = []
    
#     for target_property in available_targets:
#         logging.info(f"\n{'='*100}")
#         logging.info(f"🎯 PROCESSING TARGET PROPERTY: {target_property}")
#         logging.info(f"{'='*100}")
        
#         # Task 1: Baseline ECFP
#         try:
#             result1 = task1_baseline_ecfp(train_df, test_df, target_property)
#             if result1:
#                 all_results.append(result1)
#         except Exception as e:
#             logging.error(f"Error in Task 1 for {target_property}: {e}")
#             import traceback
#             traceback.print_exc()
        
#         # Task 2: Combined embeddings
#         try:
#             result2 = task2_combined_embeddings(train_df, test_df, target_property)
#             if result2:
#                 all_results.append(result2)
#         except Exception as e:
#             logging.error(f"Error in Task 2 for {target_property}: {e}")
#             import traceback
#             traceback.print_exc()
    
#     # Summary
#     if all_results:
#         logging.info("\n" + "="*100)
#         logging.info("📊 FINAL EXPERIMENT SUMMARY")
#         logging.info("="*100)
        
#         # Group results by target property
#         target_results = {}
#         for result in all_results:
#             target = result['target_property']
#             if target not in target_results:
#                 target_results[target] = []
#             target_results[target].append(result)
        
#         # Display results grouped by target property
#         for target_property, results in target_results.items():
#             logging.info(f"\n🎯 {target_property}:")
#             logging.info("-" * 50)
#             for result in results:
#                 logging.info(f"  {result['task']}:")
#                 logging.info(f"    Training samples: {result['n_train']}")
#                 logging.info(f"    Test samples: {result['n_test']}")
#                 logging.info(f"    MAE:  {result['mae_mean']:.3f} ± {result['mae_std']:.3f}")
#                 logging.info(f"    RMSE: {result['rmse_mean']:.3f} ± {result['rmse_std']:.3f}")
#                 logging.info(f"    R²:   {result['r2_mean']:.3f} ± {result['r2_std']:.3f}")
        
#         # Save results
#         results_df = pd.DataFrame(all_results)
#         timestamp = datetime.now().strftime("%Y%m%d_%H%M")
#         output_csv = f"Multi_Property_Polymer_Prediction_Results_tg_{timestamp}.csv"
#         results_df.to_csv(output_csv, index=False)
        
#         logging.info(f"\n💾 Results saved to: {output_csv}")
        
#         print(f"\n📋 EXPERIMENT COMPLETED:")
#         print(f"Results saved to: {output_csv}")
#         print(f"Total experiments run: {len(all_results)}")
#         print(f"Target properties processed: {len(target_results)}")
#     else:
#         logging.error("No results generated. Check for errors in the experiments.")

# if __name__ == "__main__":
#     main()