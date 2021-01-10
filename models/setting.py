from sqlalchemy import *
from sqlalchemy.orm import *
from sqlalchemy.ext.declarative import declarative_base
import os
from utils.log_conf import confLogger

logger = confLogger(__name__)

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
from models.playtime import Playtime
from models.user import User
# Base.metadata.drop_all(bind=ENGINE)  # use this, if you need to drop table

logger.info('Creating database tables...')
Base.metadata.create_all(bind=ENGINE)  # create DB tables if not exist
logger.info('Done!')
