from datetime import datetime

import pytz
from redis import Redis
from sqlalchemy import create_engine, and_
from sqlalchemy.orm import sessionmaker

from configuration import MyConfiguration
from models import Election, Vote, Participant, ElectionParticipation
from dateutil import parser

engine = create_engine(MyConfiguration.SQLALCHEMY_DATABASE_URI, echo=False)
Session = sessionmaker(bind=engine)
dameon_session = Session()

while True:
    try:
        with Redis(host=MyConfiguration.REDIS_HOST) as redis:
            while True:

                # check if next vote exist
                while True:
                    next = redis.lrange(MyConfiguration.REDIS_VOTES,0,0)
                    if len(next)==0:
                        continue

                    # read vote data
                    next_content = redis.lpop(MyConfiguration.REDIS_VOTES)
                    data = next_content.decode("utf-8").split("$")
                    vote_guid = data[0]
                    poll_number = int(data[1])
                    time = datetime.strptime(data[2], "%Y-%m-%dT%H:%M:%S%z")
                    official_jmbg = data[3]

                    # check if there is active election
                    all_elections = dameon_session.query(Election).all()
                    active_election = None
                    for election in all_elections:
                        curr_start_date = parser.parse(election.start)
                        curr_start_date = pytz.UTC.localize(curr_start_date)
                        curr_end_date = parser.parse(election.end)
                        curr_end_date = pytz.UTC.localize(curr_end_date)
                        print("election start"+str(curr_start_date))
                        print("election end"+str(curr_end_date))
                        print("vote time"+str(time))
                        if curr_start_date <= time <= curr_end_date:
                            active_election = election
                            break
                    # vote is cast for no active election, skip
                    if active_election is None:
                        continue


                    guid_exist = dameon_session.query(Vote).filter(Vote.guid==vote_guid).count()!=0

                    # invalid vote because double ballot, voteNum is not incremented
                    if guid_exist:
                        new_vote = Vote(guid=vote_guid,myElectionId=active_election.id,\
                                        pollNumber=poll_number,jmbg=official_jmbg,valid=False,\
                                        reason="Duplicate ballot.")
                        dameon_session.add(new_vote)
                        dameon_session.commit()
                        continue



                    participant = dameon_session.query(ElectionParticipation).filter(and_(\
                        ElectionParticipation.idElection==active_election.id,\
                        ElectionParticipation.ord_number==poll_number)).first()

                    # invalid vote because of pollNumber, voteNum is incremented
                    if participant is None:
                        new_vote = Vote(guid=vote_guid, myElectionId=active_election.id, \
                                        pollNumber=poll_number, jmbg=official_jmbg, valid=False,
                                        reason="Invalid poll number.")
                        dameon_session.query(Election).filter(Election.id == active_election.id) \
                            .update({'votesNum': Election.votesNum + 1});
                        dameon_session.add(new_vote)
                        dameon_session.commit()
                        continue


                    # valid vote
                    participation = dameon_session.query(ElectionParticipation).filter(and_( \
                        ElectionParticipation.idElection == active_election.id, \
                        ElectionParticipation.idParticipant == participant.idParticipant)).first()

                    new_vote = Vote(guid=vote_guid, myElectionId=active_election.id, \
                                    pollNumber=poll_number, jmbg=official_jmbg, valid=True)

                    #increment result of this participant
                    dameon_session.query(ElectionParticipation).filter(and_(
                        ElectionParticipation.idElection == active_election.id,
                        ElectionParticipation.idParticipant == participation.idParticipant
                    )).update({'result': participation.result + 1})

                    #increment number of total votes
                    dameon_session.query(Election).filter(Election.id == active_election.id) \
                        .update({'votesNum': Election.votesNum + 1})

                    dameon_session.add(new_vote)
                    dameon_session.commit()
    except Exception as err:
        print(err)







