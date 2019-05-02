import pandas as pd
import numpy as np

import midivectors

data = pd.read_csv('chorales.csv', names=[
    'name', 'event number', 'C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B', 'bass', 'meter', 'chord'
])

songs = data.name.unique()

vectors = []

for i, song_name in enumerate(songs):
    this_song = data.loc[data['name'] == song_name][['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']]
    song = np.where(this_song.values == 'YES', 1, 0).T

    tps = midivectors.chromatic_transpositions(song)
    for tp in tps:
        parts = midivectors.length_conform(tp)
        for part in parts:
            vec = midivectors.matrix_to_stacked_vector(part)
            vectors.append(vec)

new_data = np.vstack(vectors)

np.save('chorales_vectors_12.npy', new_data)
