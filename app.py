from textual import events
from textual.app import App
from textual.widgets import Header, Footer, Placeholder, ScrollView

import json

from rich.panel import Panel

from textual.app import App
from textual.reactive import Reactive
from textual.widget import Widget

import pandas as pd
import numpy as np

from rich.table import Table
from rich.tree import Tree
from csvdata import CSV
from view import View

import argparse

class Data(Widget):

    def __init__(self, filename:str):
        self.filename = filename
        self.data = CSV(filename)
        self.view = View(self.data.get_number_columns(), self.data.get_number_rows())
        super().__init__()

    async def action_toggle_bar(self) -> None:
        self.refresh()

    async def action_toggle_always_visible(self) -> None:
        self.view.toggle_always_visible()
        self.refresh()

    async def action_nav(self, direction:str, amount:int) -> None:
        self.view.navigate(direction, amount)
        self.refresh()

    async def action_col(self, operation:str, direction:str, amount:int) -> None:
        if operation == 'width':
            self.data.columns[self.view.column_select].adjust_width(direction, amount)
            new_width = self.data.columns[self.view.column_select].width
            self.view.update_column_width(self.view.column_select, new_width)
        elif operation == 'hide':
            self.data.columns[self.view.column_select].toggle_visibility()
        elif operation == 'justify':
            self.data.columns[self.view.column_select].toggle_justification()
        self.refresh()

    async def resize(self) -> None:
        self.view.update_view_size(self._size)
        self.refresh()

    async def on_resize(self, event: events.Resize) -> None:
        self.view.update_view_size(self._size)
        self.refresh()

    def render(self) -> Panel:
        self.view.update_view_size(self._size)
        table = Table(title=f'{self.filename}: {self._size.width}x{self._size.height} select {self.view.row_select},{self.view.column_select} top {self.view.row_top} bot {self.view.row_bottom} lft {self.view.column_left} rgt {self.view.column_right} {self.view.get_columns_width(self.view.column_left, self.view.column_right)} {self.view.width}')
        for icol,col_is_selected in self.view.get_drawn_columns():
            style = 'red' if col_is_selected else None
            column = self.data.get_column(icol)
            table.add_column(column.column_name, width=column.get_width()-3, header_style=style,no_wrap=True)

        for irow, row_is_selected in self.view.get_drawn_rows():
            table.add_row(*[ ('[red]' if row_is_selected or col_is_selected else '') + self.data.get_column(icol).get_value(irow) for icol,col_is_selected in self.view.get_drawn_columns()])
        return Panel(table)


class ColumnList(Widget):

    def __init__(self, data_widget):
        self.data_widget = data_widget
        super().__init__()

    async def action_nav(self, direction:str, amount:int) -> None:
        self.refresh()

    async def action_col(self, operation:str, direction:str, amount:int) -> None:
        self.refresh()

    async def on_resize(self, event: events.Resize) -> None:
        self.refresh()

    def render(self) -> Panel:
        tree = Tree('Columns')
        for icol, col_is_selected in self.data_widget.view.get_all_columns():
            column = self.data_widget.data.get_column(icol)
            column_label = f'{column.column_name}'
            if not column.visible:
                column_label += ' [H]'
            if col_is_selected:
                subtree = tree.add(f'[red]{column_label}')
                subtree.add(f'dtype: {str(column.column_dtype)}')
                subtree.add(f'format: {column.format_string}')
            else:
                tree.add(column_label)
        return Panel(tree)


class StatsView(Widget):

    def __init__(self, data_widget):
        self.data_widget = data_widget
        super().__init__()

    async def action_nav(self, direction:str, amount:int) -> None:
        self.refresh()

    async def action_col(self, operation:str, direction:str, amount:int) -> None:
        self.refresh()

    async def on_mount(self, event: events.Mount) -> None:
        self.visible = False

    async def on_resize(self, event: events.Resize) -> None:
        self.refresh()

    def render(self) -> Panel:
        column = self.data_widget.data.get_column(self.data_widget.view.column_select)
        stats = column.get_stats()
        avail_width = self._size.width-20
        stat_tree = Tree('Stats')
        # make a histogram
        if 'Quantiles' in stats.keys():
            hist = column.get_histogram(avail_width)
            #qtree = Tree('Quantiles')
            levels = stats['Quantiles']['levels']
            values = stats['Quantiles']['values']
            #for l,v in zip(stats['Quantiles']['levels'], stats['Quantiles']['values']):
            #    qtree.add(f'P{l:0.2f} = {column.format_value(v)}')
            x_axis, q_index = "", 0
            while len(x_axis) < avail_width:
                quantile = len(x_axis) / float(avail_width)
                q_index = np.argmin(stats['Quantiles']['levels'] < quantile)
                x_axis += f'|{column.format_value(stats["Quantiles"]["values"][q_index])}   '
            stat_tree.add(x_axis)
            hist_str = ""
            levels = 10
            for ii in range(levels, 0, -1):
                value = np.max(hist[0]) * (ii-1) / levels
                hist_str += ''.join([ '#' if x > value else ' ' for x in hist[0]])+'\n'
            stat_tree.add(Panel(hist_str))
        # count most frequent
        elif 'counts' in stats.keys():
            ctree = Tree('Counts')
            category_count = 0
            for key, count in zip(stats['counts'].index, stats['counts'].values):
                if category_count > self._size.height:
                    break
                ctree.add(f'{key} = {count}')
            stat_tree.add(ctree)
        return Panel(stat_tree)

