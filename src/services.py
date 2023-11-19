import bson
import os
import jwt
from datetime import datetime, timedelta
import socket
import uuid
# import base64
# from io import BytesIO
import qrcode
from dotenv import load_dotenv
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from flask import current_app, send_file
from pymongo import DESCENDING
load_dotenv()

DATABASE_URL = os.environ.get('DATABASE_URL')
print(DATABASE_URL)
client = MongoClient(DATABASE_URL)
print(client)
db = client.myDatabase


class User:
    # User Model
    def __init__(self):
        return

    def create_user(self, name="", email="", password="", section="", role="", branch="",rollno=""):
        # Create a new user
        print("createuserfn")
        user = self.get_user_by_email(email)
        if user:
            return
        refresh_token = jwt.encode({
            'exp': datetime.utcnow() + timedelta(hours=2),
        },
            current_app.config["JWT_SECRET_KEY"],
            algorithm="HS256"
        )
        new_user = None
        if role == 'student':
            new_user = db.users.insert_one({
                "name": name,
                "email": email,
                "branch": branch,
                "section": section,
                "refresh_token": refresh_token,
                "password": self.encrypt_password(password),
                "not_password": password,
                "role": role,
                "active": True
            })
        if role == 'teacher':
            new_user = db.users.insert_one({
                "name": name,
                "email": email,
                "branch": branch,
                "section": "",
                "refresh_token": refresh_token,
                "password": self.encrypt_password(password),
                "not_password": password,
                "role": role,
                "active": True
            })
        if role == 'admin':
            new_user = db.users.insert_one({
                "name": name,
                "email": email,
                "refresh_token": refresh_token,
                "password": self.encrypt_password(password),
                "not_password": password,
                "role": role,
                "active": True
            })
        # print(new_user)
        return self.get_user_by_id(new_user.inserted_id)

    def get_all_users(self):
        # get all user
        users = db.users.find({"active": True})
        return [{**user, "_id": str(user["_id"])} for user in users]

    def get_all_users_by_section(self, section=""):
        # get all user
        users = db.users.find({"section": section, "active": True})
        return [{**user, "_id": str(user["_id"])} for user in users]

    def get_user_by_id(self, user_id):
        # get user by id
        user = db.users.find_one(
            {"_id": bson.ObjectId(user_id), "active": True})
        if not user:
            return
        user["_id"] = str(user["_id"])
        user.pop("password")
        return user

    def get_user_by_email(self, email):
        # Get a user by email
        user = db.users.find_one({"email": email, "active": True})
        if not user:
            return
        user["_id"] = str(user["_id"])
        return user

    def update(self, user_id, name="", email=None, section=None, role=None, branch=None):
        # update user
        data = {}
        user = db.users.find_one(
            {"_id": bson.ObjectId(user_id), "active": True})
        if name:
            data["name"] = name or user["name"]
            data["role"] = role or user["role"]
            data["email"] = email or user["email"]
            if role == 'teacher' or role == 'student' or role != None:
                data["branch"] = branch
            else:
                data["branch"] = user["branch"]
            if role == 'student' or role != None:
                data["section"] = section
            else:
                data["section"] = user["section"]
        user = db.users.update_one(
            {"_id": bson.ObjectId(user_id)},
            {
                "$set": data
            }
        )
        user = self.get_user_by_id(user_id)
        return user

    def delete(self, user_id):
        # Delete a user
        user = db.users.delete_one({"_id": bson.ObjectId(user_id)})
        user = self.get_user_by_id(user_id)
        return user

    def disable_account(self, user_id):
        # use this funtion to use block user to use account
        user = db.users.update_one(
            {"_id": bson.ObjectId(user_id)},
            {"$set": {"active": False}}
        )
        user = self.get_user_by_id(user_id)
        return user

    def encrypt_password(self, password):
        # Encrypt password
        return generate_password_hash(password)

    def changepassword(self, user_id, password=""):
        # reset password
        user = db.users.find_one(
            {"_id": bson.ObjectId(user_id), "active": True})
        if user:
            user["password"] = self.encrypt_password(password=password)
        user.pop("_id")
        user = db.users.update_one(
            {"_id": bson.ObjectId(user_id)},
            {
                "$set": user
            }
        )
        user = self.get_user_by_id(user_id)
        return user

    def login(self, email, password):
        # Login a user
        user = self.get_user_by_email(email)
        if not user or not check_password_hash(user["password"], password):
            return
        user.pop("password")
        return user

    def generate_qrcode(self, current_user="", token="", req=""):
        # print(current_user)
        data = "Hi this is bhargav & this is sample qrimg$&" + \
            current_user["_id"] + "$&" + \
            current_user["name"] + "$&" + req + "$&" + token
        img = qrcode.make(data)
        img_directory = os.path.join(os.getcwd(), "imgs")
        os.makedirs(img_directory, exist_ok=True)
        img_name = current_user["_id"] + "qrcode.png"
        img_path = os.path.join(img_directory, img_name)
        img.save(img_path)
        return img_name
    
    def get_user_email_from_device(self,request):
    # You may implement logic here to obtain the user's email from the device.
    # For example, if the email is stored in a cookie:
    # user_email = request.cookies.get('user_email')
    # Or if it's stored in a session:
    # user_email = request.session.get('user_email')

    # For this example, let's assume you retrieve the email from a request header
        user_email = request.headers.get('X-User-Email')

        return user_email
    
    
    def find_user_by_email(self, email):
        # Search for a user by email in the database
        user = db.users.find_one({"email": email, "active": True})
        if user:
            user["_id"] = str(user["_id"])
            # print(user,"user")
            return user
        else:
            return None


