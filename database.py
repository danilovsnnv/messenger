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
    user_name = Column(String(50), nullable=False)
    user_hash = Column(Integer, nullable=False, unique=True)
    user_open_key = Column(Integer, nullable=False, unique=True)


if not os.path.exists(BDPATH):
    base.metadata.create_all(engine)
    session.commit()


def add_user(name: str, login: str, password: str):
    user_hash = hash(login + password)
    if not has_user(user_hash):
        session.add(Users(user_name=name, user_hash=user_hash, open_key=1))
        session.commit()


def has_user(user_hash: int) -> bool:
    return session.query(exists().where(Users.user_hash == user_hash)).scalar()


def password_check(login: str, password: str):
    return session.query(exists().where(Users.user_login == hash(login + password))).scalar()
