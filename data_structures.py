from ordering import describe_attrs
import pandas as pd

class Node:
    def __init__(self, data=pd.DataFrame() , children=[], level=0, parent = None):
        self.parent = parent
        self.children = children
        self.data = data
        self.cat_util = 0
        self.part_score = 0
        self.level = level
        self.partitioned_children = 0
        self.attr_desc = describe_attrs(data)

    def add_child(self, node):
        self.children += [node]
        #update_metrics
        
    def check_new_element(self, row):
        pass
        
    def calc_utility(self):
        pass
        
    def calc_part_score(self):
        pass
        
    def add_row(self, row):
        #pandas insert
        #update metrics
        pass




