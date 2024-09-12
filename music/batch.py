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
        try: 
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
        except:
            print(f'Skipping: {filename}')
            pass

    print("Preprocessing complete.")

def create_all_note_sequence_tokens(processed_midi_dir, separator="|"):
    '''
    Creates a list of all note sequence tokens from processed MIDI files,
    with separators between different sequences.
    
    Args:
    processed_midi_dir (str): Path to the directory containing processed MIDI data
    separator (str): Token used to separate different note sequences
    
    Returns:
    list: A list of all note sequence string tokens, including separators
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

def batch_generate_vocab_list(all_note_sequence_tokens: list[str], num_merges, save_every_n_merges: int = 500, separator = "|", tokens_dir = "tokens"):
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
    os.makedirs(tokens_dir, exist_ok=True)

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

        if merge_count % save_every_n_merges == 0:
            save_vocab(vocab_list, freq, merge_count)

    
    # Save final result
    save_vocab(vocab_list, freq, token_count - 1)

    return vocab_list

def save_vocab(vocab_list, freq, merge_count, tokens_dir = "tokens"):
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

    filename = f'{tokens_dir}/tokens_{merge_count}.json'
    with open(filename, 'w') as f:
        json.dump(output, f, indent=2)
    print(f"Saved vocabulary at {merge_count} merges to {filename}")


def batch_generate_vocab_list_progressive(all_note_sequence_tokens: list[str], num_merges, save_every_n_merges: int = 500, separator = "|", tokens_dir = "tokens"):
    '''
    Generates vocabulary list in batches and saves intermediate results.
    Can resume from the last saved state.

    Args:
    all_note_sequence_tokens: multiple note sequences in one array, separated by separator token
    num_merges: total number of merges to perform
    save_every_n_merges: frequency of saving intermediate results
    separator: token used to separate different note sequences
    tokens_dir: directory to save token files

    Returns:
    dict: The final vocabulary list
    '''
    # Create tokens directory if it doesn't exist
    os.makedirs(tokens_dir, exist_ok=True)

    # Check for the latest saved state
    saved_files = [f for f in os.listdir(tokens_dir) if f.startswith('tokens_') and f.endswith('.json')]
    if saved_files:
        latest_file = max(saved_files, key=lambda x: int(x.split('_')[1].split('.')[0]))
        last_merge_count = int(latest_file.split('_')[1].split('.')[0])
        
        print(f"Resuming from merge count {last_merge_count}")
        
        # Load the latest state
        with open(os.path.join(tokens_dir, latest_file), 'r') as f:
            saved_state = json.load(f)
        
        vocab_list = {k: v['tokens'] for k, v in saved_state.items()}
        freq = {k: v['freq'] for k, v in saved_state.items()}
        token_count = last_merge_count + 1
        
        # Reconstruct all_note_sequence_tokens
        all_note_sequence_tokens = reconstruct_tokens(vocab_list, all_note_sequence_tokens)
    else:
        print("Starting from scratch")
        vocab_list = {char: [char] for char in set(all_note_sequence_tokens)}
        freq = {}
        token_count = 1
        last_merge_count = 0

    for merge_count in range(last_merge_count + 1, num_merges + 1):
        new_vocab, all_note_sequence_tokens, new_freq = generate_vocab_list(
            all_note_sequence_tokens, 
            num_merges = 1, 
            vocab_list=vocab_list, 
            separator = separator, 
            token_count_start = token_count
        )

        if new_freq == {}: # if no more merges, break
            print(f"No more merges possible. Stopped at merge count {merge_count - 1}")
            break
        
        vocab_list.update(new_vocab)
        freq.update(new_freq)
        token_count += 1

        if merge_count % save_every_n_merges == 0:
            save_vocab(vocab_list, freq, merge_count, tokens_dir)
            print(f"Saved state at merge count {merge_count}")

    # Save final result
    save_vocab(vocab_list, freq, token_count - 1, tokens_dir)
    print(f"Final state saved at merge count {token_count - 1}")

    return vocab_list

def reconstruct_tokens(vocab_list, original_tokens):
    """
    Reconstruct the token list based on the vocabulary list and original tokens.
    This is needed when resuming from a saved state.
    """
    reconstructed = []
    for token in original_tokens:
        if token in vocab_list:
            reconstructed.append(token)
        else:
            reconstructed.extend(vocab_list[token])
    return reconstructed

def main():
    # # Get directory that has all midi files
    # midi_dir = input("Enter the directory containing MIDI files: ").strip()
    # if not os.path.isdir(midi_dir):
    #     print(f"Error: The directory {midi_dir} does not exist.")
    #     return
    # preprocess_midi(midi_dir)

    processed_midi_dir = "./processed_midi"  # Replace with your actual directory path
    tokens = create_all_note_sequence_tokens(processed_midi_dir)
    # print(f"Total tokens: {len(tokens)}")
    # print(f"First few tokens: {tokens[:10]}")
    # print(f"Last few tokens: {tokens[-10:]}")

    # Test batch_generate_vocab_list
    # all_tokens = ["['n_60_4']", "['n_62_4']", "['n_64_4', 'n_67_4']", "['n_r_4']", "['n_69_8']", "|",
    #               "['n_60_4']", "['n_62_4']", "['n_64_4', 'n_67_4']", "['n_r_4']", "['n_69_8']"]
    final_vocab = batch_generate_vocab_list(tokens, num_merges=300, save_every_n_merges=20)
    print("Final vocabulary size:", len(final_vocab))

if __name__ == "__main__":
    main()