import mido
import os
from dataclasses import dataclass
from typing import List

@dataclass
class MidiMessage:
    time: int
    msg: mido.Message

def get_ticks_per_beat(midi_file):
    for track in midi_file.tracks:
        for msg in track:
            if msg.type == 'time_signature':
                return msg.clocks_per_click * 4  # Multiply by 4 as clocks_per_click is per quarter note
    return 480  # Default value if no time signature is found

def delta_to_absolute(messages):
    absolute_messages = []
    current_time = 0
    for msg in messages:
        current_time += msg.time
        absolute_messages.append(MidiMessage(current_time, msg))
    return absolute_messages

def absolute_to_delta(absolute_messages):
    delta_messages = []
    prev_time = 0
    for midi_msg in absolute_messages:
        delta_time = midi_msg.time - prev_time
        new_msg = midi_msg.msg.copy(time=delta_time)
        delta_messages.append(new_msg)
        prev_time = midi_msg.time
    return delta_messages

def quantize_and_limit_note(midi_msg, quantize_ticks, max_note_ticks):
    # Quantize to 16th note grid
    quantized_time = round(midi_msg.time / quantize_ticks) * quantize_ticks
    
    # Limit duration for note_off events
    if midi_msg.msg.type == 'note_off' or (midi_msg.msg.type == 'note_on' and midi_msg.msg.velocity == 0):
        # Find corresponding note_on event
        note_on_time = None
        for m in reversed(midi_msg.track):
            if (m.msg.type == 'note_on' and
                m.msg.note == midi_msg.msg.note and
                m.time < midi_msg.time):
                note_on_time = m.time
                break
        
        # If note found, potentially clip duration
        if note_on_time is not None:
            duration = quantized_time - note_on_time
            if duration > max_note_ticks:
                quantized_time = note_on_time + max_note_ticks # ?

    return MidiMessage(quantized_time, midi_msg.msg)

def process_midi(input_file, output_file):
    midi = mido.MidiFile(input_file)
    
    TICKS_PER_BEAT = get_ticks_per_beat(midi)
    QUANTIZE_TICKS = TICKS_PER_BEAT // 4  # 16th note quantization
    MAX_NOTE_TICKS = TICKS_PER_BEAT * 16  # 16 quarter notes

    new_midi = mido.MidiFile()
    new_midi.ticks_per_beat = TICKS_PER_BEAT

    for track in midi.tracks:
        ## convert to absolute
        absolute_messages = delta_to_absolute(track)

        ## quantize
        # Add track information to MidiMessage objects
        for midi_msg in absolute_messages:
            midi_msg.track = absolute_messages
        quantized_messages = [quantize_and_limit_note(midi_msg, QUANTIZE_TICKS, MAX_NOTE_TICKS) for midi_msg in absolute_messages]

        ## convert to delta
        quantized_messages.sort(key=lambda x: x.time)  # Ensure messages are in time order
        delta_messages = absolute_to_delta(quantized_messages)
        
        new_track = mido.MidiTrack(delta_messages)
        new_midi.tracks.append(new_track)

    new_midi.save(output_file)
    print(f"Quantized and duration-limited MIDI saved as: {output_file}")
    print(f"TICKS_PER_BEAT: {TICKS_PER_BEAT}")

def main():
    input_file = input("Enter the path to your MIDI file: ").strip()
    
    if not os.path.isfile(input_file):
        print("Error: The specified file does not exist.")
        return

    file_name, file_extension = os.path.splitext(input_file)
    output_file = f"{file_name}_quantized_limited{file_extension}"

    process_midi(input_file, output_file)

if __name__ == "__main__":
    main()
