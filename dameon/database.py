from sqlalchemy import *
from sqlalchemy.ext.declarative import *
from sqlalchemy.orm import *
from configuration import MyConfiguration

engine = create_engine(MyConfiguration.SQLALCHEMY_DATABASE_URI)
session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)
base = declarative_base()
