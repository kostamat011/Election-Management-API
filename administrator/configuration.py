from datetime import timedelta
import os

database_url = os.environ["DB_URL"]

class MyConfiguration():
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://root:root@{database_url}/authentication"
    JWT_SECRET_KEY="TAJNIKLJUC"
    JSON_SORT_KEYS = False;