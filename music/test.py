import os
from quantize import quantize_midi
from note_token import midi_to_note_sequence
from encoding import serialize, generate_vocab_list, detokenize



def main():
    midi_file = input("Enter the path to your MIDI file: ").strip()
    
    if not os.path.isfile(midi_file):
        print("Error: The specified file does not exist.")
        return

    note_sequence = midi_to_note_sequence(midi_file)
    ser_note_sequence = serialize(note_sequence)
    vocab_list = generate_vocab_list(ser_note_sequence, 5)
    print(detokenize(vocab_list))

if __name__ == "__main__":
    main()
