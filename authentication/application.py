from flask import Flask, request, Response, jsonify
from configuration import MyConfiguration
from flask_jwt_extended import JWTManager, create_access_token, create_refresh_token, get_jwt, get_jwt_identity, \
    jwt_required
from re import match, search
from models import User, Role, database
from sqlalchemy import and_
from roleGuard import roleGuard


application = Flask(__name__)
application.config.from_object(MyConfiguration);
jwtManager = JWTManager(application)


#######################################################################################################################
# Register
#
# JSON request:
# {
#     "jmbg":"..."
#     "forename":"..."
#     "surname":"..."
#     "email":"..."
#     "password":"..."
# }
#
# Response: status 200 on success
#
# JSON response on failure:
# {
#     "message":"..."
# }

@application.route("/register", methods=["POST"])
def register():
    try:
        request_data= {'jmbg': request.json.get("jmbg", ""), 'forename': request.json.get("forename", ""),
                    'surname': request.json.get("surname", ""), 'email': request.json.get("email", ""),
                    'password': request.json.get("password", "")}
    except:
        return jsonify({'message': 'Field jmbg is missing.'}), 400


    if len(request_data['jmbg']) == 0:
         return jsonify({'message': 'Field jmbg is missing.'}), 400
    if len(request_data['forename']) == 0:
         return jsonify({'message':'Field forename is missing.'}), 400
    if len(request_data['surname']) == 0:
        return jsonify({'message': 'Field surname is missing.'}), 400
    if len(request_data['email']) == 0:
        return jsonify({'message': 'Field email is missing.'}), 400
    if len(request_data['password']) == 0:
        return jsonify({'message': 'Field password is missing.'}), 400

    if not checkJMBG(request_data['jmbg']):
        return jsonify({'message': 'Invalid jmbg.'}), 400

    if not checkEmail(request_data['email']):
        return jsonify({'message': 'Invalid email.'}), 400

    if not checkPassword(request_data['password']):
        return jsonify({'message': 'Invalid password.'}), 400

    # check ih email is already in the DB
    if (User.query.filter(User.email == request_data['email']).first() is not None):
        return jsonify({'message': 'Email already exists.'}), 400


    my_role = Role.query.filter(Role.name == 'zvanicnik').first()

    try:
        user = User(jmbg=request_data['jmbg'], forename=request_data['forename'],
                    surname=request_data['surname'], email=request_data['email'],
                    password=request_data['password'], idRole=my_role.id)
        database.session.add(user)
        database.session.commit()
    except Exception as e:
        print(e)
        return jsonify({'message': 'Jmbg already exists.'}), 400;

    return Response(status=200)
#######################################################################################################################

#######################################################################################################################
# Login
#
# JSON request:
# {
#     "email":"..."
#     "password":"..."
# }
#
# JSON response on success:
# {
#     "access_token":"..."
#     "refresh_token":"..."
# }
#
# JSON response on failure:
# {
#     "message":"..."
# }

@application.route("/login", methods=["POST"])
def login():
    try:
        request_data = {'email': request.json.get("email", ""), 'password': request.json.get("password", "")}
    except:
        return jsonify({'message': 'Field email is missing.'}), 400;

    if len(request_data['email']) == 0:
        return jsonify({'message': 'Field email is missing.'}), 400
    if len(request_data['password']) == 0:
        return jsonify({'message': 'Field password is missing.'}), 400

    if not checkEmail(request_data['email']):
        return jsonify({'message': 'Invalid email.'}), 400

    user = User.query.filter(and_(User.email == request_data['email'], User.password == request_data['password'])).first()
    if user is None:
        return jsonify({'message': 'Invalid credentials.'}), 400

    additional = {
        "jmbg": user.jmbg,
        "forename": user.forename,
        "surname": user.surname,
        "role": str(user.myRole)
    }

    access_token = create_access_token(identity=user.email,additional_claims=additional)
    refresh_token = create_refresh_token(identity=user.email,additional_claims=additional)

    return jsonify(accessToken=access_token, refreshToken=refresh_token),200
#######################################################################################################################

#######################################################################################################################
# Refresh
#
# Authorization header must contain JWT token with refresh type
#
# JSON response on success:
# {
#     "access_token":"..."
# }
#

@application.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()
    refresh = get_jwt()

    additional = {
        "jmbg":refresh["jmbg"],
        "forename": refresh["forename"],
        "surname": refresh["surname"],
        "role": refresh["role"]
    }

    access_token = create_access_token(identity=identity,additional_claims=additional)

    return jsonify(accessToken=access_token)
#######################################################################################################################

#######################################################################################################################
# Delete participant
# Administrator access only

# JSON request:
# {
#     "email":"..."
# }
#
# Response: status 200 on success
#
# JSON response on failure:
# {
#     "message":"..."
# }

@application.route("/delete",methods=["POST"])
@roleGuard("administrator")
def delete():
    try:
        email_to_delete = request.json.get("email","")
    except:
        return jsonify({"message":"Field email is missing."}),400

    if len(email_to_delete) == 0:
        return jsonify({"message": "Field email is missing."}), 400
    if  not checkEmail(email_to_delete):
        return jsonify({"message": "Invalid email."}), 400

    user_to_delete = User.query.filter(User.email==email_to_delete).one_or_none()
    if user_to_delete is None:
        return jsonify({"message": "Unknown user."}), 400

    database.session.delete(user_to_delete)
    database.session.commit()
    return Response(status=200)
#######################################################################################################################

#######################################################################################################################
# JWT check
@application.route("/check", methods=["POST"])
@jwt_required()
def check():
    return "Token is valid.";
#######################################################################################################################


#######################################################################################################################
# Index page
@application.route("/", methods=["GET"])
def index():
    return "Authentication web service"
#######################################################################################################################

#######################################################################################################################
# utility functions

def checkJMBG(arg):
    if match('^[0-9]{13}$', arg) == None:
        return False

    d = int(arg[0:2]);
    m = int(arg[2:4]);
    y = int(arg[4:7]);

    leap = False;
    if (y % 4) == 0:
        if not (((y % 100) == 0) and ((y % 400) == 0)):
            leap = True

    if (m in [1, 3, 5, 7, 8, 10, 12]) and d > 31:
        return False;
    elif (m in [4, 6, 9, 11]) and d > 30:
        return False;
    elif (m == 2 and leap and d > 29) or (m == 2 and not leap and d > 28):
        return False;

    regionNum = int(arg[7:9]);
    if regionNum < 70 or regionNum > 99:
        return False;

    controlNum = int(arg[12:13]);
    m = 11 - (7 * (int(arg[0]) + int(arg[6])) + 6 * (int(arg[1]) + int(arg[7])) + 5 * (int(arg[2]) + int(arg[8]))
              + 4 * (int(arg[3]) + int(arg[9])) + 3 * (int(arg[4]) + int(arg[10])) + 2 * (
                      int(arg[5]) + int(arg[11]))) % 11;
    k = m;
    if m > 9:
        k = 0;
    if k != controlNum:
        return False;

    return True;


def checkEmail(arg):
    if len(arg) > 256:
        return False
    if match('[^@]+@.*\.[a-z]{2,}$', arg) is not None:
        return True


def checkPassword(arg):
    if len(arg) < 8:
        return False
    if len(arg) > 256:
        return False
    if search('[A-Z]', arg) is None:
        return False
    if search('[a-z]', arg) is None:
        return False
    if search('[0-9]', arg) is None:
        return False

    return True
#######################################################################################################################

if (__name__ == "__main__"):
    database.init_app(application);
    application.run(host="0.0.0.0", port=5003);
