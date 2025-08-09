import warnings
import numpy as np
import pandas as pd
from collections import defaultdict
import json
import requests
warnings.filterwarnings("ignore")


def ctree():
    return defaultdict(ctree)


class CreateHTML:
    def __init__(self, df, vars, y, split_method, min_records, max_integer, max_nr_splits, min_split_values, nr_splits,
                 splits, color_reverse, name_all, reorder):
        self.df = df
        self.vars = vars
        self.y = y
        self.split_method = split_method
        self.min_records = min_records
        self.max_integer = max_integer
        self.max_nr_splits = max_nr_splits
        self.min_split_values = min_split_values
        self.nr_splits = nr_splits
        self.splits = splits
        self.color_reverse = color_reverse
        self.name_all = name_all
        self.reorder = reorder

    def split_loop(self, df, var):
        df_diff = pd.DataFrame(columns=['index', 'mean', 'gini'])

        if df[var].dtype == 'float64':
            range_list = range(0, 100, 5)
            percentile = []
            for i in range_list: # Gaat dat wel goed, percentile nergens meer gebruikt, moet dat niet range_list zijn?
                percentile.append(np.percentile(df[var], i))
            range_list = percentile
        else:
            range_list = df[var].unique()

        for value in range_list:
            lower_part = df[df[var] < value]
            upper_part = df[df[var] >= value]
            if (min(lower_part[self.y].count(), upper_part[self.y].count()) > self.min_split_values):
                df_diff.at[value, 'index'] = value
                df_diff.at[value, 'mean'] = abs(upper_part[self.y].mean() - lower_part[self.y].mean())
                df_diff.at[value, 'gini'] = max(gini_coefficient(lower_part[self.y].to_list()),
                                                gini_coefficient(upper_part[self.y].to_list()))

        if self.split_method == 'gini':
            corresponding_value = df_diff[df_diff['gini'] == df_diff['gini'].max()]['index'].mean()
            optimal_value = df_diff['gini'].max()
        elif self.split_method == 'mean':
            corresponding_value = df_diff[df_diff['mean'] == df_diff['mean'].max()]['index'].mean()
            optimal_value = df_diff['gini'].max()

        return optimal_value, corresponding_value

    def optimal_split(self, df, var, splits):
        optimal_values = []
        correspoding_values = []
        lower_value = -float('inf')
        upper_value = float('inf')

        max_nr_splits = self.max_nr_splits

        if var in self.nr_splits.keys():    # Kan dus meer splits zijn bij variabelen dan de max als je dat aangeeft.
            max_nr_splits = self.nr_splits[var]

        if len(splits) < max_nr_splits:

            if len(splits) == 0:
                optimal_value, corresponding_value = self.split_loop(df, var)

                if np.isfinite(optimal_value):
                    optimal_values.append(optimal_value)
                    correspoding_values.append(corresponding_value)
            else:
                for i in range(len(splits) + 1):
                    if i < len(splits):
                        df_split = df[(df[var] >= lower_value) & (df[var] < splits[i])]
                        lower_value = splits[i]
                    else:
                        df_split = df[(df[var] >= lower_value) & (df[var] < upper_value)]

                    optimal_value, corresponding_value = self.split_loop(df_split, var)

                    if np.isfinite(optimal_value):
                        optimal_values.append(optimal_value)
                        correspoding_values.append(corresponding_value)

            if len(optimal_values) > 0:
                max_value = max(optimal_values)
                max_index = optimal_values.index(max_value)
                new_split = correspoding_values[max_index]
                splits.append(new_split)

            splits = sorted(list(dict.fromkeys(splits)))

            return self.optimal_split(df, var, splits)
        else:
            return splits

    def adjust_variables(self):
        df_adjust = self.df.copy()

        for var in self.vars:
            if (df_adjust[var].dtype == 'float64') or (
                    df_adjust[var].dtype == 'int64' and len(df_adjust[var].unique()) > self.max_integer):

                splits = []

                if var in self.splits.keys():
                    splits = self.splits[var]

                splits = self.optimal_split(df_adjust, var, splits)

                splits.insert(0, -float("inf"))
                splits.insert(len(splits), float("inf"))

                split_labels = []

                for i in range(1, len(splits)):
                    if i == 1:
                        split_labels.append('< ' + str(splits[i]))
                    elif i > 1 and i < len(splits) - 1:
                        split_labels.append('>= ' + str(splits[i - 1]) + ' and < ' + str(splits[i]))
                    elif i == len(splits) - 1:
                        split_labels.append('>= ' + str(splits[i - 1]))

                df_adjust[var] = pd.cut(df_adjust[var], bins=splits, labels=split_labels)

        return df_adjust

    def reorder_variables(self, df):
        df_reorder = pd.DataFrame(columns=['variable', 'gini'])

        for var in self.vars:
            max_gini = 0
            for value in df[var].unique():
                gini = gini_coefficient(df[df[var] == value][self.y].to_list())
                if gini > max_gini:
                    max_gini = gini
            df_reorder.at[var, 'variable'] = var
            df_reorder.at[var, 'gini'] = max_gini

        df_reorder = df_reorder.sort_values(by='gini', ascending=False)
        reorder_list = df_reorder['variable'].tolist()

        return reorder_list

    def make_grouped_dataframe(self):
        '''
        :return: lijst met alle variabelen waarvan tenminste een record leeg of null is
        '''
        df_set = pd.DataFrame()
        df_group = pd.DataFrame()

        df_adjust = self.adjust_variables()

        if self.reorder:
            reorder_list = self.reorder_variables(df_adjust)
            self.vars = reorder_list

        df_base = pd.DataFrame([['all', df_adjust[self.y].count(), df_adjust[self.y].mean()]],
                               columns=['all', 'count0', 'mean0'])

        df_set = df_adjust.groupby(self.vars[0])[self.y].agg(['count', 'mean']).reset_index()
        df_set['all'] = 'all'

        df_set = pd.merge(df_base, df_set, on='all')

        for i in range(1, len(self.vars)):
            df_group = df_adjust.groupby(self.vars[:i + 1])[self.y].agg(['count', 'mean']).reset_index()
            df_set = pd.merge(df_set, df_group, on=self.vars[:i], suffixes=('', str(i + 1)), how='left')

        df_set = df_set.rename(columns={'count': 'count1', 'mean': 'mean1'})

        return df_set

    def build_leaf(self, name, leaf):

        res = {}
        mask = 0

        for key, value in leaf.items():
            if key == 'name':
                res['name'] = value
            if key == 'nodeId':
                res['nodeId'] = value
            if key == 'size':
                res['size'] = value
                if value < self.min_records:
                    mask = 1
            if key == 'prediction':
                res['prediction'] = value
            if key not in ('name', 'nodeId', 'size', 'prediction') and mask == 0:
                res["children"] = [self.build_leaf(k, v) for k, v in leaf.items() if
                                   not k in ('name', 'nodeId', 'size', 'prediction')]

        return res

    def create_JSON(self):

        tree = ctree()

        df_set = self.make_grouped_dataframe()

        nr = 0

        for index, row in df_set.iterrows():
            nr = nr + 1
            leaf = tree[row[0]]
            leaf['name'] = self.name_all
            leaf['nodeId'] = nr
            leaf['size'] = row[1]
            leaf['prediction'] = row[2]

            i = 0

            for value in row[self.vars]:
                i = i + 1
                nr = nr + 1
                leaf = leaf[value]
                leaf['name'] = str(df_set.columns[3 * i]) + ': ' + str(row[3 * i])
                leaf['nodeId'] = nr
                leaf['size'] = row[3 * i + 1]
                leaf['prediction'] = row[3 * i + 2]

        # building a custom tree structure
        res = []

        for name, leaf in tree.items():
            res.append(self.build_leaf(name, leaf))

        # printing results into the terminal
        return json.dumps(res, indent=4)

    def build_HTML(self, output_file, title, explanation, made_by):
        url = 'https://raw.githubusercontent.com/SimonTeg/nlodatascience/refs/heads/master/beslisboom_md_template'
        download = requests.get(url).content
        html = download.decode('UTF-8')

        if not explanation:
            explanation = 'Er is geen uitleg opgenomen.'

        if self.color_reverse:
            color = '1'
        else:
            color = '0'

        json_data = self.create_JSON()
        html = html.replace('___data___', json_data).replace('___title___', title).replace('___color___',
                                                                                           color).replace(
            '___explanation___', explanation).replace('___madeby___', made_by)

        with open(output_file, 'w') as file:
            file.write(html)


def gini_coefficient(list):
    """Calculate the Gini coefficient of a numpy array."""
    # based on bottom eq: http://www.statsdirect.com/help/content/image/stat0206_wmf.gif
    # from: http://www.statsdirect.com/help/default.htm#nonparametric_methods/gini.htm
    array = np.array(list)

    # all values are treated equally, arrays must be 1d
    array = array.flatten()

    # values cannot be negative
    if np.amin(array) < 0:
        array -= np.amin(array)

        # values cannot be 0
    # array += 0.0000001

    array = np.sort(array)
    index = np.arange(1, array.shape[0] + 1)
    n = array.shape[0]

    gini = ((np.sum((2 * index - n - 1) * array)) / (n * np.sum(array)))

    return gini



