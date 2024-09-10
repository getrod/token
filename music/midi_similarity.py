from PIL import Image
from quantize import MidiNote
from note_token import note_sequence_to_notes
import numpy as np

def calculate_image_match(image1, image2):
    '''
    Given two binary PIL images of the same dimensions, return the percentage of their match. Ex:
    Here is a matrix representation of binary images A & B
    A = [
        1 1 1 1 0 0 0 0
        0 0 0 0 1 1 1 1
        1 1 1 1 0 0 0 0
        0 0 0 0 0 0 0 0 
    ]
    B = [
        1 1 1 1 0 0 0 0
        0 0 0 0 1 1 1 1
        1 1 1 1 0 0 0 0
        0 0 0 0 1 1 1 1
    ]

    Their match percentage is 87.5%, since the top three rows of the image match (75%), 
    but the last row of B only matches half of the last row of A (25% / 2). Combined together: 75% + (25% / 2) = 87.5%
    '''
    # Convert PIL images to numpy arrays
    image_a = np.array(image1)
    image_b = np.array(image2)
    
    # Ensure images have the same dimensions
    if image_a.shape != image_b.shape:
        raise ValueError("Images must have the same dimensions")
    
    # Calculate the number of matching pixels 
    matching_black_pixels = np.sum(np.logical_and(image_a, image_b))

    # Calculate the total number of "active" pixels in both images, choose the max
    a_total_black_pixels = np.sum(image_a) / 255
    b_total_black_pixels = np.sum(image_b) / 255
    max_total_black_pixels = max(a_total_black_pixels, b_total_black_pixels)

    print('image a')
    print(image_a)
    print('image b')
    print(image_b)
    print('matching_pixels_arr: ')
    print(f'{image_a == image_b}')
    print('matching_pixels_and_op: ')
    print(f'{np.logical_and(image_a, image_b)}')
    print(f'matching_black_pixels: {matching_black_pixels}')
    print(f'max_total_black_pixels: {max_total_black_pixels}')
    
    # Calculate the percentage of matching pixels
    if b_total_black_pixels == 0: return 0
    match_percentage = (matching_black_pixels / max_total_black_pixels) 
    print(f'match percent: {match_percentage}')
    
    return match_percentage

def compare_images_piece_by_piece(image_a, image_b):
    '''
    Given two binary PIL images, A & B as before, compare them piece by piece by comparing the top
    subet of image A to the bottom subset of image B:
    '''
    arr_a = np.array(image_a)
    arr_b = np.array(image_b)
    
    if arr_a.shape != arr_b.shape:
        raise ValueError("Images must have the same dimensions")
    
    height, _ = arr_a.shape
    result_map = {}
    
    for pixel_step in range(1, height + 1):
        piece_a = arr_a[:pixel_step, :]
        piece_b = arr_b[-pixel_step:, :]
        
        piece_percentage = pixel_step / height
        piece_match = calculate_image_match(Image.fromarray(piece_a), Image.fromarray(piece_b))
        
        result_map[piece_percentage] = piece_match
    
    return result_map

def structure_similarity(image_a, image_b):
    '''
    Given binary images A & B, this method finds internal pattern similarity
    '''
    arr_a = np.array(image_a)
    arr_b = np.array(image_b)
    
    if arr_a.shape != arr_b.shape:
        raise ValueError("Images must have the same dimensions")
    
    match_normal = {}
    match_flip = {}
    match_normal = compare_images_piece_by_piece(arr_a, arr_b)
    match_flip = compare_images_piece_by_piece(arr_b, arr_a)

    match_score = 0
    for weight, match in list(match_normal.items()) + list(match_flip.items()):
        # print(f"{weight:.2f} -> {match:.1f}: {match * weight}")
        match_score = max(match * weight, match_score)
    
    return match_score
    
def normalize_notes(midi_notes: list[MidiNote]):
    '''
    Given a list of notes, subtract all notes by lowest note. Return new list of notes
    '''
    new_notes = []
    lowest_note = min(midi_notes, key=lambda n : n.note).note
    for n in midi_notes:
        n.note -= lowest_note
        new_notes.append(n)
    return new_notes


def notes_to_binary_image(notes: list[MidiNote]):
    """
    Convert a list of MidiNotes to a binary image representation.
    
    Args:
    notes (list[MidiNote]): List of MidiNote objects
    
    Returns:
    numpy.ndarray: Binary image representation of the notes
    """
    if not notes:
        return np.array([])
    
    # To make midi image more compact, notes are normalized
    notes = normalize_notes(notes)

    max_time = max(note.start_time + note.duration for note in notes)
    max_note = max(notes, key=lambda n : n.note).note

    # Create an empty image (all zeros)
    image = np.zeros((max_note + 1, max_time), dtype=np.uint8)

    # Fill in the image based on the notes
    for note in notes:
        image[note.note, note.start_time:note.start_time + note.duration] = 1

    return image

