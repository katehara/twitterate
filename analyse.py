import sys, os
import pandas as pd
from data_structures import *


def analyse():
	args = sys.argv[1:]
	if not args:
		print('Usage: python analyse.py path/to/file.csv >:(')
		return

	for file in args:
		if file[-4:] != '.csv':	
			print('Only csv files accepted. Skiping - '+file+' :(')
		elif not os.path.isfile(file):
			print(file+' doesn\'t exist. Check for typos. :/')
		else:
			data = pd.read_csv(file)
			root = Node('R', data, 0, None)
			groups = data.groupby(['partition'])
			parts = []
			for gr in groups:
				parts += [Node(gr[0], gr[1], 1, root)]

			ps = sum(p.cat_utility for p in parts)/len(parts)
			print(file + '\t\t P_Score: ' + str(ps) + ' :)')
	return

if __name__ == "__main__":
	analyse()