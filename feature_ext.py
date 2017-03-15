from nltk.sentiment.vader import SentimentIntensityAnalyzer
import json, yaml, re, pandas as pd
from pymongo import MongoClient
from collections import Counter

def nltk_senti(s_svg): # avg tweet-sentiment -> level between 0-9
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

def metrics(twee, hashtags_dict): # calculae user features from its tweets
	sid = SentimentIntensityAnalyzer() # Vader-lexicon-sentiment-analyser
	#initialise metrics & counts for aggregation 
	tweets = len(twee)
	if tweets == 0: return (0,0,0,'None',5) #return none/0 for users with no tweets
	hash_count = 0
	hash_sum = 0
	retweets = 0
	favorites = 0
	sources = []
	sentiment = 0
	for t in twee: #for all tweets - calculate sum of frequencies of all hashtags of a user
		h = t['entities']['hashtags']
		for ht in h:
			hash_count += 1
			hash_sum += hashtags_dict[ht['text']]
			
		retweets += t['retweet_count'] #sum of retweets
		favorites += t['favorite_count'] # sum of favorites
		m = re.match("<a[^>]*>([^<]+)</a>",t['source']) #extract source from anchor tag
		if m: sources += [m.group(1)]		
		sv = sid.polarity_scores(t['text']) # polarity scores of tweetd
		sentiment += sv['compound']	 #overall sentiment of tweet
	
	if hash_count == 0: hash_freq = '-1' # if no hashtags used - set frequency avg to -1
	else: hash_freq = hash_sum/hash_count # else rerurn their average
	avg_ret = retweets/tweets # avg retweets on all tweets
	avg_fav = favorites/tweets # avg favorites on all tweets
	source, s_count = Counter(sources).most_common(1)[0] # most common type of device used for tweet
	sentiment = nltk_senti(sentiment/tweets) # average sentiment level  	
	return (hash_freq, avg_ret, avg_fav, source, sentiment)
	
def collect(hashtags_dict, connection_string, db_name, collection_name):
	user_list = []
	client = MongoClient() # connect to mongod server
	tweetdb = client[db_name] # get the db named 'demon_india' (demon - demonetisation)
	user_info = tweetdb[collection_name] # get collection
	users = user_info.find({}) # get data from collection
	for u in users: # for all users -> extract features
		screen_name = u['user_screen_name'] # unique identifier for each user
		u_fol = u['user_profile']['followers_count'] # followers
		u_fav = u['user_profile']['favourites_count'] # favoites
		u_lis = u['user_profile']['listed_count'] # listed
		u_sta = u['user_profile']['statuses_count'] #statuses
		u_fri = u['user_profile']['friends_count'] #friends
		ver = u['user_profile']['verified'] #user verified - boolean
		hash_freq, avg_ret, avg_fav, source, sentiment = metrics(u['user_tweets'], hashtags_dict) # get user features from tweets
		user_list += [[screen_name, u_fol, u_fav, u_lis, u_sta, u_fri, ver, hash_freq, avg_ret, avg_fav, source, sentiment]]
	return user_list # return features for all users as list-of-lists
		
#for one time execution
if __name__ == '__main__':
	with open('config.yaml', 'r') as file: config = yaml.load(file) #read configuration and assign to variables
	connection_string = config['data']['mongo-conn-string']
	db_name = config['data']['mongo-db']
	collection_name = config['data']['mongo-collection']
	filename = config['data']['file-collection']
	hashtag_file = config['data']['hashtags-dict']
	with open(hashtag_file, 'r') as file: hashtags_dict = json.load(file) # get hashtag dict of frequency
	user_list = collect(hashtags_dict, connection_string, db_name, collection_name) # get list-of-list of features for all users
	df = pd.DataFrame(user_list) # construct dataframe for users
	df.columns = ['screen_name', 'u_fol', 'u_fav', 'u_lis', 'u_sta', 'u_fri', 'ver', 'hash_freq', 'avg_ret', 'avg_fav', 'source', 'sentiment']
	df.to_csv(filename, sep=',', index=False) # save the data as csv