import os
import json
from note_token import midi_to_note_sequence
from encoding import generate_vocab_list, expand_token, deserialize, serialize

def preprocess_midi(midi_dir, processed_midi_dir = "processed_midi"):
    '''
    Get midi files and tokenize all of them
    
    midi_dir: directory that has all midi files
    '''

    # Create output directory for processed midi data
    output_dir = os.path.join(os.path.dirname(midi_dir), processed_midi_dir)
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

def create_all_note_sequence_tokens(processed_midi_dir, separator="|"):
    '''
    Creates a list of all note sequence tokens from processed MIDI files,
    with separators between different sequences.
    
    Args:
    processed_midi_dir (str): Path to the directory containing processed MIDI data
    separator (str): Token used to separate different note sequences
    
    Returns:
    list: A list of all note sequence tokens, including separators
    '''
    all_note_sequence_tokens = []

    # For each midi folder in processed_midi_dir
    for midi_folder in os.listdir(processed_midi_dir):
        folder_path = os.path.join(processed_midi_dir, midi_folder)
        
        if os.path.isdir(folder_path):
            # Find the *_seq.json file in the folder
            seq_file = next((f for f in os.listdir(folder_path) if f.endswith('_seq.json')), None)
            
            if seq_file:
                seq_file_path = os.path.join(folder_path, seq_file)
                
                # Read the note sequence from the JSON file
                with open(seq_file_path, 'r') as f:
                    data = json.load(f)
                    note_sequence = eval(data['seq'])  # Convert string representation to list
                
                # Serialize the note sequence
                serialized_sequence = serialize(note_sequence)
                
                # Add each element of note sequence to all_note_sequence_tokens
                all_note_sequence_tokens.extend(serialized_sequence)
                
                # Add separator to distinguish different note sequences
                all_note_sequence_tokens.append(separator)
    
    # Remove the last separator if it exists
    if all_note_sequence_tokens and all_note_sequence_tokens[-1] == separator:
        all_note_sequence_tokens.pop()

    return all_note_sequence_tokens

def batch_generate_vocab_list(all_note_sequence_tokens: list[str], num_merges, save_every_n_merges: int = 20, separator = "|"):
    '''
    Generates vocabulary list in batches and saves intermediate results.

    Args:
    all_note_sequence_tokens: multiple note sequences in one array, separated by separator token
    num_merges: total number of merges to perform
    save_every_n_merges: frequency of saving intermediate results
    separator: token used to separate different note sequences

    Returns:
    dict: The final vocabulary list
    '''
    vocab_list = {char: [char] for char in set(all_note_sequence_tokens)}
    token_count = 1
    freq = {}

    # Create tokens directory if it doesn't exist
    os.makedirs('tokens', exist_ok=True)

    print(all_note_sequence_tokens)
    for merge_count in range(1, num_merges + 1):
        new_vocab, all_note_sequence_tokens, new_freq = generate_vocab_list(
            all_note_sequence_tokens, 
            num_merges = 1, 
            vocab_list=vocab_list, 
            separator = separator, 
            token_count_start = token_count
        )

        if new_freq == {}: # if no more merges, break
            break
        vocab_list.update(new_vocab)
        freq.update(new_freq)
        token_count += 1

        print(all_note_sequence_tokens)
        print(freq)

        if merge_count % save_every_n_merges == 0:
            print(vocab_list)
            save_vocab(vocab_list, freq, merge_count)

    
    # Save final result
    save_vocab(vocab_list, freq, token_count - 1)

    return vocab_list

def save_vocab(vocab_list, freq, merge_count):
    output = {}
    for token, expansion in vocab_list.items():
        if token.startswith('t_'):
            expanded_tokens = expand_token(token, vocab_list)
            seq = deserialize(expanded_tokens)
            output[token] = {
                "freq": freq.get(token, 1),  # Default to 1 if not found
                "tokens": str(expansion),
                "seq": str(seq),
                "seq_len": len(seq)
            }

    filename = f'tokens/tokens_{merge_count}.json'
    with open(filename, 'w') as f:
        json.dump(output, f, indent=2)
    print(f"Saved vocabulary at {merge_count} merges to {filename}")



   

def main():
    # # Get directory that has all midi files
    # midi_dir = input("Enter the directory containing MIDI files: ").strip()
    # if not os.path.isdir(midi_dir):
    #     print(f"Error: The directory {midi_dir} does not exist.")
    #     return
    # preprocess_midi(midi_dir)

    # processed_midi_dir = "./processed_midi"  # Replace with your actual directory path
    # tokens = create_all_note_sequence_tokens(processed_midi_dir)
    # print(f"Total tokens: {len(tokens)}")
    # print(f"First few tokens: {tokens[:10]}")
    # print(f"Last few tokens: {tokens[-10:]}")

    # Test batch_generate_vocab_list
    all_tokens = ["['n_60_4']", "['n_62_4']", "['n_64_4', 'n_67_4']", "['n_r_4']", "['n_69_8']", "|",
                  "['n_60_4']", "['n_62_4']", "['n_64_4', 'n_67_4']", "['n_r_4']", "['n_69_8']"]
    final_vocab = batch_generate_vocab_list(all_tokens, num_merges=40, save_every_n_merges=20)
    print("Final vocabulary size:", len(final_vocab))

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