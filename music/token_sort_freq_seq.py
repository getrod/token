import json
import math
from operator import itemgetter

def angle_with_diagonal(x, y):
    """Calculate the angle between a point and the 45-degree line."""
    if x == 0 and y == 0:
        return 0
    point_angle = math.atan2(y, x)
    diagonal_angle = math.pi / 4  # 45 degrees in radians
    return abs(point_angle - diagonal_angle)

def scale_vector(x, y, alpha):
    """Scale a vector based on its angle with the 45-degree line."""
    scale_factor = 1 - (alpha / (math.pi / 4))  # pi/4 radians = 45 degrees
    return x * scale_factor, y * scale_factor

def calculate_scaled_magnitude(x, y):
    """Calculate the scaled magnitude of a vector."""
    alpha = angle_with_diagonal(x, y)
    scaled_x, scaled_y = scale_vector(x, y, alpha)
    return math.sqrt(scaled_x**2 + scaled_y**2)

def sort_tokens_by_scaled_magnitude(json_file):
    # Load the JSON data
    with open(json_file, 'r') as f:
        data = json.load(f)

    # Calculate scaled magnitude for each token
    token_info = []
    for token, info in data.items():
        seq_len = info['seq_len']
        freq = info['freq']
        scaled_magnitude = calculate_scaled_magnitude(seq_len, freq)
        token_info.append({
            'token': token,
            'seq_len': seq_len,
            'freq': freq,
            'scaled_magnitude': scaled_magnitude
        })

    # Sort tokens by scaled magnitude in descending order
    sorted_tokens = sorted(token_info, key=itemgetter('scaled_magnitude'), reverse=True)

    return sorted_tokens

def print_sorted_tokens(sorted_tokens, num_tokens=None):
    if num_tokens is None:
        num_tokens = len(sorted_tokens)
    
    print(f"{'Token':<10} {'Seq Len':<10} {'Freq':<10} {'Scaled Magnitude':<20}")
    print("-" * 50)
    for info in sorted_tokens[:num_tokens]:
        print(f"{info['token']:<10} {info['seq_len']:<10} {info['freq']:<10} {info['scaled_magnitude']:<20.2f}")

if __name__ == "__main__":
    json_file = 'tokens_300.json'  # Make sure this file is in the same directory as your script
    sorted_tokens = sort_tokens_by_scaled_magnitude(json_file)
    
    # Print top 20 tokens (you can change this number or remove it to print all)
    print_sorted_tokens(sorted_tokens, 20)
