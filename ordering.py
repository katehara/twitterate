from collections import Counter
import pandas as pd
import numpy as np
import json
from scipy.spatial.distance import pdist, squareform

#takes dataframe & returns dict of all value counts as dict
def describe_attrs(df):
	desc = {col:describe_attr(df[col]) for col in df}
	return desc
	
#takes one column of dataframe & returns value with counts
def describe_attr(col):
	col = list(col)
	desc = {k:v for k,v in Counter(col).items()}
	return desc


def nominal_cityblock(u, v):
	dist = 0
	for i in range(len(u)):
		if u[i] != v[i]: dist +=1
	return dist

def manhattan_matrix(df):
	#nested loop calculte manhattan matrix
	data_values = df.values.tolist()
	dist = np.zeros((len(data_values),len(data_values)))
	for i in range(len(data_values)):
		for j in range(i,len(data_values)):
			dist[i][j] = dist[j][i] = nominal_cityblock(data_values[i], data_values[j])
	return pd.DataFrame(dist) 

def find_farthest(lastn):
	sums = lastn.sum(axis=1)
	max_index = sums.idxmax(axis=0)
	return max_index

def ADO(df, n):
	manhattan = manhattan_matrix(df)
	sums = manhattan.sum(axis=0)
	order = list(sums.argsort()[-n:][::-1])
	residual = manhattan.drop(order, axis=0)
	while len(residual)>0:
		 lastn = residual[order[-n:]]
		 far_index = find_farthest(lastn)
		 residual = residual.drop(far_index, axis=0)
		 order += [far_index]
		
	df = df.reindex(index=order).reset_index().drop(['index'],axis=1)		
	return df,order,manhattan


# #testing
# if __name__ == '__main__':
# 	df = pd.DataFrame({'A':['a','a','b','c','a','c'], 'B':['b','b','c','d','e','f'], 'C':['g','f','e','e','f','g']})
# 	new_df,order, manhattan = ADO(df,2)
# 	df.to_csv('df.csv', sep=',')
# 	new_df.to_csv('new_df.csv', sep=',')
# 	manhattan.to_csv('mat.csv', sep=',')

''' 
Test results :

df 
	| 	A	B	C
------------------
0	| 	a	b	g
1	| 	a	b	f
2	| 	b	c	e
3	| 	c	d	e
4	| 	a	e	f
5	| 	c	f	g

new_df
	|	A	B	C
------------------
0	|	b	c	e
1	|	c	f	g
2	|	a	b	f
3	|	c	d	e
4	|	a	b	g
5	|	a	e	f


mat
	|	0	1	2	3	4	5
------------------------------
0	|	0	1	3	3	2	2
1	|	1	0	3	3	1	3
2	|	3	3	0	2	3	3
3	|	3	3	2	0	3	2
4	|	2	1	3	3	0	3
5	|	2	3	3	2	3	0


'''
		
		
	

















