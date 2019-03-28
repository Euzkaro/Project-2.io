#!/usr/bin/env python
# coding: utf-8

# # Project 2 - GeoTweet
# 
# @Author Jeffery Brown (daddyjab)<br>
# @Date 3/25/19<br>
# @File ETL_for_GeoTweet
# 

# # Dependencies

# In[1]:


# Dependencies
import tweepy
import json
import time
import os
import pandas as pd
from datetime import datetime 
from dateutil import tz
import requests
from pprint import pprint

# Database dependencies
# Imports the method used for connecting to DBs
from sqlalchemy import create_engine, asc, desc, between, distinct, func, null, nullsfirst, nullslast, or_, and_, not_
from sqlalchemy.orm import sessionmaker, relationship

# Imports the methods needed to abstract classes into tables
from sqlalchemy.ext.declarative import declarative_base

# Allow us to declare column types
from sqlalchemy import Column, Integer, String, Float, ForeignKey

# API Keys
from api_config import *

# Twitter API
# key_twitter_tweetquestor_consumer_api_key
# key_twitter_tweetquestor_consumer_api_secret_key
# key_twitter_tweetquestor_access_token
# key_twitter_tweetquestor_access_secret_token

# Flickr API
# key_flicker_infoquestor_key
# key_flicker_infoquestor_secret


# # Database Configuration for `locations` and `trends` Tables

# In[2]:


# Setup the database using SQLAlchemy
Base = declarative_base()


# In[3]:


# Database schema for Twitter 'locations' table
class Location(Base):
    __tablename__ = 'locations'
    
    # Defining the columns for the table 'locations',
    # which will hold all of the locations in the U.S. for which
    # top trends data is available, as well as location specific
    # info like latitude/longitude
    id = Column( Integer, primary_key = True)
    woeid = Column( Integer )
    twitter_country = Column( String(100) )
    tritter_country_code = Column( String(10) )
    twitter_name = Column( String(250) )
    twitter_parentid = Column( Integer )
    twitter_type = Column( String(50) )
    country_name = Column( String(250) )
    country_name_only = Column( String(250) )
    country_woeid = Column( Integer )
    county_name = Column( String(250) )
    county_name_only = Column( String(250) )
    county_woeid = Column( Integer )
    latitude = Column( Float )
    longitude = Column( Float )
    name_full = Column( String(250) )
    name_only = Column( String(250) )
    name_woe = Column( String(250) )
    place_type = Column( String(250) )
    state_name = Column( String(250) )
    state_name_only = Column( String(250) )
    state_woeid = Column( Integer )
    timezone = Column( String(250) )
    
    # Relationship between Location and Trend is through 'woeid' in each
    trend = relationship("Trend", backref='Trend.woeid', primaryjoin='Location.woeid==Trend.woeid', lazy='dynamic')
    
# Database schema for Twitter 'trends' table
class Trend(Base):
    __tablename__ = 'trends'
    
    # Defining the columns for the table 'trends',
    # which will hold all of the top trends associated with
    # locations in the 'locations' table
    id = Column( Integer, primary_key = True)
    woeid = Column( Integer, ForeignKey(Location.woeid) )
    twitter_as_of = Column( String(100) )
    twitter_created_at = Column( String(100) )
    twitter_name = Column( String(250) )
    twitter_tweet_name = Column( String(250) )
    twitter_tweet_promoted_content = Column( String(250) )
    twitter_tweet_query = Column( String(250) )
    twitter_tweet_url = Column( String(250) )
    twitter_tweet_volume = Column( Float )
    
   


# In[ ]:





# # Database Setup for `twitter_trends.db` Database

# In[4]:


# Create an engine that stores data in the local directory's SQLite file
# 'data/twitter_trends.db'.
# NOTE: Since this Jupyter notebook  is running in the ./resources folder
# the path to the database is a little different
db_path_jupyter_notebook = "sqlite:///../data/twitter_trends.db"

# But the Flask app will run from the main folder
db_path_flask_app = "sqlite:///data/twitter_trends.db"

