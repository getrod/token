import os
import sys
import json
from note_token import midi_to_note_sequence

def preprocess_midi(midi_dir, processed_midi_dir):
    '''
    Get midi files and tokenize all of them
    
    midi_dir: directory that has all midi files
    processed_midi_dir: directory to store processed midi data
    '''

    # Create output directory for processed midi data
    os.makedirs(processed_midi_dir, exist_ok=True)

    # For each midi file in directory
    for filename in os.listdir(midi_dir):
        try: 
            if filename.endswith(".mid") or filename.endswith(".midi"):
                midi_path = os.path.join(midi_dir, filename)
                midi_name = os.path.splitext(filename)[0]
                
                # Create a new directory in output directory with name <midi_file_name>
                midi_output_dir = os.path.join(processed_midi_dir, midi_name)
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
        except Exception as e:
            print(f'Error processing {filename}: {str(e)}')

    print("Preprocessing complete.")

def main():
    if len(sys.argv) != 3:
        print("Usage: python preprocess_midi.py /path/to/source/midi/directory /path/to/destination/directory")
        sys.exit(1)

    source_dir = sys.argv[1]
    destination_dir = sys.argv[2]

    if not os.path.isdir(source_dir):
        print(f"Error: Source directory '{source_dir}' does not exist.")
        sys.exit(1)

    print(f"Preprocessing MIDI files from {source_dir}")
    print(f"Saving processed files to {destination_dir}")

    preprocess_midi(source_dir, destination_dir)

if __name__ == "__main__":
    main()
