import pandas as pd 
import tweepy
import datetime
import re 
import twitter_credentials
import time
import clean
pd.set_option("display.max_colwidth" , 1000)

consumer_key = twitter_credentials.consumer_key
consumer_secret = twitter_credentials.consumer_secret
access_token = twitter_credentials.access_token
access_token_secret = twitter_credentials.access_token_secret

try: 
    # create OAuthHandler object 
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret) 
    # set access token and secret 
    auth.set_access_token(access_token, access_token_secret) 
    # create tweepy API object to fetch tweets 
    api = tweepy.API(auth, wait_on_rate_limit = True, wait_on_rate_limit_notify = True) 
except: 
    print("Error: Authentication Failed")

def get_tweets(query, count = 10):
    ''' 
    Main function to fetch tweets and parse them. 
    '''
    # empty list to store parsed tweets 
    tweets = [] 
    count = int(count)
    try: 
        # call twitter api to fetch tweets 
        fetched_tweets =tweepy.Cursor(api.search , q = query, lang = "en" ,tweet_mode = 'extended', truncated = False ).items(count)
        
        # parsing tweets one by one 
        for tweet in fetched_tweets: 
            # empty dictionary to store required params of a tweet 
            parsed_tweet = {}

            parsed_tweet = {
                'tweet_id':        tweet.id,
                'name':            tweet.user.name,
                'screen_name':     tweet.user.screen_name,
                'retweet_count':   tweet.retweet_count,
                'text':            tweet.full_text,
                'mined_at':        datetime.datetime.now(),
                'created_at':      tweet.created_at,
                'favourite_count': tweet.favorite_count,
                'hashtags':        tweet.entities['hashtags'],
                'status_count':    tweet.user.statuses_count,
                'location':        tweet.place,
                'source_device':   tweet.source,
                'authorloc':       tweet.author.location 
            }
            
            # if the tweet is retweeted then try to get retweet full text
            try:
                parsed_tweet['retweet_text'] = tweet.retweeted_status.full_text
                parsed_tweet['text'] = parsed_tweet['retweet_text']
            except:
                parsed_tweet['retweet_text'] = "None"
          
            # appending parsed tweet to tweets list 
            if tweet.retweet_count > 0: 
                # if tweet has retweets, ensure that it is appended only once 
                if  parsed_tweet not in tweets: 
                    tweets.append(parsed_tweet) 
            else: 
                tweets.append(parsed_tweet) 

        #clean_tweets, hashtg = clean(tweets['text'])
        #tweets['clean_tweets'] = clean_tweets
        # return parsed tweets 
        return tweets 

    except tweepy.TweepError as e: 
        # print error (if any) 
        print("Error : " + str(e))
        print("Sleeping for 900s...............")
        time.sleep(60)

def clean_text(x):
    twt = clean.RmUrl(str(x))
    twt = clean.RmHshtg(str(twt))
    twt = clean.RmRt(str(twt))
    twt = clean.RmAt(str(twt))
    twt = clean.RmNum(str(twt))
    twt = clean.RmScP(str(twt))
    # print ("The hashtags in tweet are{hshtg}. \n The clean tweet is: {twt}.".format(hshtg = hshtg[0], twt = str(twt)))
    return twt

def extract_hashtags(x):
    hshtg = clean.GetHshtg(str(x))
    return hshtg

def print_tweets(query , count = 10):
    hashtags = []
    col_names = ['tweet_id', 'name', 'screen_name', 'retweet_count', 'text', 'mined_at',
       'created_at', 'favourite_count', 'hashtags', 'status_count', 'location',
       'source_device', 'retweet_text']
    count = int(count)
    tweets = get_tweets(query,count)
    df = pd.DataFrame(tweets)
    cleaned_text = [0]*len(df)
    for i in range(len(df)):
        cleaned_text[i] = clean_text(df['text'][i])
        hashtags.append(extract_hashtags(df['text'][i])[0])
    df['cleaned_text'] = pd.DataFrame(cleaned_text)
    return df, hashtags

def inputq(query, count):
    query = query.split()
    print("The input of query and count are: {q} and {c}\n Please wait for a few Moments.......".format(q = query , c = count))
    try:
        df, hashtags = print_tweets(query, count)
        print("Successful")
        return df, hashtags 
    except:
        print("Failed")


     