def save_binary_image(image, filename):
    """
    Save a binary numpy array as a black and white image.
    
    Args:
    image (numpy.ndarray): Binary image as a 2D numpy array
    filename (str): Output filename (should end with .png)
    """
    if image.size == 0:
        print("Error: Empty image, nothing to save.")
        return

    # Convert to PIL Image
    pil_image = Image.fromarray(np.logical_not(image).astype(np.uint8) * 255).convert('L') # 'logical_not' for black notes
    
    # Save the image
    pil_image.save(filename)
    print(f"Image saved as {filename}")


def make_same_height(image_a, image_b):
    """
    Given two binary image representations A and B, pad the shorter image
    with zeros at the bottom to match the height of the taller image.

    Args:
    image_a (numpy.ndarray): First binary image representation
    image_b (numpy.ndarray): Second binary image representation

    Returns:
    tuple: (padded_image_a, padded_image_b) with the same height
    """
    height_a, _ = image_a.shape
    height_b, _ = image_b.shape

    # Find the maximum height
    max_height = max(height_a, height_b)

    # Pad image_a if necessary
    if height_a < max_height:
        pad_height = max_height - height_a
        padded_a = np.pad(image_a, ((0, pad_height), (0, 0)), mode='constant', constant_values=0)
    else:
        padded_a = image_a

    # Pad image_b if necessary
    if height_b < max_height:
        pad_height = max_height - height_b
        padded_b = np.pad(image_b, ((0, pad_height), (0, 0)), mode='constant', constant_values=0)
    else:
        padded_b = image_b

    return padded_a, padded_b


def make_same_width(image_a, image_b, target_width):
    """
    Resize both binary image representations A and B to the specified target width.

    Args:
    image_a (numpy.ndarray): First binary image representation
    image_b (numpy.ndarray): Second binary image representation
    target_width (int): The desired width for both images

    Returns:
    tuple: (resized_image_a, resized_image_b) with the same width
    """
    # Convert numpy arrays to PIL Images
    pil_a = Image.fromarray((image_a * 255).astype(np.uint8))
    pil_b = Image.fromarray((image_b * 255).astype(np.uint8))

    # Get original dimensions
    height_a, _ = image_a.shape
    height_b, _ = image_b.shape

    # Resize images
    resized_a = pil_a.resize((target_width, height_a), Image.NEAREST)
    resized_b = pil_b.resize((target_width, height_b), Image.NEAREST)

    # Convert back to numpy arrays and ensure binary (0 or 1) values
    resized_array_a = np.array(resized_a).astype(bool).astype(np.uint8)
    resized_array_b = np.array(resized_b).astype(bool).astype(np.uint8)

    return resized_array_a, resized_array_b

def compare_midi_sequences(seq_a, seq_b, target_width=100):
    '''
    Compare similarity of two note sequneces [0.0-1.0]

    target_width (int): Controls "resolution" of midi comparison
    '''
    notes_a = note_sequence_to_notes(seq_a)
    notes_b = note_sequence_to_notes(seq_b)
    
    image_a = notes_to_binary_image(notes_a)
    image_b = notes_to_binary_image(notes_b)
    
    # Make same height first
    padded_a, padded_b = make_same_height(image_a, image_b)
    
    # Then make same width
    resized_a, resized_b = make_same_width(padded_a, padded_b, target_width)
    
    similarity = structure_similarity(resized_a, resized_b)
    return similarity


def compare_midi_usage_case():
    # Example MIDI sequences
    seq_a = [
        ['n_60_4'], ['n_62_4'], ['n_64_4', 'n_67_4'], ['n_r_4'], ['n_69_8']
    ]
    seq_b = [
        ['n_60_4'], ['n_62_4'], ['n_64_4', 'n_67_4'], ['n_r_4'], ['n_69_8'],
        ['n_67_4'], ['n_65_4'], ['n_64_4']
    ]
    seq_c = [
        ['n_72_4'], ['n_74_4'], ['n_76_4', 'n_79_4'], ['n_r_4'], ['n_81_8']
    ]

    # Compare sequences
    similarity_ab = compare_midi_sequences(seq_a, seq_b)
    similarity_ac = compare_midi_sequences(seq_a, seq_c)
    similarity_bc = compare_midi_sequences(seq_b, seq_c)

    print(f"Similarity between sequence A and B: {similarity_ab:.2f}")
    print(f"Similarity between sequence A and C: {similarity_ac:.2f}")
    print(f"Similarity between sequence B and C: {similarity_bc:.2f}")

    # Visualize the sequences
    for i, seq in enumerate([seq_a, seq_b, seq_c]):
        notes = note_sequence_to_notes(seq)
        image = notes_to_binary_image(notes)
        save_binary_image(image, f"sequence_{chr(65+i)}.png")
        print(f"Saved visualization of sequence {chr(65+i)} as sequence_{chr(65+i)}.png")

