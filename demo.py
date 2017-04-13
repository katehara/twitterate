from nltk.sentiment.vader import SentimentIntensityAnalyzer
import json, yaml, re, pandas as pd, sys, tweepy
import feature_ext, helper
from data_structures import Node
from ordering import nominal_cityblock

with open('config.yaml', 'r') as file: config = yaml.load(file) #read configuration and assign to variables

def apiTwitter():
	# authorize tweepy instance using twitter tokens and return api reference
	with open('confidential.yaml') as file: conf = yaml.load(file)
	settings = conf['settings']
	consumer_key = settings['ck']
	consumer_secret = settings['cs']
	access_token = settings['at']
	access_token_secret = settings['ats']
	auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
	auth.set_access_token(access_token, access_token_secret)
	return tweepy.API(auth, wait_on_rate_limit=True, parser=tweepy.parsers.JSONParser())

def fetch_data(handle):
	api = apiTwitter()
	try:		
		item = {
			"user_screen_name" : handle, #unique identifier for each user object
			"user_profile": api.get_user(screen_name=handle), # user profile
			"user_tweets": api.user_timeline(screen_name=handle) #get last 20 tweets for the user
		}	
		return item
	except Exception as e:
		print('Problem collecting data for handle : {}'.format(handle))
		print('1. Check your Internet connection.')
		print('2. Make sure the handle exists.')
		print('3. Try again.')
		return

def extract_features(u):
	hashtag_file = config['data']['hashtags-dict']
	with open(hashtag_file, 'r') as file: hashtags_dict = json.load(file) 
	screen_name = u['user_screen_name'] # unique identifier for each user
	u_fol = u['user_profile']['followers_count'] # followers
	u_fav = u['user_profile']['favourites_count'] # favoites
	u_lis = u['user_profile']['listed_count'] # listed
	u_sta = u['user_profile']['statuses_count'] #statuses
	u_fri = u['user_profile']['friends_count'] #friends
	ver = u['user_profile']['verified'] #user verified - boolean
	hash_freq, avg_ret, avg_fav, source, sentiment = feature_ext.metrics(u['user_tweets'], hashtags_dict) # get user features from tweets
	features = [screen_name, u_fol, u_fav, u_lis, u_sta, u_fri, ver, hash_freq, avg_ret, avg_fav, source, sentiment]
	return features

def disc_value(value, cutoffs):
	for i in range(len(cutoffs)):
		if value <= cutoffs[i]: return i
	return len(cutoffs)-1

def discretise(features):
	disc_features = []
	criteria_file = config['data']['criteria-dict']
	all_columns = config['parameters']['all-cols']
	with open(criteria_file, 'r') as file: criteria = json.load(file) 
	for i, col in enumerate(all_columns):
		if col in criteria: 
			disc_features += [disc_value(float(features[i]), criteria[col]['cutoff'])]
			# print(i, col, features[i])

		else: disc_features += [features[i]]
	return disc_features

def cluster_score(dp):
	trust_model = config['data']['file-trust']
	cols_use = config['parameters']['cols-to-be-used']
	df = pd.read_csv(trust_model)
	dl = df.values.tolist()
	cols = df.columns.tolist() 
	root = Node(name='R', data=df, level=0, parent = None)
	nodes = []
	max_cmdk = -99999
	uni_desc = helper.describe_attrs(df) #description of universal (root) data
	uni_len = len(df)
	sum_rate = 0
	sum_cmdk = 0
	for p in set(df['partition']):
		part_data = df[df['partition']==p]
		part = Node(name=p, data = part_data, level =1, parent = root)
		cm_d_k = helper.category_match(part, dp, uni_desc, uni_len, cols) # calculate category match measure for this dp to belong to this partion
		# if cm_d_k > max_cmdk: # dp should be a part of partition with highest measure of cmdk for it
		# 	max_cmdk = cm_d_k
		# 	max_part = part.name
		rate = list(part_data['trust'])[0]
		sum_rate += rate*cm_d_k
		sum_cmdk += cm_d_k 
	return sum_rate/sum_cmdk

def rate(handle):
	# get data
	user_object = fetch_data(handle)
	if user_object is None : return
	#extract features + hashtagdict
	features = extract_features(user_object)
	#discretise acc to criteria
	disc_features = discretise(features)
	# check which cluster it belongs to 
	score = cluster_score(disc_features)
	# calculate score
	norm_score = int(score*10)/10 +1.0
	if norm_score < 0: norm_score = 0
	if norm_score > 5: norm_score = 5
	print('We can trust {} on a level of {} out of 5.'.format(user_object['user_profile']['name'], norm_score))
	return

def repeat_rate():
	print('### Type "bye" to exit ###')
	while True:
		handle = input('Twitter handle : ' )
		if handle == 'bye':
			print('Bbye. Never lose trust 8-).')
			break
		elif handle == '':
			continue
		else:
			rate(handle)
			
	return

if __name__ == '__main__':
	args = sys.argv[1:]
	if not args:
		repeat_rate()
	else : 
		rate(args[0])