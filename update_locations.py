# Initial the database on Heroku start-up
from python.app import update_db_locations_table

print("PERFORMING UPDATE: Locations Table")
n_locations = update_db_locations_table()
print(n_locations)