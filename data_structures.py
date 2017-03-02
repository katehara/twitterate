from ordering import describe_attrs, ADO
import pandas as pd

class Node:
    def __init__(self, name='N0', data=pd.DataFrame() , children=[], level=0, parent = None):
        self.name = name
        self.parent = parent
        self.children = children
        self.data = data
        self.data_count = len(self.data)
        self.attr_desc = describe_attrs(self.data)
        self.cat_utility = self.calc_cat_utility(self.data)
        self.part_score = None
        self.level = level

    def sort_data(self):
        self.data = ADO(self.data)
        return

    def partition(self):
        data_list = (self.data).values.tolist()
        for obj in data_list:
            if len(self.children) == 0: 
                new_name = self.name+str(len(self.children))
                chnode = Node(name=new_name, data=[obj] , children=[], level=self.level+1, parent = self)
                self.children += [chnode]
            else:
            
            
        self.part_score =  self.calc_part_score(self.children) 
        return
                     
    def calc_cat_utility(self, df):
        sumi = 0
        sdc = self.data_count
        pdc = self.parent.data_count
        pck = sdc/pdc
        cols = df.columns.tolist()
        for row in df.value.tolist():
            i = 0
            for i, col in enumerate(cols): 
                avc = self.attr_desc[col][row[i]]/sdc
                av = self.parent.attr_desc[col][row[i]]/pdc
                j = (avc*avc)-(av*av)
                sumi += j
        cu = pck*sumi
        return cu
        
    def calc_part_score(self, children):
        sumcu = 0
        for child in self.children:
            sumcu += child.cat_util
        ps = sumcu/len(children)
        return ps
    



