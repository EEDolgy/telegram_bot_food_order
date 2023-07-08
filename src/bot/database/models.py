from sqlalchemy import Column, ForeignKey, PrimaryKeyConstraint
from sqlalchemy.types import Integer, Text, String, \
    VARCHAR, Date, Enum, DateTime, NVARCHAR
from sqlalchemy.dialects.mysql import MEDIUMBLOB
from sqlalchemy.orm import declarative_base

DB = declarative_base()


class Users(DB):
    __tablename__ = 'users'

    id = Column(Integer,
                primary_key=True,
                autoincrement="auto",
                nullable=False,
                unique=True)
    username_tg = Column(VARCHAR(100), unique=True, nullable=False)
    name = Column(VARCHAR(100), default='NULL')
    surname = Column(VARCHAR(100), default='NULL')
    telephone = Column(VARCHAR(45), default='NULL')
    address = Column(VARCHAR(1000), nullable=False)


class Images(DB):
    __tablename__ = 'images'

    name = Column(String(100),
                  primary_key=True,
                  nullable=False,
                  unique=True)
    # img = Column(MEDIUMBLOB, nullable=False)


class Dishes(DB):
    __tablename__ = 'dishes'

    idDishes = Column(Integer,
                      primary_key=True,
                      autoincrement=True,
                      unique=True,
                      nullable=False)
    description = Column(Text(1000), default='NULL')
    name = Column(String(100), nullable=False, unique=True)
    photo_name = Column(
        String(100),
        ForeignKey('images.name',
                   ondelete='NO ACTION',
                   onupdate='NO ACTION'),
        default='NULL')
    calories = Column(Text(100), default='NULL')
    price = Column(Text(100), default='NULL')
    amount = Column(String(500), default='NULL')
    category = Column(Enum('1', '2', '3', '4', '5'), nullable=False)
    PFC = Column(String(100), default='NULL')

    def show(self):
        print(self.name)


class DatesMenu(DB):
    __tablename__ = 'dates_menu'

    date_dish_id = Column(Integer,
                          primary_key=True,
                          autoincrement=True,
                          unique=True,
                          nullable=False)
    date = Column(Date, nullable=False)
    id_dish = Column(
        Integer,
        ForeignKey('dishes.idDishes',
                   ondelete='NO ACTION',
                   onupdate='NO ACTION'),
        nullable=False)
    category = Column(Enum('1', '2', '3', '4', '5'), nullable=False)


class Sprints(DB):
    __tablename__ = 'sprints'

    first_date = Column(Date,
                        primary_key=True,
                        nullable=False,
                        unique=True)
    last_date = Column(Date, nullable=False)
    all_dates = Column(String(500), nullable=False)


class Orders(DB):
    __tablename__ = 'orders'

    id_order = Column(Integer,
                      primary_key=True,
                      autoincrement=True,
                      nullable=False)
    id_user = Column(Integer,
                     ForeignKey('users.id',
                                ondelete='NO ACTION',
                                onupdate='NO ACTION'),
                     nullable=False)
    Comment = Column(Text(500), nullable=True, default='NULL')
    fst_date_sprint = Column(Date,
                             ForeignKey('sprints.first_date',
                                        ondelete='NO ACTION',
                                        onupdate='NO ACTION'),
                             nullable=False)
    order_date = Column(DateTime, nullable=False)


class OrderDishes(DB):
    __tablename__ = 'order_dishes'

    id_order_dish = Column(Integer,
                           primary_key=True,
                           autoincrement=True,
                           nullable=False,
                           unique=True)
    id_date_dish = Column(Integer,
                          ForeignKey('dates_menu.date_dish_id',
                                     ondelete='NO ACTION',
                                     onupdate='NO ACTION'),
                          nullable=False)
    size = Column(Enum('1', '1.5'), default='1', nullable=False)
    id_Order = Column(Integer,
                      ForeignKey('orders.id_order',
                                 ondelete='NO ACTION',
                                 onupdate='NO ACTION'),
                      nullable=False)


class ExtraWishes(DB):
    __tablename__ = 'extra_wishes'

    id = Column(Integer, primary_key=True,
                autoincrement=True, unique=True)
    date_received = Column(Date, nullable=False)
    user = Column(String(100), nullable=False)
    text = Column(String(500), nullable=False)


class MetaInfo(DB):
    __tablename__ = 'meta_info'

    info_type = Column(String(50), primary_key=True, unique=True)
    text = Column(NVARCHAR(1000), default='NULL')


class SpecialPermissions(DB):
    __tablename__ = 'special_permissions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username_tg = Column(String(100), nullable=False, unique=True)