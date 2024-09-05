from collections import defaultdict

def new_token(token_count):
    return f'v_{token_count}'

def replace_pair(tokens, pair, new_token):
    result = []
    i = 0
    while i < len(tokens) - 1:
        if tokens[i] == pair[0] and tokens[i+1] == pair[1]:
            result.append(new_token)
            i += 2
        else:
            result.append(tokens[i])
            i += 1
    if i == len(tokens) - 1:
        result.append(tokens[-1])
    return result

def pair_frequency(tokens):
    freq = defaultdict(int)
    for i in range(len(tokens) - 1):
        pair = (tuple(tokens[i]), tuple(tokens[i+1]))
        freq[pair] += 1
    return freq

def generate_vocab_list(note_sequence, num_merges):
    # Initialize vocab_list with individual notes and chords
    vocab_list = {tuple(chord): chord for chord in note_sequence}
    tokens = [tuple(chord) for chord in note_sequence]
    token_count = 1
    
    for _ in range(num_merges):
        freq = pair_frequency(tokens)
        if not freq:
            break
        most_frequent_pair = max(freq, key=freq.get)
        new_tok = new_token(token_count)
        token_count += 1
        vocab_list[new_tok] = list(most_frequent_pair)
        tokens = replace_pair(tokens, most_frequent_pair, new_tok)
    
    return vocab_list

def detokenize(vocab_list):
    def expand_token(token):
        if isinstance(token, tuple):
            return [token]
        else:
            return expand_token(vocab_list[token][0]) + expand_token(vocab_list[token][1])
    
    expanded_tokens = set()
    for token in vocab_list:
        if isinstance(token, tuple):
            expanded = tuple(token)
        else:
            expanded = tuple(sum(expand_token(token), []))
        expanded_tokens.add(expanded)
    
    return expanded_tokens

# Example usage
note_sequence = [
    ['n_60_4'], ['n_62_4'], ['n_64_4', 'n_67_4'], ['n_r_4'], ['n_69_8'],
    ['n_60_4'], ['n_62_4'], ['n_64_4', 'n_67_4'], ['n_r_4'], ['n_69_8'],
    ['n_72_4'], ['n_74_4'], ['n_76_4', 'n_79_4'], ['n_r_4'], ['n_81_8']
]

num_merges = 10
vocab_list = generate_vocab_list(note_sequence, num_merges)
print("Vocabulary List:")
for key, value in vocab_list.items():
    print(f"{key}: {value}")

detokenized = detokenize(vocab_list)
print("\nDetokenized Set:")
for token in sorted(detokenized, key=lambda t: len(t), reverse=True):
    print(token)
