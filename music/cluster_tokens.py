import json
import numpy as np
from scipy.cluster.hierarchy import dendrogram, linkage
from scipy.spatial.distance import squareform
from sklearn.manifold import MDS
import matplotlib.pyplot as plt
from note_token import note_sequence_to_notes
from midi_similarity import compare_midi_sequences
import os

def load_tokens(json_file):
    with open(json_file, 'r') as f:
        return json.load(f)

def create_similarity_matrix(tokens):
    n = len(tokens)
    similarity_matrix = np.zeros((n, n))
    
    for i, (token1, data1) in enumerate(tokens.items()):
        seq1 = eval(data1['seq'])
        for j, (token2, data2) in enumerate(tokens.items()):
            if i < j:
                seq2 = eval(data2['seq'])
                similarity = compare_midi_sequences(seq1, seq2)
                similarity_matrix[i, j] = similarity_matrix[j, i] = similarity
            elif i == j:
                similarity_matrix[i, j] = 1.0  # Self-similarity is 1
    
    return similarity_matrix

def save_similarity_matrix(similarity_matrix, tokens, filename):
    np.savez(filename, similarity_matrix=similarity_matrix, tokens=list(tokens.keys()))
    print(f"Similarity matrix saved to {filename}")

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
    json_file = 'tokens_300.json'
    similarity_file = f'{json_file.split('.')[0].strip()}_similarity_matrix.npz'
    
    tokens = load_tokens(json_file)
    if os.path.exists(similarity_file):
        print("Loading pre-computed similarity matrix...")
        similarity_matrix, token_list = load_similarity_matrix(similarity_file)
    else:
        print("Computing similarity matrix...")
        similarity_matrix = create_similarity_matrix(tokens)
        save_similarity_matrix(similarity_matrix, tokens, similarity_file)
    
    linkage_matrix, distance_matrix = cluster_tokens(similarity_matrix)
    
    plot_dendrogram(list(tokens.keys()), linkage_matrix)
    plot_2d_clustering(list(tokens.keys()), distance_matrix)

if __name__ == "__main__":
    main()
