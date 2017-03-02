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
    

def ctree(df):
    var root = Node( data=df , children=[], level=0, parent = None )
    var L = [root]
    for node in L[:]:
        node.sort_data()
        node.partition()
        L += node.children
        L.remove(node)        
    return root



def extract_partition(root):
    initial_partition= []
    var L = [root]
    for node in L[:]:
        smaller = 0
        children = node.children
        smaller = sum([1 for child in children if node.utility <= child.utility])
        if smaller == 0 : 
            initial_partition += [node]
        else : 
            for child in children:
                if node.utility <= child.utility: L += [child]
                else: initial_partition += [child]
        L.remove(node)
    intial_partition = rename_data(initial_partition)
    labeled = label_data(initial_partition, root.data)
    return intial_partition, labeled
  
  
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
    
def redistribute(initial_partition, labeled):
    old_lab = pd.DataFrame(labeled).values.tolist()
    new_lab = []
    part_col = labeled.columns.index("partition")
    uni_desc = describe_attrs(labeled.drop(['partition'],axis=1))
    uni_len = len(df)
    while old_lab != new_lab:
        new_lab = old_lab
        for dp in new_lab:
            max_cmdk = -9999
            max_part = dp[part_col]
            for part in initial_partition:
                cm_d_k = category_match(part, dp, uni_desc, uni_len)
                if cm_d_k > max_cmdk:
                    max_cmdk = cm_d_k
                    max_part = part
            dp[part_col] = part
    new_lab = pd.DataFrame(initial_partitioninitial_partitionnew_lab)  
    final_partition = reconstruct(new_lab)              
    return final_partition, new_lab
    
            
     
        

    
    