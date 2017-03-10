from collections import Counter
import yaml, json
from pymongo import MongoClient

def hashtags(connection_string, db_name, collection_name): #return the list of hashtags ever appeared in the db
    hashtags_list = []
    client = MongoClient() # connect to mongod server
    tweetdb = client[db_name] # get the db named 'demon_india' (demon - demonetisation)
    user_info = tweetdb[collection_name] # get collection reference for user info collection
    users = user_info.find({}) # get all data from collection
    for u in users: #for all users
        twee = u['user_tweets'] #get last 20(or less) tweets
        for t in twee: #for all tweets of this user
            h = t['entities']['hashtags'] #get list of hashtags
            for ht in h: #for all hashtags 
                hashtags_list += [ht['text']] #addit to the list
    return hashtags_list

#for one time run
if __name__ == '__main__':  
    with open('config.yaml', 'r') as file: config = yaml.load(file) #read configuration and assign to variables
    connection_string = config['data']['mongo-conn-string']
    db_name = config['data']['mongo-db']
    collection_name = config['data']['mongo-collection']
    hashtag_file = config['data']['hashtags-dict']
    hashtags_list = hashtags(connection_string, db_name, collection_name) #get list of hashtags
    hash_counter = Counter(hashtags_list) # get frequecy of all hashtags
    hash_dict = {}
    for tag, freq in hash_counter.items(): #store the hashtag and frequecy as key value pair
        hash_dict[tag] = freq
    with open(hashtag_file, 'w') as file: json.dump(hash_dict, file) #write dict as json