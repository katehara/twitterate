import json
import yaml



def collect(): ### onetime
	#read configuration
	#read tweets from mongo 
	#extract/calculate features
	#save as pandas df -> csv

def discretize(): ##onetime
	#read configration 
	# read data from csv
	#discretise columns
	# validate all columns
	# save as csv again
	#save discretisation criterion as yaml/json for further reference (unseen data)

def iterate():
	#read configuration
	#read data
	#read columns to process on
	#ctree
	#partitions
	#redistribute
	#save data

def analyse():
	#read configuration 
	# read clustered data
	# analyse all data - collective and clusterised
	#generate a report 

