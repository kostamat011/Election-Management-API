from flask import Flask, request, Response, jsonify;
from configuration import MyConfiguration

from models import database
from models import Participant
from models import Election
from models import ElectionParticipation
from models import Vote

from flask_jwt_extended import JWTManager, jwt_required;

from sqlalchemy import and_, or_, cast
from sqlalchemy import func

from roleGuard import roleGuard
import datetime
import pytz
import logging

from dateutil import parser

application = Flask(__name__)
application.config.from_object(MyConfiguration)

jwt = JWTManager(application)


#######################################################################################################################
# Create Participant
#
# JSON request:
# {
#     "name":"..."
#     "individual":"..."
# }
#
# JSON response:
# {
#     "id":1
# }

@application.route("/createParticipant", methods=["POST"])
@roleGuard("administrator")
def createParticipant():
    name = request.json.get("name", "")
    if len(name) == 0:
        return jsonify({'message': 'Field name is missing.'}), 400;

    individual = request.json.get("individual", None)
    if individual is None:
        return jsonify({'message': 'Field individual is missing.'}), 400;

    if len(name) > 256:
        return jsonify({'message': 'Field name is invalid.'}), 400;

    new_participant = Participant(name=name, individual=individual)
    database.session.add(new_participant)
    database.session.commit()

    return jsonify(id=new_participant.id), 200


#######################################################################################################################

#######################################################################################################################
# Get Participants
#
#
# JSON response:
# {
#     "participants":[{
#                  "id":1,
#                  "name":"...",
#                  "individual":true/false
#               }]
# }

@application.route("/getParticipants", methods=["GET"])
@roleGuard("administrator")
def getParticipants():
    all_participants = Participant.query.all()
    all_participants_json = []

    for p in all_participants:
        all_participants_json.append({
            "id": p.id,
            "name": p.name,
            "individual": p.individual
        })

    return jsonify(participants=all_participants_json), 200


#######################################################################################################################

#######################################################################################################################
# Create Elections

# JSON request:
# {
#     "start":"..."
#     "end":"..."
#     "individual":true/false
#     "participants:"[1,...]
# }
#
# JSON response:
# {
#     "pollNumbers":[1,...]
# }

@application.route("/createElection", methods=["POST"])
@roleGuard("administrator")
def createElection():
    # parse request data
    start_str = request.json.get("start", "")
    end_str = request.json.get("end", "")
    individual = request.json.get("individual", "None")
    participants = request.json.get("participants", "None")

    # check for missing fields
    if len(start_str) == 0:
        return jsonify(message='Field start is missing.'), 400
    if len(end_str) == 0:
        return jsonify(message='Field end is missing.'), 400
    if individual is None or not isinstance(individual, bool):
        return jsonify(message='Field individual is missing.'), 400
    if participants is None or not ("participants" in request.json):
        return jsonify(message='Field participants is missing.'), 400

    # check if datetime is in correct format ISO8601
    try:
        start_date = parser.parse(start_str)
        end_date = parser.parse(end_str)
    except:
        return jsonify(message='Invalid date and time.'), 400

    if end_date < start_date:
        return jsonify(message='Invalid date and time.'), 400

    # check if another election is in that time already
    all_elections = Election.query.all()
    for election in all_elections:
        curr_start_date = parser.parse(election.start)
        curr_end_date = parser.parse(election.end)
        if curr_start_date <= end_date and curr_end_date >= start_date:
            return jsonify(message='Invalid date and time.'), 400;

    # check if participant number is valid
    if len(participants) < 2:
        return jsonify(message='Invalid participants.'), 400

    # for each participant id in list check if that participant exists and if his individual matches election
    for participant_id in participants:
        participant = Participant.query.filter(Participant.id == participant_id).first()
        if participant is None:
            return jsonify(message='Invalid participants.'), 400
        if participant.individual != individual:
            return jsonify(message='Invalid participants.'), 400

    # save new electiond in DB
    new_election = Election(individual=individual, start=start_str, end=end_str, votesNum=0)
    database.session.add(new_election)
    database.session.commit()

    # save all participants in ElectionParticipation DB table
    pollNumber = 1
    pollNumberList = []
    for participant_id in participants:
        new_participation = ElectionParticipation(idParticipant=participant_id, idElection=new_election.id,
                                                  ord_number=pollNumber,
                                                  result=0)
        database.session.add(new_participation)
        database.session.commit()
        pollNumberList.append(pollNumber)
        pollNumber += 1

    return jsonify(pollNumbers=pollNumberList), 200


#######################################################################################################################

#######################################################################################################################
# JSON response:
# {
#     "elections":[{
#                  'id': 1,
#                  'start': "...",
#                  'end': "...",
#                  'individual': true/false,
#                  'participants': [{"id": 1, "name": "..."}]
#               }]
# }

