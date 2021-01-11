from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import relationship
from models.setting import Base, session


class User(Base):
    __tablename__ = 'users'
    id = Column('id', String(50), unique=True, primary_key=True)
    limit_time = Column('limitTime', Integer, nullable=False)
    playtimes = relationship('Playtime', backref='user', cascade='all,delete-orphan')

    def __repr__(self):
        return f"<User(id='{self.id}', playtime='{self.playtimes}', limit_time='{self.limit_time}')>"

    def __init__(self, id):
        self.id = id
        INF = 1000000
        self.limit_time = INF

    @classmethod
    def save(cls, obj):
        session.add(obj)
    
    @classmethod
    def get(cls, id):
        obj = session.query(User)\
            .filter_by(id=id)\
            .first()
        return obj
    
    @classmethod
    def get_all(cls):
        return session.query(cls).all()

    @classmethod
    def delete(cls, id):
        obj = session.query(User)\
            .filter_by(id=id)\
            .first()
        session.delete(obj)
        return obj
