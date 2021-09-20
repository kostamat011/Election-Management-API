import os
redis_host = os.environ["REDIS_HOST"]


class MyConfiguration():
    JSON_SORT_KEYS = False
    JWT_SECRET_KEY = "TAJNIKLJUC"
    REDIS_HOST = redis_host
    REDIS_VOTES= "votes_list"