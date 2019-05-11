import tweepy, re #,csv,re,sys
from textblob import TextBlob
import matplotlib.pyplot as plt
import plotly
import plotly.plotly as py
import plotly.graph_objs as go
from plotly.offline import iplot, init_notebook_mode
# Using plotly + cufflinks in offline mode
import cufflinks as cf

# Use the 'quote' function to encode search terms before API calls
# from requests.utils import quote

class SentimentAnalysis:

    def __init__(self):
        self.tweets = []
        self.tweetText = []
        self.searchTerm = "" 

    def get_search_term(self) -> str:
        return self.searchTerm

    def DownloadData(self, a_search_input):
        print(f"Entering DownloadData(self, a_search_input = '{a_search_input}'):")

        # authenticating
        consumerKey = 't6gxzqwZTX6S3BnXYM3YGqriA'
        consumerSecret = '6ByaQVf9ljEQHWwrfQbkyG674dhu0TQeJh8VrGqzrrBLaDZc94'
        accessToken = '1031172880300687361-XsNI26GX8GngiUGw3ord7vQtKdcoPk'
        accessTokenSecret = 'VnThCcjLUmqWE3UIxb62XbgIDO7oIU24CEaVheiuPoSYw'
        auth = tweepy.OAuthHandler(consumerKey, consumerSecret)
        auth.set_access_token(accessToken, accessTokenSecret)
        api = tweepy.API(auth)

        search_input_global = a_search_input

        # input for term to be searched and how many tweets to search
        self.searchTerm = search_input_global #input("Enter Keyword/Hashtag to search about: ")
        #NoOfTerms = int(input("Number of tweets to analyze: "))
        NoOfTerms = 1000

        # searching for tweets
        # NOTE: Can hit Twitter Rate Limits, so be prepared...

        try:
            self.tweets = tweepy.Cursor(api.search, q=self.searchTerm, lang = "en").items(NoOfTerms)
            print(f"API Search for self.searchTerm = '{self.searchTerm}': Successful")

        except:
            # If this failed, probably ran into Rate Limits error (429)
            # so just fail gracefully, allowing the main page to render
            print(f"API Search for self.searchTerm = '{self.searchTerm}': Failed - probably Rate Limits")
            return

        # Open/create a file to append data to
        #csvFile = open('result.csv', 'a')

        # Use csv writer
        #csvWriter = csv.writer(csvFile)


        # Creating some variables to store data
        polarity = 0
        positive = 0
        wpositive = 0
        spositive = 0
        negative = 0
        wnegative = 0
        snegative = 0
        neutral = 0


        # iterating through tweets fetched
        # This is the first use of the Twitter API Cursor,
        # so be ready for a Rate Limit (or other) error
        try:
            for tweet in self.tweets:
                #Append to temp so that we can store in csv later. Encode in UTF-8
                self.tweetText.append(self.cleanTweet(tweet.text).encode('utf-8'))
                analysis = TextBlob(tweet.text)
                #print(analysis.sentiment)  # print tweet's polarity
                polarity += analysis.sentiment.polarity  # adding up polarities to find the average

                if (analysis.sentiment.polarity == 0):  # adding how people are reacting to find average sentiment
                    neutral += 1
                elif (analysis.sentiment.polarity > 0 and analysis.sentiment.polarity <= 0.3):
                    wpositive += 1
                elif (analysis.sentiment.polarity > 0.3 and analysis.sentiment.polarity <= 0.6):
                    positive += 1
                elif (analysis.sentiment.polarity > 0.6 and analysis.sentiment.polarity <= 1):
                    spositive += 1
                elif (analysis.sentiment.polarity > -0.3 and analysis.sentiment.polarity <= 0):
                    wnegative += 1
                elif (analysis.sentiment.polarity > -0.6 and analysis.sentiment.polarity <= -0.3):
                    negative += 1
                elif (analysis.sentiment.polarity > -1 and analysis.sentiment.polarity <= -0.6):
                    snegative += 1

        except:
            # If this failed, probably ran into Rate Limits error (429)
            # so just fail gracefully, allowing the main page to render
            print(f"Looping through Twitter API Cursor for self.seachTerm = '{self.searchTerm}': Failed - probably Rate Limits")
            return

        # finding average of how people are reacting
        positive = self.percentage(positive, NoOfTerms)
        wpositive = self.percentage(wpositive, NoOfTerms)
        spositive = self.percentage(spositive, NoOfTerms)
        negative = self.percentage(negative, NoOfTerms)
        wnegative = self.percentage(wnegative, NoOfTerms)
        snegative = self.percentage(snegative, NoOfTerms)
        neutral = self.percentage(neutral, NoOfTerms)

        # finding average reaction
        polarity = polarity / NoOfTerms

        # # printing out data
        # print("How people are reacting on " + searchTerm + " by analyzing " + str(NoOfTerms) + " tweets.")
        # print()
        # print("General Report: ")

        # if (polarity == 0):
        #     print("Neutral")
        # elif (polarity > 0 and polarity <= 0.3):
        #     print("Weakly Positive")
        # elif (polarity > 0.3 and polarity <= 0.6):
        #     print("Positive")
        # elif (polarity > 0.6 and polarity <= 1):
        #     print("Strongly Positive")
        # elif (polarity > -0.3 and polarity <= 0):
        #     print("Weakly Negative")
        # elif (polarity > -0.6 and polarity <= -0.3):
        #     print("Negative")
        # elif (polarity > -1 and polarity <= -0.6):
        #     print("Strongly Negative")

        # print()
        # print("Detailed Report: ")
        # print(str(spositive) + "% people have a strongly positive reaction")
        # print(str(positive) + "% people have positive reaction")
        # print(str(wpositive) + "% people have a weakly positive reaction")
        # print(str(neutral) + "% people have a neutral reaction")
        # print(str(wnegative) + "% people have a weakly negative reaction")
        # print(str(negative) + "% people have a negative reaction")
        # print(str(snegative) + "% people have a strongly negative reaction")
        

        self.plotPieChart(spositive, positive, wpositive, neutral, wnegative, negative, snegative, self.searchTerm, NoOfTerms)


    def cleanTweet(self, tweet):
        # Remove Links, Special Characters etc from tweet
        return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t]) | (\w +:\ / \ / \S +)", " ", tweet).split())

    # function to calculate percentage
    def percentage(self, part, whole):
        temp = 100 * float(part) / float(whole)
        return format(temp, '.2f')

    def plotPieChart(self, spositive, positive, wpositive, neutral, wnegative, negative, snegative, searchTerm, noOfSearchTerms):
        #PLotly
        plotly.tools.set_credentials_file(username='Euzkaro', api_key='v9i5NlEGEpiWgmjczBUI')
        labels = ['Strongly Positive', 'Positive', 'Weakly Positive', 'Neutral', 'Weakly Negative', 'Negative', 'Strongly Negative']
        values = [spositive, positive, wpositive, neutral, wnegative, negative, snegative]
        color = ['#006400','#2E8B57','#3CB371','#FFFF99','#BC8F8F','#A52A2A','#800000']
        sizes = [spositive, positive, wpositive, neutral, wnegative, negative, snegative]
        colors = ['darkgreen','yellowgreen','lightgreen','gold', 'lightsalmon','red','darkred']
        trace = go.Pie(labels=labels,
                       values=values, 
                       marker=dict(colors=colors,
                                  line=dict(color='#FFFFFF', width=5)))
        py.iplot([trace], filename='sentiment_pie_chart')
        
