import mido
from quantize import process_midi, MidiNote, get_ticks_per_beat, absolute_to_midi_notes, delta_to_absolute, temp_file_name
import tempfile
import os

def midi_note_to_token(midi_note: MidiNote, tick_per_duration_unit: int):
    '''
    Converts Midi notes into n_<note number>_<duration> format
    '''
    return f"n_{midi_note.note}_{midi_note.duration // tick_per_duration_unit}"

def chord_to_tokens(chord: list[MidiNote], tick_per_duration_unit: int):
    '''
    Utility function for converting lists of notes into note token format 
    ex: [n_67_4, n_64_3, n_60_4]
    '''
    return [midi_note_to_token(n, tick_per_duration_unit) for n in chord]


def midi_to_note_sequence(midi_file):
    # # Create a temporary file for the quantized MIDI
    # with tempfile.NamedTemporaryFile(suffix='.mid', delete=False) as temp_file:
    #     temp_file_path = temp_file.name

    temp_file = temp_file_name(midi_file, "temp")

    # Quantize the MIDI file
    process_midi(midi_file, temp_file)

    # Read the quantized MIDI file
    midi = mido.MidiFile(temp_file)
    
    TICKS_PER_BEAT = get_ticks_per_beat(midi)
    TICKS_PER_DURATION_UNIT = TICKS_PER_BEAT // 4  # 1 quarter note = 4 duration units

    note_sequence = []
    current_chord = []
    last_note_end = 0

    for track in midi.tracks:
        absolute_messages = delta_to_absolute(track)
        midi_notes = absolute_to_midi_notes(absolute_messages)
        midi_notes.sort(key=lambda x: (x.start_time, -x.note))  # Sort by start time, then by note (higher first)

        for note in midi_notes:
            # Add rest if there's a gap
            if note.start_time > last_note_end:
                rest_duration = (note.start_time - last_note_end) // TICKS_PER_DURATION_UNIT

                # If you found a rest, save the current chord and add the rest after it
                if rest_duration > 0:
                    if current_chord:
                        note_sequence.append(chord_to_tokens(current_chord, TICKS_PER_DURATION_UNIT))
                        current_chord = []
                    note_sequence.append([f"n_r_{rest_duration}"])

            # Start a new chord if this note starts after the previous chord
            if current_chord and note.start_time > current_chord[0].start_time:
                note_sequence.append(chord_to_tokens(current_chord, TICKS_PER_DURATION_UNIT))
                current_chord = []

            # Add note to chord
            current_chord.append(note)
            last_note_end = max(last_note_end, note.start_time + note.duration)

    # Add any remaining notes
    if current_chord:
        note_sequence.append(chord_to_tokens(current_chord, TICKS_PER_DURATION_UNIT))

    # # Clean up the temporary file
    # os.unlink(temp_file_path)

    return note_sequence

def format_note_sequence(note_sequence):
    formatted = "[\n"
    for chord in note_sequence:
        if len(chord) == 1:
            formatted += f"    [{chord[0]}],\n"
        else:
            formatted += "    [\n"
            for note in chord:
                formatted += f"        {note},\n"
            formatted += "    ],\n"
    formatted += "]"
    return formatted

def main():
    input_file = input("Enter the path to your MIDI file: ").strip()
    
    if not os.path.isfile(input_file):
        print("Error: The specified file does not exist.")
        return

    note_sequence = midi_to_note_sequence(input_file)
    formatted_sequence = format_note_sequence(note_sequence)

    print(note_sequence)
    
    print("\nNote Sequence:")
    print(formatted_sequence)

    # # Optionally, save to a file
    # output_file = input("Enter a file name to save the note sequence (or press Enter to skip): ").strip()
    # if output_file:
    #     with open(output_file, 'w') as f:
    #         f.write(formatted_sequence)
    #     print(f"Note sequence saved to {output_file}")

if __name__ == "__main__":
    main()


'''
Using the program written above, write a new program `note_tokens.py` that uses `quantize.py` above that converts the midi file into the following note sequence syntax:

```
note: n_<note number>_<duration>
rest: n_r_<duration>
(1 quarter note = 4 duration units)

note sequence syntax:
[ [n_r_<duration>] or [ (n_<note number>_<duration>)*] ] (* meaning many)

note sequence example:
[
    [n_60_4], 
    [
        n_67_8,
        n_64_4,
        n_60_8
    ],
    [n_64_6],
    [n_r_4],
    [
        n_67_8,
        n_64_4,
        n_60_8
    ],
    [n_64_6],
]

note sequence is of type list[list[str]]
```
'''