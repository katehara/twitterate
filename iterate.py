from data_structures import Node
import pandas as pd
import yaml, copy
from helper import *

def ctree(df):
	root = Node(name = 'N0', data=df , level=0, parent = None )
	L = [root]
	while len(L) > 0:
		node = L[0]
		node.sort_data()
		node.partition()
		L += node.children
		L.remove(node)
	return root

def extract_partition(root):
	initial_partition= []
	L = [root]
	while len(L)>0:
		node = L[0]
		smaller = 0
		children = node.children
		smaller = sum([1 for child in children if node.cat_utility <= child.cat_utility])
		if smaller == 0: # or node.data_count < 15: # to control no of nodes & avoid overfitting
			initial_partition += [node]
		else : 
			for child in children:
				if node.cat_utility <= child.cat_utility: L += [child]
				else: initial_partition += [child]
		L.remove(node)

	intial_partition = rename_data(initial_partition)
	labeled = label_data(initial_partition, root.data)
	return intial_partition, labeled
	
def redistribute(initial_partition, labeled):
	cols = labeled.columns.tolist()
	old_lab = labeled.values.tolist()
	new_lab = copy.deepcopy(old_lab)
	part_col = labeled.columns.tolist().index("partition")
	uni_desc = describe_attrs(labeled)
	uni_len = len(labeled)
	# print(uni_desc, uni_len)
	while True:
		for i, dp in enumerate(new_lab):
			max_cmdk = -9999
			max_part = dp[part_col]
			for part in initial_partition:
				cm_d_k = category_match(part, dp, uni_desc, uni_len, labeled.columns.tolist())
				if cm_d_k > max_cmdk:
					max_cmdk = cm_d_k
					max_part = part.name
			new_lab[i][part_col] = max_part
		if (new_lab == old_lab): break
		else: old_lab = copy.deepcopy(new_lab)

	new_lab = pd.DataFrame(new_lab, columns = cols)
	final_partition = reconstruct(initial_partition, new_lab)			  
	return final_partition, new_lab
	
def iterate():
	with open('config.yaml', 'r') as file: config = yaml.load(file) #read configuration and assign to variables
	output_file = config['data']['file-iterate']
	intermediate_file = config['data']['file-init-part']
	input_file = config['data']['file-discrete']
	cols_use = config['parameters']['cols-to-be-used']
	df = pd.read_csv(input_file)
	tree = ctree(df)
	initial_partition, clustered_data = extract_partition(tree)
	clustered_data.to_csv(intermediate_file, sep=',', index=False)
	final_partition, new_clusters =	redistribute(initial_partition, clustered_data)
	new_clusters.to_csv(output_file, sep=',', index=False)
	
			
if __name__ == "__main__":
	iterate()