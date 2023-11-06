from flask import Flask
from flask_cors import CORS
import os
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL")

# Configure CORS to allow requests from your frontend origin
CORS(app, resources={r"/api/*": {"origins": "http://localhost:8080"}})


from server.classes import User, Schedule, Appointment, Service, Notification, Review, Customer_History, Holiday, Blacklist, Barber_Service


