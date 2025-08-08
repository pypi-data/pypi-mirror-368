"""Main module."""
import openpyxl as op
import xlrd
import csv
import json
import datetime
import re
import inspect
import tempfile
import os
import io
import random

from itertools import zip_longest


# Main purpose of martens, dataset class
class Dataset(dict):

    # To initialise a Dataset should be either:
    # -> A dict of {string : list} of equal length or
    # -> A list of dicts of {column_name : value,}
    # In the latter case the engine will generate None values for any missing column names in each record
    def __init__(self, template, sanitise_names=False):
        super().__init__()
        assert isinstance(template, dict) or isinstance(template, list), \
            "Type error: Template is not a dict or list"
        if isinstance(template, dict):
            assert all(isinstance(template[col], list) for col in template), \
                "Type error: Some dictionary entries are not lists"
            assert len(list(set([len(template[column]) for column in template]))) <= 1, \
                "Type Error: Columns must be equal length"
            for col in template:
                if sanitise_names:
                    self[__sanitise_column_name__(col)] = template[col]
                else:
                    self[col] = template[col]
        else:
            assert all(isinstance(record, dict) for record in template), \
                "Type error: Some records are not dicts"
            columns = set().union(*(record.keys() for record in template))
            self.update({col: [record.get(col) for record in template] for col in columns})

    def slice(self, start=None, stop=None, step=None):
        return Dataset({col: self[col][slice(start, stop, step)] for col in self.columns})

    def filter(self, filter_by, var=None):
        if callable(filter_by):
            applied = self.apply(filter_by)
            assert all(isinstance(item, bool) for item in applied), "Some returns are not boolean"
            return Dataset({col: [x[0] for x in zip(self[col], applied) if x[1]] for col in self})
        else:
            assert var is not None, "Var must be supplied unless func is callable"
            return Dataset({col: [x[0] for x in zip(self[col], self[var]) if x[1] == filter_by] for col in self})

    def apply(self, func):
        assert callable(func), "Apply requires a callable argument"
        params = inspect.signature(func).parameters
        required = [
            name for name, param in params.items()
            if param.default is param.empty
               and param.kind in (param.POSITIONAL_OR_KEYWORD, param.KEYWORD_ONLY)
        ]
        assert all(param in self for param in required), \
            f"Missing required argument(s): {[p for p in required if p not in self]}"
        arg_names = [name for name in params if name in self]
        arg_columns = [self[name] for name in arg_names]
        if not arg_names:
            return [func() for _ in range(self.record_length)]
        else:
            return [func(**dict(zip(arg_names, row))) for row in zip(*arg_columns)]

    def long_apply(self, func):
        assert callable(func), "Long apply requires a callable argument"
        params = inspect.signature(func).parameters
        assert all(param in self for param in params), \
            "Function arguments do not correspond to available columns"
        return func(**{param: self[param] for param in params})

    # TODO: This will definitely be bugged if the user doesn't sort using the group_bys first
    def window_apply(self, func, window=1, grouping_cols=None):
        assert callable(func), "Window apply requires a callable argument"
        params = list(inspect.signature(func).parameters)
        assert all(name in self for name in params), "All function parameters must match keys in self"
        if grouping_cols is not None:
            results = []
            current_group = None
            group_start = 0
            for i in range(self.record_length):
                group_key = tuple(self[col][i] for col in grouping_cols)
                if group_key != current_group:
                    current_group = group_key
                    group_start = i
                window_start = max(group_start, i - window + 1)
                results.append(func(**{name: self[name][window_start:i + 1] for name in params}))
            return results
        else:
            return [
                func(**{name: self[name][max(0, i - window + 1):i + 1] for name in params})
                for i in range(self.record_length)
            ]

    def rolling_apply(self, func, grouping_cols=None):
        assert callable(func), "Rolling apply requires a callable argument"
        params = inspect.signature(func).parameters
        assert len(params) == 1, "Rolling apply function can only accept one argument"
        name = next(iter(params))
        rtn = []
        if grouping_cols is not None:
            grouped_col = self.group_by(grouping_cols)[name]
            for each_list in grouped_col:
                val_list = []
                for val in each_list:
                    val_list.append(val)
                    rtn.append(func(val_list))
        else:
            vals = []
            for val in self[name]:
                vals.append(val)
                rtn.append(func(vals))
        return rtn

    def mutate(self, mutation, name=None):
        return self.__with__({name if name is not None else mutation.__name__: self.apply(mutation)})

    def long_mutate(self, mutation, name=None):
        result = self.long_apply(mutation)
        assert isinstance(result, list), "Some returns are not lists"
        assert len(result) == self.record_length, "Some returns are not same length as record length"
        return self.__with__({name if name is not None else mutation.__name__: result})

    # TODO: This will definitely be bugged if the user doesn't sort using the group_bys first
    def window_mutate(self, mutation, window, grouping_cols=None, name=None):
        result = self.window_apply(mutation, grouping_cols=grouping_cols, window=window)
        return self.__with__({name if name is not None else mutation.__name__: result})

    def rolling_mutate(self, mutation, grouping_cols=None, name=None):
        result = self.rolling_apply(func=mutation, grouping_cols=grouping_cols)
        return self.__with__({name if name is not None else mutation.__name__: result})

    def replace(self, mutation, included_names=None, excluded_names=None):
        if included_names is not None:
            names = included_names
        elif excluded_names is not None:
            names = [n for n in self.columns if n not in excluded_names]
        else:
            return self
        return self.__with__({name: [mutation(c) for c in self[name]] for name in names})

    # This is the pivot table where you make a column into lots of headings
    def column_squish(self, grouping_cols, headings, values, prefix=''):
        for var, name in zip([headings, values], ['Headings', 'Values']):
            assert isinstance(var, str), name + ' must be a string'
            assert var in self.columns, name + ' must be a column in this dataset'
        rtn = self.group_by(grouping_cols=grouping_cols, other_cols=[headings, values])
        new_headings = sorted(set(self[headings]))
        for heading in new_headings:
            rtn[prefix + heading] = [next(
                (value for heading_inner, value in zip(rec[headings], rec[values])
                 if heading_inner == heading
                 ), None) for rec in rtn.records]
        return rtn.select(grouping_cols + [prefix + h for h in new_headings])

    def series_list(self, names):
        return [self[name] for name in names]

    def pivot_chart_constructor(self, x_name, y_name, colour, x_sort_keys=None, colour_sort_keys=None, as_secondary=False):
        sec = 'sec_' if as_secondary else ''
        grouping_cols = colour_sort_keys + [colour] if colour_sort_keys is not None else [colour]
        colours = self.group_by(grouping_cols, other_cols=[])[colour]
        grouping_cols = x_sort_keys + [x_name] if x_sort_keys is not None else [x_name]
        x_values = self.group_by(grouping_cols, other_cols=[])[x_name]
        rtn_values = []
        rtn_names = colours
        for c in colours:
            data = [self.filter(c, colour).filter(x, x_name) for x in x_values]
            rtn_values.append([d.first[y_name] if d.record_length > 0 else None for d in data])
        rtn = {sec + 'y_values': rtn_values, sec + 'y_names': rtn_names}
        if not as_secondary:
            rtn['x_values'] = x_values
        return rtn

    def chart_constructor(self, x_name, y_names, x_sort_keys=None, colours=None, as_secondary=False):
        data = self.sort(x_sort_keys) if x_sort_keys else self
        sec = 'sec_' if as_secondary else ''
        rtn_values = [data[y_name] for y_name in y_names]
        rtn_names = y_names
        x_values = data[x_name]
        rtn = {sec + 'y_values': rtn_values, sec + 'y_names': rtn_names}
        if not as_secondary:
            rtn['x_values'] = x_values
        return rtn

    # This is kind of the reverse pivot where you stack lots of headings on top of each other
    def headings_squish(self, grouping_cols, headings, value_name, heading_name):
        return stack([Dataset({
            **{g: self[g] for g in grouping_cols},
            heading_name: [h] * len(self[h]),
            value_name: self[h]
        }) for h in headings])

    # These variants of mutate deal with functions that output multiple value where you want multiple columns
    def mutate_stretch(self, mutation, names):
        assert isinstance(names, list) or isinstance(names, dict), "Names should be a list or dict of string:function"
        results = self.apply(mutation)
        assert all([isinstance(r, list) for r in results]), "Some mutate results are not lists"
        assert all([len(r) == len(names) for r in results]), "Some results are not the same length as names"
        if isinstance(names, list):
            new = {name: list(res) for name, res in zip(names, zip(*results))}
        else:
            new = {name: [names[name](x) for x in res] for name, res in zip(names, zip(*results))}
        return Dataset({**self.__existing__, **new})

    # ... or where you want to stack the results
    # TODO: Can I use either with or existing in this section
    def mutate_stack(self, mutation, name=None, save_len=None, enumeration=None):
        new_name = name if name is not None else mutation.__name__
        return self.mutate(mutation, 'temp_col_mutate_stack') \
            .column_stack('temp_col_mutate_stack', new_name, save_len, enumeration) \
            .drop(['temp_col_mutate_stack'])

    # TODO: Check if the records are all dicts
    # This function is great for stretching out record data into
    def record_stretch(self, name, drop=True):
        seen = set()
        all_keys = []
        for record in self[name]:
            for key in record:
                if key not in seen:
                    seen.add(key)
                    all_keys.append(key)
        new = {key: [rec[key] if key in rec else None for rec in self[name]] for key in all_keys}
        return Dataset({**self.__without__([name] if drop else []), **new})

    # TODO: Check if all the records are lists
    # This is where you have a column which just has lists and you need those lists over multiple rows
    def column_stack(self, name, new_name=None, save_len=None, enumeration=None):
        existing = {col: [val for val, res in zip(self[col], self[name]) for _ in res] for col in self if
                    col not in name}
        indexes, new_data, length = zip(*[(index, val, len(rec)) for rec in self[name] for index, val in enumerate(rec)])
        new = {name if new_name is None else new_name: list(new_data)}
        if save_len is not None:
            new[save_len] = list(length)
        if enumeration is not None:
            new[enumeration] = list(indexes)
        return Dataset({**existing, **new})

    # This is for when you have a column of datasets and you want a new dataset that is stacked of these columns
    def data_column_stack(self, name: str, additional_columns: list = None, as_intersection: bool = False):
        if additional_columns is None: additional_columns = []
        return stack([
            row[0].with_constants({col: row[i + 1] for i, col in enumerate(additional_columns)})
            for row in self.generator([name] + additional_columns)
        ], as_intersection=as_intersection)

    def json_explode(self, name):
        in_scope_columns = [name]
        rtn = self
        while in_scope_columns:
            col = in_scope_columns.pop()
            if all(isinstance(element, dict) for element in rtn[col]):
                old_cols = rtn.columns
                rtn = rtn.record_stretch(col)
                in_scope_columns.extend([col for col in rtn.columns if col not in old_cols])
            elif all(isinstance(element, list) for element in rtn[col]):
                rtn = rtn.column_stack(col)
                in_scope_columns.append(col)
        return rtn

    def mutate_explode(self, mutation):
        return self.mutate(mutation, 'temp_col_mutate_explode') \
            .json_explode('temp_col_mutate_stack') \
            .drop(['temp_col_mutate_stack'])

    # Adding a simple ID to a dataset
    def with_id(self, name='id', grouping_cols=None):
        if grouping_cols is not None:
            ids = []
            current_group = None
            current_id = 0
            for i in range(self.record_length):
                group_key = tuple(self[col][i] for col in grouping_cols)
                if group_key != current_group:
                    current_group = group_key
                    current_id = 0
                ids.append(current_id)
                current_id += 1
        else:
            ids = list(range(self.record_length))
        return self.__with__({name: ids})

    # Adding a simple constant to a dataset
    def with_constant(self, value, name):
        return self.__with__({name: [value] * self.record_length})

    # Adding multiple constants to a dataset using (name, value) dict
    def with_constants(self, input_dict):
        assert isinstance(input_dict, dict), "input_dict should be a dictionary"
        rtn = self
        for key in input_dict:
            rtn = rtn.with_constant(input_dict[key], key)
        return rtn

    def __with__(self, new):
        return Dataset({**self.__existing__, **new})

    def select(self, names, allow_missing=False):
        try:
            names = list(names)
        except TypeError:
            raise TypeError(f"'names' must be an iterable of strings, got {type(names).__name__}")
        if allow_missing:
            return Dataset({name: self[name] for name in names if name in self})
        else:
            return Dataset({name: self[name] for name in names})

    def drop(self, names):
        assert isinstance(names, list), "Type error: Not a list of names"
        return Dataset({name: self[name] for name in self.columns if name not in names})

    # Neat little sorting function
    def sort(self, names, reverse=False):
        assert isinstance(names, list), "Type error: Not a list of names"
        assert all([name in self.columns for name in names]), "Columns do not match"
        sort_order = names + [col for col in self.columns if col not in names]
        sorted_data = sorted(zip(*[self[col] for col in sort_order]), reverse=reverse, key=lambda x: x[0:len(names)])
        rtn = {c: list(v) for c, v in zip(sort_order, zip(*sorted_data))}
        return Dataset({col: rtn[col] for col in sort_order})

    def group_by(self, grouping_cols, other_cols=None, count=None):
        assert isinstance(grouping_cols, list), "Type error: grouping_col should be a list"
        oth_cols = other_cols if other_cols is not None else []
        isinstance(oth_cols, list), "Type error: other_cols should be a list or None"
        # assert isinstance(count, str), "Type error: with_count should be a string"

        sorts = self.sort(grouping_cols)

        last_grouped = None
        rtn = dict()

        for col in grouping_cols + oth_cols + ([count] if count is not None else []):
            rtn[col] = list()

        for rec in sorts.records:
            grouped = [rec[g] for g in grouping_cols]
            if grouped == last_grouped:
                for o in oth_cols:
                    rtn[o][-1].append(rec[o])
                if count is not None:
                    rtn[count][-1] = rtn[count][-1] + 1
            else:
                for g in grouping_cols:
                    rtn[g].append(rec[g])
                for o in oth_cols:
                    rtn[o].append([rec[o]])
                if count is not None:
                    rtn[count].append(1)
            last_grouped = grouped

        return Dataset(rtn)

    def unique_by(self, names):
        return Dataset({name: list(val) for name, val in zip(names, zip(*sorted(set(zip(*[self[n] for n in names])))))})

    def merge(self, right, on=None, how='inner'):

        # TODO: handle error if user tries to merge on columns that don't exist
        # TODO: handle error if user tries to merge a dataset containing only the key columns
        # TODO: handle a bug if a user tries to merge a dataset with a column that exists in both but is not part of the merge
        assert isinstance(right, Dataset), "Type error: Right is not a dataset"
        assert how in ['inner', 'left', 'right', 'full'], "Expecting how to be 'inner', 'left', 'right' or 'full'"

        if on is None:
            return self.full_outer_merge(right)

        assert isinstance(on, list), "Type error: Keys are not a list"

        def tuple_key(cols):
            return tuple(cols[i] for i in range(len(on)))

        left_sorted = self.sort(on)
        right_sorted = right.sort(on)

        left_keys = set(tuple(rec[key] for key in on) for rec in left_sorted.records)
        right_keys = set(tuple(rec[key] for key in on) for rec in right_sorted.records)

        left_columns = left_sorted.columns
        right_columns = right_sorted.columns

        left_zipped = list(zip(*[left_sorted[col] for col in left_columns]))
        right_zipped = list(zip(*[right_sorted[col] for col in right_columns]))

        left_zip_len = len(left_zipped)
        right_zip_len = len(right_zipped)

        rtn = Dataset({col: [] for col in left_columns + [c for c in right_columns if c not in left_columns]})

        if how == 'inner':
            all_keys = sorted(left_keys & right_keys)
        elif how == 'right':
            all_keys = sorted(right_keys)
        elif how == 'left':
            all_keys = sorted(left_keys)
        else:
            all_keys = sorted(left_keys | right_keys)

        left_organised, right_organised = [], []
        for which, zipped, zipped_len in [('left', left_zipped, left_zip_len), ('right', right_zipped, right_zip_len)]:
            index = 0
            for key in all_keys:
                to_add = []
                while index < zipped_len:
                    key_tuple = tuple_key(zipped[index])
                    if key_tuple < key:
                        index = index + 1
                    elif key_tuple == key:
                        to_add.append(zipped[index])
                        index = index + 1
                    else:
                        break

                if not to_add and how not in [which, 'inner']:
                    to_add = [[None] * len(left_columns)]

                if which == 'left':
                    left_organised.append(to_add)
                else:
                    right_organised.append(to_add)

        for key, left_to_add, right_to_add in zip(all_keys, left_organised, right_organised):
            for left_add in left_to_add:
                for right_add in right_to_add:
                    for index, col in enumerate(on):
                        rtn[col].append(key[index])

                    for index, col in enumerate(left_columns):
                        if col not in on:
                            rtn[col].append(left_add[index])

                    for index, col in enumerate(right_columns):
                        if col not in on:
                            rtn[col].append(right_add[index])

        return rtn

    def full_outer_merge(self, right):
        assert isinstance(right, Dataset), "Type error: not a dataset"
        assert self.column_length + right.column_length == len(set(self.columns + right.columns))
        left_length, right_length = self.record_length, right.record_length
        return Dataset({
            **{col: [val for val in self[col] for _ in range(right_length)] for col in self.columns},
            **{col: [val for _ in range(left_length) for val in right[col]] for col in right.columns}
        })

    def rename(self, rename_map):
        return Dataset({(rename_map[c] if c in rename_map else c): self[c] for c in self.columns})

    def rename_and_select(self, rename_map):
        return Dataset({rename_map[c]: self[c] for c in rename_map})

    def generator(self, names=None):
        return zip(*[self[name] for name in (names if names is not None else self.columns)])

    def write_csv(self, file_path, mode='w'):
        with open(file_path, mode, newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=self.columns)
            writer.writeheader()
            for record in self.records:
                writer.writerow(record)

    def fill_none(self, value):
        return Dataset({col: [value if val is None else val for val in self[col]] for col in self.columns})

    def __str__(self):
        columns = self.columns
        print_widths = [max([len(str(val)) for val in self[col]] + [len(col)]) + 1 for col in columns]

        rtn = '|'
        for column, width in zip(columns, print_widths):
            rtn += column.ljust(width) + '|'
        rtn += '\n'

        for record in self.records:
            rtn += '|'
            for column, width in zip(columns, print_widths):
                value = record[column]
                str_value = str(value)
                if isinstance(value, (int, float, datetime.date, datetime.date)):
                    rtn += str_value.rjust(width)
                else:
                    rtn += str_value.ljust(width)
                rtn += '|'
            rtn += '\n'

        return rtn

    def first_n(self, n=10):
        return Dataset({col: self[col][0:n] for col in self})

    def random_n(self, n=10, seed=0):
        random.seed(seed)
        return self.mutate(lambda: random.random(), '__random__').sort(['__random__']).drop(['__random__']).first_n(n)

    # Unstack dataset according to the result of some function
    def unstack(self, func):
        keys = [int(x) for x in self.apply(func)]
        unique_keys = sorted(set(keys))
        index_groups = {k: [i for i, val in enumerate(keys) if val == k] for k in unique_keys}
        return [Dataset({col: [self[col][i] for i in index_groups[k]] for col in self.keys()}) for k in unique_keys]

    def guess_types_with_template(self, date_formats: list[str] = None, datetime_formats: list[str] = None) -> "Dataset":
        date_formats = date_formats or ["%d-%m-%Y", "%d/%m/%Y"]
        datetime_formats = datetime_formats or ["%Y-%m-%d %H:%M:%S", "%Y/%m/%d %H:%M:%S"]
        casters = [
            lambda v: int(v) if "." not in v else __raise__(ValueError),
            float,
            lambda v: {"true": True, "1": True, "false": False, "0": False}[v.lower()],
        ]
        casters.extend([lambda v: datetime.datetime.strptime(v, fmt).date() for fmt in date_formats])
        casters.extend([lambda v: datetime.datetime.strptime(v, fmt) for fmt in datetime_formats])

        def try_cast_column(values: list[str]) -> list:
            for caster in casters:
                try:
                    return [caster(v) if v != "" else None for v in values]
                except Exception:
                    continue
            return values

        return Dataset({col: try_cast_column(self[col]) for col in self})

    def column_lookup(self, values_col, name):
        return self.__with__({name: [rec.get(key) for key, rec in zip(self[values_col], self.records)]})

    @property
    def infer_types(self):
        return self.guess_types_with_template()

    @property
    def headings_camel_to_snake(self):
        return Dataset({__camel_to_snake__(col): self[col] for col in self.columns})

    @property
    def headings_lower(self):
        return Dataset({col.lower(): self[col] for col in self.columns})

    @property
    def rows(self):
        return [row for row in zip(*[self[col] for col in self])]

    @property
    def records(self):
        return [{col: val for col, val in zip(self.columns, row)} for row in zip(*[self[col] for col in self])]

    @property
    def records_sparse(self):
        return [{col: val for col, val in zip(self.columns, row) if val is not None} for row in
                zip(*[self[col] for col in self])]

    @property
    def first(self) -> dict:
        return {col: self[col][0] for col in self}

    @property
    def record_length(self):
        return len(self.records)

    @property
    def columns(self):
        return [col for col in self]

    @property
    def column_length(self):
        return len(self.columns)

    @property
    def pretty(self):
        return json.dumps(self, indent=4)

    @property
    def __existing__(self):
        return {col: self[col] for col in self}

    def __without__(self, without):
        return {col: self[col] for col in self if col not in without}


