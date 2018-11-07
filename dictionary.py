import base64
import glob
import io
import os
import pickle
import random
import re
import zlib

import numpy as np
import pandas as pd

from database import Database
from constants import Settings
from helps import communicate


class Dictionary:
    def __init__(self):
        self.current_word = {}
        self.data = pd.DataFrame()
        self.reviewed = np.zeros((10000,), dtype=int)
        self.reviewed_marked = np.zeros((0,), dtype=int)
        self.total_words = 0

    def total_reviewed(self):
        return np.count_nonzero(self.reviewed)

    def load(self, database: Database, file_names=[]):
        def extract_group_name(file_name):
            m = re.match(r'^\d{2}-(\w*)-(\d*).csv', file_name, re.M)
            if m:
                return '%s %d' % (m.group(1).capitalize(), int(m.group(2)))
            return 'Unknown'

        def load_from_files(_file_names: list):
            _list = []
            for file_name in _file_names:
                _df = pd.read_csv('data/' + file_name, header=None)
                _df.columns = ['Word']
                _df["Group"] = extract_group_name(file_name)
                _list.append(_df)

            return pd.concat(_list)

        def dictionary_files(_database, _file_names):
            if _file_names and len(_file_names) > 0:
                return _file_names
            else:
                if _database:
                    settings = _database.load_settings(Settings.FILE_NAMES)
                    if settings:
                        return pickle.loads(zlib.decompress(base64.decodebytes(settings)))
                    else:
                        return sorted([os.path.basename(file_name)
                                       for file_name in glob.glob('data/*.csv')])
                else:
                    return sorted([os.path.basename(file_name)
                                   for file_name in glob.glob('data/*.csv')])

        file_names_to_load = dictionary_files(database, file_names)
        df = load_from_files(file_names_to_load)
        df.reset_index(drop=True, inplace=True)

        if df.columns.size > 0 and df['Word'].size > 0:
            self.data = df
            self.total_words = df['Word'].size
            if database:
                progress = database.load_settings(Settings.REVIEWED)
                if progress:
                    load = np.load(io.BytesIO(base64.decodebytes(progress)))
                    self.reviewed = load[load.files[0]]

                database.save_settings(Settings.FILE_NAMES, zlib.compress(pickle.dumps(file_names_to_load)))
                database.update_marked_indices_cache()

    def next_word(self, marked_indices):
        column_size = self.data.columns.size
        row_size = self.data['Word'].size
        if column_size > 0 and row_size > 0:
            if marked_indices is not None and len(marked_indices) > 0:
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

        self.emit_progress()
        return self.current_word

    def emit_progress(self):
        communicate.progress_signal.emit(self.total_reviewed(), self.total_words)

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
        self.emit_progress()

    def marked_indices(self, marked_words: list):
        column_size = self.data.columns.size
        if column_size > 0 and self.data['Word'].size > 0:
            return self.data[self.data['Word'].isin(marked_words)]['Word']
        return None
