#takes dataframe & returns dict of all value counts as dict
def describe_attrs(df, cols):
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
        avc = part.attr_desc[col][dp[i]]/sdc
        av = uni_desc[col][dp[i]]/pdc
        j = (avc*avc)-(av*av)
        sumi += j
    cm = pck*sumi
    return cm

def reconstruct(parts , df):
    for p in parts:
        p.data = df[df['partition']==p.name]        
    return parts