from flask import redirect, send_file, url_for
import datetime
import jwt
import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify
# from bson.objectid import ObjectId
from flask_cors import CORS
from flask_cors import cross_origin
from validate import validate_email_and_password, validate_user
from services import User, Server, Classes,db
from auth_middleware import jwttoken_required, role_required

load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})
# CORS(app)  
SECRET_KEY = os.environ.get('SECRET_KEY')
# print(SECRET_KEY)
app.config["JWT_SECRET_KEY"] = os.environ.get('JWT_SECRET_KEY')
app.config['SECRET_KEY'] = SECRET_KEY


@app.route("/")
def hello():
    return "Hello World!"

# Render the login form


# @app.route("/login", methods=["GET"])
# def login_form():
#     return render_template("login.html")

# Render the signup form


@app.route("/signup", methods=["GET"])
def signup_form():
    return render_template("signup.html")

# Render the dashboard with classes (replace with your logic)


# @app.route("/dashboard", methods=["GET"])
# def dashboard():
#     # Replace with logic to fetch user data and classes
#     user_data = {
#         "name": "John Doe",
#         "email": "john@example.com",
#         "role": "teacher"
#     }
#     classes = ["Class A", "Class B", "Class C"]
#     return render_template("dashboard.html", current_user=user_data, classes=classes)
@app.route("/dashboard", methods=["GET"])
def dashboard():
    try:
        # Retrieve the token from the query parameters
        token = request.args.get('token')

        # Verify the token
        try:
            decoded_token = jwt.decode(token, app.config["JWT_SECRET_KEY"], algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return jsonify({
                "message": "Token has expired",
                "error": "Unauthorized"
            }), 401
        except jwt.InvalidTokenError:
            return jsonify({
                "message": "Invalid token",
                "error": "Unauthorized"
            }), 401

        # Fetch user data based on the decoded token
        user = User().get_user_by_id(decoded_token["id"])

        if user:
            # Fetch and sort classes by creation date (latest first)
            # classes = Classes().get_all_classes_sorted_by_date()
            classes = list(db.classes.find({}))
            return render_template("dashboard.html", classes=classes, current_user=user)

        return jsonify({
            "message": "User not found",
            "error": "Unauthorized"
        }), 401

    except Exception as e:
        return jsonify({
            "message": "Something went wrong",
            "error": str(e),
            "data": None
        }), 500

# Render the logout page


@app.route("/logout", methods=["GET"])
def logout():
    return render_template("logout.html")


@app.route("/users", methods=["POST"])
# @jwttoken_required
# @role_required(allowed_roles=["admin"])
def add_user():
    try:
        print("adduser")
        # if current_user is None:
        #     return {
        #         "message": "Something went wrong && current_user is none",
        #         "error": str(e),
        #         "data": None
        #     }, 500
        user = request.json
        if not user:
            return {
                "message": "Please provide user details",
                "data": None,
                "error": "Bad request"
            }, 400
        is_validated = validate_user(**user)
        print("validate")
        if is_validated is not True:
            print("in validate")
            return dict(message='Invalid data', data=None, error=is_validated), 400
        user = User().create_user(**user)
        print("createuser")
        if not user:
            return {
                "message": "User already exists",
                "error": "Conflict",
                "data": None
            }, 409
        return {
            "message": "Successfully created new user",
            "data": user
        }, 200
    except Exception as e:
        return {
            "message": "Something went wrong",
            "error": str(e),
            "data": None
        }, 500


# @app.route("/login", methods=["POST"])
# def login():
#     try:
#         data = request.json
#         if not data:
#             return {
#                 "message": "Please provide user details",
#                 "data": None,
#                 "error": "Bad request"
#             }, 400
#         # validate input
#         is_validated = validate_email_and_password(
#             data.get('email'), data.get('password'))
#         if is_validated is not True:
#             return dict(message='Invalid data', data=None, error=is_validated), 400
#         user = User().login(
#             data["email"],
#             data["password"]
#         )
#         if user:
#             try:
#                 # print(user["_id"])
#                 payload = {
#                     'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=6),
#                     'id': user["_id"],
#                     'name': user["name"],
#                     'role': user["role"],
#                     'section': user.get("section", ""),
#                     'branch': user.get("branch", ""),
#                 }
#                 access_token = jwt.encode(
#                     payload,
#                     app.config["JWT_SECRET_KEY"],
#                     algorithm="HS256"
#                 )
#                 return {"access_token": access_token, 'id': user["_id"],
#                         'name': user["name"],
#                         'role': user["role"],
#                         'section': user["section"],
#                         'branch': user["branch"]}, 200

#             except Exception as e:
#                 return {
#                     "error": "Something went wrong",
#                     "message": str(e)
#                 }, 500
#         return {
#             "message": "Error fetching auth token!, invalid email or password",
#             "data": None,
#             "error": "Unauthorized"
#         }, 404
#     except Exception as e:
#         return {
#             "message": "Something went wrong!",
#             "error": str(e),
#             "data": None
#         }, 500
# Render the login form
@app.route("/login", methods=["GET"])
def login_form():
    return render_template("login.html")

# Handle login form submission
# Import the required modules
import jwt

# ...

@app.route("/login", methods=["POST"])
def login():
    try:
        data = request.json
        if not data:
            return jsonify({
                "message": "Please provide user details",
                "data": None,
                "error": "Bad request"
            }), 400

        # Validate input
        is_validated = validate_email_and_password(
            data.get('email'), data.get('password'))

        if is_validated is not True:
            return jsonify({
                "message": "Invalid email or password",
                "data": None,
                "error": "Unauthorized"
            }), 401

        user = User().login(data["email"], data["password"])
        if user:
            try:
                # Generate the JWT token
                payload = {
                    'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=6),
                    'id': user["_id"],
                    'name': user["name"],
                    'role': user["role"],
                    'section': user.get("section", ""),
                    'branch': user.get("branch", ""),
                }
                access_token = jwt.encode(
                    payload,
                    app.config["JWT_SECRET_KEY"],
                    algorithm="HS256"
                )

                return jsonify({
                    "access_token": access_token,
                    'id': user["_id"],
                    'name': user["name"],
                    'role': user["role"],
                    'section': user["section"],
                    'branch': user["branch"]
                }), 200

            except Exception as e:
                return jsonify({
                    "message": "Something went wrong",
                    "error": str(e),
                    "data": None
                }), 500
        else:
            return jsonify({
                "message": "Invalid email or password",
                "data": None,
                "error": "Unauthorized"
            }), 401

    except Exception as e:
        return jsonify({
            "message": "Something went wrong",
            "error": str(e),
            "data": None
        }), 500


# @app.route("/login", methods=["POST"])
# @cross_origin(supports_credentials=True)
# def login():
#     try:
#         data = request.json
#         if not data:
#             return jsonify({
#                 "message": "Please provide user details",
#                 "data": None,
#                 "error": "Bad request"
#             }), 400

#         # validate input
#         is_validated = validate_email_and_password(
#             data.get('email'), data.get('password'))

#         if is_validated is not True:
#             return jsonify({
#                 "message": "Invalid email or password",
#                 "data": None,
#                 "error": "Unauthorized"
#             }), 401

#         user = User().login(data["email"], data["password"])
#         if user:
#             try:
#                 # Generate the JWT token
#                 payload = {
#                     'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=6),
#                     'id': user["_id"],
#                     'name': user["name"],
#                     'role': user["role"],
#                     'section': user.get("section", ""),
#                     'branch': user.get("branch", ""),
#                 }
#                 access_token = jwt.encode(
#                     payload,
#                     app.config["JWT_SECRET_KEY"],
#                     algorithm="HS256"
#                 )

#                 # Set the token as a cookie in the response
#                 response = jsonify({
#                     "access_token": access_token,
#                     'id': user["_id"],
#                     'name': user["name"],
#                     'role': user["role"],
#                     'section': user["section"],
#                     'branch': user["branch"]
#                 })
                
#                 # Set the access token as a cookie with HttpOnly and Secure flags
#                 response.set_cookie('access_token', access_token, httponly=True, secure=True)
                
#                 return response, 200

#             except Exception as e:
#                 return jsonify({
#                     "message": "Something went wrong",
#                     "error": str(e),
#                     "data": None
#                 }), 500
#         else:
#             return jsonify({
#                 "message": "Invalid email or password",
#                 "data": None,
#                 "error": "Unauthorized"
#             }), 401

#     except Exception as e:
#         return jsonify({
#             "message": "Something went wrong",
#             "error": str(e),
#             "data": None
#         }), 500
# def login():
#     try:
#         data = request.json
#         if not data:
#             return jsonify({
#                 "message": "Please provide user details",
#                 "data": None,
#                 "error": "Bad request"
#             }), 400

#         # Validate input (you can keep this part)
#         is_validated = validate_email_and_password(
#             data.get('email'), data.get('password'))

#         if is_validated is not True:
#             return jsonify({
#                 "message": "Invalid email or password",
#                 "data": None,
#                 "error": "Unauthorized"
#             }), 401

#         user = User().login(data["email"], data["password"])
#         if user:
#             try:
#                 # Generate the JWT token
#                 payload = {
#                     'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=6),
#                     'id': user["_id"],
#                     'name': user["name"],
#                     'role': user["role"],
#                     'section': user.get("section", ""),
#                     'branch': user.get("branch", ""),
#                 }
#                 access_token = jwt.encode(
#                     payload,
#                     app.config["JWT_SECRET_KEY"],
#                     algorithm="HS256"
#                 )

#                 # Redirect to the dashboard route with the token as a query parameter
#                 return redirect(url_for('dashboard', token=access_token))

#             except Exception as e:
#                 return jsonify({
#                     "message": "Something went wrong",
#                     "error": str(e),
#                     "data": None
#                 }), 500
#         else:
#             return jsonify({
#                 "message": "Invalid email or password",
#                 "data": None,
#                 "error": "Unauthorized"
#             }), 401

#     except Exception as e:
#         return jsonify({
#             "message": "Something went wrong",
#             "error": str(e),
#             "data": None
#         }), 500
# it will take the section argument ex: /sectionusers?section="cse-e"
@app.route("/sectionusers", methods=["GET"])
@jwttoken_required
@role_required(allowed_roles=["admin", "teacher"])
def get_section_user(current_user):
    try:
        data = request.args.get('section')
        users = User().get_all_users_by_section(data)
        return jsonify({
            "message": "successfully retrieved section users",
            "data": users,
            "current_user": current_user
        }), 200
    except Exception as e:
        return jsonify({
            "message": "failed to get users",
            "error": str(e),
            "data": None
        }), 400


@app.route("/user", methods=["GET"])
@jwttoken_required
@role_required(allowed_roles=["admin", "teacher", "student"])
def get_current_user(current_user):
    return jsonify({
        "message": "successfully retrieved user profile",
        "data": current_user
    }), 200


@app.route("/qrcode", methods=["GET"])
@jwttoken_required
@role_required(allowed_roles=["admin", "teacher"])
def qr_generate(current_user):
    payload = {
        'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=10),
        'user_id': current_user["_id"],
        'name': current_user["name"]
    }
    token = jwt.encode(
        payload, app.config["JWT_SECRET_KEY"], algorithm="HS256")
    img = User().generate_qrcode(current_user=current_user, token=token)

    img_url = f"http://{Server().get_server_ip()}:{5000}/imgs/{img}"
    return jsonify({
        "message": "Successfully generated QR code",
        "img_url": img_url
    }), 200


@app.route("/allusers", methods=["GET"])
@jwttoken_required
@role_required(allowed_roles=["admin", "teacher"])
def get_current_users(current_user):
    users = User().get_all_users()
    # app.logger.info('%s logged in successfully',users)
    return jsonify({
        "message": "successfully retrieved users",
        "data": users
    }), 200


@app.route("/users", methods=["PUT"])
@jwttoken_required
@role_required(allowed_roles=["admin"])
def update_user(current_user):
    try:
        user = request.json
        if user.get("name"):
            user = User().update(
                current_user["_id"],
                user["name"],
                user.get("email"),
                user.get("section"),
                user.get("role"),
                user.get("branch")
            )
            return jsonify({
                "message": "successfully updated account",
                "data": user
            }), 200
        return {
            "message": "Invalid data, you can only update your account name and section!",
            "data": None,
            "error": "Bad Request"
        }, 400
    except Exception as e:
        return jsonify({
            "message": "failed to update account",
            "error": str(e),
            "data": None
        }), 400


@app.route("/changepwd", methods=["PUT"])
@jwttoken_required
@role_required(allowed_roles=["admin"])
def changepassword(current_user):
    try:
        data = request.json
        user = User().changepassword(current_user["_id"], data["password"])
        return jsonify({
            "message": "successfully updated password",
            "data": user
        }), 200
    except Exception as e:
        return jsonify({
            "message": "failed to reset password",
            "error": str(e),
            "data": None
        }), 400

# Teacher creates a class and generates a QR code


@app.route("/create_class", methods=["POST"])
@jwttoken_required  # Ensure only teachers can create classes
@role_required(allowed_roles=["teacher"])
def create_class(current_user):
    try:
        # Check for timing conflicts with existing classes
        class_details = request.json
        start_time = datetime.strptime(class_details["start_time"], '%Y-%m-%dT%H:%M')
        end_time = datetime.strptime(class_details["end_time"], '%Y-%m-%dT%H:%M')

        conflicts = db.classes.find({
            "$or": [
                {"start_time": {"$lte": start_time}, "end_time": {"$gte": start_time}},
                {"start_time": {"$lte": end_time}, "end_time": {"$gte": end_time}},
                {"start_time": {"$gte": start_time}, "end_time": {"$lte": end_time}},
            ]
        })

        if conflicts.count() > 0:
            # Timing conflict exists, return an alert
            return jsonify({"error": "A class with conflicting timings already exists."})

        # Generate a unique QR code with class details and a random name
        qr_code_path = Classes().generate_unique_qr_code(class_details)

        # Store class details and QR code path in the database
        Classes().store_class_in_database(class_details, qr_code_path)

        return jsonify({
            "message": "Class created successfully",
            "qr_code_path": qr_code_path  # Provide the path to the QR code image to the teacher
        }), 200
    except Exception as e:
        return jsonify({
            "message": "Failed to create class",
            "error": str(e),
            "data": None
        }), 500


# @app.route("/qr-code/<path:image_name>", methods=["GET"])
# def serve_qr_code_image(image_name):
#     try:
#         # Define the directory where QR code images are stored
#         # qr_code_directory = "images/qr-code/"
#         qr_code_directory = "/Users/ch.sarun/Documents/MyCodes/Code/Projects/attendence/server/images/qr-code/"

#         # Define the complete path to the requested QR code image
#         qr_code_path = os.path.join(qr_code_directory, image_name)

#         # Serve the QR code image using Flask's send_file
#         return send_file(qr_code_path, mimetype='image/png')
#     except Exception as e:
#         # Handle any errors that may occur when serving the image
#         return jsonify({
#             "message": "Failed to serve QR code image",
#             "error": str(e),
#             "data": None
#         }), 500

# Sample code for students to join a class using a QR code


@app.route("/join_class", methods=["POST"])
# def join_class():
#     try:
#         qr_code_data = request.json.get("qr_code_data")

#         # Verify the student's identity based on QR code data
#         class_details = Classes().verify_qr_code_data(qr_code_data)

#         if class_details:
#             # Implement logic to add the student to the class

#             # Fetch the QR code image for display
#             qr_code_image_path = fetch_qr_code_image(
#                 class_details['qr_code_path'])

#             return jsonify({
#                 "message": "Student joined the class",
#                 "class_details": class_details,
#                 "qr_code_image_path": qr_code_image_path
#             }), 200
#         else:
#             return jsonify({
#                 "message": "Invalid QR code",
#                 "data": None,
#                 "error": "Unauthorized"
#             }), 401
#     except Exception as e:
#         return jsonify({
#             "message": "Failed to join class",
#             "error": str(e),
#             "data": None
#         }), 500
@app.route("/join_class/<string:class_id>", methods=["POST"])
# def join_class(class_id):
#     try:
#         # Get the class details based on the class ID
#         class_details = Classes().get_class_by_id(class_id)

#         if class_details:
#             # Extract the user's email from the device (replace with your method)
#             # user_email = User().get_user_email_from_device(request)
#             user_email = "teacher@gmail.com"

#             # Check if the user's email exists in the user collection
#             user = User().find_user_by_email(user_email)
#             # user = "teacher@gmail.com"
#             if user:
#                 # Implement logic to mark the user as present in a new collection
#                 Classes().mark_user_as_present(class_id, user["_id"])

#                 # Fetch the QR code image for display
#                 qr_code_image_path = fetch_qr_code_image(class_details['qr_code_path'])

#                 return jsonify({
#                     "message": "Student joined the class",
#                     "class_details": class_details,
#                     "user_email": user_email,  # Include the user's email
#                     "qr_code_image_path": qr_code_image_path
#                 }), 200
#             else:
#                 return jsonify({
#                     "message": "User with email not found",
#                     "data": None,
#                     "error": "Unauthorized"
#                 }), 401
#         else:
#             return jsonify({
#                 "message": "Invalid class ID",
#                 "data": None,
#                 "error": "Not Found"
#             }), 404
#     except Exception as e:
#         return jsonify({
#             "message": "Failed to join class",
#             "error": str(e),
#             "data": None
#         }), 500
# def join_class():
#     try:
#         # Get the class details based on the class name
#         data = request.json
#         class_name = data.get('class_name')
#         print(class_name)
#         class_details = Classes().get_class_by_name(class_name)
#         print(class_details)
#         if class_details:
#             # Extract the user's email from the device (replace with your method)
#             # user_email = User().get_user_email_from_device(request)
#             user_email = "ch.sarun0904@gmail.com"  # Replace with the student's email

#             # Check if the user's email exists in the user collection
#             user = User().find_user_by_email(user_email)
#             print(user,"ejhrgbkrjgnerwkgnk")

#             if user:
#                 # Implement logic to mark the user as present in a new collection
#                 print("panduuuuuuuuuuu")
#                 class_id=class_details["_id"]
#                 user_id=user["_id"]
#                 print(class_id,user_id ," fjhsbgvjhb")
#                 Classes().mark_user_as_present(class_details["_id"], user["_id"])

#                 # Fetch the QR code image for display
#                 qr_code_image_path = fetch_qr_code_image(class_details['qr_code_path'])
#                 print(qr_code_image_path)

#                 return jsonify({
#                     "message": "Student joined the class",
#                     "class_details": class_details,
#                     "user_email": user_email,  # Include the user's email
#                     "qr_code_image_path": qr_code_image_path
#                 }), 200
#             else:
#                 return jsonify({
#                     "message": "User with email not found",
#                     "data": None,
#                     "error": "Unauthorized"
#                 }), 401
#         else:
#             return jsonify({
#                 "message": "Class with the specified name not found",
#                 "data": None,
#                 "error": "Not Found"
#             }), 404
#     except Exception as e:
#         return jsonify({
#             "message": "Failed to join class",
#             "error": str(e),
#             "data": None
#         }), 500

def join_class():
    try:
        # Get the class details based on the class name
        data = request.json
        class_name = data.get('class_name')
        print(class_name)
        class_details = Classes().get_class_by_name(class_name)
        print(class_details)
        if class_details:
            # Extract the user's email from the device (replace with your method)
            user_email = "ch.sarun0904@gmail.com"  # Replace with the student's email

            # Check if the user's email exists in the user collection
            user = User().find_user_by_email(user_email)
            print(user, "ejhrgbkrjgnerwkgnk")

            if user:
                # Implement logic to mark the user as present in a new collection
                print("panduuuuuuuuuuu")
                # Assuming that class_details and user objects have different structures
                class_id = class_details.get("_id")  # Access class_id based on its actual structure
                user_id = user.get("_id")  # Access user_id based on its actual structure
                print(class_id, user_id, " fjhsbgvjhb")
                Classes().mark_user_as_present(class_id, user_id)

                # Fetch the QR code image for display
                qr_code_image_path = fetch_qr_code_image(class_details['qr_code_path'])
                print(qr_code_image_path)

                return jsonify({
                    "message": "Student joined the class",
                    "class_details": class_details,
                    "user_email": user_email,
                    "qr_code_image_path": qr_code_image_path
                }), 200
            else:
                return jsonify({
                    "message": "User with email not found",
                    "data": None,
                    "error": "Unauthorized"
                }), 401
        else:
            return jsonify({
                "message": "Class with the specified name not found",
                "data": None,
                "error": "Not Found"
            }), 404
    except Exception as e:
        return jsonify({
            "message": "Failed to join class",
            "error": str(e),
            "data": None
        }), 500

# Function to fetch the QR code image based on the image path
@app.route("/qrcode/<image_name>", methods=["GET"])
def serve_qr_code_image(image_name):
    try:
        # Define the directory where QR code images are stored
        qr_code_directory = "/Users/ch.sarun/Documents/MyCodes/Code/Projects/AttendanceBackEnd/images/qr-code/"

        # Define the complete path to the requested QR code image
        qr_code_path = os.path.join(qr_code_directory, image_name)

        # Serve the QR code image using Flask's send_file
        return send_file(qr_code_path, mimetype='image/png')
    except Exception as e:
        # Handle any errors that may occur when serving the image
        return jsonify({
            "message": "Failed to serve QR code image",
            "error": str(e),
            "data": None
        }), 500

def fetch_qr_code_image(image_path):
    try:
        # Serve the QR code image using Flask's send_file
        return send_file(image_path, mimetype='image/png')
    except Exception as e:
        # Handle any errors that may occur when fetching the image
        return None


@app.errorhandler(403)
def forbidden(e):
    return jsonify({
        "message": "Forbidden",
        "error": str(e),
        "data": None
    }), 403


@app.errorhandler(404)
def forbidden(e):
    return jsonify({
        "message": "Endpoint Not Found",
        "error": str(e),
        "data": None
    }), 404


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=4000)
