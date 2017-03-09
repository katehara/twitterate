from ordering import ADO
from helper import describe_attrs
import pandas as pd

class Node:
    def __init__(self, name='N0', data=pd.DataFrame(), level=0, parent = None):
        self.name = name
        self.parent = parent
        self.children = []
        self.data = data
        self.data_count = len(self.data)
        self.attr_desc = describe_attrs(self.data)
        self.cat_utility = self.calc_cat_utility(self.data, self.attr_desc, self.parent.attr_desc, self.data_count, self.parent.data_count)
        self.part_score = None
        self.level = level

    def sort_data(self):
        self.data = ADO(self.data)
        return

    def temp_util(sad, sdc, vol, col):
        df = pd.DataFrame(vol)
        df.columns = col
        temp_ad = temp_desc(vol, col)
        temp_cu = calc_cat_utility(df, temp_desc, sad, len(vol), sdc)
        return temp_cu

    def temp_desc(vol, col):
        df = pd.DataFrame(vol)
        df.columns = col
        temp_ad = describe_attrs(df)
        return temp_ad

    def temp_part(children):
        sumcu = 0
        for child in children:
            sumcu += child['util']
        ps = sumcu/len(children)
        return ps

    def best_part(children, obj, pad, pdc, col):
        temp_children = children
        # partition score if new child forms a new partition
        lala = temp_util(pad, pdc, obj, col)
        new_child_part = {
            "data" : [obj],
            "util" : lala,
            "temp_util" : lala,
            "temp_data" : [obj],
        }
        separate_part_score = temp_part(temp_children+[new_child_part])

        max_util_rise = -99999
        # max partition score when new obj placed in each child
        for temp_node in temp_children:            
            temp_node["temp_data"] = temp_node["data"]+[obj]
            temp_node["temp_util"] = temp_util(pad, pdc, temp_node["temp_data"] , col)
            diff_util = temp_node["temp_util"] - temp_node["util"]
            if diff_util > max_util_rise : 
                max_util_rise = diff_util

        for temp_node in temp_children:            
            diff_util = temp_node["temp_util"] - temp_node["util"]
            if diff_util == max_util_rise : 
                temp_node["data"] = temp_node["temp_data"]
                temp_node["util"] = temp_node["temp_util"]
                break

        prev_part_score = temp_part(temp_children)

        if prev_part_score > separate_part_score : 
            return temp_children
        else: 
            return children+[new_child_part]

    def partition(self):
        if self.data_count < 5: return
        temp_children = []
        cols = (self.data).columns.tolist()
        data_list = (self.data).values.tolist()
        for obj in data_list:
            if len(temp_children) == 0: 
                lala = temp_util(self.attr_desc, self.data_count, obj, cols)
                chnode = {
                    "data" : [obj],
                    "util" : lala,
                    "temp_util" : lala,
                    "temp_data" : [obj],
                }
                temp_children += [chnode]
            else:
                temp_children = best_part(temp_children, obj, self.attr_desc, self.data_count, col)


        for temp_node in temp_children:
            df = pd.DataFrame(temp_node['data'])
            df.columns = cols
            self.children += Node( data=df , children=[], level=self.level+1, parent = self )
           
        self.part_score =  self.calc_part_score(self.children) 
        return
                     
    def calc_cat_utility(self, df, sad, pad, sdc, pdc):
        sumi = 0
        pck = sdc/pdc
        cols = df.columns.tolist()
        for row in df.value.tolist():
            for i, col in enumerate(cols): 
                avc = sad[col][row[i]]/sdc
                av = pad[col][row[i]]/pdc
                j = (avc*avc)-(av*av)
                sumi += j
        cu = pck*sumi
        return cu
        
    def calc_part_score(self, children):
        sumcu = 0
        for child in children:
            sumcu += child.cat_util
        ps = sumcu/len(children)
        return ps
    



