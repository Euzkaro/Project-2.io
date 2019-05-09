# Initial the database on Heroku start-up
from python.app import update_db_tweets_table

print("PERFORMING UPDATE: Tweets Table")
n_tweets = update_db_tweets_table()
print(n_tweets)