# A class used to parse data from source files and access the Dataset
class SourceFile:

    def __init__(self, file_path, sheet_name=None, from_row=0, from_col=0,
                 file_type=None, to_row=None, to_col=None, date_columns=None, using_range=None):
        self.file_path = file_path
        file_tokens = file_path.split('.')
        assert len(file_tokens) > 1, "Data Error: Please include file extension in path"
        self.file_type = file_tokens[-1] if file_type is None else file_type
        self.sheet_name = sheet_name
        self.from_row = from_row
        self.from_col = from_col
        self.to_row = to_row
        self.to_col = to_col
        self.date_columns = [] if date_columns is None else date_columns
        if using_range is not None:
            self.from_row, self.from_col, self.to_row, self.to_col = parse_excel_range(using_range)

    @property
    def dataset(self) -> Dataset:
        return getattr(self, 'file_read_' + self.file_type)

    def conditional_xls_float_to_date(self, value, book, index):
        return datetime.datetime(
            *xlrd.xldate_as_tuple(value, book.datemode)).date() if index in self.date_columns else value

    @property
    def file_read_xlsx(self):
        workbook = op.load_workbook(filename=self.file_path, data_only=True)
        sheet = workbook[self.sheet_name] if self.sheet_name else workbook.worksheets[0]
        trim_col = len([x for x in sheet.columns]) if self.to_col is None else self.to_col
        return Dataset({
            __sanitise_column_name__(col[self.from_row].value):
                [cell.value for cell in col[self.from_row + 1:self.to_row]]
            for index, col in enumerate(sheet.columns) if index < trim_col
        })

    @property
    def file_read_xls(self):
        book = xlrd.open_workbook(self.file_path)
        sheet = book.sheet_by_name(self.sheet_name) if self.sheet_name else book.sheet_by_index(0)
        col_limit = sheet.ncols if self.to_col is None else self.to_col
        columns = [sheet.col_values(col) for col in range(self.from_col, col_limit)]
        return Dataset({
            __sanitise_column_name__(col[self.from_row]):
                [
                    self.conditional_xls_float_to_date(cell, book, index)
                    if cell != '' else None for cell in col[self.from_row + 1:self.to_row]
                ]
            for index, col in enumerate(columns)
        })

    @property
    def file_read_csv(self):
        with open(self.file_path, newline='', encoding='utf-8-sig') as f:
            reader = csv.reader(f)
            for _ in range(self.from_row):
                next(reader, None)
            header_row = next(reader, None)
            if not header_row:
                raise ValueError(f"Header row is missing or empty for {self.file_path}")
            headers = [__sanitise_column_name__(w) for w in header_row][self.from_col:self.to_col]
            if self.to_row:
                row_count = self.to_row - self.from_row
                rows = [next(reader, None) for _ in range(row_count)]
                rows = [r for r in rows if r is not None]
            else:
                rows = [row for row in reader if row and any(cell.strip() for cell in row)]
            rawdata = [list(d) for d in zip_longest(*rows, fillvalue='')][self.from_col:self.to_col]
            return Dataset({h: d for h, d in zip(headers, rawdata)})

    @property
    def file_read_json(self):
        return Dataset(json.loads(open(self.file_path).read()))


