import pandas as pd
import numpy as np 
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
    for i in len(data):
    	if discrete[i] in groups:
    		groups[discrete[i]] += [data[i]]
    	else:
    		groups[discrete[i]] += [data[i]]
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
	sort_col = sorted(list(map(lambda x : int(int(x/10)*10),col.dropna())))
	total = len(sort_col)
	pro_cnt = sorted(Counter(sort_col).items(), key=itemgetter(0))
	probs = OrderedDict()
	for c in pro_cnt:
		probs[c[0]] = c[1]/total
	
	split_criteria = get_split(sort_col)	

	return split_criteria

def prepare_data(df, num_cols):
	df = pd.DataFrame(df)
	criteria = {}
	for col in num_cols:
		d,c,v = discretize(df[col])
		df[col] = d
		criteria[col] = {
		'cutoff': c,
		'variance': v
		}
	return df, criteria






