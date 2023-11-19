from flask import redirect, send_file, url_for
import datetime
import jwt
import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from flask_cors import cross_origin
from validate import validate_email_and_password, validate_user
from services import User, Server, Classes,db
from auth_middleware import jwttoken_required, role_required
from flask import redirect

load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": ["http://localhost:4004", "http://192.168.77.62:4004"]}})

# CORS(app, resources={r"/*": {"origins": "http://localhost:4004"}})
# CORS(app) 

SECRET_KEY = os.environ.get('SECRET_KEY')
app.config["JWT_SECRET_KEY"] = os.environ.get('JWT_SECRET_KEY')
app.config['SECRET_KEY'] = SECRET_KEY


@app.route("/")
def hello():
    return render_template("home.html")

@app.route("/signup", methods=["GET"])
def signup_form():
    return render_template("signup.html")

@app.route("/dashboard", methods=["GET"])
def dashboard():
    try:
        token = request.args.get('token')
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
        user = User().get_user_by_id(decoded_token["id"])

        if user:
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

@app.route("/logout", methods=["GET"])
def logout():
    return redirect("/")


@app.route("/users", methods=["POST"])
# @jwttoken_required
# @role_required(allowed_roles=["admin"])
def add_user():
    try:
        print("adduser")
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
                "message": "User email or name already exists",
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
@app.route("/login", methods=["GET"])
def login_form():
    return render_template("login.html")

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
                    'email': user["email"],
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

@app.route("/create_class", methods=["POST"])
@jwttoken_required
@role_required(allowed_roles=["teacher"])
def create_class(current_user):
    try:
        class_details = request.json
        start_time = datetime.datetime.strptime(class_details["start_time"], '%Y-%m-%dT%H:%M')
        end_time = datetime.datetime.strptime(class_details["end_time"], '%Y-%m-%dT%H:%M')

        conflicts = db.classes.count_documents({
            "$or": [
                {"start_time": {"$lte": start_time}, "end_time": {"$gte": start_time}},
                {"start_time": {"$lte": end_time}, "end_time": {"$gte": end_time}},
                {"start_time": {"$gte": start_time}, "end_time": {"$lte": end_time}},
            ]
        })

        if conflicts > 0:
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
@app.route("/join_class", methods=["POST"])
@jwttoken_required
@role_required(allowed_roles=["student"])
def join_class(current_user):
    try:
        data = request.json
        token = token = request.headers["Authorization"].split(" ")[1]
        class_name = data.get('class_name')
        user_email = extract_email_from_token(token, app.config["JWT_SECRET_KEY"])
        # app.logger.info(f"Class Name: {class_name}")

        class_details = Classes().get_class_by_name(class_name)
        user = User().find_user_by_email(user_email)
        print(class_details, user, "ejhrgbkrjgnerwkgnk")
        if class_details:
            meet_link = class_details.get('meet_link')
            user_id = user.get("_id")  # Access user_id based on its actual structure
            class_id = class_details.get("class_id")  # Access class_id based on its actual structure
            user_id = user.get("_id")
            Classes().mark_user_as_present(class_id, user_id)
            if meet_link:
                return jsonify({
                    "message": "User marked as present in the class",
                    "meeting_link": meet_link
                }), 200
            return jsonify({
                "message": "Meeting link not found in class details",
                "error": "Not Found"
            }), 404
        else:
            return jsonify({
                "message": "Class with the specified name not found",
                "error": "Not Found"
            }), 404
    except Exception as e:
        return jsonify({
            "message": "Failed to join class",
            "error": str(e)
        }), 500

def extract_email_from_token(token, secret_key):
    try:
        # Decode the token to access its payload
        decoded_payload = jwt.decode(token, secret_key, algorithms=["HS256"])
        # Extract the email from the payload
        user_email = decoded_payload.get("email")
        return user_email
    except jwt.ExpiredSignatureError:
        # Handle token expiration
        return None
    except jwt.DecodeError:
        # Handle token decoding errors
        return None

# Function to fetch the QR code image based on the image path
@app.route("/qrcode/<image_name>", methods=["GET"])
def serve_qr_code_image(image_name):
    try:
        # Define the directory where QR code images are stored
        qr_code_directory = os.environ.get("QR_CODE_DIRECTORY")

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
    app.run(debug=True, host='0.0.0.0', port=4004)
