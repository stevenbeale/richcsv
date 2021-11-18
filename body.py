import sys
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.console import Console, ConsoleOptions, RenderResult

from rich import print
import pandas as pd
import numpy as np

from csvdata import CSVData

class Body:
    def __init__(self, csvfile, initial_row=0, initial_column=0):
        print(csvfile)
        self.csvdata = CSVData(csvfile)
        self.state_row = initial_row
        self.state_column = initial_column
        self.set_size(60,20)

    def increment_row(self, count=1):
        self.state_row += count
        self.state_row = min(self.state_row, self.csvdata.number_lines)

    def decrement_row(self, count=1):
        self.state_row -= count
        self.state_row = max(self.state_row-1, 0)

    def increment_column(self, count=1):
        self.state_column += count
        self.state_column = min(self.state_column-1, self.csvdata.number_columns)

    def decrement_column(self, count=1):
        self.state_column -= count
        self.state_column = max(self.state_column, 0)

    def toggle_column_visibility(self):
        self.csvdata.get_column(self.state_column).toggle_visibility()

    def set_size(self, height, width):
        self.height = height
        self.width = width

#    def __rich__(self) -> Panel:
#        grid = Table.grid(expand=True)
#        n_columns_draw = self.csvdata.get_visible_columns(self.state_column, self.width)
#
#        columns_to_draw = self.csvdata.columns[self.state_column:(self.state_column+n_columns_draw)]
#        columns_names = []
#        for icol, column in enumerate(columns_to_draw):
#            grid.add_column(justify="left", ratio=1)
#            column_name = Text(column.get_column_display())
#            column_name.stylize('red' if icol > 0 else 'bold magenta')
#            columns_names += [column_name]
#
#        grid.add_row(*[c for c in columns_names])
#        for irow in range(self.state_row,self.state_row+self.height):
#            grid.add_row(*[column.get_value(irow) for column in columns_to_draw])
#        return Panel(grid)

    def __rich__console__(self, console: Console, options: ConsoleOptions) -> RenderResult: 
        grid = Table.grid(expand=True)
        n_columns_draw = self.csvdata.get_visible_columns(self.state_column, self.width)

        columns_to_draw = self.csvdata.columns[self.state_column:(self.state_column+n_columns_draw)]
        columns_names = []
        for icol, column in enumerate(columns_to_draw):
            grid.add_column(justify="left", ratio=1)
            column_name = Text(column.get_column_display())
            column_name.stylize('red' if icol > 0 else 'bold magenta')
            columns_names += [column_name]

        grid.add_row(*[c for c in columns_names])
        for irow in range(self.state_row,self.state_row+self.height):
            grid.add_row(*[column.get_value(irow) for column in columns_to_draw])
        yield Panel(grid)


if __name__ == '__main__':
    body = Body(sys.argv[1])
    print(body)

