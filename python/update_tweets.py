# Initial the database on Heroku start-up
from python.app import get_tweet_list, update_db_tweets_table

print("PERFORMING UPDATE: Tweets Table")

# Get the list of Tweets in the Trends table
tweet_list = get_tweet_list()

# Update the tweets table for this list of tweets (add new tweets, and update existig tweets)
update_status = update_db_tweets_table(tweet_list)

print(update_status)