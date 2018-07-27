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

format_string = '%Y-%m-%d'

now_datetime = datetime.datetime.now()
end_str = datetime.datetime.strftime(now_datetime, format_string)
end_datetime = datetime.datetime.strptime(end_str, format_string)

start_datetime = end_datetime - datetime.timedelta(hours=108)

# print(ticker, start_datetime, end_datetime)

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

    chart_increasing =  u'\U0001F4C8'
    bar_chart =  u'\U0001F4CA'
    chart_with_downwards_trend =  u'\U0001F4C9'
    chart_with_upwards_trend =  u'\U0001F4C8'
    chart =  u'\U0001F4B9'
    moneybag =  u'\U0001F4B0'
    dollar_banknote =  u'\U0001F4B5'

    up_arrow = u'\U00002B06'
    down_arrow = u'\U00002B07'

    hammer_and_sickle =  u'\U0000262D'

    _chart_with_trend = chart_with_upwards_trend if _diff > 0 else chart_with_downwards_trend
    _up_down_arrow = up_arrow if _diff > 0 else down_arrow

    tweet_text = '${}: {}'.format(ticker, end_str)
    tweet_text += '\n\n{} STOCK QUOTE:\n'.format(moneybag)
    tweet_text += '${} is {} {} in the latest trading session, '.format(ticker, _up_down, _up_down_arrow)
    tweet_text += 'opening at {:.2f} and closing at {:.2f} '.format(_open, _close)
    tweet_text += 'for a {} of {:.2f}%\n{} {} {}\n\n'.format(_gain_loss, _percent_change, _chart_with_trend, _chart_with_trend, _chart_with_trend)
    tweet_text += '{} ANALYSIS:\n'.format(bar_chart)
    tweet_text += '${} should be nationalized\n{} {} {}'.format(ticker, hammer_and_sickle, hammer_and_sickle, hammer_and_sickle)

    # print(tweet_text)
    api.update_status(tweet_text)

except KeyError:
    print('KeyError')

except RemoteDataError:
    print('RemoteDataError')

