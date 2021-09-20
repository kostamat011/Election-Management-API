from flask import *
from flask_jwt_extended import JWTManager, get_jwt
from configuration import MyConfiguration
from roleGuard import roleGuard
from redis import Redis
from datetime import datetime, timezone, timedelta
import csv
import io
import pytz

application = Flask(__name__)
application.config.from_object(MyConfiguration)
jwt = JWTManager(application)

#######################################################################################################################
# Vote
# Access only for voting official
#
# Form data must include CSV file with votes with key 'file'
#
#
# Response: status 200 on success
#
# JSON response on failure:
# {
#     "message":"..."
# }
@application.route("/vote", methods=["POST"])
@roleGuard("zvanicnik")
def vote():
    filename = request.files.get("file", None)
    if (filename is None) or ("file" not in request.files):
        return jsonify(message='Field file is missing.'), 400

    #2 hours difference is for testing
    current_time = pytz.utc.localize(datetime.utcnow()+timedelta(hours=2))

    #read file
    file_content = filename.stream.read().decode("utf-8")
    file_reader = csv.reader(io.StringIO(file_content))
    line_cnt = 0

    # line[0] = guid of voting paper
    # line[1] = poll number
    # check if file is valid
    for line in file_reader:
        if len(line) != 2:
            return jsonify(message="Incorrect number of values on line " + str(line_cnt) + "."), 400

        if (not line[1].isnumeric()) or (int(line[1]) < 0):
            return jsonify(message="Incorrect poll number on line " + str(line_cnt) + "."), 400

        line_cnt += 1

    # file is valid, push votes to redis
    file_reader = csv.reader(io.StringIO(file_content))
    official_jmbg = get_jwt().get("jmbg", None)

    # format guid$pollNumber$datetime$jmbg
    for line in file_reader:
        redis = Redis(host=MyConfiguration.REDIS_HOST)
        redis.rpush(MyConfiguration.REDIS_VOTES, line[0] + "$" + line[1] + "$" + \
                    datetime.strftime(current_time, "%Y-%m-%dT%H:%M:%S%z") + "$" + official_jmbg)

    return Response(status=200)

#######################################################################################################################
# Index page
@application.route("/", methods=["GET"])
def index():
    return "Voting official web service"
#######################################################################################################################

if __name__ == "__main__":
    application.run(host="0.0.0.0", port=5002)
