from flask import Flask, jsonify, request
from flask_cors import CORS
import os
from dotenv import load_dotenv
from server.db import engine
from sqlalchemy.orm import sessionmaker
from server.classes import User, Service, Barber_Service, Schedule, Appointment, Notification, Payment, Payment_Type
from flask_bcrypt import Bcrypt
from datetime import datetime, timedelta
from sqlalchemy import func
import smtplib


app = Flask(__name__)


# Configure CORS to allow requests from your frontend origin
CORS(app, resources={r"/*": {"origins": "http://localhost:8080"}}, methods=['GET', 'POST', 'PUT', 'DELETE'])



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
        # print(data)
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
        # print(services_list)
        # Return the list of service data as JSON
        return jsonify({"services": services_list})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

@app.route("/services/<int:user_id>", methods=["GET"])
def get_services_for_barber(user_id):
    try:
        # Create a session instance
        session = Session()

        # Query the database to get all services offerd by the barber
        services = (
            session.query(Service)
            .filter(Service.barber_services.any(Barber_Service.Barber_User_ID == user_id))
            .all()
        )

        # Create a list to store the service data
        services_list = []

        # Iterate over the services and convert them to dictionaries
        for service in services:

            services_list.append({
                "Service_ID": service.Service_ID,
                "Service_Name": service.Service_Name,
                "Service_Description": service.Service_Description,
                "Service_Price": str(service.Service_Price),  # Convert to string for JSON
                "Service_Duration": service.Service_Duration,
                # Include any other fields you want here
            })

        # Close the session
        session.close()
        # print(services_list)
        # Return the list of service data as JSON
        return jsonify({"services": services_list})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()

    

@app.route('/updateservice/<int:service_id>', methods=['PUT'])
def update_service(service_id):
    try:
        session = Session()
        data = request.get_json()
        print('data', data)
        service_id = data.get('Service_ID')
        new_service_name = data.get('Service_Name')
        new_service_description = data.get('Service_Description')
        new_service_price = data.get('Service_Price')
        new_service_duration = data.get('Service_Duration')
        

        # Query the database to find the service by ID
        service = session.query(Service).filter_by(Service_ID=service_id).first()

        if service:
            # change the old data with the new data
            service.Service_Name = new_service_name
            service.Service_Description = new_service_description
            service.Service_Price = new_service_price
            service.Service_Duration = new_service_duration

            # Commit changes to the database
            session.commit()

            return jsonify({"success": True, "message": "Service updated successfully"})
        else:
            return jsonify({"success": False, "message": "Service not found"}), 404
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()



@app.route('/weeklyappointments/<int:user_id>', methods=['GET'])
def fetchWeeklyAppointments(user_id):
    try:
        session = Session()
        user_id = request.args.get('user_id')
        print('user_id', user_id)
        # Query the database to find the service by ID
        appointments = session.query(Appointment).filter_by(Barber_User_ID=user_id).all()
        print('appointments', appointments)
        # Create a list to store the service data
        appointments_list = []
        # Iterate over the services and convert them to dictionaries
        for appointment in appointments:
            appointment_data = {
                "Appointment_ID": appointment.Appointment_ID,
                "Appointment_Date_Time": appointment.Appointment_Date_Time.strftime('%Y-%m-%d %H:%M:%S'),
                "Appointment_End_Date_Time": appointment.Appointment_End_Date_Time.strftime('%Y-%m-%d %H:%M:%S'),
                "Status": appointment.Status,
                "Payment_ID": appointment.Payment_ID,
                "Service_ID": appointment.Service_ID,
                "Barber_User_ID": appointment.Barber_User_ID,
                "Customer_User_ID": appointment.Customer_User_ID,
                "F_Name": appointment.F_Name,
                "L_Name": appointment.L_Name,
                "Email": appointment.Email,
                "Phone_Number": appointment.Phone_Number,
                # Include any other fields you want here
            }
            appointments_list.append(appointment_data)
            print('fetchweeklyappts', appointments_list)

        # Close the session
        session.close()
        # print(services_list)
        # Return the list of service data as JSON
        return jsonify({"appointments": appointments_list})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()



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
        sorted_distinct_dates = sorted(distinct_dates)
        print(sorted_distinct_dates)

        # Close the session
        session.close()

        return jsonify({'available_dates': sorted_distinct_dates})

    except Exception as e:
        # Close the session in case of an exception
        if 'session' in locals():
            session.close()
        return jsonify({'error': str(e)}), 500





