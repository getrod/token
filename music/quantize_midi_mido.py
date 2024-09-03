import mido
import os

TICKS_PER_BEAT = 480  # Standard MIDI resolution
QUANTIZE_TICKS = TICKS_PER_BEAT // 4  # 16th note quantization
MAX_NOTE_TICKS = TICKS_PER_BEAT * 16  # 16 quarter notes

def limit_note_duration(duration):
    # Limit duration to 16 quarter notes
    limited_duration = min(duration, MAX_NOTE_TICKS)
    return limited_duration

def quantize_tick(tick):
    # Quantize to 16th note grid
    quantized_tick = round(tick / QUANTIZE_TICKS) * QUANTIZE_TICKS
    return quantized_tick

def process_midi(input_file, output_file):
    midi = mido.MidiFile(input_file)
    
    new_midi = mido.MidiFile()
    new_midi.ticks_per_beat = TICKS_PER_BEAT

    print(midi)

    for track in midi.tracks:
        new_track = mido.MidiTrack()
        new_midi.tracks.append(new_track)
        
        current_time = 0
        active_notes = {}

        for msg in track:
            current_time += msg.time

            if msg.type == 'note_on' and msg.velocity > 0:
                # quantized_time = quantize_tick(current_time)
                quantized_time = quantize_tick(msg.time)
                active_notes[msg.note] = quantized_time
                new_msg = msg.copy(time=quantized_time - current_time)
                new_track.append(new_msg)
                current_time = quantized_time
                print(f'start: {msg.time}')
                print(f'quantize_start: {quantized_time}')
                

            elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
                if msg.note in active_notes:
                    start_time = active_notes[msg.note]
                    limited_duration = limit_note_duration(current_time - start_time)
                    end_time = start_time + limited_duration
                    new_msg = msg.copy(time=end_time - current_time)
                    new_track.append(new_msg)
                    current_time = end_time
                    del active_notes[msg.note]
                    # print()

            else:
                new_track.append(msg.copy(time=msg.time))

        print(new_track)

    new_midi.save(output_file)
    print(f"Quantized and duration-limited MIDI saved as: {output_file}")

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
