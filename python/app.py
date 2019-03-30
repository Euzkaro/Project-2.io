# Project 2 - GeoTweet
# 
# @Author Jeffery Brown (daddyjab)
# @Date 3/27/19
# @File app.py


# import necessary libraries
import os
from flask import Flask, render_template, jsonify, request, redirect

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Database Setup
#################################################

from flask_sqlalchemy import SQLAlchemy
#Probably don't need these from SQLAlchemy: asc, desc, between, distinct, func, null, nullsfirst, nullslast, or_, and_, not_

db_path_flask_app = "sqlite:///../data/twitter_trends.db"
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', '') or db_path_flask_app

# Flask-SQLAlchemy database
db = SQLAlchemy(app)

# Import the schema for the Location and Trend tables needed for
# 'twitter_trends.sqlite' database tables 'locations' and 'trends'
from .models import (Location, Trend)

# Import database management functions needed# to update the
# 'twitter_trends.sqlite' database tables 'locations' and 'trends'
from .db_management import (
    api_calls_remaining, api_time_before_reset,
    update_db_locations_table, update_db_trends_table
    )

# Default route - display the main page
# NOTE: Flask expects rendered templates to be in the ./templates folder
@app.route("/")
def home():
    return render_template("index.html")

# Return information relevant to update
# of the 'locations' and 'trends' database tables
@app.route("/update")
def update_info():
    # Obtain remaining number of API calls for trends/place
    api_calls_remaining_place = api_calls_remaining( "place")

    # Obtain time before rate limits are reset for trends/available
    api_time_before_reset_place = api_time_before_reset( "place")

    # Obtain remaining number of API calls for trends/place
    api_calls_remaining_available = api_calls_remaining( "available")

    # Obtain time before rate limits are reset for trends/available
    api_time_before_reset_available = api_time_before_reset( "available")

    # Count the number of locations in the 'locations' table
    n_locations = db.session.query(Location).count()

    # Count the number of total trends in the 'trends' table
    n_trends = db.session.query(Trend).count()

    # Provide the average number of Twitter Trends provided per location
    # Use try/except to catch divide by zero
    try:
        n_trends_per_location_avg = n_trends / n_locations
    except ZeroDivisionError:
        n_trends_per_location_avg = None

    api_info = {
        'api_calls_remaining_place': api_calls_remaining_place,
        'api_time_before_reset_place': api_time_before_reset_place,
        'api_calls_remaining_available': api_calls_remaining_available,
        'api_time_before_reset_available': api_time_before_reset_available,
        'n_locations': n_locations,
        'n_trends': n_trends,
        'n_trends_per_location_avg' : n_trends_per_location_avg
    }

    return jsonify(api_info)


# Update the 'locations' table via API calls
# Note: Typically requires less than 1 minute
@app.route("/update/locations")
def update_locations_table():
    # Update the locations table through API calls
    n_locations = update_db_locations_table()

    api_info = {
        'n_locations': n_locations
    }

    return jsonify(api_info)

# Update the 'locations' table via API calls
# Note: Typically requires less than 1 minute
@app.route("/update/trends")
def update_trends_table():
    # Update the trends table through API calls
    n_location_trends = update_db_trends_table()

    api_info = {
        'n_location_trends': n_location_trends
    }

    return jsonify(api_info)


# Return a list of all locations with Twitter Top Trend info
@app.route("/locations")
def get_all_locations():
    results = db.session.query(Location).all()
    loc_list = []
    for r in results:
        loc_info = {
            'woeid': r.woeid,
            'latitude': r.latitude,
            'longitude': r.longitude,
            'name_full': r.name_full,
            'name_only': r.name_only,
            'name_woe': r.name_woe,
            'county_name': r.county_name,
            'county_name_only': r.county_name_only,
            'county_woeid': r.county_woeid,
            'state_name': r.state_name,
            'state_name_only': r.state_name_only,
            'state_woeid': r.state_woeid,
            'country_name': r.country_name,
            'country_name_only': r.country_name_only,
            'country_woeid': r.country_woeid,
            'place_type': r.place_type,
            'timezone': r.timezone,
            'twitter_type': r.twitter_type,
            'twitter_country': r.twitter_country,
            'tritter_country_code': r.tritter_country_code,
            'twitter_name': r.twitter_name,
            'twitter_parentid': r.twitter_parentid
        }

        loc_list.append(loc_info)

    return jsonify(loc_list)

