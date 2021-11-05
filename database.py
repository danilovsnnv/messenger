import os

from sqlalchemy import create_engine, Integer, String, Column, exists
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.session import sessionmaker

BDPATH = 'base.db'

base = declarative_base()
engine = create_engine('sqlite:///' + BDPATH + '?check_same_thread=False', echo=True)
session = sessionmaker(bind=engine)()


class Users(base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    user_name = Column(String(50), nullable=True)
    user_hash = Column(Integer, nullable=False, unique=True)
    user_open_key = Column(Integer, nullable=True, unique=True)


if not os.path.exists(BDPATH):
    base.metadata.create_all(engine)
    session.commit()


def add_user(data):
    user_hash = hash(data)
    if not has_user(user_hash):
        session.add(Users(user_hash=user_hash))
        session.commit()


def has_user(user_hash: int) -> bool:
    return session.query(exists().where(Users.user_hash == user_hash)).scalar()


def check_user(data: str):
    return session.query(exists().where(Users.user_hash == hash(data))).scalar()
