# Project 3 - GeoTweet+
# 
# @Author Jeffery Brown (daddyjab)
# @Date 5/1/19
# @File models.py

from .app import db

# Database schema for Twitter 'locations' table
class Location(db.Model):
    __tablename__ = 'locations'
    
    # Defining the columns for the table 'locations',
    # which will hold all of the locations in the U.S. for which
    # top trends data is available, as well as location specific
    # info like latitude/longitude
    id = db.Column(db.Integer, primary_key=True)
    updated_at = db.Column( db.DateTime )
    woeid = db.Column(db.Integer, unique=True, nullable=False)
    twitter_country = db.Column(db.String(100))
    tritter_country_code = db.Column(db.String(10))
    twitter_name = db.Column(db.String(250))
    twitter_parentid = db.Column(db.Integer)
    twitter_type = db.Column(db.String(50))
    country_name = db.Column(db.String(250))
    country_name_only = db.Column(db.String(250))
    country_woeid = db.Column(db.Integer)
    county_name = db.Column(db.String(250))
    county_name_only = db.Column(db.String(250))
    county_woeid = db.Column(db.Integer)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    name_full = db.Column(db.String(250))
    name_only = db.Column(db.String(250))
    name_woe = db.Column(db.String(250))
    place_type = db.Column(db.String(250))
    state_name = db.Column(db.String(250))
    state_name_only = db.Column(db.String(250))
    state_woeid = db.Column(db.Integer)
    timezone = db.Column(db.String(250))

    my_trends = db.relationship('Trend', backref=db.backref('my_location', lazy=True))
    
    def __repr__(self):
        return f"<Location {self.name_full} [updated_at: {self.updated_at}>"

# Database schema for Twitter 'trends' table
class Trend(db.Model):
    __tablename__ = 'trends'
    
    # Defining the columns for the table 'trends',
    # which will hold all of the top trends associated with
    # locations in the 'locations' table
    id = db.Column(db.Integer, primary_key=True)
    updated_at = db.Column( db.DateTime )
    woeid = db.Column(db.Integer, db.ForeignKey('locations.woeid') )
    twitter_as_of = db.Column(db.String(100))
    twitter_created_at = db.Column(db.String(100))
    twitter_name = db.Column(db.String(250))
    twitter_tweet_name = db.Column(db.String(250))
    twitter_tweet_promoted_content = db.Column(db.String(250))
    twitter_tweet_query = db.Column(db.String(250))
    twitter_tweet_url = db.Column(db.String(250))
    twitter_tweet_volume = db.Column(db.Float)

    # With more investigation, determined this is an
    # incorrect usage of relationship method below - removing it
    # locations = db.relationship('Location', backref=db.backref('trends', lazy=True))
     
    def __repr__(self):
        return f"<Trend {self.my_location.name_full}: {self.twitter_tweet_name} [updated_at: {self.updated_at}>"


class Tweet(db.Model):
    __tablename__ = 'tweets'
    
    # Defining the columns for the table 'tweets',
    # which will hold tweets associated the search terms in the 'trends' table,
    # which are referred to in that table as "twitter_tweet_name"
    id = db.Column(db.Integer, primary_key=True)
    updated_at = db.Column( db.DateTime )
    
    tweet_id = db.Column( db.Integer )
    tweet_id_str = db.Column( db.String(50), unique=True, nullable=False )
    # tweet_search_term = db.Column(db.Integer, db.ForeignKey('trends.twitter_tweet_name') )
    tweet_search_term = db.Column(db.String(250))
    tweet_created_at = db.Column(db.String(100))
   
    tweet_is_a_quote_flag = db.Column( db.Boolean )
    tweet_is_a_retweet_flag = db.Column( db.Boolean )

    tweet_entities_hashtags_count = db.Column( db.Integer )
    tweet_entities_user_mentions_count = db.Column( db.Integer )
    tweet_favorite_counts = db.Column( db.Integer )
    tweet_retweet_counts = db.Column( db.Integer )
    
    tweet_lang = db.Column( db.String(10) )
    tweet_source = db.Column(db.String(250))
    tweet_text = db.Column(db.String(250))    
    
    tweet_user_id = db.Column( db.Integer )
    tweet_user_id_str = db.Column( db.String(50) )
    tweet_user_created_at = db.Column(db.String(100))
    tweet_user_lang = db.Column( db.String(10) )
    tweet_user_name = db.Column( db.String(100) )
    tweet_user_screen_name = db.Column( db.String(100) )
    tweet_user_description = db.Column( db.String(250) )
    tweet_user_statuses_count = db.Column( db.Integer )
    tweet_user_favourites_count = db.Column( db.Integer )
    tweet_user_followers_count = db.Column( db.Integer )
    tweet_user_friends_count = db.Column( db.Integer )
    tweet_user_listed_count = db.Column( db.Integer )
    
    def __repr__(self):
        return f"<Tweet {self.tweet_search_term}: {self.tweet_id} [updated_at: {self.updated_at}>"
