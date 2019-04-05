# Initial the database on Heroku start-up
from python.app import db
db.create_all()
