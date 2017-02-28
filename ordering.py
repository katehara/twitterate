from collections import Counter
import pandas as pd
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
    #calculate dist b/w 2 objecta


def manhattan_matrix(df):
    #nested loop calculte manhattan matrix
    return pd.DataFrame(matrix) 

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


 #testing
if __name__ == '__main__':
	df = pd.DataFrame({'A':[1,1,2,3,1,3], 'B':[2,2,3,5,7,8], 'C':[9,8,7,7,8,9]})
	new_df,order, manhattan = ADO(df,2)
	df.to_csv('df.csv', sep=',')
	new_df.to_csv('new_df.csv', sep=',')
	manhattan.to_csv('blah.csv', sep=',')

        
        
    


















