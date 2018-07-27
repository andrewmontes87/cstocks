import sys, json, datetime, tweepy, time, pytz
import numpy as np
import pandas as pd

# hack to fix cannot import name 'is_list_like' https://bit.ly/2zVcdkK
pd.core.common.is_list_like = pd.api.types.is_list_like

import pandas_datareader as pdr
from pandas_datareader._utils import RemoteDataError

from tickers import *

### DEV
from credentials import *

### PROD
# from os import environ
# CONSUMER_KEY = environ['CONSUMER_KEY']
# CONSUMER_SECRET = environ['CONSUMER_SECRET']
# ACCESS_KEY = environ['ACCESS_KEY']
# ACCESS_SECRET = environ['ACCESS_SECRET']

## connect to twitter api
auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
api = tweepy.API(auth)

## choose an S&P 500 company at random
N = len(TICKERS)
choice = list(np.random.randint(N, size=1)).pop()
ticker, name = TICKERS[choice]

## specify a date range to get prices for
## account for weekends and roll back to friday
## also track if after hours
after_hours = False
now_datetime = datetime.datetime.now(tz=pytz.timezone('US/Eastern'))
today = datetime.datetime.strftime(now_datetime, '%a')
if today == 'Sat':
    now_datetime -= datetime.timedelta(hours=24)
    after_hours = True
elif today == 'Sun':
    now_datetime -= datetime.timedelta(hours=48)
    after_hours = True
today = datetime.datetime.strftime(now_datetime, '%a')

## if outside time range 9:30-4 Eastern
if not datetime.time(9,30) <= now_datetime.time() <= datetime.time(16,30):   
    after_hours = True     

format_string = '%Y-%m-%d'
end_str = datetime.datetime.strftime(now_datetime, format_string)
end_datetime = datetime.datetime.strptime(end_str, format_string)
start_datetime = end_datetime - datetime.timedelta(hours=108)

## logging for dev
# print('today\t', today)
# print('now\t', now_datetime)
# print('end\t', end_datetime)
# print('start\t', start_datetime)

try:
    ## call api for price data
    ya = pdr.yahoo.daily.YahooDailyReader([ticker],
                                          start=start_datetime,
                                          end=end_datetime)

    ## parse price data into dataframe
    df = ya.read()
    df = pd.DataFrame(df.stack()).reset_index()
    df = df.sort_values(by=['Date'], ascending=[False])

    ## logging for dev
    # print(df.head(20))

    ## grab recent prices rows
    ## second-most recent day
    df_prev = df.head(2)
    df_prev = df_prev.sort_values(by=['Date'], ascending=[True])
    df_prev = df_prev.head(1)
    ## most recent day
    df = df.head(1)

    ## parse values from dataframe
    _open = float(list(df['Open'].unique()).pop())
    _close = float(list(df['Close'].unique()).pop())
    _prev_close = float(list(df_prev['Close'].unique()).pop())
    _date_as_str = list(df['Date'].astype(str).unique()).pop()
    _date_as_datetime = datetime.datetime.strptime(_date_as_str, format_string)
    _date_as_day = datetime.datetime.strftime(_date_as_datetime, '%a %b %d')


    ## calc diff and percent change
    _diff = _close - _prev_close
    _percent_change = _diff / _prev_close * 100

    ## conditional text
    _up_down = 'UP' if _diff > 0 else 'DOWN'
    _gain_loss = 'gain' if _diff > 0 else 'loss'
    _closing_currently = 'Closed' if after_hours else 'Currently'
    _was_is = 'was' if after_hours else 'is'

    ## emojis
    bar_chart =  u'\U0001F4CA'
    chart_with_downwards_trend =  u'\U0001F4C9'
    chart_with_upwards_trend =  u'\U0001F4C8'
    moneybag =  u'\U0001F4B0'
    up_arrow = u'\U00002B06'
    down_arrow = u'\U00002B07'
    hammer_and_sickle =  u'\U0000262D'
    # dollar_banknote =  u'\U0001F4B5'
    # chart =  u'\U0001F4B9'

    ## conditional emojis
    _chart_with_trend = chart_with_upwards_trend if _diff > 0 else chart_with_downwards_trend
    _up_down_arrow = up_arrow if _diff > 0 else down_arrow

    ## build tweet string
    tweet_text = '{} - ${}'.format(name,
                                  ticker)
    tweet_text += '\n\n{} QUOTE\n'.format(moneybag)
    tweet_text += '${} {} {} {} on {}\n'.format(ticker,
                                                _was_is,
                                                _up_down,
                                                _up_down_arrow,
                                                _date_as_day)
    tweet_text += '{} at {:.2f} USD '.format(_closing_currently,
                                         _close)
    tweet_text += 'for a {:.2f}% {} from previous close\n{} {} {}\n\n'.format(_percent_change,
                                                                              _gain_loss,
                                                                              _chart_with_trend,
                                                                              _chart_with_trend,
                                                                              _chart_with_trend)
    tweet_text += '{} ANALYSIS\n'.format(bar_chart)
    
    ## conditional tweet closer
    tweet_closer = '{} should be nationalized\n{} {} {}'.format(name,
                                                                hammer_and_sickle,
                                                                hammer_and_sickle,
                                                                hammer_and_sickle)
    tweet_text += tweet_closer

    ## if too long, try a shorter closer
    if len(tweet_text) > 240:
        tweet_text -= tweet_closer
        tweet_text += '${} should be nationalized\n{} {} {}'.format(ticker,
                                                                    hammer_and_sickle,
                                                                    hammer_and_sickle,
                                                                    hammer_and_sickle)

    ## logging for dev
    # print(tweet_text)
    # print(N)

    ## post the tweet
    api.update_status(tweet_text)

## handle exceptions
except KeyError:
    print('KeyError')

except RemoteDataError:
    print('RemoteDataError')

