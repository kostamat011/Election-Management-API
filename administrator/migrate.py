from flask import Flask
from configuration import MyConfiguration
from flask_migrate import Migrate, init, migrate, upgrade
from models import database
from sqlalchemy_utils import create_database, database_exists

application = Flask(__name__)
application.config.from_object(MyConfiguration)

migrateObject = Migrate(application, database)

done = False

while not done:
    try:
        if not database_exists(application.config["SQLALCHEMY_DATABASE_URI"]):
            create_database(application.config["SQLALCHEMY_DATABASE_URI"])

        database.init_app(application)

        with application.app_context() as context:
            init()
            migrate(message="Production migration")
            upgrade()
            done = True

    except Exception as err:
        print(err)
