import pandas as pd
import numpy as np 
import json
from numpy import *
from operator import itemgetter
from collections import Counter, OrderedDict

def buckets(data, bins): #divide data into optimal #bins buckets 
	split = np.array_split(np.sort(data), bins) #sort and array split with maximum variance between groups- at peaks
	cutoffs = [x[-1] for x in split] #get cutoffs
	cutoffs = cutoffs[:-1]#remove last value
	discrete = np.digitize(data, cutoffs, right=True) #assign new value acc to cutoff
	groups = {}
	variance = 0

	#divide the data into groups for groupwise variance calculations
	for i in range(len(data)):
		if discrete[i] in groups:
			groups[discrete[i]] += [data[i]]
		else:
			groups[discrete[i]] = [data[i]]

	#sum of variance within groups		
	for i in groups:
		variance += np.var(groups[i], ddof=1)

	return discrete, cutoffs, variance

def get_split(data, max_groups):
	possible = {}
	max_diff = 0
	possible[1] = { #all dp in same group
		'd':[0]*len(data), 
		'c':[max(data)], 
		'v':np.var(data, ddof=1)
	}
	for i in range(2,max_groups+1): # for all possible groupings under max-groups numbers
		d,c,v = buckets(data, i) #get optimised buckets for given no of groups - maximum variance between groups
		possible[i] = { 
			'd':d,
			'c':c,
			'v':v
		}
		if v <= possible[i-1]['v']: #if variance less than one-less-group partition, this is not wanted partition
			found = False;
		elif (v > possible[i-1]['v']) and (not found): # if variance more than previous one and partition not found already - this is global minima for variance within groups
			return possible[i-1];

	# if no minima was reached (variance decreasing with each more partition) - find the partition with max difference from previous partition
	for i in range(1, max_groups): 
		difference = -(possible[i+1]['v'] - possible[i]['v'])
		if (difference > max_diff):
			max_diff = difference;
			best_groups = i+1; 

	return possible[best_groups] #return best partition with - newdata, cutoffs & variance

	

def discretize(col, max_groups):
	round_col = col.dropna() #remove invalid values - drop NaN's
	split_criteria = get_split(round_col, max_groups) #split now - not more than maximum groups
	return split_criteria

def prepare_data(df, num_cols, max_groups): #discretise numerical columns in the dataframe
	df = pd.DataFrame(df)
	criteria = {}
	for col in num_cols: #for all numerical columns in df
		split_criteria = discretize(df[col], max_groups) #get spliting criteria 
		df[col] = split_criteria['d'] #resulting column using cutoffs
		criteria[col] = {
			'cutoff': split_criteria['c'], #cutoffs
			'variance': split_criteria['v'] #variance due to this cutoff limits
		}
	return df, criteria #return resulting dataframe and discretisation criteria


# #testing
# if __name__ == '__main__':
# 	df = pd.DataFrame(np.random.randn(50, 4))
# 	df.columns = list('abcd')
# 	new_df,criteria = prepare_data(df,['a','c'])
# 	df.to_csv('df.csv', sep=',')
# 	new_df.to_csv('new_df.csv', sep=',')
# 	with open('cri.txt','w') as file: file.write(json.dumps(criteria))




