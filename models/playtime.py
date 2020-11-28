from sqlalchemy import ForeignKey, desc, Integer, String, Date, Column
from models.setting import Base, session


class Playtime(Base):
    __tablename__ = 'playtimes'
    user_id = Column(String(50), ForeignKey('users.id'), primary_key=True)
    date = Column(Date, index=True, primary_key=True)
    time_cnt = Column(Integer, default=0)  # time counter

    def __repr__(self):
        return f"<Playtime(user_id='{self.user_id}, \
                date='{self.date}', \
                time_cnt='{self.time_cnt}'')>"

    def __init__(self, user_id, date, time_cnt=0):
        self.user_id = user_id
        self.date = date
        self.time_cnt = time_cnt

    @classmethod
    def merge(cls, playtime):
        """Save `Playtime` or overwrite if the data already exists."""
        session.merge(playtime)

    @classmethod
    def get(cls, user_id, date):
        return session.query(cls)\
            .filter(cls.user_id == user_id, cls.date == date)\
            .one_or_none()

    @classmethod
    def get_x_days(cls, user_id, x):
        """Get x days of `playtime` for a user."""
        return session.query(cls)\
            .filter(cls.user_id == user_id)\
            .order_by(desc(cls.date))\
            .limit(x)\
            .all()