class CSView(App):

    #def __init__(self, filepath, **kwargs):
    #    self.filepath = filepath
    #    super().__init__(**kwargs)

    #async def set_filepath(self, filepath):
    #    self.filepath = filepath

    async def on_load(self, event: events.Load) -> None:
        """Bind keys with the app loads (but before entering application mode)"""
        await self.bind("b", "toggle_columns()", "Toggle Columns")
        await self.bind("s", "toggle_stats())", "Toggle Stats")
        await self.bind("q", "quit", "Quit")
        await self.bind("up", "nav('up',1)", "Up 1 row")
        await self.bind("down", "nav('down',1)", "Down 1 row")
        await self.bind("right", "nav('right',1)", "Right 1 column")
        await self.bind("left", "nav('left',1)", "Left 1 column")
        await self.bind("pageup", "nav('up',10)", "Up 10 rows")
        await self.bind("pagedown", "nav('down',10)", "Down 10 rows")
        await self.bind("ctrl+right", "nav('right',10)", "Right 10 columns")
        await self.bind("ctrl+left", "nav('left',10)", "Left 10 columns")
        #
        await self.bind("shift+up","col('width','+',1)","Increase column width")
        await self.bind("shift+down","col('width','-',1)","Decrease column width")
        await self.bind("h","col('hide','',0)","toggle visible")
        await self.bind("j","col('justify','',0)","toggle r/l justified")
        await self.bind("v","toggle_always_visible()","toggle always visible")

    async def action_nav(self, direction:str, amount:int) -> None:
        await self.data.action_nav(direction, amount)
        await self.statsview.action_nav(direction, amount)
        await self.columnlist.action_nav(direction, amount)

    async def action_col(self, operation:str, direction:str, amount:int) -> None:
        await self.data.action_col(operation, direction, amount)
        await self.columnlist.action_col(operation, direction, amount)

    async def action_toggle_columns(self):
        await self.view.action_toggle('columnsbar')
        await self.data.action_toggle_bar()

    async def action_toggle_stats(self):
        await self.view.action_toggle('statsbar')
        await self.data.action_toggle_bar()

    async def action_toggle_always_visible(self):
        await self.data.action_toggle_always_visible()
 
    async def on_resize(self, event: events.Resize) -> None:
        # redock to new view
        await self.view.dock(Header(), edge="top")
        await self.view.dock(Footer(), edge="bottom")
        await self.view.dock(self.columnlist, edge="left", size=int(0.25*self.console.width), name="columnsbar")
        await self.view.dock(self.statsview, edge="bottom", size=int(0.5*self.console.height), name="statsbar")
        # Dock the body in the remaining space
        #await self.data.resize()
        await self.view.dock(self.data, edge="right")

    async def on_mount(self, event: events.Mount) -> None:
        """Create and dock the widgets."""
        self.data = Data(self.title.split(':')[-1])
        self.columnlist = ColumnList(self.data)
        self.statsview = StatsView(self.data)
        # Header / footer / dock
        await self.view.dock(Header(), edge="top")
        await self.view.dock(Footer(), edge="bottom")
        await self.view.dock(self.columnlist, edge="left", size=int(0.25*self.console.width), name="columnsbar")
        await self.view.dock(self.statsview, edge="bottom", size=int(0.5*self.console.height), name="statsbar")

        # Dock the body in the remaining space
        await self.view.dock(self.data, edge="right")



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("filepath", help="csv file to view", type=str)
    args = parser.parse_args()
    #TODO: How to you create an app with custom init? 
    # hack solution, embedd filepath in app title
    CSView.run(title=f"CSView:{args.filepath}", log="textual.log")


