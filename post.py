from tickers import *

import sys, json, datetime, tweepy, time
import numpy as np
import pandas as pd

# hack to fix cannot import name 'is_list_like' https://bit.ly/2zVcdkK
pd.core.common.is_list_like = pd.api.types.is_list_like

import pandas_datareader as pdr
from pandas_datareader._utils import RemoteDataError

### DEV
# from credentials import *

### PROD
from os import environ
CONSUMER_KEY = environ['CONSUMER_KEY']
CONSUMER_SECRET = environ['CONSUMER_SECRET']
ACCESS_KEY = environ['ACCESS_KEY']
ACCESS_SECRET = environ['ACCESS_SECRET']

auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
api = tweepy.API(auth)


ticker = np.random.choice(TICKERS)

end_datetime =datetime.datetime.now() 
start_datetime = end_datetime - datetime.timedelta(hours=24)

date_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

try:
    ya = pdr.yahoo.daily.YahooDailyReader([ticker],
                                          start=start_datetime,
                                          end=end_datetime)

    df = ya.read()
    df = pd.DataFrame(df.stack()).reset_index()
    df = df.sort_values(by=['Date'], ascending=[False])
    df = df.head(1)
    _date = list(df['Date'].unique()).pop()
    _open = float(list(df['Open'].unique()).pop())
    _close = float(list(df['Close'].unique()).pop())
    _diff = _close - _open
    _percent_change = _diff / _open * 100
    _up_down = 'up' if _diff > 0 else 'down'
    _gain_loss = 'gain' if _diff > 0 else 'loss'
    tweet_text = 'FUNDAMENTALS:\n'
    tweet_text += '{} is {} today, '.format(ticker, _up_down)
    tweet_text += 'opening at {:.2f} and closing at {:.2f} '.format(_open, _close)
    tweet_text += 'for a {} of {:.2f}%\n\n'.format(_gain_loss, _percent_change)
    tweet_text += 'ANALYSIS:\n'
    tweet_text += '{} should be nationalized'.format(ticker)
    print(tweet_text)
    api.update_status(tweet_text)

except KeyError:
    print('KeyError')

except RemoteDataError:
    print('RemoteDataError')

    # temp_tweet = "Testing, testing, one two three: " + date_str

# print(temp_tweet)
