from collections import defaultdict

def new_token(token_count):
    return f't_{token_count}'

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
        pair = (tokens[i], tokens[i+1])
        freq[pair] += 1
    return freq

def generate_vocab_list(input_string, num_merges):
    vocab_list = {char: [char] for char in set(input_string)}
    tokens = list(input_string)
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
        if len(vocab_list[token]) == 1:
            return vocab_list[token]
        else:
            return expand_token(vocab_list[token][0]) + expand_token(vocab_list[token][1])
    
    expanded_tokens = set()
    for token in vocab_list:
        expanded = ''.join(expand_token(token))
        expanded_tokens.add(expanded)
    
    return expanded_tokens

# Example usage
f = open('./data.txt')
input_string = f.read()
num_merges = 100
vocab_list = generate_vocab_list(input_string, num_merges)
print("Vocabulary List:")
print(vocab_list)

detokenized = detokenize(vocab_list)
print("\nDetokenized Set:")
print(sorted(detokenized, key=lambda token: len(token), reverse=True))
