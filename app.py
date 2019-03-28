# Project 2 - GeoTweet
# 
# @Author Jeffery Brown (daddyjab)
# @Date 3/27/19
# @File ETL_for_GeoTweet


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
# asc, desc, between, distinct, func, null, nullsfirst, nullslast, or_, and_, not_

db_path_flask_app = "sqlite:///data/twitter_trends.db"

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', '') or db_path_flask_app
db = SQLAlchemy(app)

# from models import (Location, Trend)

# Database schema for Twitter 'locations' table
class Location(db.Model):
    __tablename__ = 'locations'
    
    # Defining the columns for the table 'locations',
    # which will hold all of the locations in the U.S. for which
    # top trends data is available, as well as location specific
    # info like latitude/longitude
    id = db.Column(db.Integer, primary_key=True)
    woeid = db.Column(db.Integer)
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
    
    def __repr__(self):
        return '<Location %r>' % (self.name)

# Database schema for Twitter 'trends' table
class Trend(db.Model):
    __tablename__ = 'trends'
    
    # Defining the columns for the table 'trends',
    # which will hold all of the top trends associated with
    # locations in the 'locations' table
    id = db.Column(db.Integer, primary_key=True)
    woeid = db.Column(db.Integer, db.ForeignKey('locations.woeid') )
    twitter_as_of = db.Column(db.String(100))
    twitter_created_at = db.Column(db.String(100))
    twitter_name = db.Column(db.String(250))
    twitter_tweet_name = db.Column(db.String(250))
    twitter_tweet_promoted_content = db.Column(db.String(250))
    twitter_tweet_query = db.Column(db.String(250))
    twitter_tweet_url = db.Column(db.String(250))
    twitter_tweet_volume = db.Column(db.Float)

    locations = db.relationship('Location', backref=db.backref('trends', lazy=True))
     
    def __repr__(self):
        return '<Trend %r>' % (self.name)



# Default rote - display the main page
# NOTE: Flask expects rendered templates to be in the ./templates folder
@app.route("/")
def home():
    return render_template("index.html")
    
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
