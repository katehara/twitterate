import sys, os
import pandas as pd
from data_structures import *


def analyse(): # find P_score for all files given as sys.args
	args = sys.argv[1:] # read file names from sys args
	if not args: # print usage & return if file names not given
		print('Usage: python analyse.py path/to/file.csv')
		return

	for file in args: # for each file in args
		if file[-4:] != '.csv':	# skip files not in csv format
			print(file + '\tOnly csv files accepted. Skiping - "'+file+'"')
		elif not os.path.isfile(file): # notify if file doesn't exist
			print(file + 'File doesn\'t exist. Check for typos. "'+file+'"')
		else: # if file is csv and exists calculate P_score and print
			data = pd.read_csv(file) #read csv
			root = Node('R', data, 0, None) # create root node
			groups = data.groupby(['partition']) # group data by partition
			parts = []
			for gr in groups: # for all partitons
				parts += [Node(gr[0], gr[1], 1, root)] # make nodes - for category utility

			ps = sum(p.cat_utility for p in parts)/len(parts) # calulate P_score for the partition
			print(file + '\t ' + str(ps) ) # give results
	return

if __name__ == "__main__":
	analyse()