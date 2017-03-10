from nltk.sentiment.vader import SentimentIntensityAnalyzer
import json, yaml, re, pandas as pd
from pymongo import MongoClient
from collections import Counter

def nltk_senti(s_svg):
	if -1.0 <= s_svg < -0.8: return 0
	elif -0.8 <= s_svg < -0.6: return 1
	elif -0.6 <= s_svg < -0.4: return 2
	elif -0.4 <= s_svg < -0.2: return 3
	elif -0.2 <= s_svg < 0.0: return 4
	elif 0.0 <= s_svg < 0.2: return 5
	elif 0.2 <= s_svg < 0.4: return 6
	elif 0.4 <= s_svg < 0.6: return 7
	elif 0.6 <= s_svg < 0.8: return 8
	elif 0.8 <= s_svg <= 1.0: return 9 

def metrics(twee, hashtags_dict):
	sid = SentimentIntensityAnalyzer()
	tweets = len(twee)
	if tweets == 0: return (0,0,0,'None',0)
	hash_count = 0
	hash_sum = 0
	retweets = 0
	favorites = 0
	sources = []
	sentiment = 0	
	for t in twee:
		h = t['entities']['hashtags']
		for ht in h:
			hash_count += 1
			hash_sum += hashtags_dict[ht['text']]
			
		retweets += t['retweet_count']
		favorites += t['favorite_count']
		m = re.match("<a[^>]*>([^<]+)</a>",t['source'])
		if m: sources += [m.group(1)]		
		sv = sid.polarity_scores(t['text'])
		sentiment += sv['compound']	 
	
	if hash_count == 0: hash_freq = '-1'
	else: hash_freq = hash_sum/hash_count
	avg_ret = retweets/tweets
	avg_fav = favorites/tweets
	source, s_count = Counter(sources).most_common(1)[0] 
	sentiment = nltk_senti(sentiment/tweets)  	
	return (hash_freq, avg_ret, avg_fav, source, sentiment)
	
def collect(hashtags_dict, connection_string, db_name, collection_name):
	user_list = []
	client = MongoClient() # connect to mongod server
	tweetdb = client[db_name] # get the db named 'demon_india' (demon - demonetisation)
	user_info = tweetdb[collection_name]
	users = user_info.find({})
	for u in users:
		screen_name = u['user_screen_name']
		u_fol = u['user_profile']['followers_count']
		u_fav = u['user_profile']['favourites_count']
		u_lis = u['user_profile']['listed_count']
		u_sta = u['user_profile']['statuses_count']
		u_fri = u['user_profile']['friends_count']
		ver = u['user_profile']['verified']
		hash_freq, avg_ret, avg_fav, source, sentiment = metrics(u['user_tweets'], hashtags_dict)
		user_list += [[screen_name, u_fol, u_fav, u_lis, u_sta, u_fri, ver, hash_freq, avg_ret, avg_fav, source, sentiment]]
	return user_list
		
#for one time execution
if __name__ == '__main__':
	with open('config.yaml', 'r') as file: config = yaml.load(file)
	connection_string = config['data']['mongo-conn-string']
	db_name = config['data']['mongo-db']
	collection_name = config['data']['mongo-collection']
	filename = config['data']['file-collection']
	hashtag_file = config['data']['hashtags-dict']
	with open(hashtag_file, 'r') as file: hashtags_dict = json.load(file)
	user_list = collect(hashtags_dict, connection_string, db_name, collection_name)
	df = pd.DataFrame(user_list)
	df.columns = ['screen_name', 'u_fol', 'u_fav', 'u_lis', 'u_sta', 'u_fri', 'ver', 'hash_freq', 'avg_ret', 'avg_fav', 'source', 'sentiment']
	df.to_csv(filename, sep=',')