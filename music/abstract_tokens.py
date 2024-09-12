import os
import sys
from cluster_progressive import load_tokens, load_similarity_matrix, create_similarity_matrix, cluster_tokens, create_abstracted_tokens, save_abstracted_tokens
def abstract_tokens(token_file, output_dir):
    tokens = load_tokens(token_file)
    similarity_file = os.path.join(output_dir, 'similarity_matrix.npz')
    abstracted_file = os.path.join(output_dir, 'abstracted_tokens.json')
    
    if os.path.exists(similarity_file):
        print("Loading pre-computed similarity matrix...")
        similarity_matrix, _ = load_similarity_matrix(similarity_file)
    else:
        print("Computing similarity matrix...")
        similarity_matrix = create_similarity_matrix(tokens, similarity_file)
    
    print("Performing clustering...")
    clusters = cluster_tokens(similarity_matrix, distance_threshold=0.2)
    
    print("Creating abstracted tokens...")
    abstracted_tokens = create_abstracted_tokens(tokens, clusters)
    
    print("Saving abstracted tokens...")
    save_abstracted_tokens(abstracted_tokens, abstracted_file)
    
    print(f"Number of original tokens: {len(tokens)}")
    print(f"Number of abstracted token groups: {len(abstracted_tokens)}")

def main():
    if len(sys.argv) != 3:
        print("Usage: python abstract_tokens.py /path/to/token/file /path/to/save/abstracted/tokens")
        sys.exit(1)

    token_file = sys.argv[1]
    output_dir = sys.argv[2]

    if not os.path.isfile(token_file):
        print(f"Error: Token file '{token_file}' does not exist.")
        sys.exit(1)

    os.makedirs(output_dir, exist_ok=True)

    print(f"Abstracting tokens from {token_file}")
    print(f"Saving results to {output_dir}")

    abstract_tokens(token_file, output_dir)

if __name__ == "__main__":
    main()