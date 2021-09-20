import os
redis_host = os.environ["REDIS_HOST"]
database_url = os.environ["DB_URL"]



class MyConfiguration():
    JSON_SORT_KEYS = False
    JWT_SECRET_KEY = "TAJNIKLJUC"
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://root:root@{database_url}/authentication"
    REDIS_HOST = redis_host
    REDIS_VOTES= "votes_list"