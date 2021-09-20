from flask_sqlalchemy import SQLAlchemy

database = SQLAlchemy()

class User(database.Model):
    __tablename__ = "User"

    jmbg = database.Column(database.String(13), primary_key=True)
    email = database.Column(database.String(256), nullable=False, unique=True)
    password = database.Column(database.String(256), nullable=False)
    forename = database.Column(database.String(256), nullable=False)
    surname = database.Column(database.String(256), nullable=False)

    idRole = database.Column(database.Integer, database.ForeignKey("Role.id"), nullable=False);
    myRole = database.relationship("Role", back_populates="myUsers")


class Role(database.Model):
    __tablename__="Role"

    id = database.Column(database.Integer, primary_key=True)
    name = database.Column(database.String(256), nullable=False)
    myUsers = database.relationship("User", back_populates="myRole")

    def __str__(self):
        return self.name

