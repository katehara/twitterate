from collections import Counter
import pandas as pd
import yaml

with open('config.yaml', 'r') as file: config = yaml.load(file) #read configuration and assign to variables
cols_use = config['parameters']['cols-to-be-used']

#takes dataframe & returns dict of all value counts as dict
def describe_attrs(df):
	cols = cols_use
	desc = {col:describe_attr(df[col]) for col in cols}
	return desc

#takes one column of dataframe & returns value with counts
def describe_attr(col):
	col = list(col)
	desc = {k:v for k,v in Counter(col).items()}
	return desc

def rename_data(partitions):
	i=0
	for p in partitions:
		p.name = 'N'+str(i)
		i += 1
	return partitions


def label_data(partitions, df):
	dfs = []
	for part in partitions:
		pdf = part.data
		pdf['partition'] = [part.name]
		dfs += [pdf]
	labeled = pd.concat(dfs)
	labeled = labeled.reset_index().drop(['index'], axis=1)
	return labeled

def category_match(part, dp, uni_desc, uni_len):
	sumi = 0
	sdc = part.data_count
	pdc = uni_len
	pck = sdc/pdc
	cols = uni_desc.keys()
	for i, col in enumerate(cols): 
		if col in cols_use:
			if part.attr_desc[col][dp[i]] in part.attr_desc[col]: 
				avc = part.attr_desc[col][dp[i]]/sdc
				if uni_desc[col][dp[i]] in uni_desc[col]:
					av = uni_desc[col][dp[i]]/pdc
					j = (avc*avc)-(av*av)
					sumi += j
	cm = pck*sumi
	return cm

def reconstruct(parts , df):
	for p in parts:
		p.data = df[df['partition']==p.name]		
	return parts