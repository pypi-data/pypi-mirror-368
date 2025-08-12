import torch
import torch.nn.functional as F
from torch import nn
import pandas as pd
import numpy as np
from pysr import PySRRegressor
import sympy as sym
from sympy import lambdify
import os

class ResidualConnection(nn.Module):
    """Residual connection for skip connections"""
    def forward(self, x):
        return x

class NeuralTgPredictor(nn.Module):
    """Enhanced neural network component for Tg prediction with improved architecture"""
    def __init__(self, input_dim=10, hidden_dims=[256, 512, 256], dropout_rate=0.2):
        super().__init__()
        self.input_dim = input_dim
        self.hidden_dims = hidden_dims
        
        # Input batch normalization
        self.input_bn = nn.BatchNorm1d(input_dim)
        
        # Create network layers
        layers = []
        prev_dim = input_dim
        
        for hidden_dim in hidden_dims:
            # Dense block
            block = nn.Sequential(
                nn.Linear(prev_dim, hidden_dim),
                nn.BatchNorm1d(hidden_dim),
                nn.ReLU(),
                nn.Dropout(dropout_rate)
            )
            layers.append(block)
            
            # Residual connection if dimensions match
            if prev_dim == hidden_dim:
                layers.append(ResidualConnection())
                
            prev_dim = hidden_dim
        
        # Final output layer
        self.feature_layers = nn.ModuleList(layers)
        self.output_layer = nn.Linear(hidden_dims[-1], 1)
        
        # Initialize weights
        self.apply(self._init_weights)
        
    def _init_weights(self, module):
        """Initialize network weights using He initialization"""
        if isinstance(module, nn.Linear):
            nn.init.kaiming_normal_(module.weight, mode='fan_in', nonlinearity='relu')
            if module.bias is not None:
                nn.init.constant_(module.bias, 0)
                
    def forward(self, x):
        # Input normalization
        x = self.input_bn(x)
        
        # Process through feature layers
        for layer in self.feature_layers:
            x = layer(x)
            
        # Output prediction
        return self.output_layer(x)

