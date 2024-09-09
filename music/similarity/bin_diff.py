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

def calculate_image_difference(image1, image2):
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
    match_percentage = (matching_pixels / total_pixels) * 100
    
    return match_percentage

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

    difference = calculate_image_difference(A, B)
    print(f"Difference percentage for 8x4 images: {difference:.2f}%")

# Example usage for 200x200 images
def example_200x200():
    # Create 200x200 random binary images
    np.random.seed(42)  # for reproducibility
    A = Image.fromarray((np.random.rand(200, 200) > 0.5).astype(np.uint8) * 255)
    B = Image.fromarray((np.random.rand(200, 200) > 0.5).astype(np.uint8) * 255)

    difference = calculate_image_difference(A, B)
    print(f"Difference percentage for 200x200 images: {difference:.2f}%")

# Example usage for 1920x1080 images
def example_1920x1080():
    # Create 1920x1080 random binary images
    np.random.seed(42)  # for reproducibility
    A = Image.fromarray((np.random.rand(1080, 1920) > 0.5).astype(np.uint8) * 255)
    B = Image.fromarray((np.random.rand(1080, 1920) > 0.5).astype(np.uint8) * 255)

    difference = calculate_image_difference(A, B)
    print(f"Difference percentage for 1920x1080 images: {difference:.2f}%")

if __name__ == "__main__":
    example_8x4()
    example_200x200()
    example_1920x1080()
