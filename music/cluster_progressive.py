import json
import numpy as np
from scipy.cluster.hierarchy import dendrogram, linkage, fcluster
from scipy.spatial.distance import squareform
import os
import time
from midi_similarity import compare_midi_sequences

def load_tokens(json_file):
    with open(json_file, 'r') as f:
        return json.load(f)

def create_similarity_matrix(tokens, similarity_file, checkpoint_interval=100):
    n = len(tokens)
    token_list = list(tokens.keys())
    
    # Check if there's a partial similarity matrix
    if os.path.exists(similarity_file):
        print("Loading partial similarity matrix...")
        data = np.load(similarity_file)
        similarity_matrix = data['similarity_matrix']
        completed_rows = data['completed_rows']
        start_row = completed_rows
    else:
        similarity_matrix = np.zeros((n, n))
        start_row = 0
        completed_rows = 0

    print(f"Starting from row {start_row}")
    
    try:
        for i in range(start_row, n):
            seq1 = eval(tokens[token_list[i]]['seq'])
            for j in range(i+1, n):
                seq2 = eval(tokens[token_list[j]]['seq'])
                similarity = compare_midi_sequences(seq1, seq2)
                similarity_matrix[i, j] = similarity_matrix[j, i] = similarity
            
            similarity_matrix[i, i] = 1.0  # Self-similarity is 1
            completed_rows = i + 1
            
            if (i + 1) % checkpoint_interval == 0:
                save_similarity_matrix(similarity_matrix, token_list, similarity_file, completed_rows)
                print(f"Checkpoint saved at row {i+1}/{n}")
            
    except KeyboardInterrupt:
        print("\nInterrupted. Saving progress...")
    finally:
        save_similarity_matrix(similarity_matrix, token_list, similarity_file, completed_rows)
        print(f"Progress saved. Completed {completed_rows}/{n} rows.")
    
    return similarity_matrix

def save_similarity_matrix(similarity_matrix, tokens, filename, completed_rows):
    np.savez(filename, similarity_matrix=similarity_matrix, tokens=tokens, completed_rows=completed_rows)

def load_similarity_matrix(filename):
    data = np.load(filename)
    return data['similarity_matrix'], data['tokens'], data['completed_rows']

def cluster_tokens(similarity_matrix, distance_threshold=0.5):
    distance_matrix = 1 - similarity_matrix
    linkage_matrix = linkage(squareform(distance_matrix), method='average')
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
        similarity_matrix, _, completed_rows = load_similarity_matrix(similarity_file)
        if completed_rows == len(tokens):
            print("Loading complete pre-computed similarity matrix...")
        else:
            print(f"Resuming similarity matrix computation from row {completed_rows}...")
            similarity_matrix = create_similarity_matrix(tokens, similarity_file)
    else:
        print("Computing similarity matrix...")
        similarity_matrix = create_similarity_matrix(tokens, similarity_file)
    
    # Perform clustering
    clusters = cluster_tokens(similarity_matrix)
    
    # Create abstracted tokens
    abstracted_tokens = create_abstracted_tokens(tokens, clusters)
    
    # Save abstracted tokens
    save_abstracted_tokens(abstracted_tokens, abstracted_file)
    
    # Print some statistics
    print(f"Number of original tokens: {len(tokens)}")
    print(f"Number of abstracted token groups: {len(abstracted_tokens)}")

if __name__ == "__main__":
    main()
