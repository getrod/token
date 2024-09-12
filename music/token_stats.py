import json
import matplotlib.pyplot as plt
import numpy as np
import math

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

def plot_token_stats(json_file, label_points=True, apply_scaling=False):
    # Load the JSON data
    with open(json_file, 'r') as f:
        data = json.load(f)

    # Extract seq_len and freq for each token
    seq_lens = []
    freqs = []
    tokens = []

    for token, info in data.items():
        seq_lens.append(info['seq_len'])
        freqs.append(info['freq'])
        tokens.append(token)

    # Create the scatter plot
    plt.figure(figsize=(12, 8))

    # Apply scaling if requested
    if apply_scaling:
        scaled_seq_lens = []
        scaled_freqs = []
        for x, y in zip(seq_lens, freqs):
            alpha = angle_with_diagonal(x, y)
            scaled_x, scaled_y = scale_vector(x, y, alpha)
            scaled_seq_lens.append(scaled_x)
            scaled_freqs.append(scaled_y)
        plt.scatter(scaled_seq_lens, scaled_freqs, alpha=0.6)
    else:
        plt.scatter(seq_lens, freqs, alpha=0.6)

    # Add labels to the points if label_points is True
    if label_points:
        for i, token in enumerate(tokens):
            x = scaled_seq_lens[i] if apply_scaling else seq_lens[i]
            y = scaled_freqs[i] if apply_scaling else freqs[i]
            plt.annotate(token, (x, y), fontsize=8, alpha=0.7)

    # Add the 45-degree diagonal line
    max_val = max(max(seq_lens), max(freqs))
    diagonal = np.linspace(0, max_val, 100)
    plt.plot(diagonal, diagonal, '--', color='red', alpha=0.5, label='45° line')

    # Set labels and title
    plt.xlabel('Sequence Length')
    plt.ylabel('Frequency')
    title = 'Token Statistics: Sequence Length vs Frequency'
    if apply_scaling:
        title += ' (Scaled)'
    plt.title(title)

    # Add legend
    plt.legend()

    # Show grid
    plt.grid(True, alpha=0.3)

    # Adjust layout to prevent clipping of labels
    plt.tight_layout()

    # Show the plot
    plt.show()

if __name__ == "__main__":
    json_file = 'tokens_300.json'  # Make sure this file is in the same directory as your script
    plot_token_stats(json_file, label_points=True, apply_scaling=True)  # Set apply_scaling to False for unscaled plot
