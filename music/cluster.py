import json
import numpy as np
from scipy.cluster.hierarchy import dendrogram, linkage, fcluster
from scipy.spatial.distance import squareform
from sklearn.manifold import MDS
import matplotlib.pyplot as plt
import os
from midi_similarity import compare_midi_sequences

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

def cluster_tokens(similarity_matrix, distance_threshold=0.5):
    distance_matrix = 1 - similarity_matrix
    linkage_matrix = linkage(squareform(distance_matrix), method='average')
    
    # Perform clustering
    clusters = fcluster(linkage_matrix, t=distance_threshold, criterion='distance')
    
    return clusters

def create_abstracted_tokens(tokens, clusters):
    abstracted_tokens = {}
    for cluster_id in np.unique(clusters):
        cluster_tokens = [list(tokens.keys())[i] for i, c in enumerate(clusters) if c == cluster_id]
        collective_freq = sum(tokens[t]['freq'] for t in cluster_tokens)
        abstracted_tokens[f"r_{cluster_id}"] = {
            "collective_freq": collective_freq,
            "tokens": cluster_tokens
        }
    return abstracted_tokens

def save_abstracted_tokens(abstracted_tokens, filename):
    with open(filename, 'w') as f:
        json.dump(abstracted_tokens, f, indent=2)
    print(f"Abstracted tokens saved to {filename}")

def main():
    json_file = 'tokens_300.json'
    similarity_file = 'similarity_matrix.npz'
    abstracted_file = 'abstracted_tokens.json'
    
    tokens = load_tokens(json_file)
    
    if os.path.exists(similarity_file):
        print("Loading pre-computed similarity matrix...")
        similarity_matrix, _ = load_similarity_matrix(similarity_file)
    else:
        print("Computing similarity matrix...")
        similarity_matrix = create_similarity_matrix(tokens)
        save_similarity_matrix(similarity_matrix, tokens, similarity_file)
    
    # Perform clustering
    clusters = cluster_tokens(similarity_matrix, distance_threshold=0.3)
    
    # Create abstracted tokens
    abstracted_tokens = create_abstracted_tokens(tokens, clusters)
    
    # Save abstracted tokens
    save_abstracted_tokens(abstracted_tokens, abstracted_file)
    
    # Print some statistics
    print(f"Number of original tokens: {len(tokens)}")
    print(f"Number of abstracted token groups: {len(abstracted_tokens)}")

if __name__ == "__main__":
    main()
