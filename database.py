import os

from sqlalchemy import create_engine, Integer, String, Column, exists
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.session import sessionmaker

BDPATH = 'dbase.db'

base = declarative_base()
engine = create_engine('sqlite:///' + BDPATH + '?check_same_thread=False', echo=True)
session = sessionmaker(bind=engine)()


class Users(base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    user_name = Column(String(50), nullable=True, unique=True)
    user_hash = Column(Integer, nullable=False, unique=False)
    user_open_key = Column(Integer, nullable=True)


if not os.path.exists(BDPATH):
    base.metadata.create_all(engine)
    session.commit()


def add_user(username: str, data: str) -> bool:
    user_exists = has_user(username, data)
    if not user_exists:
        session.add(Users(user_name=username, user_hash=hash(data)))
        session.commit()
    return not user_exists


def has_user(user_name: str, data: str) -> bool:
    return session.query(exists().where(Users.user_name == user_name and
                                        Users.user_hash == hash(data))).scalar()
