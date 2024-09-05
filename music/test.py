from itertools import groupby
from quantize import MidiNote
from dataclasses import dataclass

notes = [
    MidiNote(start_time=0, note=60, duration=3, velocity=64, _note_on_msg = None, _note_off_msg = None),
    MidiNote(start_time=0, note=64, duration=3, velocity=64, _note_on_msg = None, _note_off_msg = None),
    MidiNote(start_time=0, note=67, duration=3, velocity=64, _note_on_msg = None, _note_off_msg = None),
    MidiNote(start_time=2, note=57, duration=3, velocity=64, _note_on_msg = None, _note_off_msg = None),
    MidiNote(start_time=2, note=60, duration=3, velocity=64, _note_on_msg = None, _note_off_msg = None),
]


def overlap_clip_midi(midi_notes: list[MidiNote]):
    '''
    If one chord overlaps with another, clip the first one to make space for the second so that while
    the second chord is playing, the first one is completely ended.
    '''
    # Sort notes by start time, then by note (higher first)
    midi_notes.sort(key=lambda x: (x.start_time, -x.note))  

    # create chords
    @dataclass
    class Chord:
        notes: list[MidiNote]
        start_time: int 
    
    chords : list[Chord] = []
    res = groupby(notes, lambda k : k.start_time)

    for key, group in res:
        start_time = key
        chord = list(group)
        chords.append(Chord(notes=chord, start_time=start_time))

    # overlap clip
    for i in range(len(chords) - 1):
        new_duration = chords[i + 1].start_time - chords[i].start_time
        for j in range(len(chords[i].notes)):
            chords[i].notes[j].duration = new_duration
    
    # return new notes
    new_notes = []
    for chord in chords:
        for n in chord.notes:
            new_notes.append(n)
    
    return new_notes

