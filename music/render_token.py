import os
import json
from quantize import quantize_midi
from note_token import midi_to_note_sequence, note_sequence_to_midi
from encoding import serialize, generate_vocab_list, detokenize, deserialize

def render_token(token_file, token_to_render):
    if not os.path.isfile(token_file):
        print("Error: The specified file does not exist.")
        return
    
    # Load the token file
    with open(token_file, 'r') as f:
        token_data = json.load(f)

    if token_to_render not in token_data:
        print("Error: The specified token does not exist in the file.")
        return
    
    # Get note sequence from token file
    note_sequence_str = token_data[token_to_render]['seq']
    note_sequence = eval(note_sequence_str)  # Convert string representation to list

    # Save note sequence to MIDI file
    output_file = f"t_{token_to_render[2:]}.mid"  # Assuming token format is 't_X'
    note_sequence_to_midi(note_sequence, output_file)

    print(f"MIDI file saved as: {output_file}")

def main():
    token_file = input("Enter the path to your token file: ").strip()
    
    if not os.path.isfile(token_file):
        print("Error: The specified file does not exist.")
        return

    # Load the token file
    with open(token_file, 'r') as f:
        token_data = json.load(f)

    # Display available tokens
    print("Available tokens:")
    for token in token_data.keys():
        print(f"{token}: {token_data[token]['seq_len']} tokens freq: {token_data[token]['freq']}")

    # Specify which token to render
    token_to_render = input("Enter the token you want to render into MIDI: ").strip()

    if token_to_render not in token_data:
        print("Error: The specified token does not exist in the file.")
        return

    # Get note sequence from token file
    note_sequence_str = token_data[token_to_render]['seq']
    note_sequence = eval(note_sequence_str)  # Convert string representation to list

    # Save note sequence to MIDI file
    output_file = f"t_{token_to_render[2:]}.mid"  # Assuming token format is 't_X'
    note_sequence_to_midi(note_sequence, output_file)

    print(f"MIDI file saved as: {output_file}")

if __name__ == "__main__":
    main()