@app.route('/schedule/<int:barber_id>/available-time-slots', methods=['GET'])
def get_available_time_slots_for_barber(barber_id):
    try:
        date_str = request.args.get('date')
        # print('date_str', date_str)
        # Create a session
        session = Session()
        
        # Format the date string to match the database format 'YYYY-MM-DD'
        formatted_date = datetime.strptime(date_str, '%a, %d %b %Y %H:%M:%S GMT').strftime('%Y-%m-%d')
        # print('formatted date', formatted_date)

        # Calculate the start and end times for the selected day
        start_datetime = datetime.strptime(formatted_date, '%Y-%m-%d')
        # print('start_datetime', start_datetime)
        end_datetime = start_datetime + timedelta(days=1)
        # print('end_datetime', end_datetime)
        # Query the Schedule table to find available time slots for the selected barber on the selected date
        available_time_slots = session.query(Schedule).filter_by(
            Barber_User_ID=barber_id,
            Day_Of_Week=formatted_date,
            Status='Available'
        ).all()
        # print('available_time_slots', available_time_slots)

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
        # print('time_slots_dict', time_slots_dict)

        # Close the session
        session.close()

        # Return the time_slots_dict as JSON
        return jsonify({'available_time_slots': time_slots_dict})
    except Exception as e:
        # Close the session in case of an exception
        if 'session' in locals():
            session.close()
        return jsonify({'error': str(e)}), 500
    


@app.route('/bookings', methods=['POST'])
def create_booking():
    # Get data from the request's JSON body
    data = request.get_json()

    # Extract data from the request
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    email = data.get('email')
    phone = data.get('phone')
    barber_id = data.get('barber_id')
    date_str = data.get('date')
    start_time_str = data.get('start_time')
    end_time_str = data.get('end_time')
    service = data.get('service_id')
    customer_id = data.get('customer_id')
    # print('customer_id', customer_id)

    # Convert date and times to the desired format
    date_obj = datetime.strptime(date_str, '%a, %d %b %Y %H:%M:%S %Z')
    date_formatted = date_obj.strftime('%Y-%m-%d')
    start_time_formatted = start_time_str + ':00'  # Add seconds to start_time if needed
    end_time_formatted = end_time_str + ':00'
    start_datetime_str = f"{date_formatted} {start_time_formatted}"
    start_datetime = datetime.strptime(start_datetime_str, '%Y-%m-%d %H:%M:%S')
    end_datetime_str = f"{date_formatted} {end_time_formatted}"
    end_datetime = datetime.strptime(end_datetime_str, '%Y-%m-%d %H:%M:%S')

    try:
        session = Session()

        # Determine the selected schedule for the time slot
        selected_schedule = session.query(Schedule).filter_by(
            Barber_User_ID=barber_id,
            Day_Of_Week=date_formatted,
            Start_Time=start_datetime.strftime('%Y-%m-%d %H:%M:%S'),  # Format start_datetime
            End_Time=end_datetime.strftime('%Y-%m-%d %H:%M:%S'),  # Format end_datetime
        ).first()

        if selected_schedule:
            # User is authenticated or not, use data from the request
            appointment = Appointment(
                F_Name=first_name,
                L_Name=last_name,
                Email=email,
                Phone_Number=phone,
                Customer_User_ID=customer_id,
                Barber_User_ID=barber_id,
                Appointment_Date_Time=start_datetime,  # Use start_datetime as the appointment time
                Appointment_End_Date_Time=end_datetime,
                Status='Confirmed',  # Set an appropriate status
                Service_ID=service,
                Schedule_ID=selected_schedule.Schedule_ID  # Assign the Schedule_ID from the selected schedule
            )

            session.add(appointment)
            session.commit()  # Commit the appointment to the database to obtain the Appointment_ID

            # Create a notification
            appointment_id = appointment.Appointment_ID  # Get the appointment ID
            notification = Notification(
                User_ID=barber_id,
                Appointment_ID=appointment_id,
                Message='Your appointment has been booked.',
                Notification_Type='Booking Confirmation',
                Notification_Date_Time=datetime.now(),
                Notification_Status='Unread'
            )

            session.add(notification)

            # Update the schedule status
            selected_schedule.Status = 'Unavailable'


            # Get service data 
            service_booked = session.query(Service).filter_by(Service_ID=service).first()
            service_name = service_booked.Service_Name


            session.commit()  # Commit the notification and schedule changes

        else:
            # Handle the case when the selected schedule is None, indicating an error
            # print('Selected schedule not found')
            return jsonify({'error': 'Selected schedule not found'}), 400
        

        # Query barber/admin's email by barber_id
        barber = session.query(User).filter_by(User_ID=barber_id).first()
        if barber:
            barber_email = barber.Email

            # Use Outlook.com's SMTP server
            smtp_server = 'smtp-mail.outlook.com'
            smtp_port = 587

            # Now send email to customer and barber that appointment was booked with relevant information of appointment
            # Email to customer
            sender_email = os.getenv('EMAIL_ADDRESS')
            sender_password = os.getenv('EMAIL_PASSWORD')
            receiver_email = email

            message = f"""\
            Subject: Appointment Confirmation

            Dear {first_name} {last_name},
            Your appointment has been booked with {barber.F_Name} on {date_formatted} at {start_time_formatted} for {service_name}.
            """
            try:
                with smtplib.SMTP(smtp_server, smtp_port) as smtp:
                    smtp.starttls()
                    smtp.login(sender_email, sender_password)
                    smtp.sendmail(sender_email, receiver_email, message)

                # Email to barber/admin
                message = f"""\
                Subject: New Appointment Scheduled

                Dear {barber.F_Name},
                A new appointment has been scheduled by {first_name} {last_name} on {date_formatted} at {start_time_formatted} for {service_name}.
                """
                with smtplib.SMTP(smtp_server, smtp_port) as smtp:
                    smtp.starttls()
                    smtp.login(sender_email, sender_password)
                    smtp.sendmail(sender_email, barber_email, message)

            except Exception as e:
                print('Error:', str(e))
                return jsonify({'error': str(e)}), 500
        else:
            return jsonify({'error': 'Barber not found'}), 404
        



        session.close()

        # Return a success response
        return jsonify({'message': 'Appointment created successfully'}), 201

    except Exception as e:
        print('Error:', str(e))
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()