class SymbolicTgPredictor:
    """Symbolic regression component for finding analytical Tg expressions"""
    def __init__(self, output_dir="symbolic_results"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self.round_num = 0
        self.model = None
        
    def create_pysr_model(self, round_num):
        """Create PySR model with specified parameters for each round"""
        round_dir = os.path.join(self.output_dir, f"round_{round_num}")
        os.makedirs(round_dir, exist_ok=True)
        
        model_params = {
            'binary_operators': ["+", "*", "-", "/"],
            'unary_operators': ["exp", "square", "log10", "cube"],
            'extra_sympy_mappings': {"inv": lambda x: 1 / x, "sqrt": lambda x: x**0.5},
            'loss': "loss(prediction, target) = abs(prediction - target)",
            'niterations': 1000,
            'early_stop_condition': "stop_if(loss, complexity) = loss < 20 && complexity < 10",
            'populations': 144,
            'batching': True,
            'maxsize': 15,
            'parsimony': 0.0001,
            'weight_optimize': 0.001,
            'bumper': True,
            'adaptive_parsimony_scaling': 1000,
            'precision': 64,
            'equation_file': os.path.join(round_dir, 'equations.csv')
        }
        
        self.model = PySRRegressor(**model_params)
        return self.model
        
    def fit(self, X, y):
        """Fit symbolic regression to neural network outputs"""
        self.round_num += 1
        self.model = self.create_pysr_model(self.round_num)
        return self.model.fit(X, y)

class CoNSALTgPredictor:
    """Combined Neural-Symbolic approach for Tg prediction"""
    def __init__(self, input_dim=50, hidden_dims=[256, 512, 256], output_dir="consal_results_1000", 
                 device='cuda' if torch.cuda.is_available() else 'cpu'):
        self.device = device
        self.neural_model = NeuralTgPredictor(
            input_dim=input_dim,
            hidden_dims=hidden_dims
        ).to(device)
        self.symbolic_model = SymbolicTgPredictor(output_dir=os.path.join(output_dir, "symbolic"))
        self.feature_names = None
        self.current_equation = None
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
    def prepare_data(self, train_path, test_path, features):
        """Prepare data without scaling"""
        self.feature_names = features
        train_data = pd.read_csv(train_path)
        test_data = pd.read_csv(test_path)
        
        X_train = train_data[features].values
        y_train = train_data['Exp_Tg(K)'].values.reshape(-1, 1)
        X_test = test_data[features].values
        y_test = test_data['Exp_Tg(K)'].values.reshape(-1, 1)
        
        return (X_train, y_train), (X_test, y_test)
    
    def train_neural(self, X_train, y_train, epochs=10, batch_size=64, patience=10):
        """Enhanced training procedure with learning rate scheduling and early stopping"""
        optimizer = torch.optim.Adam(self.neural_model.parameters(), lr=0.001, weight_decay=1e-5)
        scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
            optimizer, mode='min', factor=0.5, patience=5, verbose=True
        )
        
        # Convert to tensors
        X = torch.FloatTensor(X_train).to(self.device)
        y = torch.FloatTensor(y_train).to(self.device)
        
        # Create data loader for batch processing
        dataset = torch.utils.data.TensorDataset(X, y)
        dataloader = torch.utils.data.DataLoader(
            dataset, batch_size=batch_size, shuffle=True
        )
        
        # Early stopping setup
        best_loss = float('inf')
        patience_counter = 0
        best_state = None
        
        for epoch in range(epochs):
            self.neural_model.train()
            epoch_losses = []
            
            for batch_X, batch_y in dataloader:
                optimizer.zero_grad()
                
                # Forward pass
                y_pred = self.neural_model(batch_X)
                loss = F.l1_loss(y_pred, batch_y)
                
                # Backward pass with gradient clipping
                loss.backward()
                torch.nn.utils.clip_grad_norm_(self.neural_model.parameters(), max_norm=1.0)
                optimizer.step()
                
                epoch_losses.append(loss.item())
            
            # Calculate average epoch loss
            avg_loss = np.mean(epoch_losses)
            scheduler.step(avg_loss)
            
            # Early stopping check
            if avg_loss < best_loss:
                best_loss = avg_loss
                patience_counter = 0
                best_state = self.neural_model.state_dict()
            else:
                patience_counter += 1
                
            if patience_counter >= patience:
                print(f"Early stopping triggered at epoch {epoch}")
                break
                
            if epoch % 10 == 0:
                print(f"Epoch {epoch}, MAE Loss: {avg_loss:.4f}")
        
        # Restore best model
        if best_state is not None:
            self.neural_model.load_state_dict(best_state)
    
    def find_symbolic_expression(self, X):
        """Use symbolic regression to find analytical expression"""
        self.neural_model.eval()
        with torch.no_grad():
            X_tensor = torch.FloatTensor(X).to(self.device)
            predictions = self.neural_model(X_tensor).cpu().numpy()
        
        # Fit symbolic regression
        self.symbolic_model.fit(X, predictions)
        best_equation = self.symbolic_model.model.equations_.iloc[-1].sympy_format
        self.current_equation = best_equation
        
        return best_equation
    
    def train(self, train_data, test_data, n_iterations=1):
        """Complete training process with neural-symbolic iteration"""
        X_train, y_train = train_data
        X_test, y_test = test_data
        
        for iteration in range(n_iterations):
            print(f"\nIteration {iteration + 1}/{n_iterations}")
            
            # Train neural network
            print("Training neural network...")
            self.train_neural(X_train, y_train)
            
            # Find symbolic expression
            print("Finding symbolic expression...")
            equation = self.find_symbolic_expression(X_train)
            print(f"Found equation: {equation}")
            
            # Evaluate current model
            mae = self.evaluate(X_test, y_test)
            print(f"Test MAE: {mae:.4f}")
    
    def evaluate(self, X, y_true):
        """Evaluate the current model using MAE"""
        if self.current_equation is None:
            return float('inf')
        
        # Create lambda function from symbolic expression
        variables = [sym.Symbol(f'x{i}') for i in range(X.shape[1])]
        f = lambdify(variables, self.current_equation, 'numpy')
        
        # Make predictions
        y_pred = f(*[X[:, i] for i in range(X.shape[1])])
        
        # Calculate MAE
        mae = np.mean(np.abs(y_pred - y_true.flatten()))
        return mae
    
    def predict(self, X):
        """Make predictions using the current symbolic expression"""
        if self.current_equation is None:
            raise ValueError("No symbolic expression has been found yet")
        
        variables = [sym.Symbol(f'x{i}') for i in range(X.shape[1])]
        f = lambdify(variables, self.current_equation, 'numpy')
        
        predictions = f(*[X[:, i] for i in range(X.shape[1])])
        return predictions.reshape(-1, 1)