@application.route("/getElections", methods=["GET"])
@roleGuard("administrator")
def getElections():
    all_elections = Election.query.all()
    all_elections_json = []

    for e in all_elections:
        all_elections_json.append({
            'id': e.id,
            'start': e.start,
            'end': e.end,
            'individual': e.individual,
            'participants': [{"id": participant.id, "name": participant.name} for participant in e.myParticipants]
        })

    return jsonify(elections=all_elections_json), 200


#######################################################################################################################


#######################################################################################################################
# JSON response:
# {
# "participants": [
#       {
#           "pollNumber": 1,
#           "name": ".....",
#           "result": 1
#       },
#       ......
#       ],
#  "invalidVotes": [
#       {
#           "electionOfficialJmbg": "....",
#           "ballotGuid": "....",
#           "pollNumber": 1,
#           "reason": "....."
#       },
#       .....
#       ]
# }

def calculateParliamentary(results, total_votes):
    print("total votes="+str(total_votes))
    mandates = 250
    threshold = 0.05

    # result_curr = number of votes participant received
    # result_final = number of mandates participant will receive
    # V = current number in D'Hondt method

    # check which participants crossed threshold
    participants_over = []
    for participant_res in results:
        if total_votes==0:
            participant_res["result_final"]=0
        else:
            if (participant_res["result_curr"] / total_votes) > threshold:
                participant_res["V"] = participant_res["result_curr"]
                participants_over.append(participant_res)
            else:
                participant_res["result_final"] = 0

    if total_votes==0:
        return

    while mandates > 0:
        # find current max V
        max_pos = -1;
        max_V = -1
        pos_cnt = 0
        for participant in participants_over:
            if participant["V"] > max_V:
                max_V = participant["V"]
                max_pos = pos_cnt
            pos_cnt += 1

        # current highest V gets next mandate
        # new V is calculated as number_of_votes/num_of_mandates+1

        participants_over[max_pos]["result_final"] += 1
        new_V = participants_over[max_pos]["result_curr"] / (participants_over[max_pos]["result_final"] + 1)
        participants_over[max_pos]["V"] = new_V

        # reduce number of left mandates
        mandates -= 1

    return


def calculatePresidential(results, total_votes):
    print("total votes=" + str(total_votes))
    # result_current = number of votes participant received
    # result_final = percentage of votes participant received 0-1

    for participant_res in results:
        if total_votes == 0:
            participant_res["result_final"] = 0
        else:
            participant_res["result_final"] = round(participant_res["result_curr"] / total_votes, 2)


@application.route("/getResults", methods=["GET"])
@roleGuard("administrator")
def getResults():
    # check if election id arg exist
    election_id = request.args.get("id", None)
    if election_id is None:
        return jsonify(message="Field id is missing."), 400

    # check if election id arg is a number
    try:
        election_id = int(election_id)
    except:
        return jsonify(message="Election does not exist."), 400

    # check if election id arg is valid
    election_exist = Election.query.filter(Election.id == election_id).count()
    if not election_exist:
        return jsonify(message="Election does not exist."), 400

    election = Election.query.filter(Election.id == election_id).first()

    # check if election is currently ongoing
    time_now = datetime.datetime.now().replace(microsecond=0) + datetime.timedelta(hours=2)
    election_end_time = parser.parse(election.end)
    if election_end_time > time_now:
        return jsonify(message="Election is ongoing."), 400

    # get data for all participants in this election
    election_results = ElectionParticipation.query.join(Participant).filter(
        ElectionParticipation.idElection == election.id) \
        .with_entities(ElectionParticipation.idParticipant, Participant.name,
                       ElectionParticipation.ord_number, ElectionParticipation.result).all()

    result_list = []
    for e in election_results:
        result_list.append({
            "poll_number": e.ord_number,
            "name": e.name,
            "result_curr": e.result,
            "V": 0,
            "result_final": 0
        })

    # calculate results of election
    if election.individual:
        calculatePresidential(result_list, election.votesNum)
    else:
        calculateParliamentary(result_list, election.votesNum)

    # format json response
    result_list_json = []
    for result in result_list:
        result_list_json.append({
            "pollNumber": result["poll_number"],
            "name": result["name"],
            "result": result["result_final"]
        })

    # get all invalid votes data
    invalid_votes_all = Vote.query.filter(and_(Vote.myElectionId == election.id, Vote.valid == False)).all()
    invalid_votes_json = []
    for i in invalid_votes_all:
        invalid_votes_json.append({
            'ballotGuid': i.guid,
            'electionOfficialJmbg': i.jmbg,
            'pollNumber': i.pollNumber,
            'reason': i.reason
        });

    return jsonify(participants=result_list_json, invalidVotes=invalid_votes_json)


#######################################################################################################################

#######################################################################################################################


#######################################################################################################################
@application.route("/", methods=["GET"])
def index():
    return "Administrator web service"


#######################################################################################################################


if (__name__ == "__main__"):
    database.init_app(application);
    application.run(host="0.0.0.0", port=5001);
