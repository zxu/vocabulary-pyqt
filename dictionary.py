import pandas as pd


class Dictionary:
    def __init__(self):
        self.data = pd.DataFrame()

    def load(self):
        def read_groups(group, _range):
            file_names = [group + '-' + str(i) for i in _range]
            group_names = [group.capitalize() + ' ' + str(i) for i in _range]

            _list = []
            for index, elem in enumerate(file_names):
                df = pd.read_csv('data/' + elem + '.csv', header=None)
                df.columns = ['Word']
                df["Group"] = group_names[index]
                _list.append(df)

            return pd.concat(_list)

        _list = []
        _list.append(read_groups('common', range(1, 7)))
        _list.append(read_groups('basic', range(1, 6)))

        df = pd.concat(_list)
        df.reset_index(drop=True, inplace=True)
        self.data = df
