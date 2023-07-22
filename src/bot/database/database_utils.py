import re

from sqlalchemy.orm import sessionmaker
from sqlalchemy import select

from src.bot.database.create_db import ENGINE
from src.bot.database.models import Users, Images, Dishes, \
    DatesMenu, Sprints, Orders, OrderDishes, \
    ExtraWishes, MetaInfo, SpecialPermissions


def add_meta_info(filename):
    info_type = re.sub(r'\.txt', '', filename)
    info_type = info_type.split('/')[-1]
    with open(filename, 'r', encoding='UTF-8') as f:
        text = f.read()

    Session = sessionmaker(bind=ENGINE)
    session = Session()

    meta_data = MetaInfo(text=text, info_type=info_type)
    session.merge(meta_data)

    session.commit()
    session.close()


def get_meta_info(info_type):
    Session = sessionmaker(bind=ENGINE)
    session = Session()

    result = session.scalars(
        select(MetaInfo.text).where(MetaInfo.info_type == info_type)).first()

    session.close()

    return result


def get_users_last_order(username_tg):
    Session = sessionmaker(bind=ENGINE)
    session = Session()

    user_id = session.scalars(
        select(Users.id).where(Users.username_tg == username_tg)).first()

    if user_id is not None:
        pass
    else:
        orders = False

    session.close()

    return orders