from data_structures import Node
import pandas as pd
import yaml, copy
from helper import *


#Part - I
def ctree(df): # build herarchial classification tree for data
	root = Node(name = 'N0', data=df , level=0, parent = None ) # root node named-N0, on level=0
	L = [root] #L = List of nodes to be partitioned - initialised with root
	while len(L) > 0: #till all nodes are partitioned to the leaf
		node = L[0] # node to be partitioned - first element in list
		node.sort_data() # sort data in the node - criteria defined in sort_data funtion of Node class
		node.partition() # partition the node into its children
		L += node.children # add children nodes to the list for further partition
		L.remove(node) # remove this node from the list
		print(node.name, node.data_count, len(node.children))
	return root #return root node 

#Part - II
def extract_partition(root): # extract cluster nodes from the tree by traversing over every node
	initial_partition= [] # empty_list
	L = [root] # start traversal from root
	while len(L)>0: # loop till all nodes are covered
		node = L[0] 
		smaller = 0
		children = node.children # get children of node
 		smaller = sum([1 for child in children if node.cat_utility <= child.cat_utility]) # count no of children having utility more than self
		if smaller == 0: # if node utility more than all if its children    ---[or node.data_count < 15: #to control no of nodes & avoid overfitting]
			initial_partition += [node] # this node is an initial partition
		else : # if node utility less than one or more of its children nodes
			for child in children: # for all child node
				if node.cat_utility <= child.cat_utility: L += [child] # if node utility less than this child - add this child to list for futher traversal
				else: initial_partition += [child] # if node utility more than this child - this child is an initial partition
		L.remove(node) # remove current node from list of traversal

	intial_partition = rename_data(initial_partition) # rename initial partion to sequential names rather than heirarchial ones for readability
	labeled = label_data(initial_partition, root.data) # label the data according to new partition names
	return intial_partition, labeled # return partitions and new data
	
#Part - III
def redistribute(initial_partition, labeled): # redistribute data to optimise clusters
	cols = labeled.columns.tolist() # column names to list
	old_lab = labeled.values.tolist() # data values to list
	new_lab = copy.deepcopy(old_lab) # make a copy to edit and compare
	part_col = labeled.columns.tolist().index("partition") #index of partition column to update
	uni_desc = describe_attrs(labeled) #description of universal (root) data
	uni_len = len(labeled) #length of universal (root) data
	while True: # loop till no scope of optimisation left
		for i, dp in enumerate(new_lab): # for every dtaa point 
			max_cmdk = -99999 # practically lowest value for cmdk measure
			max_part = dp[part_col] # current partition
			for part in initial_partition: # check this dp's compatibility with every partition
				cm_d_k = category_match(part, dp, uni_desc, uni_len, labeled.columns.tolist()) # calculate category match measure for this dp to belong to this partion
				if cm_d_k > max_cmdk: # dp should be a part of partition with highest measure of cmdk for it
					max_cmdk = cm_d_k
					max_part = part.name
			new_lab[i][part_col] = max_part #update partition name
		if (new_lab == old_lab): break #break out when no scope of optimisation left
		else: old_lab = copy.deepcopy(new_lab) #else update old lables with new ones and again check for any change

	new_lab = pd.DataFrame(new_lab, columns = cols) # dataframe for new labled data
	final_partition = reconstruct(initial_partition, new_lab) # reconstruct partitions accordingto new lables
	return final_partition, new_lab # return new partitions and corresponding data 
	
def conceptually_cluster():
	print('...reading configuration')
	with open('config.yaml', 'r') as file: config = yaml.load(file) #read configuration and assign to variables
	output_file = config['data']['file-concept-cluster'] # final results output file
	intermediate_file = config['data']['file-init-part'] # results after initial_partiton (Part-II)
	input_file = config['data']['file-discrete'] # input file for data
	cols_use = config['parameters']['cols-to-be-used'] # columns tobe used for clustering
	print('...reading data') 
	df = pd.read_csv(input_file)[:1500] # read data into dataframe
	print('...making ctree')
	tree = ctree(df) # get classification tree (Part-I)
	print('...extracting partitons')
	initial_partition, clustered_data = extract_partition(tree) # get initial partitions (Part-II)
	# TO DO: code to make moreclusters if required
	clustered_data.to_csv(intermediate_file, sep=',', index=False) # write initial partitions to file
	print('...refining clusters')
	final_partition, new_clusters =	redistribute(initial_partition, clustered_data) # redistribute data into partitions(Part-III)
	new_clusters.to_csv(output_file, sep=',', index=False) #write final results to file
	print('.... done clustering into %d clusters'.format(len(final_partition)))
	
			
if __name__ == "__main__":
	conceptually_cluster()