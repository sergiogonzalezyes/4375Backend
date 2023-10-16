from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
import os
from dotenv import load_dotenv
# import pymysql

# Load environment variables from .env file
load_dotenv()

# Get the database URL from the environment variables
database_url = os.getenv("DATABASE_URL")
print('LOOK HERE', database_url)

if database_url is None:
    raise ValueError("DATABASE_URL environment variable is not set")

# # Convert the MySQL URL to use pymysql (if using mysqlclient previously)
# if database_url.startswith('mysql'):
#     database_url = database_url.replace('mysql', 'mysql+pymysql', 1)

# Create the engine using the database URL
engine = create_engine(database_url, connect_args={'ssl': {'ssl_cert': None}})
Base = declarative_base()