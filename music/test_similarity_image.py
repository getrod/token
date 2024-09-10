from midi_similarity import notes_to_binary_image, save_binary_image
from note_token import note_sequence_to_notes

# Assuming you have a note_sequence
note_sequence = [['n_60_4', 'n_61_4'], ['n_62_4'], ['n_64_4', 'n_67_4'], ['n_r_4'], ['n_69_16']]

# Convert note sequence to MidiNote objects
midi_notes = note_sequence_to_notes(note_sequence)

# Convert to binary image
binary_image = notes_to_binary_image(midi_notes)

# Save the image
save_binary_image(binary_image, "midi_visualization.png")