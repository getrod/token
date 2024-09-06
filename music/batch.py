import os
import json
from quantize import quantize_midi
from note_token import midi_to_note_sequence

def preprocess_midi(midi_dir):
    '''
    Get midi files and tokenize all of them
    
    midi_dir: directory that has all midi files
    '''

    # Create output directory for processed midi data
    output_dir = os.path.join(os.path.dirname(midi_dir), "processed_midi")
    os.makedirs(output_dir, exist_ok=True)

    # For each midi file in directory
    for filename in os.listdir(midi_dir):
        if filename.endswith(".mid") or filename.endswith(".midi"):
            midi_path = os.path.join(midi_dir, filename)
            midi_name = os.path.splitext(filename)[0]
            
            # Create a new directory in output directory with name <midi_file_name>
            midi_output_dir = os.path.join(output_dir, midi_name)
            os.makedirs(midi_output_dir, exist_ok=True)

            # Create <midi_file_name>_quantized.mid file by calling quantize_midi
            # Convert <midi_file_name> into note sequence tokens
            quantized_midi_path = os.path.join(midi_output_dir, f"{midi_name}_quantized.mid")
            note_sequence = midi_to_note_sequence(midi_path, quantize_midi_file_name=quantized_midi_path)

            # Save note sequence tokens in <midi_file_name>_seq.json
            seq_json_path = os.path.join(midi_output_dir, f"{midi_name}_seq.json")
            with open(seq_json_path, 'w') as f:
                json.dump({"seq": str(note_sequence)}, f, indent=2)

            print(f"Processed {filename}")

    print("Preprocessing complete.")

def batch_generate_vocab_list(all_note_sequence_tokens: list[str], separator: str = "|", save_every_n_merge: int = 20):
    '''
    all_note_sequence_tokens: multiple note sequences in one array, separated by separator token ie. "|"

    save_every_n_merge: save tokens_<merge_count>.json. This file has the format:
    {
        name: 't_3',
        freq: 127,
        tokens: "['t_1', "['n_69_8']"]",
        seq: "[['n_64_4', 'n_67_4'], ['n_r_4'], ['n_69_8']]",
        seq_len: 3,
    }
    '''
    pass

def main():
    # Get directory that has all midi files
    midi_dir = input("Enter the directory containing MIDI files: ").strip()
    if not os.path.isdir(midi_dir):
        print(f"Error: The directory {midi_dir} does not exist.")
        return
    preprocess_midi(midi_dir)

if __name__ == "__main__":
    main()
    


# Implement the following function:

# ```
# def preprocess_midi():
#     # get directory that has all midi files

#     # create output directory for processed midi data

#     # for each midi file in directory 
#         # create a new directory in output directory with name <midi_file_name>. Create the following files in this directory
#             # create <midi_file_name>_quantized.mid file by calling quantize_midi
#             # get convert <midi_file_name> into note sequence tokens and save them in <midi_file_name>_seq.json
#                 # midi_file_name>_seq.json has the following format:
#                 '''
#                 {
#                     "seq": "[['n_60_4'], ['n_62_4'], ['n_64_4', 'n_67_4'], ['n_r_4'], ['n_69_8']]" // str(note_sequence)
#                 }
#                 '''
# ```