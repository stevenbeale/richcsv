import pandas as pd
import re

from column import Column

class CSV:
    """
    csv class contains csv data and the pad through which it is viewed
    
    Required Args:
        filepath: path to the source csv file
    """
    def __init__(self, filepath):
        self.filepath = filepath
        self.columns = []
        #
        pd_data = pd.read_csv(self.filepath)
        self.number_lines = len(pd_data)
        self.number_columns = len(pd_data.columns)
        # Include column for index
        self.columns += [Column('index', int, [str(i) for i in range(0,self.number_lines)])] 
        for column in pd_data.columns:
            new_column = Column(column, pd_data[column].dtype, pd_data[column].values)
            self.columns += [new_column]
   
    def get_number_columns(self):
        return self.number_columns

    def get_columns(self):
        return self.columns

    def get_column(self, index):
        return self.columns[index]

    def get_number_rows(self):
        return self.number_lines


