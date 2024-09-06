from collections import defaultdict
import ast
from dataclasses import dataclass

def serialize(note_sequence: list[list[str]]) -> list[str]:
    '''
    Converts note_sequence into string list (tokens)
    '''
    ser = []
    for chord in note_sequence:
        ser.append(str(chord))
    return ser

def deserialize(note_sequence_tokens: list[str]) -> list[list[str]]:
    '''
    Converts string list (tokens) into note_sequence
    '''
    de_ser = []
    for token in note_sequence_tokens:
        # Use ast.literal_eval to safely convert the string representation of a list back into a list
        chord = ast.literal_eval(token)
        # Ensure that each element in the chord is a string
        chord = [str(note) for note in chord]
        de_ser.append(chord)
    return de_ser

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

def pair_frequency(tokens, separator):
    freq = defaultdict(int)
    for i in range(len(tokens) - 1):
        pair = (tokens[i], tokens[i+1])
        if separator in pair: # Skip pairs that have separators
            continue
        else:
            freq[pair] += 1
    return freq

def generate_vocab_list(note_sequence_tokens: list[str], num_merges, vocab_list = None, separator = "|", token_count_start: int = 1):
    '''
    Generates vocab list.

    If no vocab list provided, generate one from each element of note_sequence

    returns vocab_list, tokens, freq
    '''
    if vocab_list == None:
        vocab_list = {char: [char] for char in set(note_sequence_tokens)}
    tokens = note_sequence_tokens
    token_count = token_count_start
    tok_freq = {}
    
    for _ in range(num_merges):
        freq = pair_frequency(tokens, separator)
        if not freq:
            break
        most_frequent_pair = max(freq, key=freq.get)
        # if no more frequent pairs, break
        if freq[most_frequent_pair] == 1: 
            break
        new_tok = new_token(token_count)
        token_count += 1
        vocab_list[new_tok] = list(most_frequent_pair)
        tok_freq[new_tok] = freq[most_frequent_pair]
        tokens = replace_pair(tokens, most_frequent_pair, new_tok)
    return vocab_list, tokens, tok_freq

def expand_token(token, vocab_list):
    if len(vocab_list[token]) == 1:
        return vocab_list[token]
    else:
        return expand_token(vocab_list[token][0], vocab_list) + expand_token(vocab_list[token][1], vocab_list)
        
def detokenize(vocab_list, sort = True):
    expanded_tokens = set()
    for token in vocab_list:
        expanded = ','.join(expand_token(token, vocab_list))
        expanded_tokens.add(expanded)
    
    if sort:
        return sorted(expanded_tokens, key=lambda token: len(token), reverse=True)
    return expanded_tokens

if __name__ == '__main__':
    # Example usage:
    note_sequence = [['n_60_4'], ['n_62_4'], ['n_64_4', 'n_67_4'], ['n_r_4'], ['n_69_8'], ['n_60_4'], ['n_62_4'], ['n_64_4', 'n_67_4'],]
    serialized = serialize(note_sequence)
    print("Serialized:", serialized)

    deserialized = deserialize(serialized)
    print("Deserialized:", deserialized)

    # Verify that the deserialized version matches the original
    print("Match:", note_sequence == deserialized)

    num_merges = 5
    vocab_list = generate_vocab_list(serialized, num_merges)
    print("Vocabulary List:")
    print(vocab_list)

    detokenized = detokenize(vocab_list)
    print("\nDetokenized Set:")
    print(sorted(detokenized, key=lambda token: len(token), reverse=True))