engine = create_engine(db_path_jupyter_notebook)

# Create all table in the engine
# (The equivalent of Create Table statements in raw SQL)
Base.metadata.create_all(engine)

# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)

# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()


# In[ ]:





# # Tweepy Setup for Twitter API Access

# In[5]:


# Setup Tweepy API Authentication to access Twitter
auth = tweepy.OAuthHandler(key_twitter_tweetquestor_consumer_api_key, key_twitter_tweetquestor_consumer_api_secret_key)
auth.set_access_token(key_twitter_tweetquestor_access_token, key_twitter_tweetquestor_access_secret_token)
api = tweepy.API(auth, parser=tweepy.parsers.JSONParser())


# In[ ]:





# # Function Definitions: Twitter API Rate Limit Management

# In[6]:


def api_calls_remaining( a_api, a_type = "place"):
# Return the number of Twitter API calls remaining
# for the specified API type:
# 'place': Top 10 trending topics for a WOEID
# 'closest': Locations near a specificed lat/long for which Twitter has trending topic info
# 'available': Locations for which Twitter has topic info

    # Get Twitter rate limit information using the Tweepy API
    rate_limits = a_api.rate_limit_status()
    
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


# In[7]:


def api_time_before_reset( a_api, a_type = "place"):
# Return the number of minutes until the Twitter API is reset
# for the specified API type:
# 'place': Top 10 trending topics for a WOEID
# 'closest': Locations near a specificed lat/long for which Twitter has trending topic info
# 'available': Locations for which Twitter has topic info

    # Get Twitter rate limit information using the Tweepy API
    rate_limits = a_api.rate_limit_status()
    
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


# In[ ]:





# # Function Definitions: Twitter Locations with Available Trends Info

# In[8]:


def get_loc_with_trends_available_to_df( a_api ):
# Get locations that have trends data from a api.trends_available() call,
# flatten the data, and create a dataframe

    # Obtain the WOEID locations for which Twitter Trends info is available
    try:
        trends_avail = a_api.trends_available()
        
    except TweepError as e:
        # No top trends info available for this WOEID, return False
        print(f"Error obtaining top trends for WOEID {a_woeid}: ", e)
        return False
    
    # Import trend availability info into a dataframe
    trends_avail_df = pd.DataFrame.from_dict(trends_avail, orient='columns')

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


# In[9]:


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
        print("Error obtaining location information for WOEID {a_woeid}: ", e)
        return False
    
    # Parse the json
    location_data = response.json()
    
    # Check for failure to locate the information
    if (location_data['stat'] == 'fail'):
        print(f"Error finding location WOEID {a_woeid}: {location_data['message']}")
        
        
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


# In[10]:


def update_db_locations_table(a_api, a_engine):
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
    loc_with_trends_available_df = get_loc_with_trends_available_to_df( a_api )

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
    session.query(Location).delete()
    session.commit()

    # Write this table of location data to the database 'locations' table
    twitter_trend_locations_df.to_sql( 'locations', con=a_engine, if_exists='append', index=False)

    # Print an informative message regarding the update just performed
    q_results = session.query(Location).all()
    print(f"Updated {len(q_results)} locations")

    for row in q_results:
        print(row.woeid, row.name_full)


# In[ ]:





# # Function Definitions: Twitter Top Trends for Twitter Locations

# In[11]:


