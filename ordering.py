from collections import Counter
import pandas as pd
import numpy as np
import json

# manhattan distance between two data points - nominal attribtutes (no of attributes havving different values)
def nominal_cityblock(u, v):
	dist = 0
	for i in range(len(u)):
		if u[i] != v[i]: dist +=1
	return dist

#distance matrix for data points using manhattan distance
def manhattan_matrix(df):
	data_values = df.values.tolist()
	dist = np.zeros((len(data_values),len(data_values))) #initialise matrixwith zeros
	for i in range(len(data_values)): #for all data points
		for j in range(i,len(data_values)): #for all next data point
			dist[i][j] = dist[j][i] = nominal_cityblock(data_values[i], data_values[j]) #get distance and place in symmetrical square matrix
	return pd.DataFrame(dist) 

def find_farthest(lastn):
	sums = lastn.sum(axis=1) #row with sum of distances of each point from last-n 
	max_index = sums.idxmax(axis=0) #index of point fartest from last-n
	return max_index

def ADO(df, n):
	manhattan = manhattan_matrix(df) #get distance matrix for all datapoints
	sums = manhattan.sum(axis=1) #row with sum of distances of each point from every other one
	order = list(sums.argsort()[-n:][::-1]) #order of index sorted descending by sums - take last n
	residual = manhattan.drop(order, axis=0) #drop the data points from rows which have been aken in ordered indexes
	while len(residual)>0: #for every data point in matrix (rows)
		lastn = residual[order[-n:]] #get last n points distances - columns
		far_index = find_farthest(lastn) #find farthest of them all
		residual = residual.drop(far_index, axis=0) # drop the selected one from matrix
		order += [far_index] #add the selected on to the order
		
	df = df.reindex(index=order).reset_index().drop(['index'],axis=1) #order the data frame according the ordering of indexes - reindex from 0 -> n-1 -drop the jumbled index column		
	return df,order,manhattan #return ordered dataframe , odere of indexes , manhattan distance matrix


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
		
		
	


















