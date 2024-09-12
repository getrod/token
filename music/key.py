import music21

# Create a stream from your MIDI notes
stream = music21.stream.Stream()
for note in [67, 60, 64, 67]:
    stream.append(music21.note.Note(note))

# Analyze the key
key = stream.analyze('key')

print(f"Most likely key: {key.tonic.name} {key.mode}")
print(f"Key's pitch class: {key.tonic.pitchClass}")
