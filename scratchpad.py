import midivectors
from pygame import mixer

'''
m = midivectors.Midi(
    r"dataset/Classical Archives - The Greats (MIDI)/Bach/Jesu Joy of Man Desiring.mid",
    track_index=2,
    octaves=3
)
#m = midivectors.Midi('standard.mid')

midi_file = m.to_midi()
midi_file.save('standard_2.mid')
'''

mixer.init()
mixer.music.load('jsbach_chorals_harmony/0.mid')
mixer.music.play()

while True:
    pass
