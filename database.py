import base64
import sqlite3

import pandas

import helps
from helps import communicate

class Database:
    def __init__(self):
        self.db = sqlite3.connect('data/words.db')
        self.cursor = self.db.cursor()
        self.marked_indices = []
        self.marked_indices_set = set()

        try:
            self.cursor.execute('CREATE TABLE IF NOT EXISTS `marked` (`word` TEXT, '
                                '`index` INTEGER, PRIMARY KEY(`word`))')
            self.cursor.execute(
                'CREATE TABLE IF NOT EXISTS `settings` (`type` TEXT, `value` TEXT, PRIMARY KEY(`type`))')
            self.db.commit()
            self.update_marked_indices_cache()
        except sqlite3.Error:
            self.db.rollback()

    def mark(self, word, _index):
        if word is None:
            return
        try:
            self.cursor.execute('INSERT INTO `marked` (`word`, `index`) VALUES (?, ?)', (word, _index))
            self.db.commit()
            self.update_marked_indices_cache()
        except sqlite3.Error:
            self.db.rollback()

    def un_mark(self, word):
        if word is None:
            return
        try:
            self.cursor.execute('DELETE FROM `marked` where (`word`) = ?', (word,))
            self.db.commit()
            self.update_marked_indices_cache()
        except sqlite3.Error:
            self.db.rollback()

    def save_settings(self, _type, value):
        if _type is None or value is None:
            return
        try:
            self.cursor.execute('INSERT OR REPLACE INTO `settings` (`type`, `value`) VALUES (?, ?)',
                                (_type, base64.encodebytes(value)))
            self.db.commit()
        except sqlite3.Error:
            self.db.rollback()

    def load_settings(self, _type):
        if _type is None:
            return None
        try:
            self.cursor.execute('SELECT `value` FROM `settings` WHERE `type` = ?', (_type,))
            data = self.cursor.fetchone()
            return data[0] if data else data
        except sqlite3.Error:
            return None

    def is_marked(self, word: str):
        if word is None:
            return False
        try:
            self.cursor.execute('SELECT count(*) FROM `marked` WHERE `word` = ?', (word,))
            data = self.cursor.fetchone()[0]
            if data == 0:
                return False
            else:
                return True
        except sqlite3.Error:
            return False

    def is_marked(self, idx: int):
        return idx in self.marked_indices_set

    def load_marked_indices(self):
        try:
            self.cursor.execute('SELECT `index` FROM `marked` WHERE `index` >= 0')
            data = self.cursor.fetchall()
            indices = []
            for row in data:
                indices.append(row[0])
            return indices
        except sqlite3.Error:
            return []

    def update_marked_indices_cache(self, indices=None):
        self.marked_indices = indices if isinstance(indices, list) else self.load_marked_indices()
        self.marked_indices_set = set(self.marked_indices)

        communicate.total_marked_signal.emit(len(self.marked_indices))

    def marked_as_list(self):
        try:
            self.cursor.execute('SELECT `word` FROM `marked`')
            data = self.cursor.fetchall()
            words = []
            for row in data:
                words.append(row[0])
            return words
        except sqlite3.Error:
            return []

    def update_marked_indices(self, marked_words_with_new_indices: pandas.Series):
        try:
            self.cursor.execute('UPDATE `marked` SET `index` = -1')
            self.db.commit()
        except sqlite3.Error:
            self.db.rollback()
            return

        updated = False
        for i, v in marked_words_with_new_indices.items():
            try:
                self.cursor.execute('UPDATE `marked` SET `index` = ? WHERE `word` = ?',
                                    (i, v))
                updated = True
            except sqlite3.Error:
                self.db.rollback()
                return
        if updated:
            self.db.commit()






