# Initial the database on Heroku start-up
from python.app import update_db_trends_table

print("PERFORMING UPDATE: Trends Table")
n_trends = update_db_trends_table()
print(n_trends)