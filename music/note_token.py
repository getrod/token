import mido
from quantize import process_midi, MidiNote, get_ticks_per_beat, absolute_to_midi_notes, delta_to_absolute, temp_file_name, midi_notes_to_absolute, absolute_to_delta, DURATION_UNITS_PER_QUARTER_NOTE
import os


def midi_note_to_token(midi_note: MidiNote, tick_per_duration_unit: int):
    '''
    Converts Midi notes into note tokens: n_<note number>_<duration> 
    '''
    return f"n_{midi_note.note}_{midi_note.duration // tick_per_duration_unit}"

def chord_to_tokens(chord: list[MidiNote], tick_per_duration_unit: int):
    '''
    Utility function for converting lists of notes into note token format 
    ex: [n_67_4, n_64_3, n_60_4]
    '''
    return [midi_note_to_token(n, tick_per_duration_unit) for n in chord]


def midi_to_note_sequence(midi_file):
    # Quantize the MIDI file
    temp_file = temp_file_name(midi_file, "temp")
    process_midi(midi_file, temp_file)

    # Read the quantized MIDI file
    midi = mido.MidiFile(temp_file)
    
    TICKS_PER_BEAT = get_ticks_per_beat(midi)
    TICKS_PER_DURATION_UNIT = TICKS_PER_BEAT // DURATION_UNITS_PER_QUARTER_NOTE

    note_sequence = []
    current_chord = []
    last_note_end = 0

    for track in midi.tracks: #TODO: might be an issue if multiple tracks
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

            # Add note to current chord
            current_chord.append(note)
            last_note_end = max(last_note_end, note.start_time + note.duration)

    # Add any remaining notes
    if current_chord:
        note_sequence.append(chord_to_tokens(current_chord, TICKS_PER_DURATION_UNIT))

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

def note_sequence_to_midi(note_sequence, output_file, ticks_per_beat=480, default_velocity=64):
    def token_to_midi_note(token, start_time):
        parts = token.split('_')
        note = int(parts[1])
        duration = int(parts[2]) * (ticks_per_beat // DURATION_UNITS_PER_QUARTER_NOTE)
        return MidiNote(
            note=note,
            start_time=start_time,
            velocity=default_velocity,
            duration=duration,
            _note_on_msg=mido.Message('note_on', note=note, velocity=default_velocity),
            _note_off_msg=mido.Message('note_off', note=note, velocity=default_velocity)
        )

    midi_notes = []
    current_time = 0

    for chord in note_sequence:
        if chord[0].startswith('n_r'):  # Rest
            rest_duration = int(chord[0].split('_')[2]) * (ticks_per_beat // DURATION_UNITS_PER_QUARTER_NOTE)
            current_time += rest_duration
        else:
            chord_notes = [token_to_midi_note(token, current_time) for token in chord]
            midi_notes.extend(chord_notes)
            current_time += max(note.duration for note in chord_notes)

    absolute_messages = midi_notes_to_absolute(midi_notes)
    delta_messages = absolute_to_delta(absolute_messages)

    midi = mido.MidiFile(ticks_per_beat=ticks_per_beat)
    track = mido.MidiTrack()
    midi.tracks.append(track)

    for msg in delta_messages:
        track.append(msg)

    midi.save(output_file)
    print(f"MIDI file saved as: {output_file}")

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

    # Optionally, save to a file
    output_file = input("Convert note sequence to midi? (or press Enter to skip): ").strip()
    if output_file:
        note_sequence_to_midi(note_sequence, 'note_sequence.mid')
        print(f"Note sequence saved.")

if __name__ == "__main__":
    main()