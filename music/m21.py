import os
from music21 import converter, environment, note, chord

def limit_note_duration(element, max_duration=16.0):
    if isinstance(element, (note.Note, chord.Chord)):
        if element.duration.quarterLength > max_duration:
            element.duration.quarterLength = max_duration
    return element

def quantize_midi(input_file, output_file, max_duration=32.0):
    # Set up the music21 environment
    env = environment.Environment()
    env['musicxmlPath'] = '/usr/bin/musescore'  # Adjust this path if needed

    # Parse the MIDI file with 16th note quantization
    score = converter.parse(input_file)

    # # Limit note durations
    # for part in score.parts:
    #     for element in part.recurse():
    #         limit_note_duration(element, max_duration)

    # Save the quantized and duration-limited MIDI file
    score.write('midi', fp=output_file)

    print(f"Quantized and duration-limited MIDI saved as: {output_file}")

def main():
    # Get input file from user
    input_file = input("Enter the path to your MIDI file: ").strip()

    # Check if the file exists
    if not os.path.isfile(input_file):
        print("Error: The specified file does not exist.")
        return

    # Generate output file name
    file_name, file_extension = os.path.splitext(input_file)
    output_file = f"{file_name}_quantized_limited{file_extension}"

    # Quantize the MIDI file and limit note durations
    quantize_midi(input_file, output_file)

if __name__ == "__main__":
    main()
