# Project 3 - GeoTweet+
# 
# @Author Jeffery Brown (daddyjab)
# @Date 5/1/19
# @File db_management.py

# This file contains function which update the
# 'tritter_trends.sqlite' database tables
# 'locations' and 'trends' via API calls to Twitter and Flickr

# The following dependencies are only required for update/mgmt of
# 'locations' and 'trends' data
# datetime (datetime, date) and dateutil(parser)
# may be required by some Flask routes
# indirectly via the parse_date_range() function
import json
import time
import os
import pandas as pd
import numpy as np
from datetime import datetime, date
from dateutil import tz, parser

import requests
from requests.utils import quote

from pprint import pprint

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql.expression import func, and_, or_
from sqlalchemy.sql.functions import coalesce

# Import a pointer to the Flask-SQLAlchemy database session
# created in the main app.py file
from .app import db, app

# Import the Database models defined in the models.py file
from .models import Location, Trend, Tweet

# Only perform import of local API config file if this Flask app is being run locally.
# If being run from Heroku the keys will be provided
# via the app environment variables configured there

try:
    # This will run if the keys are all set via Heroku environment

    # Twitter API
    key_twitter_tweetquestor_consumer_api_key = os.environ['key_twitter_tweetquestor_consumer_api_key']
    key_twitter_tweetquestor_consumer_api_secret_key = os.environ['key_twitter_tweetquestor_consumer_api_secret_key']
    key_twitter_tweetquestor_access_token = os.environ['key_twitter_tweetquestor_access_token']
    key_twitter_tweetquestor_access_secret_token = os.environ['key_twitter_tweetquestor_access_secret_token']

    # Flickr API
    key_flicker_infoquestor_key = os.environ['key_flicker_infoquestor_key']
    key_flicker_infoquestor_secret = os.environ['key_flicker_infoquestor_secret']

except KeyError:
    # Keys have not been set in the environment
    # So need to import them locally
    try:
        # Twitter API keys
        # Flickr API keys
        from .api_config import *

    # If the api_config file is not available, then all we can do is flag an error
    except ImportError:
        print("Import Keys: At least one of the API Keys has not been populated on Heroku, and api_config not available!")

# Setup Tweepy API Authentication to access Twitter
import tweepy

try:
    auth = tweepy.OAuthHandler(key_twitter_tweetquestor_consumer_api_key, key_twitter_tweetquestor_consumer_api_secret_key)
    auth.set_access_token(key_twitter_tweetquestor_access_token, key_twitter_tweetquestor_access_secret_token)
    api = tweepy.API(auth, parser=tweepy.parsers.JSONParser())

except TweepError:
    print("Authentication error: Problem authenticating Twitter API using Tweepy (TweepError)")

# # Function Definitions: Twitter API Rate Limit Management

def api_rate_limits():
# Return the number of Twitter API calls remaining
# for the specified API type:
# "trends/place": Top 10 trending topics for a WOEID
# "trends/closest": Locations near a specificed lat/long for which Twitter has trending topic info
# "trends/available": Locations for which Twitter has topic info
# "search/tweets": 
# "users/search"
# "users/shows"
# "users/lookup"
# 
# Global Variable: 'api': Tweepy API
# 

    # Get Twitter rate limit information using the Tweepy API
    try:
        rate_limits = api.rate_limit_status()
    
    except RateLimitError as e:
        print("Tweepy API: Problem getting Twitter rate limits information using tweepy - RateLimitError")
        pprint(e)
        
    except:
        print("Tweepy API: Problem getting Twitter rate limits information using tweepy")
        return ""

    # Return the remaining requests available for the
    # requested type of trends query (or "" if not a valid type)
    try:
        return rate_limits['resources']

    except:
        return ""



def api_calls_remaining( a_type = "place"):
# Return the number of Twitter API calls remaining
# for the specified API type:
# 'place': Top 10 trending topics for a WOEID
# 'closest': Locations near a specificed lat/long for which Twitter has trending topic info
# 'available': Locations for which Twitter has topic info
# 
# Global Variable: 'api': Tweepy API
# 

    # Get Twitter rate limit information using the Tweepy API
    rate_limits = api.rate_limit_status()
    
    # Focus on the rate limits for trends calls
    trends_limits = rate_limits['resources']['trends']
    
    # Return the remaining requests available for the
    # requested type of trends query (or "" if not a valid type)
    try:
        remaining = trends_limits[ f"/trends/{a_type}" ]['remaining']
        print(f"Twitter API 'trends/{a_type}' - API Calls Remaining: {remaining}")

    except:
        return ""

    return remaining


