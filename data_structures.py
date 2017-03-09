from ordering import ADO
from helper import describe_attrs
import pandas as pd

class Node: #tree node structure for each partition
    def __init__(self, name='N0', data=pd.DataFrame(), level=0, parent = None):
        self.name = name #unique identifier for each node 
        self.parent = parent #parent node reference - none for root
        self.children = [] #children node list - initiallly empty
        self.data = data #dataframe having all data points for this node
        self.data_count = len(self.data) #size of data at this node
        self.attr_desc = describe_attrs(self.data) #attribute stats description for data at this node - used for metric calculations
        self.cat_utility = self.calc_cat_utility(self.data, self.attr_desc,  #category utility for this node
                        self.parent.attr_desc, self.data_count, self.parent.data_count)
        self.part_score = None #partition score for this node - calculated after partioning
        self.level = level #level of this node from root - root level is 0

    def sort_data(self):
        self.data = ADO(self.data) #Anchored dissimilarity ordering for data - called before partitioning
        return

    def temp_util(sad, sdc, vol, col): #category utility calculator for intermediate data while partioning in list-of-list format
        df = pd.DataFrame(vol)         
        df.columns = col
        temp_ad = temp_desc(vol, col) 
        temp_cu = calc_cat_utility(df, temp_desc, sad, len(vol), sdc)
        return temp_cu

    def temp_desc(vol, col): #attribute description calculator for intermediate data while partioning in list-of-list format
        df = pd.DataFrame(vol)
        df.columns = col
        temp_ad = describe_attrs(df)
        return temp_ad

    def temp_part(children): #partition score calculator for intermediate data while partioning in list-of-list format
        sumcu = 0
        for child in children:
            sumcu += child['util']
        ps = sumcu/len(children)
        return ps

    def best_part(children, obj, pad, pdc, col): #calculate best partition on adding new object to the sub-tree
        temp_children = children #make changes to temp_children to compare with children

        # partition score if new child forms a new partition
        first_util = temp_util(pad, pdc, obj, col)
        new_child_part = { #new child partition with only one object 
            "data" : [obj],
            "util" : first_util,
            "temp_util" : first_util,
            "temp_data" : [obj],
        }
        separate_part_score = temp_part(temp_children+[new_child_part]) #separate partition score

        max_util_rise = -99999 #initialise to lowest variable (practically possible for this data set)

        # max category utility score when new obj placed in each child
        for temp_node in temp_children:            
            temp_node["temp_data"] = temp_node["data"]+[obj]
            temp_node["temp_util"] = temp_util(pad, pdc, temp_node["temp_data"] , col)
            diff_util = temp_node["temp_util"] - temp_node["util"]
            if diff_util > max_util_rise : # partition that gives maximum rise in cat_util increases the partion score by max value possible
                max_util_rise = diff_util

        # place the object in partition with maximum rise in category utility - hence gives max partition score
        for temp_node in temp_children:            
            diff_util = temp_node["temp_util"] - temp_node["util"]
            if diff_util == max_util_rise : 
                temp_node["data"] = temp_node["temp_data"]
                temp_node["util"] = temp_node["temp_util"]
                break

        prev_part_score = temp_part(temp_children) #max partition score if data point placed in any of the existing children
        # return the partion - separate or modified previous children - which gives maximum partition score
        if prev_part_score >= separate_part_score : 
            return temp_children
        else: 
            return children+[new_child_part]

    def partition(self, min_node_pop): #partitionthe objects in this node into children nodes
        if self.data_count <= min_node_pop: return #do not partition if datapoints less than min - population required
        temp_children = [] #container for temp children dicts
        cols = (self.data).columns.tolist() #list of column values in order to be used for metric calculatins
        data_list = (self.data).values.tolist() #convert dataframe to list-of-lists for ease of traversal and calculation
        for obj in data_list: #for each data point
            if len(temp_children) == 0: # if data point is firstin this node -> make a new child node for it
                first_util = temp_util(self.attr_desc, self.data_count, obj, cols)
                chnode = {
                    "data" : [obj],
                    "util" : first_util,
                    "temp_util" : first_util,
                    "temp_data" : [obj],
                }
                temp_children += [chnode]
            else:
                # if not first data point, find best partition - separate or into existing nodes
                temp_children = best_part(temp_children, obj, self.attr_desc, self.data_count, col)

        # after complete partition -> finalise the children into Node objects from temporary dicts
        for temp_node in temp_children:
            df = pd.DataFrame(temp_node['data'])
            df.columns = cols
            self.children += Node( data=df , children=[], level=self.level+1, parent = self )
           
        # set partition score for self 
        self.part_score =  self.calc_part_score(self.children) 
        return
                     
    def calc_cat_utility(self, df, sad, pad, sdc, pdc):
        sumi = 0 #sum of utility score for all rows
        pck = sdc/pdc #P(Ck)
        cols = df.columns.tolist()
        for row in df.values.tolist():
            j=0
            for i, col in enumerate(cols):
                avc = sad[col][row[i]]/sdc #P(Ai==Vij | Ck)
                av = pad[col][row[i]]/pdc #(P(Ai==Vij)
                k = (avc*avc)-(av*av) #(P(Ai==Vij | Ck))^2 - (P(Ai==Vij)^2)
                j += k #SUMj((P(Ai==Vij | Ck))^2 - (P(Ai==Vij)^2)
            sumi += j #SUMi(SUMj((P(Ai==Vij | Ck))^2 - (P(Ai==Vij)^2))
        cu = pck*sumi # P(Ck) * SUMi(SUMj((P(Ai==Vij | Ck))^2 - (P(Ai==Vij)^2))
        return cu
        
    def calc_part_score(self, children): #Partition score = avg. of category utility of children nodes
        sumcu = 0
        for child in children:
            sumcu += child.cat_utility
        ps = sumcu/len(children)
        return ps
    



