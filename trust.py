import yaml, operator
import pandas as pd
from collections import Counter
from ordering import nominal_cityblock

def dist_bw_part(df1, df2):
	dl1 = df1.values.tolist()
	dl2 = df2.values.tolist()
	dist = []
	for i in dl1:
		dij = []
		for j in dl2:
			dij += [nominal_cityblock(i, j)]
		dist += [min(dij)]
	return sum(dist)/len(dist)

def get_score(df):
	dist_list = {}
	rating = {}
	parts = sorted(set(df['partition']))
	for p in parts:
		d = dist_bw_part(df[df['partition'] == p], df[df['ver'] == True]) #df[df['partition'] == p0])
		dist_list[p] =  d
	dist_tup = sorted(dist_list.items(), key = operator.itemgetter(1), reverse = True)
	for i, (p, d) in enumerate(dist_tup):
		rating[p] = i+1
	df['trust'] = df.apply(lambda x: rating[x['partition']], axis = 1)
	return df

def trust():
	with open('config.yaml', 'r') as file: config = yaml.load(file) #read configuration and assign to variables
	input_file = config['data']['file-concept-cluster'] # input file for clustered data
	output_file = config['data']['file-trust'] # final results output file for trust scores
	df = pd.read_csv(input_file)
	df = get_score(df)
	df.to_csv(output_file, sep=',', index=False)
	return

if __name__ == '__main__':
	trust()