from sqlalchemy import create_engine

from src.bot.database.models import DB, MetaInfo

DB_ABSOLUTE_PATH = 'C:\\Users\\Raven\\Desktop\\Menu_Bot_3\\src\\'
DB_NAME = 'database.db'

ENGINE = create_engine("sqlite:///" + DB_ABSOLUTE_PATH + DB_NAME)

DB.metadata.create_all(ENGINE)