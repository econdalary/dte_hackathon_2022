"""
Try to get more tweet data
"""

import tweepy

# your bearer token
MY_BEARER_TOKEN = "put-it-here"

# create your client 
headers = {
        'Content-Type': 'application/json',
        'accept': 'application/json',
        "User-Agent" : "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36"
    }
client = tweepy.Client(
    bearer_token=MY_BEARER_TOKEN,
)

# client.session(
#     headers=headers, 
#     proxies={"https": "the-proxy"},
#     verify=False
# )

# query to search for tweets
query = "#dte_energy lang:en"

# your start and end time for fetching tweets
start_time = "2021-09-01T00:00:00Z"
end_time = "2022-09-30T00:00:00Z"

# get tweets from the API
tweets = client.search_recent_tweets(
    query=query,
    start_time=start_time,
    end_time=end_time,
    tweet_fields = ["created_at", "text", "source"],
    user_fields = ["name", "username", "location", "verified", "description"],
    max_results = 10,
    expansions='author_id',
)

# tweet specific info
print(len(tweets.data))
# user specific info
print(len(tweets.includes["users"]))

# first tweet
first_tweet = tweets.data[0]
print(dict(first_tweet))

