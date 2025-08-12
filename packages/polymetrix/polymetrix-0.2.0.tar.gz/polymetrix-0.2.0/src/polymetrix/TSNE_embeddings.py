import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.manifold import TSNE
import ast
import pandas as pd
data = pd.read_csv('/home/ta45woj/PolyMetriX/src/polymetrix/datasets/valid_dataset_20250626_1016_with_psmiles_bigsmiles_embed_recall.csv')
data

data_train = data[data['recall'] == 1]
data_train

data_test = data[data['recall'] == 0]
data_test

# Set seaborn style and color palette
sns.set_style("whitegrid")
sns.set_palette("Set2")  # Nice color palette
plt.rcParams['figure.facecolor'] = 'white'

# Load the datasets
# data_train = pd.read_csv('/home/ta45woj/PolyMetriX/src/polymetrix/datasets/valid_dataset_20250626_1016_with_psmiles_bigsmiles_embed_tg_train.csv')
# data_test = pd.read_csv('/home/ta45woj/PolyMetriX/src/polymetrix/datasets/valid_dataset_20250626_1016_with_psmiles_bigsmiles_embed_tg_test.csv')
# data_train = pd.read_csv('/home/ta45woj/PolyMetriX/src/polymetrix/datasets/valid_dataset_20250626_1016_with_psmiles_polymername_embed_tg_train.csv')
# data_test = pd.read_csv('/home/ta45woj/PolyMetriX/src/polymetrix/datasets/valid_dataset_20250626_1016_with_psmiles_polymername_embed_tg_test.csv')
data_train = data_train
data_test = data_test
print(f"Train data shape: {data_train.shape}")
print(f"Test data shape: {data_test.shape}")

def parse_embedding(embedding_str):
    """Parse embedding string to numpy array"""
    if isinstance(embedding_str, str):
        # Remove 'tensor(' and ')' if present, then parse as list
        embedding_str = embedding_str.replace('tensor(', '').replace(')', '')
        return np.array(ast.literal_eval(embedding_str))
    return np.array(embedding_str)

def process_embeddings(data, label):
    """Process embeddings and concatenate them"""
    embeddings = []
    valid_indices = []
    
    for i, row in data.iterrows():
        try:
            psmiles_embed = parse_embedding(row['psmiles_embed'])
            bigsmiles_embed = parse_embedding(row['bigsmiles_embed'])
            # bigsmiles_embed = parse_embedding(row['polymer_name_embed'])
            
            # Concatenate the embeddings
            concat_embed = np.concatenate([psmiles_embed, bigsmiles_embed])
            embeddings.append(concat_embed)
            valid_indices.append(i)
        except Exception as e:
            print(f"Skipping row {i} due to parsing error: {e}")
    
    embeddings = np.array(embeddings)
    print(f"{label} - Valid embeddings: {len(embeddings)}, Embedding dimension: {embeddings.shape[1] if len(embeddings) > 0 else 0}")
    
    return embeddings, valid_indices

# Process train and test embeddings
print("Processing train embeddings...")
train_embeddings, train_indices = process_embeddings(data_train, "Train")

print("Processing test embeddings...")
test_embeddings, test_indices = process_embeddings(data_test, "Test")

# Combine all embeddings for t-SNE
all_embeddings = np.vstack([train_embeddings, test_embeddings])
labels = ['Train'] * len(train_embeddings) + ['Test'] * len(test_embeddings)

print(f"Combined embeddings shape: {all_embeddings.shape}")

# Apply t-SNE
print("Applying t-SNE...")
tsne = TSNE(n_components=2, random_state=42, perplexity=30, n_iter=1000)
embeddings_2d = tsne.fit_transform(all_embeddings)

# Create DataFrame for seaborn plotting
tsne_df = pd.DataFrame({
    'TSNE1': embeddings_2d[:, 0],
    'TSNE2': embeddings_2d[:, 1],
    'Dataset': labels
})

# Create the plot with seaborn
plt.figure(figsize=(12, 8))

# Use seaborn scatterplot with nice styling
sns.scatterplot(data=tsne_df, x='TSNE1', y='TSNE2', hue='Dataset', 
                s=60, alpha=0.7, edgecolor='white', linewidth=0.5)

# Customize the plot
plt.xlabel('t-SNE Component 1', fontsize=12)
plt.ylabel('t-SNE Component 2', fontsize=12)
plt.title('t-SNE Visualization of Concatenated psmiles + bigsmiles Embeddings', 
          fontsize=14, pad=20)

# Customize legend
legend = plt.legend(title='Dataset', title_fontsize=12, fontsize=11, 
                   frameon=True, fancybox=True, shadow=True)
legend.get_frame().set_facecolor('white')
legend.get_frame().set_alpha(0.9)

# Add count information to legend labels
handles, labels = plt.gca().get_legend_handles_labels()
new_labels = [f'{label} (n={len(train_embeddings)})' if label == 'Train' 
              else f'{label} (n={len(test_embeddings)})' for label in labels]
plt.legend(handles, new_labels, title='Dataset', title_fontsize=12, fontsize=11,
           frameon=True, fancybox=True, shadow=True)

# Remove top and right spines for cleaner look
sns.despine()

# Add some statistics as text box
stats_text = f'Embedding dimension: {all_embeddings.shape[1]}\nTotal samples: {len(all_embeddings)}'
plt.text(0.02, 0.98, stats_text, transform=plt.gca().transAxes, 
         fontsize=10, verticalalignment='top',
         bbox=dict(boxstyle='round', facecolor='lightgray', alpha=0.8))

plt.tight_layout()
plt.show()

# Save the plot
plt.savefig('/home/ta45woj/PolyMetriX/src/polymetrix/datasets//tsne_concatenated_embeddings_seaborn.png', dpi=300, bbox_inches='tight', 
            facecolor='white', edgecolor='none')
print("Plot ready to be saved as 'tsne_concatenated_embeddings_seaborn.png'")

# # Optional: Print some statistics
# print(f"\nStatistics:")
# print(f"Train embeddings: {len(train_embeddings)}")
# print(f"Test embeddings: {len(test_embeddings)}")
# print(f"Total valid embeddings: {len(all_embeddings)}")
# print(f"Embedding dimension: {all_embeddings.shape[1]}")

# # Additional visualization: Distribution plots
# fig, axes = plt.subplots(1, 2, figsize=(15, 5))

# # Distribution of TSNE1
# sns.histplot(data=tsne_df, x='TSNE1', hue='Dataset', alpha=0.6, kde=True, ax=axes[0])
# axes[0].set_title('Distribution of t-SNE Component 1', fontweight='bold')
# axes[0].set_xlabel('t-SNE Component 1')

# # Distribution of TSNE2
# sns.histplot(data=tsne_df, x='TSNE2', hue='Dataset', alpha=0.6, kde=True, ax=axes[1])
# axes[1].set_title('Distribution of t-SNE Component 2', fontweight='bold')
# axes[1].set_xlabel('t-SNE Component 2')

# plt.tight_layout()
# plt.show()