def get_trends_for_loc( a_api, a_woeid ):
# Get top Twitter trending tweets for a location specified by a WOEID,
# flatten the data, and return it as a list of dictionaries

    # Import trend availability info into a dataframe
    try:
        top_trends = a_api.trends_place( a_woeid )[0]
        
    except TweepError as e:
        # No top trends info available for this WOEID, return False
        print(f"Error obtaining top trends for WOEID {a_woeid}: ", e)
        return False
    
    #pprint(top_trends)
    
    # Repeat some information that is common for all elements in the trends list
    common_info = {}
        
    # Basic information that should be present for any location
    # 'as_of': '2019-03-26T21:22:42Z',
    # 'created_at': '2019-03-26T21:17:18Z',
    # 'locations': [{'name': 'Atlanta', 'woeid': 2357024}]
    try:
        common_info.update( {
            'woeid': int(top_trends['locations'][0]['woeid']),
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


# In[12]:


def update_db_trends_table(a_api, a_engine):
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
    loc_list = [ x[0] for x in session.query(Location.woeid).all()]
    print(f"Retrieved {len(loc_list)} locations for processing")
    
    # Keep track of the actual number of locations
    # where trend info was written to the 'trends' table
    num_location_trends_written_to_db = 0
    
    for tw_woeid in loc_list:
        print(f">> Updating trends for location {tw_woeid}")

        # Make sure we haven't hit the rate limit yet
        calls_remaining = api_calls_remaining( a_api, "place" )
        time_before_reset = api_time_before_reset( a_api, "place")

        # If we're close to hitting the rate limit for the trends/place API,
        # then wait until the next reset =
        # 'time_before_reset' minutes + 1 minute buffer
        if (calls_remaining < 2):
            print (f">> Waiting {time_before_reset} minutes due to rate limit")
            time.sleep( (time_before_reset+1) * 60)

        # Get trend info for a WOEID location
        t_info = get_trends_for_loc(a_api, tw_woeid)

        try:
            # Create a DataFrame
            t_info_df = pd.DataFrame.from_dict(t_info)
            
            # Delete any trends associated with this WOEID
            # before appending new trends to the 'trends' table for this WOEID
            session.query(Trend).filter(Trend.woeid == tw_woeid).delete()
            session.commit()

            # Append trends for this WOEID to the 'trends' database table
            t_info_df.to_sql( 'trends', con=a_engine, if_exists='append', index=False)
            
            # Increment the count
            num_location_trends_written_to_db += 1

        except:
            print(f">> Error occurred with location {tw_woeid} while attempting to prepare and write trends data")
            
    return num_location_trends_written_to_db


# In[ ]:





# # Function Call to Update Twitter Location `locations` Table

# In[13]:


# This is a call to the function that fully updates the database 'locations' table
# Note: This function deletes the location data before the updated information is added
#locations_written_to_db = update_db_locations_table(api, engine)
#locations_written_to_db


# In[ ]:





# # Function Call to Update Twitter Top Trends `trends` Table

# In[14]:


# This is a call to the function that fully updates the database 'trends' table
# for the locations in the 'locations' table
# Note: This function deletes the trends data for each location before new information is added
#trends_written_to_db = update_db_trends_table(api, engine)
#trends_written_to_db


# In[ ]:





# # Ways to Access the Data: Get Location List from the `locations` Table

# In[15]:


# Get the full location list from the 'locations' table
locations_results = session.query(Location).all()
for loc_info in locations_results[0:5]:
    print(f"Location Information: {loc_info.woeid} {loc_info.name_full}")


# In[ ]:





# # Ways to Access the Data: Get info from the `trends` and `locations` Tables

# ### Database code needed to open the twitter_trends.db database

# In[16]:


# Code needed to open the database in the Flask App
# NOTE: DON'T RUN THIS SETUP IF THE DB SETUP AT THE TOP HAS ALREADY BEEN RUN!


# In[17]:


# import sqlalchemy
# from sqlalchemy.ext.automap import automap_base
# from sqlalchemy.orm import Session
# from sqlalchemy import create_engine, asc, desc, between, distinct, func, null, nullsfirst, nullslast, or_, and_, not_

# from flask import Flask, jsonify

# # Create an engine that stores data in the local directory's SQLite file
# # 'data/twitter_trends.db'.
# # NOTE: Since this Jupyter notebook  is running in the ./resources folder
# # the path to the database is a little different
# db_path_jupyter_notebook = "sqlite:///../data/twitter_trends.db"

# # But the Flask app will run from the main folder
# db_path_flask_app = "sqlite:///data/twitter_trends.db"

# engine = create_engine(db_path_jupyter_notebook)

# # Reflect an existing database into a new model
# Base = automap_base()

# # Reflect the tables
# Base.prepare(engine, reflect=True)

# # Save reference to the tables
# Location = Base.classes.locations
# Trend = Base.classes.trends

# # Create our session (link) from Python to the DB
# session = Session(engine)


# ### Will likely need to implement these queries with routes in the Flask App

# In[18]:


# Get the top trends for a single location from the 'trends' table
trends_results = session.query(Trend).filter(Trend.woeid == 2357024).all()
for trend_info in trends_results[0:5]:
    print(f"Trend Information: {trend_info.woeid} {trend_info.twitter_name}: {trend_info.twitter_tweet_name} {trend_info.twitter_tweet_volume}")


# In[19]:


# Get the top 5 trends for a single location from the 'trends' table
trends_results = session.query(Trend).filter(Trend.woeid == 2357024).order_by(desc(Trend.twitter_tweet_volume)).all()
for trend_info in trends_results[0:5]:
    print(f"Trend Information: {trend_info.woeid} {trend_info.twitter_name}: {trend_info.twitter_tweet_name} {trend_info.twitter_tweet_volume}")


# In[20]:


# Get the top 5 trends for the U.S. overall from the 'trends' table
# NOTE: "U.S. overall" is WOEID = 23424977 and is different than tallying across all towns in the U.S.
trends_results = session.query(Trend).filter(Trend.twitter_name == "United States").order_by(desc(Trend.twitter_tweet_volume)).all()
for trend_info in trends_results[0:5]:
    print(f"Trend Information: {trend_info.woeid} {trend_info.twitter_name}: {trend_info.twitter_tweet_name} {trend_info.twitter_tweet_volume}")


# In[ ]:





# In[21]:


# Get the top 5 trends for all "Towns" in the U.S. from the 'trends' table
# NOTE: "U.S. overall" is WOEID = 23424977 and is different than tallying across all towns in the U.S.
# trends_results = session.query(Trend, Location).filter(Location.twitter_type == "Town").order_by(desc(Trend.twitter_tweet_volume)).all()
trends_results = session.query(Trend).join(Location).filter(Location.twitter_type == "Town").order_by(desc(Trend.twitter_tweet_volume)).all()
for trend_info in trends_results[0:5]:
    print(f"Trend Information: {trend_info.woeid} {trend_info.twitter_name}: {trend_info.twitter_tweet_name} {trend_info.twitter_tweet_volume}")


# In[ ]:





# In[22]:


# Get all locations which have a specified tweet in it's top trends list
trends_results = session.query(Trend).filter(Trend.twitter_tweet_name == 'People').order_by(desc(Trend.twitter_tweet_volume)).all()
for trend_info in trends_results:
    print(f"Trend Information: {trend_info.woeid} {trend_info.twitter_name}: {trend_info.twitter_tweet_name} {trend_info.twitter_tweet_volume}")


# In[ ]:





# In[23]:


# Get useful location information about a specific WOEID
# Get all locations which have a specified tweet in it's top trends list
loc_results = session.query(Location).filter(Location.woeid == 2357024 ).all()
for loc_info in loc_results:
    print(f"Location Information: {loc_info.woeid} {loc_info.name_only}: {loc_info.twitter_type} in {loc_info.county_name_only} / {loc_info.state_name_only} / {loc_info.country_name_only} [ {loc_info.latitude}, {loc_info.longitude} ]")


# In[ ]:





# In[24]:


# Get the 'name_full' info for locations which have a specified tweet in it's top trends list
info_results = session.query(Trend, Location).join(Location).filter(Trend.twitter_tweet_name == 'People').order_by(desc(Trend.twitter_tweet_volume)).all()
for info in info_results:
    print(f"Trend Information for {info.Trend.woeid} {info.Location.name_full}: {info.Trend.twitter_tweet_name} {info.Trend.twitter_tweet_volume}")


# In[ ]:




