from collections import namedtuple

import mido
import numpy as np


class Midi(object):
    Note = namedtuple('MidiNote', ['note', 'time', 'length'])

    def __init__(self, midi_file=None, notes=None, track_index=0, octaves=2, subdivisions_per_beat=4):
        self.__notes = []
        self.__note_range = 12 * octaves
        self.__subdivisions_per_beat = subdivisions_per_beat

        if midi_file is None:
            if notes is not None:
                self.__notes = [Midi.Note(note=i.note % self.__note_range, time=i.time, length=i.length) for i in notes]
        else:
            if type(midi_file) == str:
                file = mido.MidiFile(midi_file)
            else:
                file = midi_file

            track = file.tracks[track_index]
            tpb = file.ticks_per_beat
            ticks_per_sub = tpb / subdivisions_per_beat

            sub = 0
            current_time = 0
            currently_on = {}
            for msg in track:
                if msg.type == 'time_signature':
                    if msg.numerator != 4 or msg.denominator != 4:
                        raise NotImplementedError("Time sig must be 4/4")

                try:
                    note = msg.note % self.__note_range
                    sub_delta = msg.time / ticks_per_sub
                    current_time += sub_delta

                    if msg.type == 'note_on':
                        currently_on[note] = current_time
                    if (msg.type == 'note_off' or msg.velocity == 0) and note in currently_on.keys():
                        self.__notes.append(Midi.Note(
                            note=note,
                            time=currently_on[note],
                            length=current_time - currently_on[note]
                        ))
                        currently_on.pop(note)

                except AttributeError:
                    pass

    def to_midi(self, bpm=120, low_c=48):
        midi = mido.MidiFile()
        track = mido.MidiTrack()
        midi.tracks.append(track)

        track.append(mido.MetaMessage('set_tempo', tempo=mido.bpm2tempo(bpm)))

        sec_per_sub = 60. / bpm / self.subdivisions_per_beat

        subdiv_delta = int(mido.second2tick(
            sec_per_sub,
            midi.ticks_per_beat,
            mido.bpm2tempo(bpm)
        ))

        current_delta = 0
        last_time = 0

        note_on_events = [('note_on', i.note, i.time) for i in self.__notes]
        note_off_events = [('note_off', i.note, i.time + i.length) for i in self.__notes]
        note_events = sorted(note_on_events + note_off_events, key=lambda x: x[2])

        for note_type, note, time in note_events:
            current_time = int((time - last_time) * subdiv_delta)
            track.append(
                mido.Message(note_type, note=note + low_c, velocity=80, time=current_time)
            )
            last_time = time

        return midi

    '''
    def to_matrix(self, track_index=0, octaves=2, subdivisions_per_beat=4, measures=0, trim=True):
        max_length = measures * 4 * subdivisions_per_beat

        note_range = 12 * octaves

        notes = []

        track = self.__file.tracks[track_index]

        tpb = self.__file.ticks_per_beat
        ticks_per_sub = tpb / subdivisions_per_beat
        sub = 0
        current_note = np.zeros(note_range, dtype=np.int)

        for msg in track:
            if msg.type == 'time_signature':
                if msg.numerator != 4 or msg.denominator != 4:
                    raise NotImplementedError("Time sig must be 4/4")

            if len(notes) < max_length or not measures:
                try:
                    note = msg.note % note_range
                    sub_delta = msg.time / ticks_per_sub
                    sub += sub_delta
                    total_subs = int(np.floor(sub))

                    if total_subs:
                        for i in range(total_subs):
                            if len(notes) < max_length or not measures:
                                notes.append(current_note.copy())
                                current_note = np.zeros(note_range, dtype=np.int)
                        sub = 0

                    if msg.type == 'note_on':
                        current_note[note] = 1
                    elif msg.type == 'note_off':
                        current_note[note] = 0

                except AttributeError:
                    pass

        while len(notes) < max_length and measures:
            notes.append(current_note.copy())

        try:
            note_matrix = np.vstack(notes).T
        except ValueError:
            return None

        if trim:
            mask = ~np.all(note_matrix == 0, axis=0)
            note_matrix = note_matrix[:, np.where(mask)[0][0]:]

        return note_matrix
    '''

    @property
    def subdivisions_per_beat(self):
        return self.__subdivisions_per_beat


def matrix_to_midi(matrix, subdivisions_per_beat, bpm=120, low_c=60, hold_notes=False):
    midi = mido.MidiFile()
    track = mido.MidiTrack()
    midi.tracks.append(track)

    track.append(mido.MetaMessage('set_tempo', tempo=mido.bpm2tempo(bpm)))

    sec_per_sub = 60. / bpm / subdivisions_per_beat

    subdiv_delta = int(mido.second2tick(
        sec_per_sub,
        midi.ticks_per_beat,
        mido.bpm2tempo(bpm)
    ))

    for subdivision in range(matrix.shape[1]):
        current_delta = subdiv_delta
        try:
            for note in range(matrix.shape[0]):
                off = matrix[note, subdivision - 1] and not matrix[note, subdivision] if hold_notes \
                    else matrix[note, subdivision - 1]
                on = matrix[note, subdivision] and not matrix[note, subdivision - 1] if hold_notes \
                    else matrix[note, subdivision]

                if off:
                    track.append(mido.Message('note_off', note=note + low_c, velocity=80, time=current_delta))
                    current_delta = 0
                if on:
                    track.append(mido.Message('note_on', note=note + low_c, velocity=80, time=current_delta))
                    current_delta = 0
        except IndexError:
            for note in range(matrix.shape[0]):
                if matrix[note, subdivision]:
                    track.append(mido.Message('note_on', note=note + low_c, velocity=80, time=0))
    return midi


def length_conform(matrix, subdivisions=32, trim=True):
    total_len = matrix.shape[1]
    indices = [i for i in range(total_len) if not i % subdivisions][1:]
    matrices = np.split(matrix, indices, axis=1)
    if trim:
        return [i for i in matrices if i.shape == (matrix.shape[0], subdivisions)]
    return list(matrices)


def chromatic_transpositions(matrix):
    transpositions = []
    note_range = matrix.shape[0]

    for i in range(note_range):
        upper, lower = np.split(matrix, [i], axis=0)
        transpositions.append(np.concatenate((lower, upper), axis=0))
    return transpositions


def matrix_to_stacked_vector(matrix):
    return np.ravel(matrix.T)
