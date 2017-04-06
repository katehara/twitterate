# get users screenname
# get their new data from twitter
# make new hashtags dict
# extract features
# discretise
import yaml, json, tweepy

def apiTwitter():
	with open('config.yaml') as file: conf = yaml.load(file)
	settings = conf['settings']
	consumer_key = settings['ck']
	consumer_secret = settings['cs']
	access_token = settings['at']
	access_token_secret = settings['ats']
	# authorize tweepy instance using twitter tokens and return api reference
	print('connecting to stream...')
	auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
	auth.set_access_token(access_token, access_token_secret)
	return tweepy.API(auth, wait_on_rate_limit=True,parser=tweepy.parsers.JSONParser())

def get_user_data(api, user):


   


def new_data():
	with open('config.yaml', 'r') as file: config = yaml.load(file) #read configuration and assign to variables
	output_file = config['data']['new-data'] # new data output file
	input_file = config['data']['file-discrete'] # input file for screen_names
	user_data = []
	sreen_names = pd.read_csv(input_file)['screen_name']
	api = apiTwitter()
	for user in screen_names:
		row = get_user_data(api, user)
		user_data += row

	user_data = pd.DataFrame(user_data)
	user_data.to_csv(output_file, sep=',', index=False

if __name__ == '__main__':
	new_data()
