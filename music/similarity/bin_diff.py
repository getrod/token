'''
Write a python program where:
Given two binary PIL images of the same dimensions, return the percentage of their difference. Ex:
```
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

Their difference percentage is 87.5%, since the top three rows of the image match (75%), but the last row of B only matches half of the last row of A (25% / 2). Combined together: 75% + (25% / 2) = 87.5%
```
Create two additional example usage programs of binary images with dimensions (200,200) and (1920, 1080)
'''
from PIL import Image
import numpy as np

def calculate_image_match(image1, image2):
    # Convert PIL images to numpy arrays
    arr1 = np.array(image1)
    arr2 = np.array(image2)
    
    # Ensure images have the same dimensions
    if arr1.shape != arr2.shape:
        raise ValueError("Images must have the same dimensions")
    
    # Calculate the total number of pixels
    total_pixels = arr1.size
    
    # Calculate the number of matching pixels
    matching_pixels = np.sum(arr1 == arr2)
    
    # Calculate the percentage of matching pixels
    match_percentage = (matching_pixels / total_pixels) 
    
    return match_percentage

def compare_images_piece_by_piece(image_a, image_b):
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
        match_score = max(match * weight, match_score)
    
    return match_score
    

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
