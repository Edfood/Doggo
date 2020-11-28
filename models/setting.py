from sqlalchemy import *
from sqlalchemy.orm import *
from sqlalchemy.ext.declarative import declarative_base
import os

DATABASE = 'postgresql://%s:%s@%s/%s?client_encoding=utf8' % (
    os.environ['POSTGRES_USER'],           # user name
    os.environ['POSTGRES_PASSWORD'],  # password
    os.environ['HOST'],     # host
    os.environ['POSTGRES_DB'],     # db name
)

ENGINE = create_engine(
    DATABASE,
    encoding="utf-8",
    echo=True
)

session = scoped_session(
    sessionmaker(
            autocommit = False,
            autoflush = False,
            bind = ENGINE
    )
)

Base = declarative_base()
Base.query = session.query_property()

######## Don't move the imports below! ###############
# Import all models to create the table 
# by Base.metadata.create_all().
from models import playtime
from models import user