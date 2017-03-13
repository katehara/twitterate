from ordering import ADO
from helper import *
import pandas as pd
import yaml

with open('config.yaml', 'r') as file: config = yaml.load(file) #read configuration and assign to variables
cols_use = config['parameters']['cols-to-be-used']
topn = config['parameters']['topn']
min_node_pop = config['parameters']['min-pop']

class Node: #tree node structure for each partition
	def __init__(self, name='N0', data=pd.DataFrame(), level=0, parent = None):
		self.name = name #unique identifier for each node 
		self.parent = parent #parent node reference - none for root
		self.children = [] #children node list - initiallly empty
		self.data = data #dataframe having all data points for this node
		self.data_count = len(self.data) #size of data at this node
		self.attr_desc = describe_attrs(self.data) #attribute stats description for data at this node - used for metric calculations
		if self.parent is None: 
			self.cat_utility = 0
		else: 
			self.cat_utility = self.calc_cat_utility(self.data, self.attr_desc,  #category utility for this node
						self.parent.attr_desc, self.data_count, self.parent.data_count)
		self.part_score = None #partition score for this node - calculated after partioning
		self.level = level #level of this node from root - root level is 0

	def sort_data(self):
		# self.data = self.data.sort_values(by = ['u_fav'], ascending=[True])

		self.data = ADO(self.data, topn) #Anchored dissimilarity ordering for data - called before partitioning
		return

	def temp_util(self, sad, sdc, vol, col): #category utility calculator for intermediate data while partioning in list-of-list format
		df = pd.DataFrame(vol, columns=col)
		temp_ad = describe_attrs(df) 
		temp_cu = self.calc_cat_utility(df, temp_ad, sad, len(vol), sdc)
		return temp_cu

	def temp_part(self, children): #partition score calculator for intermediate data while partioning in list-of-list format
		sumcu = 0
		for child in children:
			sumcu += child['util']
		ps = sumcu/len(children)
		return ps

	def best_part(self, children, obj, pad, pdc, col): #calculate best partition on adding new object to the sub-tree
		import copy
		temp_children = copy.deepcopy(children) #make changes to temp_children to compare with children
		# partition score if new child forms a new partition
		first_util = self.temp_util(pad, pdc, [obj], col)
		new_child_part = { #new child partition with only one object 
			"data" : [obj],
			"util" : first_util,
			"temp_util" : first_util,
			"temp_data" : [obj],
		}
		separate_part_score = self.temp_part(temp_children+[new_child_part]) #separate partition scores
		max_util_rise = -99999 #initialise to lowest variable (practically possible for this data set)

		# max category utility score when new obj placed in each child
		for temp_node in temp_children:			
			temp_node["temp_data"] = temp_node["data"]+[obj]
			temp_node["temp_util"] = self.temp_util(pad, pdc, temp_node["temp_data"] , col)
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

		prev_part_score = self.temp_part(temp_children) #max partition score if data point placed in any of the existing children
		# return the partion - separate or modified previous children - which gives maximum partition score
		if prev_part_score >= separate_part_score : 
			return temp_children
		else: 
			return children+[new_child_part]


	def partition(self): #partitionthe objects in this node into children nodes
		# if self.data_count <= 1: return #do not partition if datapoints less than min - population required
		temp_children = [] #container for temp children dicts
		cols = self.data.columns.tolist() #list of column values in order to be used for metric calculatins
		data_list = self.data.values.tolist() #convert dataframe to list-of-lists for ease of traversal and calculation
		for obj in data_list: #for each data point
			if len(temp_children) == 0: # if data point is firstin this node -> make a new child node for it
				first_util = self.temp_util(self.attr_desc, self.data_count, [obj], cols)
				chnode = {
					"data" : [obj],
					"util" : first_util,
					"temp_util" : first_util,
					"temp_data" : [obj],
				}
				temp_children += [chnode]
			else:
				# if not first data point, find best partition - separate or into existing nodes
				temp_children = self.best_part(temp_children, obj, self.attr_desc, self.data_count, cols)

		if len(temp_children) > 1:
			# after complete partition -> finalise the children into Node objects from temporary dicts
			child_count = 0
			for temp_node in temp_children:
				child_count += 1
				child_name = self.name + str(child_count)
				df = pd.DataFrame(temp_node['data'], columns = cols)
				self.children += [Node( name=child_name, data=df, level=self.level+1, parent = self )]
			   
			# set partition score for self 
			self.part_score =  self.calc_part_score(self.children) 
		else: 
			self.children = []
			self.part_score = 0

		return
					 
	def calc_cat_utility(self, df, sad, pad, sdc, pdc):
		sumi = 0 #sum of utility score for all rows
		pck = sdc/pdc #P(Ck)
		cols = df.columns.tolist()
		for row in df.values.tolist():
			j=0
			for i, col in enumerate(cols):
				if col in cols_use:
					if row[i] in sad[col]: 
						avc = sad[col][row[i]]/sdc #P(Ai==Vij | Ck)
						if row[i] in pad[col]: 
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
	



