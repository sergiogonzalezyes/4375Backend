from server import app
from server.classes import User, Schedule, Appointment, Service, Notification, Payment, Review, Appointment_Service, Customer_History, Holiday, Blacklist, Barber_Service
import pandas as pd
from server.db import engine
from sqlalchemy.orm import sessionmaker



Session = sessionmaker(bind=engine)



@app.route("/")
def home():
    return "Hello, World!"
    

@app.route("/dashboard")
def api():
    return "Hello from localhost 5000!"

from flask import jsonify

@app.route("/user")
def user():
    session = Session()  # Create a new session
    cars = session.query(User).statement
    df = pd.read_sql(cars, session.bind)
    print('look here', df)
    session.close()
    return jsonify(df.to_dict(orient='records'))


# @app.route('/login', methods=['POST'])
# def login():
#     if request.method == 'POST':
#         # Handle the POST request here
#         # Example: Check credentials and return a response
#         data = request.get_json()
#         username = data.get('username')
#         password = data.get('password')

#         # Add your authentication logic here
#         # Example: Check if username and password are valid
#         if username == 'adminuser' and password == 'adminpass123':
#             return jsonify({'message': 'Login successful'}), 200
#         else:
#             return jsonify({'message': 'Login failed'}), 401

#     return Response