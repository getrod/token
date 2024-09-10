from PIL import Image
import numpy as np
from music.midi_similarity import structure_similarity, calculate_image_match, compare_images_piece_by_piece

# Example usage for 8x4 images (as in the given example)
def example_8x4():
    # Create 8x4 binary images
    A = Image.fromarray(np.array([
        [1, 1, 1, 1, 0, 0, 0, 0],
        [0, 0, 0, 0, 1, 1, 1, 1],
        [1, 1, 1, 1, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0]
    ], dtype=np.uint8) * 255)

    B = Image.fromarray(np.array([
        [1, 1, 1, 1, 0, 0, 0, 0],
        [0, 0, 0, 0, 1, 1, 1, 1],
        [1, 1, 1, 1, 0, 0, 0, 0],
        [0, 0, 0, 0, 1, 1, 1, 1]
    ], dtype=np.uint8) * 255)

    # match = calculate_image_match(A, B)
    # print(f"Difference percentage for 8x4 images: {match:.2f}%")
    # result = compare_images_piece_by_piece(A, B)
    # print("Result map for 8x4 images:")
    # for percentage, match in result.items():
    #     print(f"{percentage:.2f} -> {match:.3f}")

    structure_similar = structure_similarity(A, B)
    print(structure_similar)


# Example usage for 200x200 images
def example_200x200():
    # Create 200x200 random binary images
    np.random.seed(42)  # for reproducibility
    A = Image.fromarray((np.random.rand(200, 200) > 0.5).astype(np.uint8) * 255)
    B = Image.fromarray((np.random.rand(200, 200) > 0.5).astype(np.uint8) * 255)

    match = calculate_image_match(A, B)
    print(f"Difference percentage for 200x200 images: {match:.2f}%")
    result = compare_images_piece_by_piece(A, B)
    print("\nResult map for 200x200 images (showing every 10th step):")
    for i, (percentage, match) in enumerate(result.items()):
        if i % 10 == 0:
            print(f"{percentage:.2f} -> {match:.1f}")

    


# Example usage for 1920x1080 images
def example_1920x1080():
    # Create 1920x1080 random binary images
    np.random.seed(42)  # for reproducibility
    A = Image.fromarray((np.random.rand(1080, 1920) > 0.5).astype(np.uint8) * 255)
    B = Image.fromarray((np.random.rand(1080, 1920) > 0.5).astype(np.uint8) * 255)

    match = calculate_image_match(A, B)
    print(f"Difference percentage for 1920x1080 images: {match:.2f}%")

if __name__ == "__main__":
    example_8x4()
    example_200x200()
    example_1920x1080()
