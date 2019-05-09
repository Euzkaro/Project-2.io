from twitter import *
import tweepy
import networkx as nx
import json
import os

# Clear screen
os.system('cls' if os.name=='nt' else 'clear')

graph=nx.DiGraph()

print (".....................................................")
print ("Network of Hashtag")
print ("")

hashtag = input("Enter the hashtag you want to anlyze: ")

# Log in
CONSUMER_KEY = 't6gxzqwZTX6S3BnXYM3YGqriA'
CONSUMER_SECRET = '6ByaQVf9ljEQHWwrfQbkyG674dhu0TQeJh8VrGqzrrBLaDZc94'
OAUTH_TOKEN = '1031172880300687361-XsNI26GX8GngiUGw3ord7vQtKdcoPk'
OAUTH_TOKEN_SECRET = 'VnThCcjLUmqWE3UIxb62XbgIDO7oIU24CEaVheiuPoSYw'

auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(OAUTH_TOKEN, OAUTH_TOKEN_SECRET)

twitter_api = twitter.Twitter(auth=auth)


# search
# https://dev.twitter.com/docs/api/1.1/get/search/tweets
search_results = twitter_api.search.tweets(q=q, count=count)

# Debug line
#print json.dumps(query, sort_keys=True, indent=4)

# Print results
print ("Search complete (%f seconds)" % (query["search_metadata"]["completed_in"]))
print ("Found",len(query["statuses"]),"results.")

# Get results and find retweets and mentions
for result in query["statuses"]:
    print ("")
    print ("Tweet:",result["text"])
    print ("By user:",result["user"]["name"])
    if len(result["entities"]["user_mentions"]) != 0:
        print ("Mentions:")
        for i in result["entities"]["user_mentions"]:
            print (" - by",i["screen_name"])
            graph.add_edge(i["screen_name"],result["user"]["name"])
    if "retweeted_status" in result:
        if len(result["retweeted_status"]["entities"]["user_mentions"]) != 0:
            print ("Retweets:")
            for i in result["retweeted_status"]["entities"]["user_mentions"]:
                print (" - by",i["screen_name"])
                graph.add_edge(i["screen_name"],result["user"]["name"])
    else:
        pass

# Save graph
print ("")
print ("The network of the hashtag was analyzed succesfully!")
print ("")
#print ("Saving the file as "+hashtag+"-rt-network.gexf...")
nx.write_gexf(graph, hashtag+"-rt-network.gexf")