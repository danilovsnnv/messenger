import os
import datetime

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
    username = Column(String(50), nullable=True, unique=True)
    hash = Column(Integer, nullable=False, unique=False)
    open_key = Column(String, nullable=True)


class Messages(base):
    __tablename__ = 'messages'

    id = Column(Integer, primary_key=True)
    user_from = Column(String(50), nullable=False)
    user_to = Column(String(50), nullable=False)
    time = Column(String, nullable=False)
    message = Column(String, nullable=False)


class UnreceivedMessages(base):
    __tablename__ = 'unreserved'

    id = Column(Integer, primary_key=True)
    user_from = Column(String(50), nullable=False)
    user_to = Column(String(50), nullable=False)
    time = Column(String, nullable=False)
    message = Column(String, nullable=False)


if not os.path.exists(BDPATH):
    base.metadata.create_all(engine)
    session.commit()


def add_user(username: str, data: str, key: str) -> bool:
    """
    Поиск пользователя в базе данных
         :param username: Имя пользователя
         :param data: Строка логин + пароль
         :param key: Открытый RSA ключ

         :return True: Пользователь существует в базе данных
         :return False: Пользователя нет или введены неверные данные
    """
    user_exists = has_user(username, data)
    if not user_exists:
        session.add(Users(username=username, hash=hash(data), open_key=key))
        session.commit()
    return not user_exists


def has_user(username: str, data: str) -> bool:
    """
    Поиск пользователя в базе данных
        :param username: Имя пользователя
        :param data: Строка логин + пароль

        :return: True: Пользователь существует в базе данных
        :return: False: Пользователя нет или введены неверные данные
    """
    return session.query(exists().where(Users.username == username and
                                        Users.hash == hash(data))).scalar()


def get_users_list(username_part: str) -> list:
    """
    Поиск пользователей по логину или его части
    :param username_part: Строка с логином
    :return: Список пользователей или пустой список, если пользователи не были найдены или запрос слишком короткий
    """
    users = [user[0] for user in session.query(Users.username).filter(Users.username.ilike(username_part + '%')).all()]
    return users


def add_message(user_from: str, user_to: str, message: str, time=datetime.datetime.now()):
    """
    Добавление информации о сообщении в базу данных
        :param user_from: Имя пользователя-отправителя
        :param user_to: Имя пользователя-адресата
        :param message: Текст сообщения
        :param time: Время отправки сообщения (по умолчанию текущее время)
    """
    session.add(Messages(user_from=user_from, user_to=user_to, time=str(time), message=message))
    session.commit()


def add_unreceived_message(user_from: str, user_to: str, message: str, time=datetime.datetime.now()):
    """
    Добавление в базу данных информации о сообщении, которое не дошло до адресата
        :param user_from: Имя пользователя-отправителя
        :param user_to: Имя пользователя-адресата
        :param message: Текст сообщения
        :param time: Время отправки сообщения (по умолчанию текущее время)
    """
    session.add(UnreceivedMessages(user_from=user_from, user_to=user_to, time=str(time), message=message))
    session.commit()


def get_unreceived_message(username: str):
    """
    Ищет неполучаенные сообщения для конкретного пользователя, удаляет их и возвращает
    :param username: Имя пользователя для поиска
    :return: Список сообщений
    """
    messages = session.query(UnreceivedMessages).filter(UnreceivedMessages.user_to == username).all()
    res = []
    for message in messages:
        res.append([message.user_from, message.message, message.time])
    session.query(UnreceivedMessages).filter(UnreceivedMessages.user_to == username).delete(synchronize_session='fetch')
    session.commit()
    return res


def get_open_key(username: str) -> str:
    """
    Получает открытый ключ по логину пользователя
    :param username: Имя пользователя
    :return: Открытый ключ пользователя
    """
    user = session.query(Users).filter_by(username=username).one()
    return user.open_key
