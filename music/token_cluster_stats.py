import sys
import os 
import numpy as np
from scipy.cluster.hierarchy import dendrogram, linkage
from scipy.spatial.distance import squareform
import matplotlib.pyplot as plt
from sklearn.manifold import MDS

def load_similarity_matrix(filename):
    data = np.load(filename)
    similarity_matrix = data['similarity_matrix']
    tokens = data['tokens']
    return similarity_matrix, tokens

def cluster_tokens(similarity_matrix):
    # Convert similarity to distance
    distance_matrix = 1 - similarity_matrix
    
    # Perform hierarchical clustering
    linkage_matrix = linkage(squareform(distance_matrix), method='average')
    
    return linkage_matrix, distance_matrix

def plot_dendrogram(tokens, linkage_matrix):
    plt.figure(figsize=(15, 10))
    dendrogram(linkage_matrix, labels=tokens, leaf_rotation=90, leaf_font_size=8)
    plt.title('Hierarchical Clustering Dendrogram')
    plt.xlabel('Token')
    plt.ylabel('Distance')
    plt.tight_layout()
    plt.show()

def plot_2d_clustering(tokens, distance_matrix):
    # Use Multidimensional Scaling to reduce to 2D
    mds = MDS(n_components=2, dissimilarity='precomputed', random_state=42)
    pos = mds.fit_transform(distance_matrix)
    
    plt.figure(figsize=(12, 8))
    plt.scatter(pos[:, 0], pos[:, 1], marker='o')
    
    # Add labels for each point
    for i, token in enumerate(tokens):
        plt.annotate(token, (pos[i, 0], pos[i, 1]), fontsize=8, alpha=0.7)
    
    plt.title('2D Representation of Token Clusters')
    plt.xlabel('Dimension 1')
    plt.ylabel('Dimension 2')
    plt.tight_layout()
    plt.show()

def main():
    if len(sys.argv) != 2:
        print("Usage: python token_cluster_stats.py /path/to/similarity_matrix/file")
        sys.exit(1)

    similarity_matrix_file = sys.argv[1]
    
    if not os.path.isfile(similarity_matrix_file):
        print(f"Error: Similarity matrix file '{similarity_matrix_file}' does not exist.")
        sys.exit(1)

    similarity_matrix, token_list = load_similarity_matrix(similarity_matrix_file)
    linkage_matrix, distance_matrix = cluster_tokens(similarity_matrix)

    plot_dendrogram(token_list, linkage_matrix)
    plot_2d_clustering(token_list, distance_matrix)

if __name__ == "__main__":
    main()