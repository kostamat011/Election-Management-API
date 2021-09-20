from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKeyConstraint


database = SQLAlchemy()


class ElectionParticipation(database.Model):
    __tablename__ = "ElectionParticipation"

    idParticipant = database.Column(database.Integer, database.ForeignKey("Participant.id"), primary_key=True, nullable=False)
    idElection = database.Column(database.Integer, database.ForeignKey("Election.id"), primary_key=True, nullable=False)

    ord_number = database.Column(database.Integer, nullable=False)
    result = database.Column(database.Integer, nullable=True)


class Participant (database.Model):
    __tablename__ = "Participant"

    id = database.Column(database.Integer, primary_key=True)
    name = database.Column(database.String(256), nullable=False)
    individual = database.Column(database.Boolean, nullable=False)

    myElections = database.relationship("Election",
                                        secondary = ElectionParticipation.__table__,
                                        back_populates="myParticipants")

    def __repr__(self):
        return "{ id:" + str(self.id) + ", name:" + self.name + ", individual:" + str(self.individual) + "}"

    def to_json(self):
        return {
            'id': self.id,
            'name': self.name,
            'individual': self.individual
        }


class Election(database.Model):
    __tablename__ = "Election"

    id = database.Column(database.Integer, primary_key=True)
    start = database.Column(database.String(24), nullable=False)
    end = database.Column(database.String(24), nullable=False)
    individual = database.Column(database.Boolean, nullable=False)
    votesNum = database.Column(database.Integer, nullable=True)

    myParticipants = database.relationship("Participant", secondary=ElectionParticipation.__table__,
                                         back_populates="myElections")

    myVotes = database.relationship("Vote", back_populates="myElection")

    def to_json(self):
        return {
            'id': self.id,
            'start': self.start,
            'end': self.end,
            'individual': self.individual,
            'participants': [{"id": participant.id, "name": participant.name} for participant in self.myParticipants]
        }


class Vote(database.Model):
    __tablename__ = "Vote"

    id = database.Column(database.Integer, primary_key=True)
    pollNumber = database.Column(database.Integer, nullable=False)
    guid = database.Column(database.String(36), nullable=False)
    jmbg = database.Column(database.String(13), nullable=False)
    myElectionId = database.Column(database.Integer, database.ForeignKey('Election.id'), nullable=False);
    valid = database.Column(database.Boolean, nullable=False)
    reason = database.Column(database.String(256), nullable=True)

    myElection = database.relationship("Election", back_populates="myVotes");

    def to_json(self):
        return {
            'electionOfficialJmbg': self.jmbg,
            'ballotGuid': self.guid,
            'pollNumber': self.pollNumber,
            'reason': self.reason
        }


