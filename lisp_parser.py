from pygame import mixer
from pyparsing import OneOrMore, nestedExpr

from midivectors import Midi

with open("chorales.lisp") as fp:
    inputdata = fp.read()

data = [{j[0]:int(j[1]) for j in i} for i in OneOrMore(nestedExpr()).parseString(inputdata)[0][1:]]
data += [{j[0]:int(j[1]) for j in i} for i in OneOrMore(nestedExpr()).parseString(inputdata)[1][1:]]

notes = [Midi.Note(note=i['pitch'], time=i['st'], length=i['dur']) for i in data]

print(notes)

m = Midi(
    notes=notes,
    subdivisions_per_beat=4
)

midi_file = m.to_midi()
midi_file.save('standard_2.mid')

mixer.init()
mixer.music.load('standard_2.mid')
mixer.music.play()

while True:
    pass
