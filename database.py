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
    user_name = Column(String, nullable=False)
    user_login = Column(String, nullable=False, unique=True)
    user_password = Column(String, nullable=False, unique=True)


if not os.path.exists(BDPATH):
    base.metadata.create_all(engine)
    session.commit()


def add_user(name: str, login: str, password: str):
    if not has_user(login):
        session.add(Users(user_name=name, user_login=login, user_password=password))
        session.commit()


def has_user(login: str) -> bool:
    return session.query(exists().where(Users.user_login == login)).scalar()


def password_check(login: str, password: str):
    return session.query(exists().where(Users.user_login == login, Users.user_password == password)).scalar()
