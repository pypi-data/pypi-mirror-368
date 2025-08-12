import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import ast

# Load the data
data = pd.read_csv(
    "/home/ta45woj/PolyMetriX/src/polymetrix/valid_dataset_20250723_1042_case_study_two_neurips_challenge_dataset_Tg_FFV_unsqueeze_embeddings_ecfp_info_train_test_FFV.csv",
)


# Convert ECFP fingerprint strings to arrays
# Assuming the fingerprints are stored as string representations of lists/arrays
def parse_fingerprint(fp_string):
    """Parse fingerprint string to numpy array"""
    try:
        # If it's a string representation of a list
        if isinstance(fp_string, str):
            # Remove any brackets and split by spaces or commas
            fp_string = fp_string.strip("[]")
            # Try different parsing methods
            if "," in fp_string:
                fp_array = np.array([float(x.strip()) for x in fp_string.split(",")])
            else:
                fp_array = np.array([float(x.strip()) for x in fp_string.split()])
        else:
            # If it's already a numeric type
            fp_array = np.array(fp_string)
        return fp_array
    except:
        # If parsing fails, return None
        return None


# Parse ECFP fingerprints
print("Parsing ECFP fingerprints...")
fingerprints = []
valid_indices = []

for idx, fp in enumerate(data["ecfp_fingerprint"]):
    parsed_fp = parse_fingerprint(fp)
    if parsed_fp is not None:
        fingerprints.append(parsed_fp)
        valid_indices.append(idx)

# Convert to numpy array
fingerprints_array = np.array(fingerprints)
print(f"Successfully parsed {len(fingerprints)} fingerprints")
print(f"Fingerprint dimensions: {fingerprints_array.shape}")

# Standardize the features (optional but recommended for K-means)
scaler = StandardScaler()
fingerprints_scaled = scaler.fit_transform(fingerprints_array)

# Perform K-means clustering with 6 clusters (0-5)
print("Performing K-means clustering...")
kmeans = KMeans(n_clusters=10, random_state=42, n_init=10)
cluster_labels = kmeans.fit_predict(fingerprints_scaled)

# Create cluster labels in the format cluster_0, cluster_1, etc.
cluster_names = [f"cluster_{label}" for label in cluster_labels]

# Add cluster column to the original dataframe
# Initialize all rows with NaN for cluster assignment
data["cluster"] = np.nan
data["cluster"] = data["cluster"].astype("object")

# Assign cluster labels only to rows with valid fingerprints
for i, idx in enumerate(valid_indices):
    data.loc[idx, "cluster"] = cluster_names[i]

# Display cluster distribution
print("\nCluster distribution:")
cluster_counts = data["cluster"].value_counts().sort_index()
for cluster, count in cluster_counts.items():
    print(f"{cluster}: {count} polymers")

# Display some statistics
print(f"\nTotal polymers: {len(data)}")
print(f"Polymers with valid fingerprints: {len(valid_indices)}")
print(f"Polymers without valid fingerprints: {len(data) - len(valid_indices)}")

# Save the updated dataframe
output_path = "/home/ta45woj/PolyMetriX/src/polymetrix/valid_dataset_20250723_1042_case_study_two_neurips_challenge_dataset_Tg_FFV_unsqueeze_embeddings_ecfp_info_train_test_FFV_cluster_info.csv"
data.to_csv(output_path, index=False)
print(f"\nUpdated dataset saved to: {output_path}")

# Display first few rows with cluster assignments
print("\nFirst 10 rows with cluster assignments:")
display_cols = ["psmiles", "polymer_class", "cluster"]
print(data[display_cols].head(10))

# # Optional: Display cluster centers (scaled)
# print("\nCluster centers (first 10 dimensions):")
# for i, center in enumerate(kmeans.cluster_centers_[:, :10]):
#     print(f"cluster_{i}: {center}")
