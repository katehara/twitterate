from collections import Counter
import yaml, json
from pymongo import MongoClient

def hashtags(connection_string, db_name, collection_name):
    hashtags_list = []
    client = MongoClient() # connect to mongod server
    tweetdb = client[db_name] # get the db named 'demon_india' (demon - demonetisation)
    user_info = tweetdb[collection_name]
    users = user_info.find({})
    for u in users:
        twee = u['user_tweets']
        for t in twee:
            h = t['entities']['hashtags']
            for ht in h:
                hashtags_list += [ht['text']]
    return hashtags_list


#for one time run
if __name__ == '__main__':  
    with open('config.yaml', 'r') as file: config = yaml.load(file)
    connection_string = config['data']['mongo-conn-string']
    db_name = config['data']['mongo-db']
    collection_name = config['data']['mongo-collection']
    hashtag_file = config['data']['hashtags-dict']
    hashtags_list = hashtags(connection_string, db_name, collection_name)
    hash_counter = Counter(hashtags_list)
    hash_dict = {}

    for tag, freq in hash_counter.items():
        hash_dict[tag] = freq

    with open(hashtag_file, 'w') as file: json.dump(hash_dict, file)
               