class Server:
    # server Model
    def __init__(self):
        return

    def get_server_ip(self):
        hostname = socket.gethostname()
        ip_address = socket.gethostbyname(hostname)
        return ip_address


class Classes:

    def __init__(self):
        self.client = MongoClient(DATABASE_URL)
        self.db = self.client.myDatabase
        return
    
    def get_all_classes_sorted_by_date(self):
        try:
            # Assuming you have a MongoDB collection called 'classes'
            # Replace 'your_database_name' and 'your_collection_name' with actual values
            db = self.client["myDatabase"]
            collection = db["classes"]

            # Fetch all classes sorted by 'created_date' in descending order (latest first)
            classes = collection.find().sort("created_date", DESCENDING)

            # Convert the cursor to a list of classes
            class_list = list(classes)

            return class_list
        except Exception as e:
            # Handle any exceptions or errors here
            print(f"Error in get_all_classes_sorted_by_date: {str(e)}")
            return []

    def generate_unique_qr_code(self, class_details):
        try:
            # Create a unique random name for the QR code image
            qr_code_name = str(uuid.uuid4()) + ".png"

            # Create a string that represents the class details
            class_info = f"Class: {class_details['class_name']}, Timings: {class_details['start_time']}-{class_details['end_time']}, Meet Link: {class_details['meet_link']},section: {class_details['section']},branch: {class_details['branch']}"
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(class_info)
            qr.make(fit=True)
            qr_img = qr.make_image(fill_color="black", back_color="white")
            qr_code_directory = "images/qr-code/"
            os.makedirs(qr_code_directory, exist_ok=True)
            qr_code_path = os.path.join(qr_code_directory, qr_code_name)
            qr_img.save(qr_code_path)

            return qr_code_path
        except Exception as e:
            print(f"Failed to generate QR code: {str(e)}")
            return None

    def store_class_in_database(self, user,class_details, qr_code_path):
        try:
            class_id = str(uuid.uuid4())
            start_time = datetime.strptime(class_details["start_time"], '%Y-%m-%dT%H:%M')
            end_time = datetime.strptime(class_details["end_time"], '%Y-%m-%dT%H:%M')
            class_data = {
                "_id": class_id,
                "class_name": class_details["class_name"],
                # "timings": class_details["start_time"]-class_details["end_time"],
                "created_date": datetime.now(),
                "start_time": start_time,
                "end_time": end_time,
                "meet_link": class_details["meet_link"],
                "qr_code_path": qr_code_path,
                "section": class_details["section"],
                "branch": class_details["branch"],
                'created_by':user["name"]
            }
            classes = db.classes.insert_one(class_data)
            return classes
        except Exception as e:
            print(f"Failed to store class data in the database: {str(e)}")
            return None
        
    def get_class_by_id(self, class_id):
        try:
            class_data = self.db.classes.find_one({"_id": class_id})
            if class_data:
                return {
                    "class_id": str(class_data["_id"]),
                    "qr_code_path": class_data["qr_code_path"],
                    # Include other class details as needed
                }
            else:
                return None
        except Exception as e:
            print(f"Failed to retrieve class data by ID: {str(e)}")
            return None
        
    def mark_user_as_present(self, class_id, user_id):
        try:
            attendance_data = {
                "class_id": class_id,
                "user_id": user_id,
                "timestamp": datetime.now()
            }
            db.attendance.insert_one(attendance_data)
            return True
        except Exception as e:
            current_app.logger.error(f"Failed to mark user as present: {str(e)}")
            return False
        
    def get_class_by_name(self, class_name):
        try:
            current_app.logger.info(class_name)
            # current_app.logger.info(f"Searching for class with name: {class_name}")
            # classes = db.classes.find()
            # current_app.logger.info(classes)
            class_data = db.classes.find_one({"class_name": class_name})
            # current_app.logger.info(class_data)
            current_app.logger.info(class_data)

            if class_data:
                return {
                    "class_id": str(class_data["_id"]),
                    "class_name": class_data["class_name"],
                    "start_time": class_data["start_time"],
                    "end_time": class_data["end_time"],
                    "meet_link": class_data["meet_link"],
                    "qr_code_path": class_data["qr_code_path"],
                    "section": class_data["section"],
                    "branch": class_data["branch"]
                }
            else:
                return None
        except Exception as e:
            current_app.logger.error(f"Failed to retrieve class by name: {str(e)}")
        return None