# Example usage
if __name__ == "__main__":
    # Define features
    # features = [
    #     "sp2_carbon_count_fullpolymerfeaturizer",
    #     "num_rotatable_bonds_fullpolymerfeaturizer",
    #     "num_rings_fullpolymerfeaturizer",
    #     "num_aromatic_rings_fullpolymerfeaturizer",
    #     "bridging_rings_count_fullpolymerfeaturizer",
    #     "balaban_j_index_fullpolymerfeaturizer",
    #     "slogp_vsa1_fullpolymerfeaturizer",
    #     "num_atoms_backbonefeaturizer",
    #     "num_aliphatic_heterocycles_fullpolymerfeaturizer",
    #     "fp_density_morgan1_fullpolymerfeaturizer",
    # ]
    
    # Define features
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
        "double_bonds_fullpolymerfeaturizer",
        "max_estate_index_fullpolymerfeaturizer",
        "topological_surface_area_fullpolymerfeaturizer",
        "smr_vsa5_fullpolymerfeaturizer",
        "sp3_carbon_count_fullpolymerfeaturizer",
        "heteroatom_count_fullpolymerfeaturizer",
        "heteroatom_density_fullpolymerfeaturizer",
        "num_hbond_acceptors_fullpolymerfeaturizer",
        "heteroatom_distance_max_fullpolymerfeaturizer",
        "heteroatom_distance_mean_fullpolymerfeaturizer",
        "heteroatom_distance_sum_fullpolymerfeaturizer",
        "numsidechainfeaturizer",
        "num_atoms_sidechainfeaturizer_min",
        "num_atoms_sidechainfeaturizer_mean",
        "num_hbond_donors_fullpolymerfeaturizer",
        "num_atoms_sidechainfeaturizer_max",
        "fluorine_count_fullpolymerfeaturizer",
        "total_halogens_fullpolymerfeaturizer",
        "single_bonds_fullpolymerfeaturizer",
        "heteroatom_distance_min_fullpolymerfeaturizer",
        "num_atoms_sidechainfeaturizer_sum",
        "bromine_count_fullpolymerfeaturizer",
        "triple_bonds_fullpolymerfeaturizer",
        "chlorine_count_fullpolymerfeaturizer"
    ]
    
    # Initialize predictor with improved architecture
    predictor = CoNSALTgPredictor(
        input_dim=len(features),
        hidden_dims=[256, 512, 256]  # Customizable architecture
    )
    
    # Prepare data
    train_data, test_data = predictor.prepare_data(
        '/home/ta45woj/PolyMetriX/src/polymetrix/sym_datasets/Polymer_Tg_new_featurizers_20_09_2024.csv',
        '/home/ta45woj/PolyMetriX/src/polymetrix/sym_datasets/uncommon_mdpi_trained_set.csv',
        features
    )
    
    # Train model
    predictor.train(train_data, test_data)