from datetime import timedelta
import os

database_url = os.environ["DB_URL"]

class MyConfiguration():
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://root:root@{database_url}/authentication"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY="TAJNIKLJUC"
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)