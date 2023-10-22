from flask import Flask, jsonify, request
from flask_cors import CORS
import os
from dotenv import load_dotenv
from server.db import engine
from sqlalchemy.orm import sessionmaker
from server.classes import User, Service, Barber_Service
from flask_bcrypt import Bcrypt


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
                    "username": user.Username,
                    "role": user.User_Type,
                    "first_name": user.F_Name,
                    "last_name": user.L_Name,
                    "email": user.Email,
                    "phone": user.Phone_Number,
                }
            }
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


@app.route("/services/<int:barber_id>", methods=["GET"])
def get_barber_services(barber_id):
    try:
        # Query the database to get the list of services offered by the specific barber
        services = (
            Service.query
            .join(Barber_Service)  # Assuming you have a relationship defined in your models
            .filter(Barber_Service.Barber_User_ID == barber_id)
            .all()
        )

        # Convert the services to a list of dictionaries
        services_list = [service.to_dict() for service in services]
        return jsonify({"services": services_list})
    except Exception as e:
        return jsonify({"error": str(e)}), 500





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
    
