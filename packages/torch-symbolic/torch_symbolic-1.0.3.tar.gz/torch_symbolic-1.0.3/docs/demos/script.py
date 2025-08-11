import torch
import numpy as np
import torch.nn as nn


import sys
sys.path.append('../../src')

from symtorch.toolkit import Pruning_MLP
from symtorch.mlp_sr import MLP_SR

class MLP(nn.Module):
    """
    Simple MLP.
    """
    def __init__(self, input_dim, output_dim, hidden_dim):
        super(MLP, self).__init__()
        self.mlp = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, output_dim)
        )

    def forward(self, x):
        return self.mlp(x)

class SimpleModel(nn.Module):
    """
    Model with MLP f (to be pruned to 2 dims) and linear g_net.
    """
    def __init__(self, input_dim, g_vars_dim, output_dim, output_dim_f=32, hidden_dim=128):
        super(SimpleModel, self).__init__()

        self.f = MLP(input_dim, output_dim_f, hidden_dim)
        # g is linear - only learns to combine the 2 pruned outputs from f
        self.g_net = nn.Linear(output_dim_f, output_dim)  # Will use first 2 dims of f after pruning

    def forward(self, x, g_vars=None):
        f_output = self.f(x)
        # Use only first 2 dimensions for g_net (these should be pruned/learned features)
        return self.g_net(f_output)
    
# Make the dataset 
x = np.array([np.random.uniform(0, 1, 10_000) for _ in range(5)]).T

def f_func(x):
    """Ground truth feature functions: f0 = x0^2, f1 = sin(x4)"""
    f0 = x[:, 0]**2  # x0^2
    f1 = np.sin(x[:, 4])  # sin(x4)
    return np.stack([f0, f1], axis=1)

def g_func(f_output):
    """Ground truth linear combination: y = a*f0 + b*f1"""
    # Use specific coefficients that g_net should learn
    a, b = 2.5, -1.3  # Linear coefficients for the combination
    return a * f_output[:, 0] + b * f_output[:, 1]

# Generate ground truth data
f_true = f_func(x)
y = g_func(f_true)

noise = np.array([np.random.normal(0, 0.05*np.std(y)) for _ in range(len(y))])
y = y + noise 

# Create model with pruning for f, linear g_net
model = SimpleModel(input_dim=x.shape[1], g_vars_dim=0, output_dim=1, output_dim_f=32)
model.f = Pruning_MLP(model.f,
                      initial_dim=32, # Initial dimensionality of the MLP
                      target_dim=2    # Target dimensionality - final output dim after pruning
                      )

# Wrap g_net with MLP_SR for symbolic regression
model.g_net = MLP_SR(model.g_net, mlp_name="g_net")

# Set up the pruning schedule
epochs = 100
model.f.set_schedule(total_epochs=epochs, 
                     end_epoch_frac=0.7 # End pruning after 70% of epochs
                     )


# Set up training

import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
from sklearn.model_selection import train_test_split

