import mido
import os
from dataclasses import dataclass
from typing import List, Optional
from collections import defaultdict

@dataclass
class MidiNote:
    note: int
    start_time: int
    velocity: int
    duration: int
    _note_on_msg: mido.Message = None
    _note_off_msg: mido.Message = None

    def note_on_msg(self):
        return self._note_on_msg.copy(time=self.start_time)

    def note_off_msg(self):
        return self._note_off_msg.copy(time=self.start_time + self.duration)

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

def absolute_to_delta(absolute_messages: list[MidiMessage]):
    delta_messages = []
    prev_time = 0
    for midi_msg in absolute_messages:
        delta_time = midi_msg.time - prev_time
        new_msg = midi_msg.msg.copy(time=delta_time) # kevin change
        delta_messages.append(new_msg)
        prev_time = midi_msg.time
    return delta_messages

def absolute_to_midi_notes(absolute_messages) -> list[MidiNote]:
    midi_notes = []
    active_notes = {}
    skip_note_off = defaultdict(int)

    for midi_msg in absolute_messages:
        if midi_msg.msg.type == 'note_on' and midi_msg.msg.velocity > 0:
            # if another 'note_on' without a 'note_off', add midi note
            if midi_msg.msg.note in active_notes.keys():
                start_time, note_on_msg = active_notes[midi_msg.msg.note]
                midi_notes.append(MidiNote(
                    note=midi_msg.msg.note,
                    start_time=start_time,
                    velocity=note_on_msg.velocity,
                    duration=midi_msg.time - start_time,
                    _note_on_msg=note_on_msg,
                    _note_off_msg=mido.Message(
                        'note_off', 
                        channel=note_on_msg.channel, 
                        note=note_on_msg.note, 
                        velocity=64, 
                    )
                ))
                skip_note_off[midi_msg.msg.note] += 1
            active_notes[midi_msg.msg.note] = (midi_msg.time, midi_msg.msg)
        elif midi_msg.msg.type == 'note_off' or (midi_msg.msg.type == 'note_on' and midi_msg.msg.velocity == 0):
            # this if is to deal with overlapping notes in fl studio
            if midi_msg.msg.note in skip_note_off and skip_note_off[midi_msg.msg.note] > 0:
                skip_note_off[midi_msg.msg.note] -= 1
            # this part of the if is what normally happens
            elif midi_msg.msg.note in active_notes:
                start_time, note_on_msg = active_notes[midi_msg.msg.note]
                midi_notes.append(MidiNote(
                    note=midi_msg.msg.note,
                    start_time=start_time,
                    velocity=note_on_msg.velocity,
                    duration=midi_msg.time - start_time,
                    _note_on_msg=note_on_msg,
                    _note_off_msg=midi_msg.msg
                ))
                del active_notes[midi_msg.msg.note]

    return midi_notes

def midi_notes_to_absolute(midi_notes):
    absolute_messages = []
    for note in midi_notes:
        absolute_messages.append(MidiMessage(note.start_time, note.note_on_msg()))
        absolute_messages.append(MidiMessage(note.start_time + note.duration, note.note_off_msg()))
    return sorted(absolute_messages, key=lambda x: x.time)

def quantize_midi_notes(midi_notes, quantize_ticks, max_note_ticks):
    quantized_notes = []
    for note in midi_notes:
        quantized_start = round(note.start_time / quantize_ticks) * quantize_ticks
        quantized_duration = min(round(note.duration / quantize_ticks) * quantize_ticks, max_note_ticks)
        quantized_notes.append(MidiNote(
            note=note.note,
            start_time=quantized_start,
            velocity=note.velocity,
            duration=quantized_duration,
            _note_on_msg=note._note_on_msg,
            _note_off_msg=note._note_off_msg
        ))
    return quantized_notes

DURATION_UNITS_PER_QUARTER_NOTE = 4 # 1 quarter note = 4 duration units

def quantize_midi(input_file, output_file):
    midi = mido.MidiFile(input_file)
    
    TICKS_PER_BEAT = get_ticks_per_beat(midi)
    QUANTIZE_TICKS = TICKS_PER_BEAT // DURATION_UNITS_PER_QUARTER_NOTE  # 16th note quantization
    MAX_NOTE_TICKS = TICKS_PER_BEAT * 16  # 16 quarter notes

    new_midi = mido.MidiFile()
    new_midi.ticks_per_beat = TICKS_PER_BEAT

    for track in midi.tracks:
        absolute_messages = delta_to_absolute(track)
        midi_notes = absolute_to_midi_notes(absolute_messages)
        quantized_notes = quantize_midi_notes(midi_notes, QUANTIZE_TICKS, MAX_NOTE_TICKS)
        quantized_absolute = midi_notes_to_absolute(quantized_notes)
        
        # Preserve non-note messages
        for msg in absolute_messages:
            if msg.msg.type not in ['note_on', 'note_off']:
                quantized_absolute.append(msg)
        
        quantized_absolute.sort(key=lambda x: x.time)
        delta_messages = absolute_to_delta(quantized_absolute)
        
        new_track = mido.MidiTrack(delta_messages)
        new_midi.tracks.append(new_track)

    new_midi.save(output_file)
    print(f"Quantized and duration-limited MIDI saved as: {output_file}")
    print(f"TICKS_PER_BEAT: {TICKS_PER_BEAT}")

def temp_file_name(input_file, temp_file_name=None):
    file_name, file_extension = os.path.splitext(input_file)
    file_name = temp_file_name if temp_file_name != None else f'{file_name}_quantized_limited'
    output_file = f"{file_name}{file_extension}"
    
    return output_file

def main():
    input_file = input("Enter the path to your MIDI file: ").strip()
    
    if not os.path.isfile(input_file):
        print("Error: The specified file does not exist.")
        return

    file_name, file_extension = os.path.splitext(input_file)
    output_file = f"{file_name}_quantized_limited{file_extension}"

    quantize_midi(input_file, output_file)

if __name__ == "__main__":
    main()