class SourceStream(SourceFile):
    def __init__(self, stream, file_type="csv", sheet_name="Sheet1", from_row=0, from_col=0,
                 to_row=None, to_col=None, date_columns=None, using_range=None):
        file_type = file_type.lower()
        suffix = f".{file_type}"
        mode = 'w+b' if isinstance(stream, io.BytesIO) else 'w+'
        self._temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix, mode=mode)
        self._temp_file.write(stream.getvalue())
        self._temp_file.flush()
        self._temp_file.close()
        super().__init__(
            file_path=self._temp_file.name,
            sheet_name=sheet_name,
            from_row=from_row,
            from_col=from_col,
            file_type=file_type,
            to_row=to_row,
            to_col=to_col,
            date_columns=date_columns,
            using_range=using_range
        )

    def __del__(self):
        try:
            os.remove(self._temp_file.name)
        except Exception:
            pass


def __sanitise_column_name__(column_name):
    replace_map = {
        ':': '',
        ' ': '_',
        ')': '',
        '(': '_',
        '.': '_',
        "'": '',
        '%': 'pct',
        '+': 'plus',
        '-': '_',
        '"': ''
    }
    column_name = str(column_name)
    for k in replace_map:
        column_name = column_name.replace(k, replace_map[k])
    return column_name


