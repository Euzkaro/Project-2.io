from app import db

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
