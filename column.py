import pandas as pd
import numpy as np
import typing

class Column:
    """
    Column data and statistics. Note, data is stored as string, regardless of the actual numeric data type.
    """
    def __init__(self, column_name, column_dtype, column_data):
        self.column_name = column_name
        self.column_dtype = column_dtype
        self.column_data = column_data
        self.format_string = ''
        self.visible = True
        self.hidden_string = '.'
        self.stats = None
        self.width = 10
        self.justified = '<'

    @staticmethod
    def test_float(x):
        try:
            _ = float(x)
            return '.' in str(x)
        except:
            return False

    @staticmethod
    def test_int(x):
        try:
            _ = int(x)
            return True
        except:
            return False

    def toggle_visibility(self):
        self.visible = not self.visible

    def toggle_justification(self):
        if self.justified == '<':
            self.justified = '>'
        else:
            self.justified = '<'

    def compute_width(self, exclude_name=True):
        if len(self.format_string) > 0:
            maxlen = max([len(f'{x:self.format_string}') for x in self.column_data])
        elif Column.test_float(self.column_dtype(1)):
            decimal_split = [ x.split('.') for x in self.column_data ]
            # get the maximum number of digits before the decimal point
            number_after_decimal = max([ len(ds[1]) for ds in decimal_split if len(ds) == 2])
            # get the maximum number of digits after the decimal point
            number_before_decimal = max([ len(ds[0]) for ds in decimal_split if len(ds) == 2])
            maxlen = number_before_decimal + number_after_decimal + 1
            self.format_string=f'{maxlen}.{number_after_decimal}f'
        else:
            maxlen = max([len(x) for x in self.column_data])
        if not exclude_name:
            maxlen = max(len(self.column_name), maxlen)
        return maxlen

    def adjust_width(self, direction, amount):
        if direction == '+':
            self.width += amount
        elif direction == '-':
            self.width -= amount
        if self.width < 1:
            self.width = 1

    def set_width(self, width):
        self.width = width
        if self.width < 1:
            self.width = 1

    def get_width(self):
        return self.width if self.visible else len(self.hidden_string)

    def get_column_display(self):
        return f'{self.column_name}' if self.visible else 'H'

    def get_value(self,index):
        if len(self.format_string) > 0:
            value = f'{{0:{self.format_string}}}'.format(self.column_data[index])
        else:
            value = f'{self.column_data[index]}'
        return self.format_value(value)

    def format_value(self, value):
            if self.visible:
                value = f'{value:{self.justified}{self.width}}'
                return value[0:self.width]
            else:
                return self.hidden_string

    def get_stats(self):
        if type(self.stats) == type(None):
            if np.issubdtype(self.column_dtype, np.integer) or np.issubdtype(self.column_dtype, np.float):
                typed_data = [x for x in self.column_data if not np.isnan(x)]
                self.stats = { 'Quantiles': {'levels':np.arange(0,1.05,0.05),
                                             'values':np.quantile(typed_data, np.arange(0,1.05,0.05))},
                               'mean':np.mean(typed_data),
                               'nan':len([x for x in self.column_data if np.isnan(x)]) }
            else:
                self.stats = { 'counts': pd.value_counts(self.column_data)}
        return self.stats

    def get_histogram(self, N):
        if self.column_dtype in [int, float]:
            stats = self.get_stats()
            return np.histogram([x for x in self.column_data if not np.isnan(x)],N)
        else:
            return None


