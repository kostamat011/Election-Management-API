from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKeyConstraint, Column, Integer, ForeignKey, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class ElectionParticipation(Base):
    __tablename__ = "ElectionParticipation"

    idParticipant = Column(Integer, ForeignKey("Participant.id"), primary_key=True, nullable=False)
    idElection = Column(Integer, ForeignKey("Election.id"), primary_key=True, nullable=False)

    ord_number = Column(Integer, nullable=False)
    result = Column(Integer, nullable=True)


class Participant (Base):
    __tablename__ = "Participant"

    id = Column(Integer, primary_key=True)
    name = Column(String(256), nullable=False)
    individual = Column(Boolean, nullable=False)

    myElections = relationship("Election",
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


class Election(Base):
    __tablename__ = "Election"

    id = Column(Integer, primary_key=True)
    start = Column(String(24), nullable=False)
    end = Column(String(24), nullable=False)
    individual = Column(Boolean, nullable=False)
    votesNum = Column(Integer, nullable=True)

    myParticipants = relationship("Participant", secondary=ElectionParticipation.__table__,
                                         back_populates="myElections")

    myVotes = relationship("Vote", back_populates="myElection")

    def to_json(self):
        return {
            'id': self.id,
            'start': self.start,
            'end': self.end,
            'individual': self.individual,
            'participants': [{"id": participant.id, "name": participant.name} for participant in self.myParticipants]
        }


class Vote(Base):
    __tablename__ = "Vote"

    id = Column(Integer, primary_key=True)
    pollNumber =Column(Integer, nullable=False)
    guid = Column(String(36), nullable=False)
    jmbg = Column(String(13), nullable=False)
    myElectionId = Column(Integer, ForeignKey('Election.id'), nullable=False);
    valid = Column(Boolean, nullable=False)
    reason = Column(String(256), nullable=True)

    myElection = relationship("Election", back_populates="myVotes");

    def to_json(self):
        return {
            'electionOfficialJmbg': self.jmbg,
            'ballotGuid': self.guid,
            'pollNumber': self.pollNumber,
            'reason': self.reason
        }


