from flask import Flask, jsonify, request
from flask_cors import CORS
import os
from dotenv import load_dotenv
from server.db import engine
from sqlalchemy.orm import sessionmaker
from server.classes import User, Service, Barber_Service, Schedule
from flask_bcrypt import Bcrypt
from datetime import datetime, timedelta


app = Flask(__name__)


# Configure CORS to allow requests from your frontend origin
CORS(app, resources={r"/*": {"origins": "http://localhost:8080"}})



# Create a session factory and bind it to your SQLAlchemy engine
Session = sessionmaker(bind=engine)


bcrypt = Bcrypt()


@app.route("/login", methods=['POST'])
def login():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        # Create a session instance
        session = Session()

        user = session.query(User).filter_by(Username=username).first()

        if user and bcrypt.check_password_hash(user.Password, password):
            # Password is correct
            response_data = {
                "success": True,
                "user": {
                    "user_id": user.User_ID,  # Add the user ID to the response
                    "username": user.Username,
                    "role": user.User_Type,
                    "first_name": user.F_Name,
                    "last_name": user.L_Name,
                    "email": user.Email,
                    "phone": user.Phone_Number,
                }
            }
            print(response_data)
            return jsonify(response_data)
        else:
            # Invalid credentials
            return jsonify({"success": False, "message": "Invalid credentials"}), 401
    except Exception as e:
        # Handle exceptions (e.g., database errors)
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        # Ensure the session is closed
        session.close()
        


@app.route("/update-profile", methods=['PUT'])
def update_profile():
    # Your update profile logic here
    try:
        data = request.json
        print(data)
        username = data.get('username')
        
        # Create a session instance
        session = Session()

        # Retrieve the user to be updated
        user = session.query(User).filter_by(Username=username).first()

        if user:
            # Update user profile fields
            user.F_Name = data.get('firstName', user.F_Name)
            user.L_Name = data.get('lastName', user.L_Name)
            user.Email = data.get('email', user.Email)
            user.Phone_Number = data.get('phoneNumber', user.Phone_Number)
            
            # Commit changes to the database
            session.commit()

            return jsonify({"success": True, "user": {
                "username": user.Username,
                "firstName": user.F_Name,
                "lastName": user.L_Name,
                "email": user.Email,
                "phoneNumber": user.Phone_Number
            }})
        else:
            return jsonify({"success": False, "message": "User not found"}), 404
    except Exception as e:
        # Handle exceptions (e.g., database errors)
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        # Ensure the session is closed
        session.close()



@app.route("/register", methods=['POST'])
def register():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        first_name = data.get('firstName')
        last_name = data.get('lastName')
        email = data.get('email')
        phone_number = data.get('phoneNumber')

        # Check if the username already exists
        session = Session()
        existing_user = session.query(User).filter_by(Username=username).first()

        if existing_user:
            return jsonify({"success": False, "message": "Username already exists"}), 400

        # Hash the plain text password using bcrypt
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        # Create a new user record with additional attributes
        new_user = User(
            Username=username,
            Password=hashed_password,  # Store the hashed password
            F_Name=first_name,  # First name
            L_Name=last_name,  # Last name
            Email=email,  # Email
            Phone_Number=phone_number,  # Phone number
            User_Type='customer'
        )

        # Add the user to the database
        session.add(new_user)
        session.commit()

        return jsonify({"success": True, "message": "User registered successfully"})
    
    except Exception as e:
        # Log the error
        print(f"Error: {str(e)}")
        # Handle exceptions (e.g., database errors)
        return jsonify({"success": False, "message": str(e)}), 500

    finally:
        # Ensure the session is closed
        session.close()


@app.route("/services", methods=["GET"])
def get_all_services():
    try:
        # Create a session instance
        session = Session()

        # Query the database to get all services
        services = session.query(Service).all()

        # Create a list to store the service data
        services_list = []

        # Iterate over the services and convert them to dictionaries
        for service in services:
            service_data = {
                "Service_ID": service.Service_ID,
                "Service_Name": service.Service_Name,
                "Service_Description": service.Service_Description,
                "Service_Price": str(service.Service_Price),  # Convert to string for JSON
                "Service_Duration": service.Service_Duration,
                # Include any other fields you want here
            }
            services_list.append(service_data)

        # Close the session
        session.close()
        print(services_list)
        # Return the list of service data as JSON
        return jsonify({"services": services_list})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    



# @app.route('/service/<int:service_id>/availability', methods=['GET'])
# def get_service_availability(service_id):
#     try:
#         # Create a sessions # Replace 'your_database_engine' with your actual database engine
#         session = Session()

#         # Find the service
#         service = Service.query.get(service_id)

#         if not service:
#             session.close()
#             return jsonify(message="Service not found"), 404

#         # Find users (barbers) who offer the service
#         barbers = (
#             User.query
#             .filter(User.user_type.in_(['admin', 'barber']))
#             .join(User.barber_services)
#             .filter(Barber_Service.Service_ID == service_id)
#             .all()
#         )

#         availability_data = []

#         for barber in barbers:
#             barber_data = {
#                 'barber_id': barber.User_ID,
#                 'barber_name': barber.name,
#                 'availability': []
#             }

#             # Find available time slots for the barber on specific days (modify as needed)
#             schedules = session.query(Schedule).filter_by(Barber_User_ID=barber.User_ID).all()
#             for schedule in schedules:
#                 availability_data.append({
#                     'barber_id': barber.User_ID,
#                     'barber_name': barber.name,
#                     'day_of_week': schedule.Day_Of_Week,
#                     'start_time': schedule.Start_Time.strftime('%H:%M'),
#                     'end_time': schedule.End_Time.strftime('%H:%M'),
#                 })

