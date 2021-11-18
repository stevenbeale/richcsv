# Constants:
TOP_PAD = 4
BOT_PAD = 3
RIG_PAD = 3
LEF_PAD = 3


class View:
    def __init__(self, number_columns, number_rows, initial_column_width=10, initial_row_height=1):
        self.number_columns = number_columns
        self.number_rows = number_rows
        """
        Note: columns are separated by '. | ' 
        Also, drawning area is bordered by '| |' 
        so an area with size 30 has 30-3-3=24 char for drawing data and 4 char between data, 
        """
        self.column_width = [initial_column_width for _ in range(0,number_columns)]
        self.row_height = [initial_row_height for _ in range(0,number_rows)]
        self.column_left = 0
        self.column_select = 0
        self.column_right = self.number_columns-1
        self.row_top = 0
        self.row_select = 0
        self.row_bottom = self.number_rows-1
        self.width = 0
        self.height = 0
        self.expand_tolerance = 10

    def get_drawn_columns(self):
        return [(icol,icol==self.column_select) for icol in range(self.column_left, self.column_right+1)]

    def get_all_columns(self):
        return [(icol,icol==self.column_select) for icol in range(0,self.number_columns)]

    def get_drawn_rows(self):
        return [(irow,irow==self.row_select) for irow in range(self.row_top, self.row_bottom+1)]

    def is_column_visible(self, column_index):
        return column_index >= self.column_left and column_index <= self.column_right

    def is_row_visible(self, row_index):
        return row_index >= self.row_top and row_index <= self.row_bottom

    def is_column_selected(self, column_index):
        return column_index == self.column_select

    def is_row_selected(self, row_index):
        return row_index == self.row_select

    def update_column_width(self, column_index, new_width):
        if column_index < 0 or column_index > self.number_columns:
            raise Exception('Invalid column')
        self.column_width[column_index] = new_width
        self.fit()

    def update_row_height(self, row_index, new_height):
        if row_index < 0 or row_index > self.number_rows:
            raise Exception('Invalid row')
        self.row_height[row_index] = new_height

    def update_view_size(self, size):
        self.width = size.width
        self.height = size.height
        self.fit()

    def navigate(self, direction:str, amount:int):
        if direction == 'up':
            self.row_select -= amount
        elif direction == 'down':
            self.row_select += amount
        elif direction == 'right':
            self.column_select += amount
        elif direction == 'left':
            self.column_select -= amount
        else:
            pass
        self.limit()
        self.justify()

    def find_row_index_up(self, start_row_index:int, target_size:int):
        size = 0
        row =  start_row_index
        while size < target_size and row >= 0: 
            size += self.row_height[row]
            row -= 1
        return row

    def find_row_index_down(self, start_row_index:int, target_size:int):
        size = 0
        row =  start_row_index
        while size < target_size and row < self.number_rows: 
            size += self.row_height[row]
            row += 1
        return row

    def find_column_index_right(self, start_column_index:int, target_size:int):
        size = 0
        column =  start_column_index
        while (size+3) < target_size and column < self.number_columns: 
            size += (self.column_width[column])
            column += 1
        return column

    def find_column_index_left(self, start_column_index:int, target_size:int):
        size = 0
        column =  start_column_index
        while (size+3) < target_size and column >= 0:
            size += (self.column_width[column])
            column -= 1
        return column

    def get_columns_width(self, start_column_index:int, end_column_index:int):
        return sum(self.column_width[start_column_index:end_column_index+1])

    def get_rows_height(self, start_row_index:int, end_row_index:int):
        return sum(self.row_height[start_row_index:end_row_index+1])

    def fit(self):
        """
        adjust size to fit the viewable area
        TODO: You need a better way to control size
        textual has some tolerance to fit to viewable area, so this only needs to be rough
        """
        # shrink if too many rows, expand if too few rows
        rows_height = self.get_rows_height(self.row_top, self.row_bottom)
        cols_width = self.get_columns_width(self.column_left, self.column_right)
        rows_allowed = self.height+1-TOP_PAD-BOT_PAD
        cols_allowed = self.width-RIG_PAD-LEF_PAD
        if rows_height > rows_allowed or rows_height < (rows_allowed-self.expand_tolerance):
            self.row_top = self.row_select
            self.row_bottom = self.find_row_index_down(self.row_top, self.height-TOP_PAD-BOT_PAD)
        # shrink if too many columns, expand if too few columns
        if cols_width > cols_allowed or cols_width < (cols_allowed-self.expand_tolerance):
            #self.column_left = self.column_select
            self.column_right = self.find_column_index_right(self.column_left, self.width-RIG_PAD-LEF_PAD)

    def limit(self):
        """
        ensure row/column selection is valid
        """
        if self.row_select < 0:
            self.row_select = 0
        if self.row_select >= self.number_rows:
            self.row_select = self.number_rows-1
        if self.column_select < 0:
            self.column_select = 0
        if self.column_select >= self.number_columns:
            self.column_select = self.number_columns-1

    def justify(self):
        """
        shift column view if selection has moved beyond current view
        """
        if self.row_select > self.row_bottom:
            self.row_bottom = self.row_select
            self.row_top = self.find_row_index_up(self.row_bottom, self.height-TOP_PAD-BOT_PAD)
        if self.row_select < self.row_top:
            self.row_top = self.row_select
            self.row_bottom = self.find_row_index_down(self.row_top, self.height-TOP_PAD-BOT_PAD)
        if self.column_select > self.column_right:
            self.column_right = self.column_select
            self.column_left = self.find_column_index_left(self.column_right, self.width-RIG_PAD-LEF_PAD)
        if self.column_select < self.column_left:
            self.column_left = self.column_select
            self.column_right = self.find_column_index_right(self.column_left, self.width-RIG_PAD-LEF_PAD)