# Return a list of all locations with Twitter Top Trend info
@app.route("/locations/<a_woeid>")
def get_info_for_location(a_woeid):
    results = db.session.query(Location).filter(Location.woeid == a_woeid).all()

    loc_list = []
    for r in results:
        loc_info = {
            'woeid': r.woeid,
            'latitude': r.latitude,
            'longitude': r.longitude,
            'name_full': r.name_full,
            'name_only': r.name_only,
            'name_woe': r.name_woe,
            'county_name': r.county_name,
            'county_name_only': r.county_name_only,
            'county_woeid': r.county_woeid,
            'state_name': r.state_name,
            'state_name_only': r.state_name_only,
            'state_woeid': r.state_woeid,
            'country_name': r.country_name,
            'country_name_only': r.country_name_only,
            'country_woeid': r.country_woeid,
            'place_type': r.place_type,
            'timezone': r.timezone,
            'twitter_type': r.twitter_type,
            'twitter_country': r.twitter_country,
            'tritter_country_code': r.tritter_country_code,
            'twitter_name': r.twitter_name,
            'twitter_parentid': r.twitter_parentid
        }

        loc_list.append(loc_info)

    return jsonify(loc_list)

# Return the full list of all trends with Twitter Top Trend info
@app.route("/trends")
def get_all_trends():
    results = db.session.query(Trend).all()

    trend_list = []
    for r in results:
        trend_info = {
            'woeid': r.woeid,
            'twitter_as_of': r.twitter_as_of,
            'twitter_created_at': r.twitter_created_at,
            'twitter_name': r.twitter_name,
            'twitter_tweet_name': r.twitter_tweet_name,
            'twitter_tweet_promoted_content': r.twitter_tweet_promoted_content,
            'twitter_tweet_query': r.twitter_tweet_query,
            'twitter_tweet_url': r.twitter_tweet_url,
            'twitter_tweet_volume': r.twitter_tweet_volume
        }

        trend_list.append(trend_info)

    return jsonify(trend_list)

# Return the full list of Twitter Top Trends for a specific location
@app.route("/trends/<a_woeid>")
def get_trends_for_location(a_woeid):
    results = db.session.query(Trend).filter(Trend.woeid == a_woeid).all()

    trend_list = []
    for r in results:
        trend_info = {
            'woeid': r.woeid,
            'twitter_as_of': r.twitter_as_of,
            'twitter_created_at': r.twitter_created_at,
            'twitter_name': r.twitter_name,
            'twitter_tweet_name': r.twitter_tweet_name,
            'twitter_tweet_promoted_content': r.twitter_tweet_promoted_content,
            'twitter_tweet_query': r.twitter_tweet_query,
            'twitter_tweet_url': r.twitter_tweet_url,
            'twitter_tweet_volume': r.twitter_tweet_volume
        }

        trend_list.append(trend_info)

    return jsonify(trend_list)

# Return the top 5 list of Twitter Top Trends for a specific location
@app.route("/trends/top/<a_woeid>")
def get_top_trends_for_location(a_woeid):
    results = db.session.query(Trend).filter(Trend.woeid == a_woeid).order_by(Trend.twitter_tweet_volume.desc()).limit(5).all()

    trend_list = []
    for r in results:
        trend_info = {
            'woeid': r.woeid,
            'twitter_as_of': r.twitter_as_of,
            'twitter_created_at': r.twitter_created_at,
            'twitter_name': r.twitter_name,
            'twitter_tweet_name': r.twitter_tweet_name,
            'twitter_tweet_promoted_content': r.twitter_tweet_promoted_content,
            'twitter_tweet_query': r.twitter_tweet_query,
            'twitter_tweet_url': r.twitter_tweet_url,
            'twitter_tweet_volume': r.twitter_tweet_volume
        }

        trend_list.append(trend_info)

    return jsonify(trend_list)


if __name__ == "__main__":
    app.run()