def train_model(model, dataloader, X_val, y_val, opt, criterion, epochs=100):
    """
    Train model with MLP f (with pruning) and linear g_net.
    
    Args:
        model: PyTorch model to train
        dataloader: DataLoader for training data
        X_val, y_val: Validation data for pruning
        opt: Optimizer
        criterion: Loss function
        epochs: Number of training epochs
        
    Returns:
        tuple: (trained_model, loss_tracker, active_dims_tracker)
    """
    loss_tracker = []
    active_dims_tracker = []
    
    for epoch in range(epochs):
        epoch_loss = 0.0
        
        for batch_x, batch_y in dataloader:
            # Forward pass
            pred = model(batch_x)
            main_loss = criterion(pred, batch_y)
            
            # # Intermediate supervision: f should learn f_func in first 2 dimensions
            # f_pred = model.f(batch_x)
            # f_true = torch.FloatTensor(f_func(batch_x.numpy()))
            
            # # Only supervise the first 2 dimensions of f's output
            # f_pred_target = f_pred[:, :2]  # First 2 dimensions
            # intermediate_loss = criterion(f_pred_target, f_true)
            
            # # Combined loss
            # loss = main_loss + 0.7 * intermediate_loss 
            loss = main_loss
            # Backward pass
            opt.zero_grad()
            loss.backward()
            opt.step()
            
            epoch_loss += loss.item()
        
        loss_tracker.append(epoch_loss)
        active_dims_tracker.append(model.f.pruning_mask.sum().item())
        
        # Create validation data for pruning
        val_x_tensor = torch.FloatTensor(X_val)
        val_y_tensor = torch.FloatTensor(y_val)
        val_dataset = TensorDataset(val_x_tensor, val_y_tensor)
        val_dataloader = DataLoader(val_dataset, batch_size=32, shuffle=False)
        
        model.f.prune(epoch, val_x_tensor)

        if (epoch + 1) % 10 == 0:
            avg_loss = epoch_loss / len(dataloader)
            active_dims = model.f.pruning_mask.sum().item()
            print(f'Epoch [{epoch+1}/{epochs}], Avg Loss: {avg_loss:.6f}, Active dims: {active_dims}')
            
    return model, loss_tracker, active_dims_tracker

# Set up training
criterion = nn.MSELoss()
opt = optim.Adam(model.parameters(), lr=0.001)
# Split data
X_train, X_val, y_train, y_val = train_test_split(
    x, y.reshape(-1,1), test_size=0.1, random_state=290402)

# Set up dataset - only x as input now
dataset = TensorDataset(torch.FloatTensor(X_train), torch.FloatTensor(y_train))
dataloader = DataLoader(dataset, batch_size=32, shuffle=True)


# Train the model and save the weights
print("Starting training...")
model, losses, active_dims = train_model(model, dataloader, X_val, y_val, opt, criterion, 100)
print("Training completed!")
torch.save(model.state_dict(), 'model_weights.pth')

# Print learned coefficients  
# print(f"\nLearned g_net weights: {model.g_net.weight.data.numpy()}")
# print(f"Learned g_net bias: {model.g_net.bias.data.numpy()}")
# print(f"Ground truth coefficients: a=2.5, b=-1.3")

# Test the model
with torch.no_grad():
    test_x = torch.FloatTensor(X_val)
    pred_y = model(test_x)
    test_loss = nn.MSELoss()(pred_y, torch.FloatTensor(y_val))
    print(f"Test loss: {test_loss.item():.6f}")

# Check how well f learned the target functions
with torch.no_grad():
    f_pred = model.f(torch.FloatTensor(X_val))
    f_true = torch.FloatTensor(f_func(X_val))
    f_loss = nn.MSELoss()(f_pred[:, :2], f_true)
    print(f"F approximation loss (first 2 dims): {f_loss.item():.6f}")

# print(f"\nFinal active dimensions in f: {model.f.pruning_mask.sum().item()}")
# print(f"g_net learned: {model.g_net.weight.data.numpy()[0][0]:.3f} * f0 + {model.g_net.weight.data.numpy()[0][1]:.3f} * f1 + {model.g_net.bias.data.numpy()[0]:.3f}")

# Now run symbolic regression on the pruned f network
print("\nRunning symbolic regression on pruned f...")
model.f.interpret(torch.FloatTensor(X_train), 
                       niterations=100,
                       complexity_of_operators={"sin":3, "exp":3}, 
                       constraints={"sin": 3, "exp":3},
                       complexity_of_constants=2,
                       parsimony=0.1)

# Run symbolic regression on g_net using parent_model to get correct intermediate inputs
print("\nRunning symbolic regression on g_net...")
model.g_net.interpret(torch.FloatTensor(X_train), 
                     parent_model=model,
                     niterations=100,
                     complexity_of_operators={"sin":3, "exp":3}, 
                     constraints={"sin": 3, "exp":3},
                     complexity_of_constants=2,
                     parsimony=0.1)



