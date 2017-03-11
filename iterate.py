from data_structures import Node
import pandas as pd
import yaml
from helper import *
   

def ctree(df):
	root = Node(name = 'N0', data=df , level=0, parent = None )
	L = [root]
	for node in L[:]:
		node.sort_data()
		node.partition()
		L += node.children
		L.remove(node)		
	return root

def extract_partition(root):
	initial_partition= []
	var L = [root]
	for node in L[:]:
		smaller = 0
		children = node.children
		smaller = sum([1 for child in children if node.utility <= child.utility])
		if smaller == 0 : 
			initial_partition += [node]
		else : 
			for child in children:
				if node.utility <= child.utility: L += [child]
				else: initial_partition += [child]
		L.remove(node)
	intial_partition = rename_data(initial_partition)
	labeled = label_data(initial_partition, root.data)
	return intial_partition, labeled
	
def redistribute(initial_partition, labeled):
	old_lab = pd.DataFrame(labeled).values.tolist()
	new_lab = []
	part_col = labeled.columns.index("partition")
	uni_desc = describe_attrs(labeled.drop(['partition'],axis=1))
	uni_len = len(df)
	while old_lab != new_lab:
		new_lab = old_lab
		for dp in new_lab:
			max_cmdk = -9999
			max_part = dp[part_col]
			for part in initial_partition:
				cm_d_k = category_match(part, dp, uni_desc, uni_len)
				if cm_d_k > max_cmdk:
					max_cmdk = cm_d_k
					max_part = part
			dp[part_col] = part
	new_lab = pd.DataFrame(initial_partitioninitial_partitionnew_lab)  
	final_partition = reconstruct(new_lab)			  
	return final_partition, new_lab
	
			
if __name__ == "__main__":
with open('config.yaml', 'r') as file: config = yaml.load(file) #read configuration and assign to variables
output_file = config['data']['file-iterate']
input_file = config['data']['file-discrete']
cols_use = config['parameters']['cols-to-be-used']
df = pd.read_csv(input_file)
	# tree = ctree(df)
		

	
	