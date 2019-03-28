# Project 2 - GeoTweet
# 
# @Author Jeffery Brown (daddyjab)
# @Date 3/27/19
# @File ETL_for_GeoTweet


# import necessary libraries
import os
from flask import (Flask, render_template, jsonify, request, redirect)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Database Setup
#################################################

from flask_sqlalchemy import SQLAlchemy

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

    locations = db.relationship('Location',
                backref=db.backref('trends', lazy=True))
     
    def __repr__(self):
        return '<Trend %r>' % (self.name)



# Default rote - display the main page
@app.route("/")
def home():
    return render_template("index.html")

# Return a list of all locations with Twitter Top Trend info
@app.route("/locations")
def get_all_locations():
    #results = db.session.query(Location.woeid, Location.name_full, Location.latitude, Location.longitude).all()
    results = db.session.query(Location).all()
    return jsonify(results)

# Return a list of all locations with Twitter Top Trend info
@app.route("/locations/<a_woeid>")
def get_info_for_location(a_woeid):
    results = db.session.query(Location).filter(Location.woeid == a_woeid).all()
    return jsonify(results)

# Return a list of all trends with Twitter Top Trend info
@app.route("/trends")
def get_all_trends(a_woeid):
    results = db.session.query(Trend).all()
    return jsonify(results)

# Return a list of Twitter Top Trends for a specific location
@app.route("/trends/<a_woeid>")
def get_trends_for_location(a_woeid):
    results = db.session.query(Trend).filter(Trend.woeid == a_woeid).all()
    return jsonify(results)

if __name__ == "__main__":
    app.run()
