import numpy as np
import pandas as pd
import pandas_datareader as pdr
import sys, json, datetime, tweepy, time

# from credentials import *

from os import environ
CONSUMER_KEY = environ['CONSUMER_KEY']
CONSUMER_SECRET = environ['CONSUMER_SECRET']
ACCESS_KEY = environ['ACCESS_KEY']
ACCESS_SECRET = environ['ACCESS_SECRET']

auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
api = tweepy.API(auth)

INTERVAL = 60 * 10  # tweet every 6 hours

temp_tweet = "Testing, testing, one two three: " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

print("Starting here!")

while True:
    print(temp_tweet)
    api.update_status(temp_tweet)
    time.sleep(INTERVAL)