@app.route('/notifications/<int:user_id>', methods=['GET'])
def get_notifications(user_id):
    try:
        session = Session()

        # Query the User table to find the user by User_ID
        user = session.query(User).filter_by(User_ID=user_id).first()
        # print('user', user)

        if user:
            # Query the Notification table to fetch notifications for the user
            notifications = session.query(Notification).filter_by(User_ID=user_id).all()
            # print('notifications', notifications)
            for notification in notifications:
                print(notification.Notification_Date_Time.strftime('%Y-%m-%d %H:%M:%S'))



            # Convert notifications to a list of dictionaries with desired fields
            formatted_notifications = []
            for notification in notifications:
                formatted_notification = {
                    'id': notification.Notification_ID,
                    'appointment_id': notification.Appointment_ID,
                    'title': notification.Notification_Type,
                    'content': notification.Message,
                    'created_at': notification.Notification_Date_Time.strftime('%Y-%m-%d %H:%M:%S'),
                    'status': notification.Notification_Status
                }
                formatted_notifications.append(formatted_notification)
            
            return jsonify({'notifications': formatted_notifications}), 200

        else:
            return jsonify({'message': 'User not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()


# Define a route to mark a notification as read
@app.route('/mark-as-read/<int:notification_id>', methods=['PUT'])
def mark_as_read(notification_id):
    try:
        session = Session()

        # Query the Notification table to find the notification by ID
        notification = session.query(Notification).filter_by(Notification_ID=notification_id).first()

        if notification:
            # Update the notification status to "Read"
            notification.Notification_Status = 'Read'
            session.commit()
            return jsonify({'message': 'Notification marked as read.'}), 200
        else:
            return jsonify({'message': 'Notification not found.'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()


@app.route('/mark-all-as-read', methods=['PUT'])
def mark_all_notifications_as_read():
    try:
        data = request.get_json()
        notification_ids = data.get('notificationIds', [])

        session = Session()

        # Update the status of all notifications with the given IDs to 'Read'
        session.query(Notification).filter(Notification.Notification_ID.in_(notification_ids)).update(
            {"Notification_Status": "Read"},
            synchronize_session=False
        )

        session.commit()
        return jsonify({'success': True}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()

        

@app.route('/appointments/<int:appointment_id>', methods=['GET'])
def get_appointment_details(appointment_id):
    try:
        # Create a new session
        session = Session()

        # Query the Appointment table by appointment_id
        appointment = session.query(Appointment).filter_by(Appointment_ID=appointment_id).first()

        # Check if the appointment exists
        if appointment is not None:
            # Convert the appointment object to a dictionary for JSON serialization
            appointment_details = {
                'Appointment_ID': appointment.Appointment_ID,
                'Appointment_Date_Time': appointment.Appointment_Date_Time.strftime('%Y-%m-%d %H:%M:%S'),
                'Appointment_End_Date_Time': appointment.Appointment_End_Date_Time.strftime('%Y-%m-%d %H:%M:%S'),
                'Status': appointment.Status,
                'Payment_ID': appointment.Payment_ID,
                'Service_ID': appointment.Service_ID,
                'Barber_User_ID': appointment.Barber_User_ID,
                'Customer_User_ID': appointment.Customer_User_ID,
                'F_Name': appointment.F_Name,
                'L_Name': appointment.L_Name,
                'Email': appointment.Email,
                'Phone_Number': appointment.Phone_Number,
            }

            # Check if the appointment is associated with a logged-in user
            if appointment.Customer_User_ID is not None:
                # Query the User table to get user details
                user = session.query(User).filter_by(User_ID=appointment.Customer_User_ID).first()
                if user is not None:
                    appointment_details['F_Name'] = user.F_Name
                    appointment_details['L_Name'] = user.L_Name
                    appointment_details['Email'] = user.Email
                    appointment_details['Phone_Number'] = user.Phone_Number

            # Query the Service table to get service details
            service = session.query(Service).filter_by(Service_ID=appointment.Service_ID).first()
            if service is not None:
                appointment_details['Service_Name'] = service.Service_Name
                appointment_details['Service_Description'] = service.Service_Description
                appointment_details['Service_Price'] = service.Service_Price

            return jsonify(appointment_details)
        else:
            # If the appointment doesn't exist, return a 404 error
            return jsonify({'error': 'Appointment not found'}), 404
    except Exception as e:
        # Handle exceptions (e.g., database errors)
        return jsonify({'error': str(e)}), 500
    finally:
        # Close the session
        session.close()



@app.route('/dailyappointments/<int:user_id>/<string:date>', methods=['GET'])
def get_appointments_for_barber_by_date(user_id, date):
    try:
        session = Session()
        
        print('user_id', user_id)
        print('date', date)

        # Convert the 'date' string to a date object
        date_obj = datetime.strptime(date, '%Y-%m-%d').date()

        # Query the Appointment table to find appointments for the user and date
        appointments = session.query(Appointment).filter(
            Appointment.Barber_User_ID == user_id,
            func.date(Appointment.Appointment_Date_Time) == date_obj
        ).all()

        # Convert appointments to a list of dictionaries with desired fields
        formatted_appointments = []
        for appointment in appointments:
            # Get the service associated with the appointment
            service = session.query(Service).filter_by(Service_ID=appointment.Service_ID).first()

            # Get the schedule information associated with the appointment
            schedule = session.query(Schedule).filter_by(Schedule_ID=appointment.Schedule_ID).first()

            # Initialize customer details
            customer_details = {
                'customer_user_id': appointment.Customer_User_ID,
                'email': None,
                'first_name': None,
                'last_name': None,
                'phone_number': None
            }

            # Check if customer_user_id is not None and retrieve customer details if available
            if appointment.Customer_User_ID:
                customer = session.query(User).filter_by(User_ID=appointment.Customer_User_ID).first()
                if customer:
                    customer_details['email'] = customer.Email
                    customer_details['first_name'] = customer.F_Name
                    customer_details['last_name'] = customer.L_Name
                    customer_details['phone_number'] = customer.Phone_Number
            else:
                customer_details['email'] = appointment.Email
                customer_details['first_name'] = appointment.F_Name
                customer_details['last_name'] = appointment.L_Name
                customer_details['phone_number'] = appointment.Phone_Number

            if service and schedule:
                formatted_appointment = {
                    'id': appointment.Appointment_ID,
                    'appointment_date_time': appointment.Appointment_Date_Time.strftime('%Y-%m-%d %H:%M:%S'),
                    'appointment_end_date_time': appointment.Appointment_End_Date_Time.strftime('%Y-%m-%d %H:%M:%S'),
                    'status': appointment.Status,
                    'customer': customer_details,
                    'service': {
                        'service_id': service.Service_ID,
                        'service_name': service.Service_Name,  # Use service name as 'name'
                        'service_description': service.Service_Description,
                        'service_price': service.Service_Price,
                        'service_duration': service.Service_Duration
                    },
                    'start_time': schedule.Start_Time.strftime('%H:%M:%S'),
                    'end_time': schedule.End_Time.strftime('%H:%M:%S')
                }
                formatted_appointments.append(formatted_appointment)

        return jsonify({'appointments': formatted_appointments}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()


from flask import request

@app.route('/services/<int:service_id>/<int:user_id>', methods=['DELETE'])
def delete_service(service_id, user_id):
    try:
        session = Session()
        
        # Check if the user making the request is an 'admin' or a 'barber'
        user = session.query(User).filter_by(User_ID=user_id).first()
        print('user', user)
        print('user.User_Type', user.User_Type)
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        if user.User_Type == 'admin':
            # Admin user, perform hard delete of the service
            service = session.query(Service).filter_by(Service_ID=service_id).first()
            print('service', service.Service_ID)

            if service:
                # Delete the service
                session.delete(service)
                session.commit()
                return jsonify({'message': 'Service deleted successfully'}), 200
            else:
                return jsonify({'message': 'Service not found'}), 404
        elif user.User_Type == 'barber':
            # Barber user, delete records from Barber_Service table
            session.query(Barber_Service).filter_by(Barber_User_ID=user_id, Service_ID=service_id).delete()
            session.commit()
            return jsonify({'message': 'Barber disconnected from the service'}), 200
        else:
            # Handle other user roles as needed
            return jsonify({'message': 'User role not supported for service deletion'}), 403

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()


@app.route('/addservice', methods=['POST'])
def add_service():
    try:
        data = request.get_json()
        service_name = data.get('Service_Name')
        service_description = data.get('Service_Description')
        service_price = data.get('Service_Price')
        service_duration = data.get('Service_Duration')

        session = Session()

        # Create a new service record
        new_service = Service(
            Service_Name=service_name,
            Service_Description=service_description,
            Service_Price=service_price,
            Service_Duration=service_duration
        )

        # Add the service to the database
        session.add(new_service)
        session.commit()

        return jsonify({'message': 'Service added successfully'}), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()


# @app.route('/payment-methods', methods=['GET'])
# def get_payment_methods():

#     try:
#         session = Session()

#         # Query the Payment_Method table to get all payment methods
#         payment_methods = session.query(Payment_Type).all()
#         print()

#         # Convert payment methods to a list of dictionaries with desired fields
#         formatted_payment_methods = []
#         for payment_method in payment_methods:
#             formatted_payment_method = {
#                 'id': payment_method.Payment_ID,
#                 'name': payment_method.Payment_Type_Name,
#             }
#             formatted_payment_methods.append(formatted_payment_method)

#         return jsonify({'payment_methods': formatted_payment_methods}), 200

#     except Exception as e:
#         return jsonify({'error': str(e)}), 500
#     finally:
#         session.close()




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

# @app.route('/update_schedule_status', methods=['POST'])
# def update_schedule_status():
#     session = Session()
#     try:
#         # Query and update all schedule records to set Status to 'Available'
#         schedule_records = session.query(Schedule).all()
#         for schedule_record in schedule_records:
#             schedule_record.Status = 'Available'

#         # Commit the changes to the database
#         session.commit()
#         return jsonify({'message': 'Status of all schedule records updated to "Available"'}), 200

#     except Exception as e:
#         # Handle exceptions if any
#         session.rollback()
#         return jsonify({'error': str(e)}), 500

#     finally:
#         session.close()


# # create a week of schedule records 
# @app.route('/create_schedule_records', methods=['POST'])
# def create_schedule_records():
#     session = Session()
#     try:
#         # Create a list of days of the week
#         days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

#         #
#         # Query the User table to find all barbers
#         barbers = session.query(User).filter_by(User_Type='barber').all()

#         # Create a list of schedule records
#         schedule_records = []

#         # Iterate over the barbers and days of the week to create schedule records
#         for barber in barbers:
#             for day in days_of_week:
#                 schedule_record = Schedule(
#                     Barber_User_ID=barber.User_ID,
#                     Day_Of_Week=day,
#                     Start_Time=datetime.strptime('09:00', '%H:%M'),
#                     End_Time=datetime.strptime('17:00', '%H:%M'),
#                     Status='Available'
#                 )
#                 schedule_records.append(schedule_record)

#         # Add the schedule records to the database
#         session.add_all(schedule_records)
#         session.commit()

#         return jsonify({'message': 'Schedule records created successfully'}), 201
    
#     except Exception as e:
#         print('Error', str(e))
#         # Handle exceptions if any
#         session.rollback()
#         return jsonify({'error': str(e)}), 500

    
    # finally:
    #     session.close()




        




if __name__ == "__main__":
    # hash_passwords_in_database()
    app.run(host="localhost", port=5001)
    