#         # Close the session when done
#         session.close()

#         return jsonify(availability_data), 200

#     except Exception as e:
#         # Rollback the session in case of an error
#         session.rollback()
#         return jsonify(error=str(e)), 500



@app.route('/service/<int:service_id>/availability', methods=['GET'])
def get_service_availability(service_id):
    try:
        # Create a session
        session = Session()

        # Find the service
        service = session.query(Service).get(service_id)

        if not service:
            return jsonify(message="Service not found"), 404

        # Find users (barbers) who offer the service
        barbers = (
            session.query(User)
            .filter(User.User_Type.in_(['admin', 'barber']))
            .join(User.barber_services)
            .filter(Barber_Service.Service_ID == service_id)
            .all()
        )

        availability_data = []

        for barber in barbers:
            barber_data = {
                'barber_id': barber.User_ID,
                'barber_name': barber.F_Name + " " + barber.L_Name,
                'availability': []
            }
            # Find available time slots for the barber on specific days (modify as needed)
            schedules = session.query(Schedule).filter_by(Barber_User_ID=barber.User_ID).all()
            for schedule in schedules:
                availability_data.append({
                    'barber_id': barber.User_ID,
                    'barber_name': barber.F_Name + " " + barber.L_Name,
                    'day_of_week': schedule.Day_Of_Week,
                    'start_time': schedule.Start_Time.strftime('%H:%M'),
                    'end_time': schedule.End_Time.strftime('%H:%M'),
                    'availability': schedule.Status
                })

        # Close the session when done
        session.close()

        return jsonify(availability_data), 200

    except Exception as e:
        # Rollback the session in case of an error
        session.rollback()
        return jsonify(error=str(e)), 500


# Endpoint to retrieve available dates for a selected barber by ID
@app.route('/schedule/<int:barber_id>/available-dates', methods=['GET'])
def get_available_dates_for_barber(barber_id):
    try:
        # Create a session
        session = Session()

        # Query the Schedule table to find available dates for the selected barber
        available_dates = session.query(Schedule.Day_Of_Week).filter_by(Barber_User_ID=barber_id, Status='Available').distinct().all()

        # Extract distinct dates from the results
        distinct_dates = list(set(date[0] for date in available_dates))
        print(distinct_dates)
        # Close the session
        session.close()

        return jsonify({'available_dates': distinct_dates})

    except Exception as e:
        # Close the session in case of an exception
        if 'session' in locals():
            session.close()
        return jsonify({'error': str(e)}), 500





@app.route('/schedule/<int:barber_id>/available-time-slots', methods=['GET'])
def get_available_time_slots_for_barber(barber_id):
    try:
        date_str = request.args.get('date')
        print('date_str', date_str)
        # Create a session
        session = Session()
        
        # Format the date string to match the database format 'YYYY-MM-DD'
        formatted_date = datetime.strptime(date_str, '%a, %d %b %Y %H:%M:%S GMT').strftime('%Y-%m-%d')
        print('formatted date', formatted_date)

        # Calculate the start and end times for the selected day
        start_datetime = datetime.strptime(formatted_date, '%Y-%m-%d')
        print('start_datetime', start_datetime)
        end_datetime = start_datetime + timedelta(days=1)
        print('end_datetime', end_datetime)
        # Query the Schedule table to find available time slots for the selected barber on the selected date
        available_time_slots = session.query(Schedule).filter_by(
            Barber_User_ID=barber_id,
            Day_Of_Week=formatted_date,
            Status='Available'
        ).all()
        print('available_time_slots', available_time_slots)

        # Extract the start and end times from the query result
        start_times = [slot.Start_Time for slot in available_time_slots]
        end_times = [slot.End_Time for slot in available_time_slots]

        # Combine the start and end times into a list of time slots
        time_slots = list(zip(start_times, end_times))

        # Create a dictionary with auto-incremented slot numbers
        time_slots_dict = {}
        for index, (start_time, end_time) in enumerate(time_slots, start=1):
            time_slots_dict[index] = {
                'start_time': start_time.strftime('%H:%M'),
                'end_time': end_time.strftime('%H:%M')
            }
        print('time_slots_dict', time_slots_dict)

        # Close the session
        session.close()

        # Return the time_slots_dict as JSON
        return jsonify({'available_time_slots': time_slots_dict})

    except Exception as e:
        # Close the session in case of an exception
        if 'session' in locals():
            session.close()
        return jsonify({'error': str(e)}), 500








# def hash_passwords_in_database():
#     print("Hashing passwords in database...")
#     try:
#         # Create a session instance
#         session = Session()

#         # Retrieve users with plain text passwords
#         users_with_plain_passwords = session.query(User).filter(User.Password != None).all()

#         for user in users_with_plain_passwords:
#             # Hash the plain text password using bcrypt
#             hashed_password = bcrypt.generate_password_hash(user.Password).decode('utf-8')
            
#             print(f"User: {user.Username}, Plain Password: {user.Password}")
#             print(f"Hashed Password: {hashed_password}")

#             # Update the user's record with the hashed password
#             user.Password = hashed_password

#         # Commit the changes to the database
#         session.commit()
#         print("Passwords hashed successfully.")
#     except Exception as e:
#         # Handle exceptions (e.g., database errors)
#         print(f"An error occurred: {str(e)}")
#     finally:
#         # Ensure the session is closed
#         session.close()




if __name__ == "__main__":
    # hash_passwords_in_database()
    app.run(host="localhost", port=5001)
    