def api_time_before_reset( a_type = "place"):
# Return the number of minutes until the Twitter API is reset
# for the specified API type:
# 'place': Top 10 trending topics for a WOEID
# 'closest': Locations near a specificed lat/long for which Twitter has trending topic info
# 'available': Locations for which Twitter has topic info
# 
# Global Variable: 'api': Tweepy API
# 

    # Get Twitter rate limit information using the Tweepy API
    rate_limits = api.rate_limit_status()
    
    # Focus on the rate limits for trends calls
    trends_limits = rate_limits['resources']['trends']
    
    
    # Return the reset time for the
    # requested type of trends query (or "" if not a valid type)
    try:
        reset_ts = trends_limits[ f"/trends/{a_type}" ]['reset']
    except:
        return -1
        
    # Calculate the remaining time using datetime methods to
    # get the UTC time from the POSIX timestamp
    reset_utc = datetime.utcfromtimestamp(reset_ts)
    
    # Current the current time
    current_utc = datetime.utcnow()
    
    # Calculate the number of seconds remaining,
    # Assumption: reset time will be >= current time
    time_before_reset = (reset_utc - current_utc).total_seconds() / 60.0
    
    # Tell the datetime object that it's in UTC time zone since 
    # datetime objects are 'naive' by default
    reset_utc = reset_utc.replace(tzinfo = tz.tzutc() )
    
    # Convert time zone
    reset_local = reset_utc.astimezone( tz.tzlocal() )

    # Tell the datetime object that it's in UTC time zone since 
    # datetime objects are 'naive' by default
    current_utc = current_utc.replace(tzinfo = tz.tzutc() )
    
    # Convert time zone
    current_local = current_utc.astimezone( tz.tzlocal() )
    print(f"Twitter API 'trends/{a_type}' - Time Before Rate Limit Reset: {time_before_reset:.1f}: Reset Time: {reset_local.strftime('%Y-%m-%d %H:%M:%S')}, Local Time: {current_local.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Return the time before reset (in minutes)
    return time_before_reset


# # Function Definitions: Twitter Locations with Available Trends Info

def get_loc_with_trends_available_to_df( ):
# Get locations that have trends data from a api.trends_available() call,
# flatten the data, and create a dataframe

    # Obtain the WOEID locations for which Twitter Trends info is available
    try:
        trends_avail = api.trends_available()
        
    except:
        # No locations info available, return False
        print(f"Tweepy API: Problem getting locations that have trends available information")
        return False
    
    # Import trend availability info into a dataframe
    trends_avail_df = pd.DataFrame.from_dict(trends_avail, orient='columns')
    
    # Set the 'updated_at' column to the current time in UTC timezone for all locations
    trends_avail_df['updated_at'] = datetime.utcnow()

    # Retain only locations in the U.S.
    trends_avail_df = trends_avail_df[ (trends_avail_df['countryCode'] == "US") ]
        
    # Reset the index
    trends_avail_df.reset_index(drop=True, inplace=True)

    # Flatten the dataframe by unpacking the placeType column information into separate columns
    trends_avail_df['twitter_type'] = trends_avail_df['placeType'].map( lambda x: x['name'])

    # Remove unneeded fields
    trends_avail_df.drop(['placeType', 'url' ], axis='columns' , inplace = True)

    # Rename the fields
    trends_avail_df.rename(columns={
        'woeid': 'woeid',
        'country': 'twitter_country',
        'countryCode': 'tritter_country_code',
        'name': 'twitter_name',
        'parentid': 'twitter_parentid' }, inplace=True)
    
    return trends_avail_df



def get_location_info( a_woeid ):
# Use Flickr API call to get location information associated with a Yahoo! WOEID
# Note: Yahoo! no longer supports this type of lookup! :(

    # Setup the Flickr API base URL
    flickr_api_base_url = f"https://api.flickr.com/services/rest/?method=flickr.places.getInfo&api_key={key_flicker_infoquestor_key}&format=json&nojsoncallback=1&woe_id="

    # Populate the WOEID and convert to string format
    woeid_to_search = str(a_woeid)
    
    # Build the full URL for API REST request
    flickr_api_url = flickr_api_base_url + woeid_to_search

    try:
        # Get the REST response, which will be in JSON format
        response = requests.get(url=flickr_api_url)
        
    except requests.exceptions.RequestException as e:
        print(f"Flickr API: Problem getting location information for WOEID {a_woeid}: ")
        return False
    
    # Parse the json
    location_data = response.json()
    
    # Check for failure to locate the information
    if (location_data['stat'] == 'fail'):
        print(f"Flickr API: Problem finding location WOEID {a_woeid}: {location_data['message']}")
        
        
    #pprint(location_data)
    
    # Return just a useful subset of the location info as flattened dictionary
    key_location_info = {}
    
    # Basic information that should be present for any location
    try:
        key_location_info.update( {
            'woeid': int(location_data['place']['woeid']),
            'name_woe': location_data['place']['woe_name'],
            'name_full': location_data['place']['name'],
            'name_only': location_data['place']['name'].split(",")[0].strip(),
            'place_type': location_data['place']['place_type'],
            'latitude': float(location_data['place']['latitude']),
            'longitude': float(location_data['place']['longitude']),
        })
                
    except:
        print("Error - basic location information not returned for WOEID{a_woeid}: ", sys.exc_info()[0])
    
    # Timezone associated with the location - if available
    try:
        key_location_info.update( {
            'timezone': location_data['place']['timezone']  
        })
        
    except:
        key_location_info.update( {
            'timezone': None
        })
        
    # County associated with the location - if available
    try:
        key_location_info.update( {
            'county_name': location_data['place']['county']['_content'],
            'county_name_only': location_data['place']['county']['_content'].split(",")[0].strip(),
            'county_woeid': int(location_data['place']['county']['woeid']),
        })
    except:
        key_location_info.update( {
            'county_name': None,
            'county_name_only': None,
            'county_woeid': None,
        })
        
    # State associated with the location - if available
    try:
        key_location_info.update( {
            'state_name': location_data['place']['region']['_content'],
            'state_name_only': location_data['place']['region']['_content'].split(",")[0].strip(),
            'state_woeid': int(location_data['place']['region']['woeid']),
        })
    except:
        key_location_info.update( {
            'state_name': None,
            'state_name_only': None,
            'state_woeid': None,
        })
        
    # Country associated with the location - if available
    try:
        key_location_info.update( {
            'country_name': location_data['place']['country']['_content'],
            'country_name_only': location_data['place']['country']['_content'].split(",")[0].strip(),
            'country_woeid': int(location_data['place']['country']['woeid']),
        })
    except:
        key_location_info.update( {
            'country_name': None,
            'country_name_only': None,
            'country_woeid': None, 
        })
    
    return key_location_info


def update_db_locations_table():
# Function to update the list of Twitter locations in the'locations' DB table.
# This function uses a Twitter API to get the list of locations for which top trends
# information is available.  It then uses a Flickr API to obtain location details for
# each of these Twitter specified locations.  A merge is then performed of the two
# DataFrames, resulting in a single dataframe that is used to update the 'locations' table.
# NOTE: The Twitter 'trends/available' API call is not rate limited.
#
# This function assumes that the 'locations' table in the database has already been configured
# and is ready for data.

    # Flatten the Twitter Trends results and populate in a Dataframe
    loc_with_trends_available_df = get_loc_with_trends_available_to_df( )

    # Use the get_location_info() function to add location info (from Flickr)
    # for each location (Twitter WOEID) that has trend info
    loc_info_list =  list( loc_with_trends_available_df['woeid'].apply( get_location_info ) )

    # Create a DataFrame from the location info list
    loc_info_df = pd.DataFrame.from_dict(loc_info_list)

    # Merge the Twitter trend location available dataframe with the
    # location info dataframe to create a master list of all
    # Twitter Trend locations and associated location information
    twitter_trend_locations_df = loc_with_trends_available_df.merge(loc_info_df, how='inner', on='woeid')

    # Delete all location information currently in the database 'locations' table

    # CHANGED FOR GeoTweet+: Keep all entries - don't delete them!
    # db.session.query(Location).delete()
    # db.session.commit()

    # Write this table of location data to the database 'locations' table
    # twitter_trend_locations_df.to_sql( 'locations', con=db.engine, if_exists='append', index=False)
    # db.session.commit()

    # CHANGED FOR GeoTweet+: Update locations already in the table and add locations that are not
    # There is no cross-database SQLAlchemy support for the 'upsert' operation,
    # So query for each WOEID in the dataframe and decide if an 'add' or an 'update' is needed...
    
    # Convert all 'NaN' values to 'None' to avoid issues when updating the database
    # Note: Some cities had county_woeid set to "NaN", which caused much havoc with db operations
    twitter_trend_locations_df = twitter_trend_locations_df.where((pd.notnull(twitter_trend_locations_df)), None)
    
    # Loop through all rows in the update dataframe
    n_adds = 0
    n_updates = 0
    for index, row in twitter_trend_locations_df.iterrows():
        # Get this row into a dictionary, but exclude primary key 'woeid'
        row_dict = row.to_dict()

        # pprint(f"DataFrame: {row['woeid']}")
        result = db.session.query(Location).filter( Location.woeid == row['woeid'] ).first()

        if result is None:
            # This location is not in the table, so add this entrry to the 'locations' table.
            # NOTE: 
            # Location is the Class mapped to the 'locations' table
            # row_dict is a dictionary containing all of the column values for this row as key/value pairs
            # The term "**row_dict" creates a "key=value" parameter for each key/value pair
#             print(f"ADD: DataFrame twitter_trend_locations_df: {row['woeid']} => Database 'locations': New Entry")
            try:
                db.session.add( Location(**row_dict) )
                db.session.commit()
                n_adds += 1
                
            except:
                print(f">>> Error while attempting to add record to 'locations'")
                db.session.rollback()
            
        else:
            # This location is in the table, so update this entry in the 'locations' table.
#             print(f"UPDATE: DataFrame twitter_trend_locations_df: {row['woeid']} => Database 'locations': {result.woeid}: {result.name_full}")
            
            try:
                db.session.query(Location).filter( Location.woeid == row['woeid'] ).update( row_dict )
                db.session.commit()
                n_updates += 1
                
            except:
                print(f">>> Error while attempting to update record in 'locations'")
                db.session.rollback()
                
    # Return the total number of entries in the Locations table
    num_loc = db.session.query(Location).count()
    
#   print(f"Adds/Updates complete: Adds: {n_adds}, Updates {n_updates} => Rows in 'locations' table: {num_loc}")
    
    return num_loc



# # Function Definitions: Twitter Top Trends for Twitter Locations

def get_trends_for_loc( a_woeid ):
# Get top Twitter trending tweets for a location specified by a WOEID,
# flatten the data, and return it as a list of dictionaries

    # Import trend availability info into a dataframe
    try:
        top_trends = api.trends_place( a_woeid )[0]
        
    except:
        # No top trends info available for this WOEID, return False
        print(f"Tweepy API: Problem getting trends information for WOEID {a_woeid}")
        return False
    
    #pprint(top_trends)
    
    # Repeat some information that is common for all elements in the trends list
    common_info = {}
        
    # Basic information that should be present for any location
    # 'updated_at': Current time in UTC timezone
    # 'as_of': '2019-03-26T21:22:42Z',
    # 'created_at': '2019-03-26T21:17:18Z',
    # 'locations': [{'name': 'Atlanta', 'woeid': 2357024}]
    try:
        common_info.update( {
            'woeid': int(top_trends['locations'][0]['woeid']),
            'updated_at': datetime.utcnow(),
            'twitter_name': top_trends['locations'][0]['name'],
            'twitter_created_at': top_trends['created_at'],
            'twitter_as_of': top_trends['as_of']
        })
                
    except:
        print("Error - basic location information not returned for WOEID{a_woeid}: ", sys.exc_info()[0])
   
    # Loop through all of the trends and store in an array of dictionary elements
    # 'name': 'Jussie Smollett'
    # 'promoted_content': None
    # 'query': '%22Jussie+Smollett%22'
    # 'tweet_volume': 581331
    # 'url': 'http://twitter.com/search?q=%22Jussie+Smollett%22'

    # Return the trends as an array of flattened dictionaries
    trend_info = []

    for ti in top_trends['trends']:
        
        # Put the trend info into a dictionary, starting with the common info
        this_trend = common_info.copy()
        
        # Timezone associated with the location - if available
        try:
            this_trend.update( {
                'twitter_tweet_name': ti['name'],
                'twitter_tweet_promoted_content': ti['promoted_content'],
                'twitter_tweet_query': ti['query'],
                'twitter_tweet_volume': ti['tweet_volume'],
                'twitter_tweet_url': ti['url']
            })

        except:
            this_trend.update( {
                'twitter_tweet_name': None,
                'twitter_tweet_promoted_content': None,
                'twitter_tweet_query': None,
                'twitter_tweet_volume': None,
                'twitter_tweet_url': None
            })
            
        # Append this trend to the list
        trend_info.append( this_trend )
    
    return trend_info



def update_db_trends_table():
# Function to obtain the list of Twitter locations from the 'locations' DB table.
# The function then loops through each location,
# obtains the Twitter top trends info, and then appends that data to the 'trends' table.
# The function uses rate limit check functions to see if the Twitter API call rate limit
# is about to be reached, and if so, delays the next relevant API call until the rate limit
# is scheduled to be reset (a period of up to 15minutes) before continuing.
#
# This function assumes that the 'trends' table in the database has already been configured
# and is ready for data.

    # Obtain the list of Twitter locations from the 'locations' DB table
    loc_list = [ x[0] for x in db.session.query(Location.woeid).all()]
    print(f"Retrieved {len(loc_list)} locations for processing")
    
    # Keep track of the actual number of locations
    # where trend info was written to the 'trends' table
    num_location_trends_written_to_db = 0
    
    for tw_woeid in loc_list:
        print(f">> Updating trends for location {tw_woeid}")

        # Make sure we haven't hit the rate limit yet
        calls_remaining = api_calls_remaining( "place" )
        time_before_reset = api_time_before_reset( "place" )

        # If we're close to hitting the rate limit for the trends/place API,
        # then wait until the next reset =
        # 'time_before_reset' minutes + 1 minute buffer
        if (calls_remaining < 2):
            print (f">> Waiting {time_before_reset} minutes due to rate limit")
            time.sleep( (time_before_reset+1) * 60)

        # Get trend info for a WOEID location
        t_info = get_trends_for_loc(tw_woeid)

        try:
            # Create a DataFrame
            t_info_df = pd.DataFrame.from_dict(t_info)
            
            # Delete any trends associated with this WOEID
            # before appending new trends to the 'trends' table for this WOEID
            
            # CHANGED FOR GeoTweet+: Keep all entries - don't delete them!
            # db.session.query(Trend).filter(Trend.woeid == tw_woeid).delete()
            # db.session.commit()

            # Append trends for this WOEID to the 'trends' database table
            t_info_df.to_sql( 'trends', con=db.engine, if_exists='append', index=False)
            db.session.commit()

            # Increment the count
            num_location_trends_written_to_db += 1

        except:
            print(f">> Error occurred with location {tw_woeid} while attempting to prepare and write trends data")
            
    return num_location_trends_written_to_db

def parse_date_range(a_date_range = None):
# Function to parse date ranges specified with the Flask API '/period' routes
# Note, 
# Arguments: Single string a_date_range with possible formats:
#     a_date_range = "2019-03-01"    ->   ">= 3/1/19"
#     a_date_range = ":2019-06-01"    ->   "<= 6/30/19"
#     a_date_range = "2019-03-01:2019-06-30"  ->   ">= 3/1/19 and  <= 6/30/19"
#     a_date_range = "all"  -> all dates
#     a_date_range = ":"  -> same as "all"
#     a_date_range = ""   -> same as "all"
#
# Returns:
#     start_date: Earliest date (inclusive), for use in date comparison
#     end_date: Latest date (inclusive), for use in date comparison
#     If either date cannot be parsed, an error message is returned

    # Max and Min dates
    DATE_EARLIEST_POSSIBLE = parser.parse("2000-01-01").date()
    DATE_LATEST_POSSIBLE = parser.parse("2100-12-31").date()

    # Initialize default return valus - no date restriction
    start_date = DATE_EARLIEST_POSSIBLE
    end_date = DATE_LATEST_POSSIBLE
    
    # Parse the argument to obtain the start and end dates - if provided
    
    # If no argument provided, provide full date range (i.e., no date restriction)
    if a_date_range is None:
        # Return default values
        return (start_date, end_date)

    # Prep the date range for additional processing
    date_range = a_date_range.strip().lower()
    
    # Check for "all" and similar indications of no date restriction
    if date_range == "all" or date_range == "" or date_range == ":" :
        # Return default values
        return (start_date, end_date)
    
    # Attempt to split the date range (seperator = ":")
    arg_list = a_date_range.split(":")
    
    # If only one argument provided (i.e., no ":")
    # then restrict date range to just that one date
    if len(arg_list) == 1:
        try:
            start_date = parser.parse(arg_list[0]).date()
            end_date = start_date
            
        except ValueError:
            start_date = f"ERROR"
            end_date = start_date

        return (start_date, end_date)
    
    # At least 2 args provided, so assume they are start and end dates
    
    # Populate start date if the argument is populated, otherwise leave the default
    if len(arg_list[0])>0:
        try:
            start_date = parser.parse(arg_list[0]).date()
        except ValueError:
            start_date = f"ERROR"

    # Populate end date if the argument is populated, otherwise leave the default
    if len(arg_list[1])>0:
        try:
            end_date = parser.parse(arg_list[1]).date()
        except ValueError:
            end_date =  f"ERROR"

    # Get the date range from the arguments
    return (start_date, end_date)


# ## DB Management: Twitter Tweet info

# # Function Definitions: Twitter Tweet Info
def search_for_tweets( a_search_term ):
# Get a list of specific tweets associated with search term a_search_term,
# flatten the relevant data, and return it as a list of dictionaries

    # Number of tweets per page (up to 100) to be returned from the API query
    tweets_count_limit = 100       # PRODUCTION
    # tweets_count_limit = 5         # DEBUG
    
    try:
        # Perform API search query and obtain only the 1st page of results
        tweets = api.search(quote(a_search_term), lang='en', count=tweets_count_limit)
        
    except:
        # No tweet info available for this search term, return False
        print(f"Tweepy API Error: Problem getting tweet information for search term {a_search_term}")
        return False
    
    
    # Create a list of dictionaries of Tweets info associated with a_search_term
    tweet_list = []

    # Repeat some information that is common for all elements in the tweet list
    common_info = {
        'updated_at': datetime.utcnow(),
        'tweet_search_term': a_search_term
    }

    # Loop through each tweet in the tweet search results
    for t in tweets['statuses']:
        
        # Start the dictionary with some common information
        tweet_info = dict(common_info)

        # Info about this Tweet (i.e., "Status")
        # UPDATE: Force both 'tweet_id' and 'tweet_user_id' to be 0
        # to avoid possible integer range error in database
        # NOTE: The string representations are used, not the integer
        try:            
            tweet_info.update( {                
                'tweet_id': 0,
                'tweet_id_str': t['id_str'],
                'tweet_created_at': t['created_at'],
                'tweet_text': t['text'],
                'tweet_lang': t['lang'],
                'tweet_source': t['source'],
                'tweet_is_a_quote_flag': t['is_quote_status'],    # If True, then this is a Quoted Tweet (i.e., Tweet w/ comments/mods)
            })

        except:
            print(f"Tweepy API Error: Problem getting tweet-related info")

        # If the 'retweeted_status' key exists in the results,
        # then this Tweet is a Retweet (i.e., Tweet forwarded "as is")
        if 'retweeted_status' in t:
            tweet_info.update( { 'tweet_is_a_retweet_flag': True })
        else:
            tweet_info.update( { 'tweet_is_a_retweet_flag': False })

        # Counts associated with the tweet
        try:            
            tweet_info.update( {                
                'tweet_entities_hashtags_count': len(t['entities']['hashtags']),
                'tweet_entities_user_mentions_count': len(t['entities']['user_mentions']),
                'tweet_favorite_counts': t['favorite_count'],
                'tweet_retweet_counts': t['retweet_count'],
            })

        except:
            print(f"Tweepy API Error: Problem getting tweet-related info")
        
        # User who created this Tweet
        # UPDATE: Force both 'tweet_id' and 'tweet_user_id' to be 0
        # to avoid possible integer range error in database
        # NOTE: The string representations are used, not the integer
        try:
            tweet_info.update( {                
                'tweet_user_id': 0,
                'tweet_user_id_str': t['user']['id_str'],
                'tweet_user_created_at': t['user']['created_at'],
                'tweet_user_name': t['user']['name'],
                'tweet_user_screen_name': t['user']['screen_name'],
                'tweet_user_description': t['user']['description'],
                'tweet_user_lang': t['user']['lang'],
                'tweet_user_statuses_count': t['user']['statuses_count'],     # No. of Tweets/Retweets issued by this user
                'tweet_user_favourites_count': t['user']['favourites_count'],    # No. of Tweets this user has liked (in account's lifetime)
                'tweet_user_followers_count': t['user']['followers_count'],     # No. of Followers this account currently has
                'tweet_user_friends_count': t['user']['friends_count'],       # No. of Users this account is following
                'tweet_user_listed_count': t['user']['listed_count']        # No. of Public lists this user is a member of
            })
            
        except:
            print(f"Tweepy API Error: Problem getting user-related info")            

        # Append this tweet to the list
        tweet_list.append( tweet_info )
        
        # DEBUG *******************************************************************
        # print(f">>> In search_for_tweets( '{a_search_term}' ) - Just appended tweet_info:")
        # pprint(tweet_info)
        
        # print(f">>> In search_for_tweets( '{a_search_term}' ) - tweet_list is now:")
        # pprint(tweet_list)

    return(tweet_list)

def get_search_terms_from_trends(a_date_range=None):
# Get a list of the unique tweet search terms specified in
# the 'trends' table.
# Ensure that all tweets in the list are unique by using a Python "set"
    
    # Parse the date range
    q_start_date, q_end_date = parse_date_range(a_date_range)

    # Return with an error if there was a problem parsing the date range
    if q_start_date == "ERROR" or q_end_date == "ERROR":
        search_term_list = [{'ERROR': 'ERROR'}]
        # return jsonify(search_term_list)
        return(search_term_list)
    
    # Query to get the search_terms (i.e., 'twitter_tweet_name')
    # from the 'trends' table for the specified date range
    results = db.session.query(Trend.twitter_tweet_name) \
                            .filter( and_( \
                                func.date(Trend.updated_at) >= q_start_date, \
                                func.date(Trend.updated_at) <= q_end_date)) \
                            .order_by( Trend.twitter_tweet_name ).all()

    # Get the list of unique search terms using set()
    # Note: The results list is a list of tuples, with first tuple being the desired value
    search_term_set = set([ t[0] for t in results])

    # To support the hashtag/no hashtag Tweet Analysis,
    # add the complementary tweet to the table for each unique tweet
    search_term_alt_set = set([ f"{y[1:]}" if y[:1] == "#" else f"#{y}" for y in search_term_set ])

    # Combined the sets
    search_term_set.update(search_term_alt_set)
    
    # Return a list
    search_term_list = sorted(list(search_term_set))

    return(search_term_list)


def get_search_terms_from_tweets(a_date_range=None):
# Get a list of the unique tweet search terms specified in
# the 'tweets' table.
# Ensure that all tweets in the list are unique by using a Python "set"
    
    # Parse the date range
    q_start_date, q_end_date = parse_date_range(a_date_range)

    # Return with an error if there was a problem parsing the date range
    if q_start_date == "ERROR" or q_end_date == "ERROR":
        search_term_list = [{'ERROR': 'ERROR'}]
        # return jsonify(search_term_list)
        return(search_term_list)
    
    # Query to get the search_terms (i.e., 'twitter_tweet_name')
    # from the 'tweets' table for the specified date range
    results = db.session.query(Tweet.tweet_search_term) \
                            .filter( and_( \
                                func.date(Tweet.updated_at) >= q_start_date, \
                                func.date(Tweet.updated_at) <= q_end_date)) \
                            .order_by( Tweet.tweet_search_term ).all()

    # Get the list of unique search terms using set()
    # Note: The results list is a list of tuples, with first tuple being the desired value
    search_term_set = set([ t[0] for t in results])

    # To support the hashtag/no hashtag Tweet Analysis,
    # add the complementary tweet to the table for each unique tweet
    search_term_alt_set = set([ f"{y[1:]}" if y[:1] == "#" else f"#{y}" for y in search_term_set ])

    # Combined the sets
    search_term_set.update(search_term_alt_set)
    
    # Return a list
    search_term_list = sorted(list(search_term_set))

    return(search_term_list)


def get_tweet_list():
# Based upon the search terms in 'trends' and 'tweets' tables,
# use the Twitter Search API to get tweets for search terms
# that are in the 'trends' table but not already in the 'tweet' table
    
    # Get all of the Twitter search terms in the 'trends' table
    trends_search_term_list = get_search_terms_from_trends()
    
    # Get the Twitter search terms from the 'tweets' table
    # and remove existing search terms from the list of search terms
    # for which api calls will be performed --> Minimizes API calls
    tweets_search_term_list = get_search_terms_from_tweets()
    
    # Create a list of search terms that include all terms from the 'trends'
    # table and removes all those already in the 'tweets' table
    add_search_term_list = list( set(trends_search_term_list) - set(tweets_search_term_list) )
    print( f"Search Terms - Trends: {len(trends_search_term_list)}, Tweets {len(tweets_search_term_list)}, Add: {len(add_search_term_list)}" )        
    
    #DEBUG *******************************************************************************************
    # return add_search_term_list
    #DEBUG *******************************************************************************************

    # Loop through each search term and perform
    # a search for tweets associated with that term
    tweet_list = []
    search_term_count = 0
    
    for s in add_search_term_list:
        
        # Check the rate limits to see if there's enough left to make a search
        try:
            retval = api_rate_limits()
            searches_remaining = retval['search']['/search/tweets']['remaining']
    
        except:
            # Most likely hit rate limits -- break out of the loop and process what we have so far
            print("POSSIBLE RATE LIMITS: search tweets 'remaining' not populated in API results")
            break
            
        # If searches remaining are too low -- break out of the loop and process what we have so far
        if searches_remaining < 10:
            print("RATE LIMITS: Too close to rate limits to perform additional searches")
            break
                
        # Get Tweets for this Twitter search term
        tweets_for_this_search_term = search_for_tweets(s)
        print(f"Search Term '{s}' => Tweet Count: {len(tweets_for_this_search_term)}")
        
        # Build a list of Tweets
        tweet_list.extend( tweets_for_this_search_term )
        
        search_term_count += 1
        
        # DEBUG *******************************************************************************
        # if search_term_count > 10:
        #    break
        # DEBUG *******************************************************************************
    
    print(f"OVERALL => Tweet Count: {len(tweet_list)}, API Search Calls: {search_term_count}")
    
    # Return the tweet_list
    return tweet_list


def update_db_tweets_table(a_tweet_list):
# Update the tweets table by adding tweets for each
# twitter search term in the 'trends' table
#
# Arguments:
#    a_tweet_list: A list of tweets generated by get_tweet_list()
#                  to be added to the 'tweets' table
       
    print(f"Tweets to add to the 'tweets' table: {len(a_tweet_list)}")
       
    # Return the total number of entries in the Locations table
    num_tweets_start = db.session.query(Tweet).count()

    # Loop through all tweet entries
    n_adds = 0
    n_error_adds = 0
    n_updates = 0
    n_error_updates = 0
    for t in a_tweet_list:

        # Force integer representations of these ids to be 0
        # to avoid integer range errors in database
        # NOTE: String representations of both IDs are in different fields
        t['tweet_id'] = 0
        t['tweet_user_id'] = 0

        # Search for this tweet in the 'tweets' table -- just in case it's there
        result = db.session.query(Tweet).filter( Tweet.tweet_id_str == t['tweet_id_str'] ).first()

        if result is None:
            # This tweet is not in the table, so add this entrry to the 'tweets' table.
            # NOTE: 
            # Tweet is the Class mapped to the 'tweet' table
            # t is a dictionary containing all of the column values for this row as key/value pairs
            # The term "**t" creates a "key=value" parameter for each key/value pair
            try:
                db.session.add( Tweet(**t) )
                db.session.commit()
                n_adds += 1
                print(f">>> ADDED: Record to 'tweets': Search Term '{t['tweet_search_term']}' => Tweet ID: '{t['tweet_id_str']}'")
                
            except:
                n_error_adds += 1
                print(f">>> ADD: Error while attempting to add record to 'tweets': Search Term '{t['tweet_search_term']}' => Tweet ID: '{t['tweet_id_str']}'")
                db.session.rollback()
            
        else:
            # DEBUG *************************************************************************************
            # print(result)
            # DEBUG *************************************************************************************
            
            # This tweet is in the table, so update this entry in the 'tweets' table.            
            try:
                db.session.query(Tweet).filter( Tweet.tweet_id_str == t['tweet_id_str'] ).update( t )
                db.session.commit()
                n_updates += 1
                print(f">>> UPDATED: Record in 'tweets': Search Term '{t['tweet_search_term']}' => Tweet ID: '{t['tweet_id_str']}'")
                
            except:
                n_error_updates += 1
                print(f">>> UPDATE: Error while attempting to add record to 'tweets': Search Term '{t['tweet_search_term']}' => Tweet ID: '{t['tweet_id_str']}'")
                db.session.rollback()
                
    # Return the total number of entries in the Locations table
    num_tweets_finish = db.session.query(Tweet).count()
    
    print(f"COMPLETE: ADDS: [{n_adds} success, {n_error_adds} error], UPDATES: [{n_updates} success, {n_error_updates}] error => 'tweets' table rows: {num_tweets_start}->{num_tweets_finish}")
    
    retval = {
        'n_tweet_list_input': len(a_tweet_list),
        'n_tweet_table_entries_start': num_tweets_start,
        'n_tweet_table_entries_finish': num_tweets_finish,
        
        'n_adds': n_adds,
        'n_error_adds': n_error_adds,
        'n_updates': n_updates,
        'n_error_updates': n_error_updates
    }
    
    # Return the counts of add/update actions
    return retval


