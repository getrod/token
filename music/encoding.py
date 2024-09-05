from collections import defaultdict
import ast

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

# Example usage:
note_sequence = [['n_60_4'], ['n_62_4'], ['n_64_4', 'n_67_4'], ['n_r_4'], ['n_69_8']]
serialized = serialize(note_sequence)
print("Serialized:", serialized)

deserialized = deserialize(serialized)
print("Deserialized:", deserialized)

# Verify that the deserialized version matches the original
print("Match:", note_sequence == deserialized)
