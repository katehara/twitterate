# #!/usr/bin/python
import nltk
import json
import nltk.classify.util
from nltk.classify import NaiveBayesClassifier
from nltk.metrics import BigramAssocMeasures
from nltk.metrics.scores import precision, recall
from nltk.probability import FreqDist, ConditionalFreqDist
from nltk.corpus import stopwords
from nltk.corpus import twitter_samples
from nltk.corpus import stopwords
import re
global classifier
testRead = json.loads(open('sampleTweets.json').read())

stop = set(stopwords.words('english'))

emoticons_str = r"""
	    (?:
        [:=;] # Eyes
        [oO\-]?
        [D\)\]\(\]/\\OpP] # Mouth
        )"""

regex_str = [
    emoticons_str,
    r'<[^>]+>', # HTML tags
    r'(?:@[\w_]+)', # @-mentions
    r"(?:\#+[\w_]+[\w\'_\-]*[\w_]+)", # hash-tags
    r'http[s]?://(?:[a-z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-f][0-9a-f]))+', # URLs
 
    r'(?:(?:\d+,?)+(?:\.?\d+)?)', # numbers
    r"(?:[a-z][a-z'\-_]+[a-z])", # words with - and '
    r'(?:[\w_]+)', # other words
    r'(?:\S)' # anything else
]

tokens_re = re.compile(
        r'(' + '|'.join(regex_str) + ')', re.VERBOSE | re.IGNORECASE)

emoticon_re = re.compile(
        r'^' + emoticons_str + '$', re.VERBOSE | re.IGNORECASE)


def extract_features(document):
    
    document_words = set(document)
    features = {}
    for word in word_features:
    	features['contains(%s)' % word] = (word in document_words)
    return features


class DataCleaning:
	# regex_str = [emoticons_str, r'<[^>]+>', r'(?:@[\w_]+)', r"(?:\#+[\w_]+[\w\'_\-]*[\w_]+)", r'http[s]?://(?:[a-z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-f][0-9a-f]))+', r'(?:(?:\d+,?)+(?:\.?\d+)?)', r"(?:[a-z][a-z'\-_]+[a-z])", r'(?:[\w_]+)', r'(?:\S)']

    # simple_regex = [ r'(@\w+)', r'(\d+)', r'(#\w+)', r'(#\d+\w+)']
    def __init__(self, some_list):
    	self.some_list = some_list

    def tokenize(self, s):
    	self.s = s
    	return tokens_re.findall(s)

    def preprocess(self, some_list, tag, lowercase=False):
        # print ("some list is\n", some_list)
        output_list = []
        for s in self.some_list:
        	
        	s = [i for i in s.lower().split() if i not in stop]
        	s = " ".join(s)
        	tokens = self.tokenize(s)


        	# print ("Tokens are\n", tokens)

        	for token in tokens:
        		# print (token)
        		output_dict = {}

        		for reg in regex_str:

        			if bool(re.search(reg, token)) or token.startswith('#') or token.startswith('@') or len(token)<3:
        				continue
        			else:
        				if token not in output_dict:
        					output_dict[token] = 1
        				else:
        					output_dict[token]+= 1
        		if len(output_dict)>0:
        			values = (output_dict,) + (tag,)
        			output_list.append(values)
        # 	break
        # print("output List\t", output_list)

        return output_list




#----------File reading of all tweets---------
files = twitter_samples.fileids()

positive_tweets_list = twitter_samples.open(files[1]).readlines()
negative_tweets_list = twitter_samples.open(files[0]).readlines()

def tweets_in_json(tweets_list):

	temp_list = []

	for tweets in tweets_list:

		tweets = json.loads(tweets)
		text_of_tweet = tweets['text']
		temp_list.append(text_of_tweet)

	return temp_list

positive_tweets = tweets_in_json(positive_tweets_list)
negative_tweets = tweets_in_json(negative_tweets_list)

dataCleanerPos = DataCleaning(positive_tweets)
dataCleanerNeg = DataCleaning(negative_tweets)

preprocess_pos_tweets = []
preprocess_neg_tweets = []

preprocess_pos_tweets = dataCleanerPos.preprocess(positive_tweets, 'positive')
preprocess_neg_tweets = dataCleanerNeg.preprocess(negative_tweets, 'negative')

trainFeatures = preprocess_pos_tweets + preprocess_neg_tweets

word_features = []
word_features.append(tup[0][0] for tup in trainFeatures)

classifier = NaiveBayesClassifier.train(trainFeatures)

def classify_tweet(tweet):
	
	return classifier.classify(extract_features(tweet.split()))

sen = 'i am wondering that cashless India is better way for developing our Indias future'
print(classify_tweet(sen))