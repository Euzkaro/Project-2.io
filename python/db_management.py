# Project 2 - GeoTweet
# 
# @Author Jeffery Brown (daddyjab)
# @Date 3/27/19
# @File db_management.py

# This file contains function which update the
# 'tritter_trends.sqlite' database tables
# 'locations' and 'trends' via API calls to Twitter and Flickr

# The following dependencies are only required for update/mgmt of
# 'locations' and 'trends' data, not for reading the data
import json
import time
import os
import pandas as pd
from datetime import datetime 
from dateutil import tz
import requests
from pprint import pprint

# Import a pointer to the Flask-SQLAlchemy database session
# created in the main app.py file
# from app import db, Location, Trend
from .app import db, Location, Trend

# DEBUG - Try this to ensure imports are working
def try_db_access():
    results = db.session.query(Location).all()
    return results

# # Function Definitions: Twitter API Rate Limit Management

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
