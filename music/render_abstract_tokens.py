import json
import sys
import os
from note_token import note_sequence_to_midi

def load_abstracted_tokens(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

def load_tokens(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

def render_representative_token(rep_token, index, tokens, destination, separator=['n_r_64']):
    concatenated_sequence = []
    for token in rep_token['tokens']:
        token_sequence = eval(tokens[token]['seq'])
        concatenated_sequence.extend(token_sequence)
        concatenated_sequence.extend([separator])  # Add 1-measure rest

    # Remove the last separator
    if len(concatenated_sequence) > len(separator):
        concatenated_sequence = concatenated_sequence[:-len(separator)]

    midi_file = os.path.join(destination, f"{index}_{rep_token['name']}.mid")
    note_sequence_to_midi(concatenated_sequence, midi_file)
    print(f"Rendered {rep_token['name']} to {midi_file}")

def render_abstract_tokens(abstracted_tokens_file, tokens_file, destination, top_n):
    abstracted_tokens = load_abstracted_tokens(abstracted_tokens_file)
    tokens = load_tokens(tokens_file)

    # Sort abstracted tokens by collective frequency
    sorted_tokens = sorted(
        [{'name': k, **v} for k, v in abstracted_tokens.items()],
        key=lambda x: x['collective_freq'],
        reverse=True
    )

    # Create destination directory if it doesn't exist
    os.makedirs(destination, exist_ok=True)

    # Render top N representative tokens
    for i, rep_token in enumerate(sorted_tokens[:top_n]):
        render_representative_token(rep_token, i, tokens, destination)

def main():
    if len(sys.argv) != 5:
        print("Usage: python render_abstract_tokens.py path/to/abstracted_tokens.json path/to/tokens/file path/to/destination N")
        sys.exit(1)

    abstracted_tokens_file = sys.argv[1]
    tokens_file = sys.argv[2]
    destination = sys.argv[3]
    top_n = int(sys.argv[4])

    render_abstract_tokens(abstracted_tokens_file, tokens_file, destination, top_n)

if __name__ == "__main__":
    main()
