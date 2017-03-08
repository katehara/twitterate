from pymongo import MongoClient
from bs4 import BeautifulSoup
import pandas as pd

client = MongoClient()
db = client['twitter'] #Put database name here
collection = db['tweets'] # put table name here

cursor = collection.find()
final = []
for val in cursor:
	temp = []
	
	#user_screen_name:
	screen_name = val['user_screen_name']
	is_reply = False
	source = ''
	retweetCount = 0
	hashtags = []

	#Values fetched from user_profile
	followers_count = val['user_profile']['followers_count']

	favourites_count = val['user_profile']['favourites_count']

	listed_count = val['user_profile']['listed_count']

	statuses_count = val['user_profile']['statuses_count']

	verified = val['user_profile']['verified']

	location = val['user_profile']['location']

	#tweets
	tweets = []
	for x in range(0, len(val['user_tweets'])):
		try:
			soup = BeautifulSoup(val['user_tweets'][x]['source'], 'html.parser')
			source = soup.a.text
		except IndexError:
			continue
		try:
			if 'text' in val['user_tweets'][x]:
				tweets.append(val['user_tweets'][x]['text'])
		except IndexError:
			continue
		try:
			soup = BeautifulSoup(val['user_tweets'][x]['source'], 'html.parser')
			source = soup.a.text
		except IndexError:
			continue

		try:
			retweetCount = val['user_tweets'][x]['retweet_count']
		except IndexError:
			continue

		try:
			if val['user_tweets'][x]['in_reply_to_user_id']:
				is_reply = True
		except IndexError:
			continue

		try:
			if 'entities' in val['user_tweets'][x]:
				hList = val['user_tweets'][x]['entities']['hashtags']
				for i in range(0, len(hList)):
					if 'text' in hList[i]:
						hashtags = hList[i]['text']

		except IndexError:
			continue

	temp = list([screen_name , followers_count, favourites_count, listed_count, statuses_count, verified, location, tweets,
		source, is_reply, hashtags])
	final.append(temp)


headers = [screen_name , followers_count, favourites_count, listed_count, statuses_count, verified, location, tweets,
		source, is_reply, hashtags]
df = pd.DataFrame(final, columns = headers)
print(df)









	# print(screen_name)
	# print(followers_count)
	# print(favourites_count)
	# print(listed_count)
	# print(statuses_count)
	# print(verified)
	# print(location)
	# print(tweets)
	# print(source)
	# print(retweetCount)
	# print(is_reply)
	# print(hashtags)

	# print('\n\n')
