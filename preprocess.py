import pandas as pd
import numpy as np 
import json
from numpy import *
from operator import itemgetter
from collections import Counter, OrderedDict

def buckets(data, bins):
	split = np.array_split(np.sort(data), bins)
	cutoffs = [x[-1] for x in split]
	cutoffs = cutoffs[:-1]
	discrete = np.digitize(data, cutoffs, right=True)
	groups = {}
	variance = 0
	for i in range(len(data)):
		if discrete[i] in groups:
			groups[discrete[i]] += [data[i]]
		else:
			groups[discrete[i]] = [data[i]]
	for i in groups:
		variance += np.var(groups[i], ddof=1)
	return discrete, cutoffs, variance

def get_split(data):
	possible = {}
	max_diff = 0
	possible[1] = {
		'd':[0]*len(data),
		'c':[max(data)],
		'v':np.var(data, ddof=1)
	}
	for i in range(2,11):
		d,c,v = buckets(data, i)
		possible[i] = {
			'd':d,
			'c':c,
			'v':v
		}
		if v <= possible[i-1]['v']:
			found = False;
		elif (v > possible[i-1]['v']) and (not found):

			return possible[i-1];

	for i in range(1,10): 
		difference = -(possible[i+1]['v'] - possible[i]['v'])
		if (difference > max_diff):
			max_diff = difference;
			best_groups = i+1; 

	return possible[best_groups]

	

def discretize(col):
	round_col = col.dropna() #list(map(lambda x : int(int(x/10)*10),col.dropna()))
	split_criteria = get_split(round_col)	
	return split_criteria

def prepare_data(df, num_cols):
	df = pd.DataFrame(df)
	criteria = {}
	for col in num_cols:
		split_criteria = discretize(df[col])
		df[col] = split_criteria['d']
		criteria[col] = {
		'cutoff': split_criteria['c'],
		'variance': split_criteria['v']
		}
	return df, criteria


#testing
# if __name__ == '__main__':
# 	df = pd.DataFrame(np.random.randn(50, 4))
# 	df.columns = list('abcd')
# 	new_df,criteria = prepare_data(df,['a','c'])
# 	df.to_csv('df.csv', sep=',')
# 	new_df.to_csv('new_df.csv', sep=',')
# 	with open('cri.txt','w') as file: file.write(json.dumps(criteria))