def compare_midi_dissimilar():
    # Highly dissimilar note sequences
    seq_dissimilar_1 = [
        ['n_60_1'],                  # Short, low note
        ['n_r_7'],                   # Long rest
        ['n_84_8', 'n_88_8', 'n_91_8'], # High chord, long duration
        ['n_r_16'],                  # Very long rest
        ['n_48_2', 'n_52_2'],        # Low chord, medium duration
        ['n_72_1', 'n_75_1', 'n_79_1', 'n_82_1']  # High dense chord, short duration
    ]

    seq_dissimilar_2 = [
        ['n_96_32'],                 # Very high note, very long duration
        ['n_36_1', 'n_40_1'],        # Very low chord, short duration
        ['n_r_1'],                   # Short rest
        ['n_72_2'],                  # Medium-high note, medium duration
        ['n_48_1', 'n_52_1', 'n_55_1', 'n_59_1', 'n_62_1'],  # Low dense chord, short duration
        ['n_84_4'],                  # High note, medium-long duration
        ['n_r_2'],                   # Medium rest
        ['n_60_1', 'n_64_1', 'n_67_1']  # Medium chord, short duration
    ]

    # Compare highly dissimilar sequences
    similarity_dissimilar = compare_midi_sequences(seq_dissimilar_1, seq_dissimilar_2)
    print(f"Similarity between highly dissimilar sequences: {similarity_dissimilar:.2f}")

    # Visualize the dissimilar sequences
    for i, seq in enumerate([seq_dissimilar_1, seq_dissimilar_2]):
        notes = note_sequence_to_notes(seq)
        image = notes_to_binary_image(notes)
        save_binary_image(image, f"sequence_dissimilar_{i+1}.png")
        print(f"Saved visualization of dissimilar sequence {i+1} as sequence_dissimilar_{i+1}.png")
    pass


# Example usage
def main():
    notes = [
        MidiNote(note=0, start_time=0, velocity=64, duration=4),
        MidiNote(note=2, start_time=0, velocity=64, duration=4),
        MidiNote(note=1, start_time=4, velocity=64, duration=4),
    ]
    
    binary_image = notes_to_binary_image(notes)
    print("Binary Image Representation:")
    print(binary_image)
    
    save_binary_image(binary_image, "midi_visualization.png")

    # Example usage of make_same_height
    notes_a = [
        MidiNote(note=0, start_time=0, velocity=64, duration=4),
        MidiNote(note=2, start_time=0, velocity=64, duration=4),
        MidiNote(note=1, start_time=4, velocity=64, duration=4),
    ]
    
    notes_b = [
        MidiNote(note=0, start_time=0, velocity=64, duration=4),
        MidiNote(note=2, start_time=0, velocity=64, duration=4),
        MidiNote(note=1, start_time=4, velocity=64, duration=4),
        MidiNote(note=3, start_time=4, velocity=64, duration=4),
    ]

    binary_image_a = notes_to_binary_image(notes_a)
    binary_image_b = notes_to_binary_image(notes_b)

    print("Original Image A:")
    print(binary_image_a)
    print("\nOriginal Image B:")
    print(binary_image_b)

    padded_a, padded_b = make_same_height(binary_image_a, binary_image_b)

    print("\nPadded Image A:")
    print(padded_a)
    print("\nPadded Image B:")
    print(padded_b)

    save_binary_image(padded_a, "padded_image_a.png")
    save_binary_image(padded_b, "padded_image_b.png")

    # Example usage of make_same_width
    notes_a = [
        MidiNote(note=0, start_time=0, velocity=64, duration=4),
        MidiNote(note=2, start_time=0, velocity=64, duration=4),
        MidiNote(note=1, start_time=4, velocity=64, duration=4),
    ]
    
    notes_b = [
        MidiNote(note=0, start_time=0, velocity=64, duration=8),
        MidiNote(note=2, start_time=0, velocity=64, duration=8),
        MidiNote(note=1, start_time=8, velocity=64, duration=8),
    ]

    binary_image_a = notes_to_binary_image(notes_a)
    binary_image_b = notes_to_binary_image(notes_b)

    print("Original Image A:")
    print(binary_image_a)
    print("\nOriginal Image B:")
    print(binary_image_b)

    target_width = 12  # Example target width
    resized_a, resized_b = make_same_width(binary_image_a, binary_image_b, target_width)

    print(f"\nResized Image A (width {target_width}):")
    print(resized_a)
    print(f"\nResized Image B (width {target_width}):")
    print(resized_b)

    # save_binary_image(resized_a, "resized_image_a.png")
    # save_binary_image(resized_b, "resized_image_b.png")
    # compare_midi_usage_case()
    # compare_midi_dissimilar()

if __name__ == "__main__":
    main()