def __camel_to_snake__(camel):
    return re.sub(r'(?<!^)(?=[A-Z])', '_', camel).lower()


def initialise(id_length, id_name='id'):
    return Dataset({id_name: list(range(id_length))})


def average(input_list):
    return sum(input_list) / len(input_list)


def median(input_list):
    s = sorted(input_list)
    n = len(s)
    return s[n // 2] if n % 2 else (s[n // 2 - 1] + s[n // 2]) / 2


def __raise__(ex):
    raise ex


def stack(list_of_datasets: list, as_intersection: bool = False):
    if not isinstance(list_of_datasets, list):
        raise TypeError("Type error: Not a list")
    if not all(isinstance(element, Dataset) for element in list_of_datasets):
        raise TypeError("Type error: Not a list of Datasets")

    if not list_of_datasets:
        return Dataset({})

    cols = [x for x in list_of_datasets[0]]

    if as_intersection:
        # Find columns that exist in ALL datasets (intersection)
        common_cols = set(cols)
        for dataset in list_of_datasets[1:]:
            common_cols = common_cols.intersection(set(dataset.columns))

        # Preserve the order from the first dataset
        cols = [col for col in cols if col in common_cols]

        if not cols:
            raise ValueError("No common columns found across all datasets")
    else:
        # Original behavior - require all datasets to have same columns
        if not all(sorted(cols) == sorted([x for x in y]) for y in list_of_datasets):
            raise ValueError("Available columns do not correspond")

    return Dataset({col: [val for element in list_of_datasets for val in element[col]] for col in cols})


def excel_column_name_to_number(col):
    num = 0
    for c in col:
        num = num * 26 + ord(c.upper()) - ord('A') + 1
        return num


def parse_excel_range(excel_range):
    pattern = r'^([A-Za-z]+)(\d+):([A-Za-z]+)(\d+)$'
    if match := re.match(pattern, excel_range):
        start_col_str, start_row_str, end_col_str, end_row_str = match.groups()
        start_col = excel_column_name_to_number(start_col_str)
        end_col = excel_column_name_to_number(end_col_str)
        start_row = int(start_row_str)
        end_row = int(end_row_str)
        return start_row - 1, start_col - 1, end_row, end_col
    else:
        return 0, 0, None, None
