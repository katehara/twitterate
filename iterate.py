

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
    labeled = label_data(initial_partition, root.data)
    return intial_partition, labeled
    
def redistribute(initial_partition, labeled):
    old_lab = pd.DataFrame(labeled)
    new_lab = pd.Dataframe()
    while old_lab != new_lab:
        new_lab = old_lab
        for dp in new_lab.iterrows():
            max_cmdk = -9999
            max_part = dp['partition']
            for part in initial_partition:
                cm_d_k = category_match(part, dp)
                if cm_d_k > max_cmdk:
                    max_cmdk = cm_d_k
                    max_part = part
                dp['partition'] = part
                
    final_partition = reconstruct(new_lab)              
    return final_partition, new_lab
    
            
     
        

    
    