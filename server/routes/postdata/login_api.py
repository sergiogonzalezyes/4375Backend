# from server import app
# from server.classes import User, Schedule, Appointment, Service, Notification, Payment, Review, Appointment_Service, Customer_History, Holiday, Blacklist, Barber_Service
# import pandas as pd
# from server.db import engine
# from sqlalchemy.orm import sessionmaker
# from flask import jsonify, request, Response


# Session = sessionmaker(bind=engine)


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



# @app.route("/login", methods=['OPTIONS'])
# def login_options():
#     response = app.make_default_options_response()

#     # Add your custom headers
#     response.headers['Access-Control-Allow-Origin'] = 'http://localhost:8080'
#     response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
#     response.headers['Access-Control-Allow-Headers'] = 'content-type'
    
#     return response
