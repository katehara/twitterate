import pandas as pd
import numpy as np 
import json, yaml
from numpy import *
from operator import itemgetter
from collections import Counter, OrderedDict

def array_parse(data):
	for i in range(len(data)):
		data[i] = int(data[i])

	return data

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
		if len(groups[i]) == 1: d = 0
		else: d= 1
		variance += np.var(groups[i], ddof=d)

	# cutoff_dict = {}
	# for i in range(len(cutoffs)):
	# 	cutoff_dict[i] = cutoffs[i]
	return discrete, array_parse(cutoffs), float(variance)

def get_split(col, max_groups):
	data = col.dropna() #remove invalid values - drop NaN's
	possible = {}
	found = True
	max_diff = -99999
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

	best_groups=0
	
	# if no minima was reached (variance decreasing with each more partition) - find the partition with max difference from previous partition
	for i in range(1, max_groups): 
		difference = -(possible[i+1]['v'] - possible[i]['v'])
		if (difference > max_diff):
			max_diff = difference;
			best_groups = i+1; 

	if best_groups == 0: best_groups =5

	return possible[best_groups] #return best partition with - newdata, cutoffs & variance

def discretise(df, num_cols, max_groups): #discretise numerical columns in the dataframe
	df = pd.DataFrame(df)
	criteria = {}
	for col in num_cols: #for all numerical columns in df
		split_criteria = get_split(df[col], max_groups) #get spliting criteria 
		df[col] = split_criteria['d'] #resulting column using cutoffs
		criteria[col] = {
			'cutoff': split_criteria['c'], #cutoffs
			'variance': split_criteria['v'] #variance due to this cutoff limits
		}
	return df, criteria #return resulting dataframe and discretisation criteria

if __name__ == '__main__':
	with open('config.yaml', 'r') as file: config = yaml.load(file) #read configuration and assign to variables
	input_file = config['data']['file-collection']
	output_file = config['data']['file-discrete']
	dis_cri_file = config['data']['criteria-dict']
	num_cols = config['parameters']['num-cols']
	max_groups = config['parameters']['max-groups']
	df = pd.read_csv(input_file)
	discrete_data, criteria = discretise(df, num_cols, max_groups) # get discrete dataframe and criteria 
	df.to_csv(output_file, sep=',', index=False) # save the data as csv
	with open(dis_cri_file, 'w') as file: json.dump(criteria, file) #save criteria as json file

# #testing
# if __name__ == '__main__':
# 	df = pd.DataFrame(np.random.randn(50, 4))
# 	df.columns = list('abcd')
# 	new_df,criteria = discretise(df,['a','c'])
# 	df.to_csv('df.csv', sep=',')
# 	new_df.to_csv('new_df.csv', sep=',')
# 	with open('cri.txt','w') as file: file.write(json.dumps(criteria)