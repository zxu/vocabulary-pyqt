import base64
import io
import random

import numpy as np
import pandas as pd

from database import Database


class Dictionary:
    def __init__(self):
        self.current_word = {}
        self.data = pd.DataFrame()
        self.reviewed = np.zeros((10000,), dtype=int)
        self.reviewed_marked = np.zeros((0,), dtype=int)
        self.total_words = 0

    def total_reviewed(self):
        return np.count_nonzero(self.reviewed)

    def load(self, database: Database):
        def read_groups(group, _range):
            file_names = [group + '-' + str(i) for i in _range]
            group_names = [group.capitalize() + ' ' + str(i) for i in _range]

            _list = []
            for index, elem in enumerate(file_names):
                _df = pd.read_csv('data/' + elem + '.csv', header=None)
                _df.columns = ['Word']
                _df["Group"] = group_names[index]
                _list.append(_df)

            return pd.concat(_list)

        df = pd.concat([read_groups('common', range(1, 7)),
                        read_groups('basic', range(1, 6))])
        df.reset_index(drop=True, inplace=True)

        if df.columns.size > 0 and df['Word'].size > 0:
            self.data = df
            self.total_words = df['Word'].size
            if database:
                progress = database.load_settings('reviewed')
                if progress:
                    load = np.load(io.BytesIO(base64.decodebytes(progress)))
                    self.reviewed = load[load.files[0]]

    def next_word(self, marked_indices):
        column_size = self.data.columns.size
        row_size = self.data['Word'].size
        if column_size > 0 and row_size > 0:
            if marked_indices and len(marked_indices) > 0:
                if self.reviewed_marked.size != len(marked_indices):
                    self.reviewed_marked = np.resize(self.reviewed_marked, (len(marked_indices),))
                if len(marked_indices) == 1:
                    idx = marked_indices[0]
                else:
                    randint = random.randint(0, len(marked_indices) - 1)
                    if self.reviewed_marked[randint] == 1:
                        randint_new = self.next_different(randint, len(marked_indices), self.reviewed_marked)
                        if randint_new == randint:
                            self.reviewed_marked.fill(0)
                        randint = randint_new
                    self.reviewed_marked[randint] = 1

                    idx = marked_indices[randint]
            else:
                idx = random.randint(0, row_size - 1)
                if self.reviewed[idx] == 1:
                    idx = self.next_different(idx, row_size, self.reviewed)

            if idx > row_size - 1 or idx < 0:
                return {}

            self.current_word['word'] = self.data['Word'][idx]
            self.current_word['idx'] = idx
            self.reviewed[idx] = 1
        return self.current_word

    @staticmethod
    def next_different(idx, row_size, reviewed: np.ndarray):
        r = range(idx + 1, idx + row_size)
        for i in r:
            if reviewed[i % row_size] == 0:
                idx = i % row_size
                break
        return idx

    def reviewed_as_string(self):
        output = io.BytesIO()
        np.savez_compressed(output, self.reviewed)
        return output.getvalue()

    def reset_progress(self):
        self.reviewed = np.zeros((10000,), dtype=int)
