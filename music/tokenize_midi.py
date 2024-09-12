import os
import sys
import json
from batch import batch_generate_vocab_list_progressive, create_all_note_sequence_tokens

'''
Usage: python3 tokenize_midi.py /path/to/preprocessed/midi/directory /path/to/tokens/directory 
'''

def load_note_sequences(preprocessed_dir):
    all_note_sequences = create_all_note_sequence_tokens(preprocessed_dir)
    return all_note_sequences

def tokenize_midi(preprocessed_dir, tokens_dir, num_merges=500_000, save_every_n_merges=5000):
    print(f"Loading note sequences from {preprocessed_dir}")
    all_note_sequence_tokens = load_note_sequences(preprocessed_dir)
    
    print(f"Generating vocabulary list")
    vocab_list = batch_generate_vocab_list_progressive(
        all_note_sequence_tokens,
        num_merges=num_merges,
        save_every_n_merges=save_every_n_merges,
        tokens_dir=tokens_dir
    )
    
    print(f"Tokenization complete. Tokens saved in {tokens_dir}")
    return vocab_list

def main():
    if len(sys.argv) != 3:
        print("Usage: python tokenize_midi.py /path/to/preprocessed/midi/directory /path/to/tokens/directory")
        sys.exit(1)

    preprocessed_dir = sys.argv[1]
    tokens_dir = sys.argv[2]

    if not os.path.isdir(preprocessed_dir):
        print(f"Error: Preprocessed directory '{preprocessed_dir}' does not exist.")
        sys.exit(1)

    print(f"Tokenizing preprocessed MIDI files from {preprocessed_dir}")
    print(f"Saving tokens to {tokens_dir}")

    tokenize_midi(preprocessed_dir, tokens_dir)

if __name__ == "__main__":
    main()
