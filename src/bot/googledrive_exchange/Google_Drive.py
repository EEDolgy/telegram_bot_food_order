from datetime import datetime
import re
import os

from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, desc
import pandas as pd

from src.bot.database import DB, Users, Images, Dishes, \
    DatesMenu, Sprints, Orders, OrderDishes, \
    ExtraWishes, MetaInfo, SpecialPermissions, ENGINE


FOLDER = 'МАМА ДОМА. Рабочая папка. Проект.'

MIMETYPES = {
        # Drive Document files as MS dox
        'application/vnd.google-apps.document': 'text/plain',
        # Drive Sheets files as MS Excel files.
        'application/vnd.google-apps.spreadsheet': 'text/csv'
  }

gauth = GoogleAuth()
gauth.LocalWebserverAuth()
drive = GoogleDrive(gauth)


def get_folder_id(folder_name, parent_folder="root"):
    if parent_folder != "root":
        parent_folder_id = get_folder_id(parent_folder)
    else:
        parent_folder_id = parent_folder

    file_list = drive.ListFile({
        'q': f"'{parent_folder_id}' in parents and trashed=false"
    }).GetList()

    for file in file_list:
        if file['title'] == folder_name:
            return file['id']


MAMA_FOLDER_ID = get_folder_id(FOLDER)


def get_data_from_google_drive():

    '''Getting data from Google Drive and adding it to database'''

    menu_folder = 'Меню'
    menu_folder_id = get_folder_id(menu_folder, FOLDER)

    def get_sheet_content(file):
        title = file['title']
        temp_file = 'dish.csv'
        download_mimetype = MIMETYPES[file['mimeType']]
        file.GetContentFile(filename=temp_file, mimetype=download_mimetype)
        if title != 'Меню на неделю':
            result = pd.read_csv(temp_file, names=columns, skiprows=1)
            num = re.search(r'\d', title)[0]
            category = pd.Series([num] * result.shape[0])
            result['category'] = category
        else:
            col = ['month', 'week_day', 'date', 'Dish_1',
                   'Dish_2', 'Dish_3', 'Dish_4', 'Dish_5']
            result = pd.read_csv(temp_file, names=col, skiprows=1)
        os.remove(temp_file)

        return result

    menu_sheets = ('1. Основное блюдо (список)',
                   '2. Гарнир (список)',
                   '3. Суп (список)',
                   '4. Салат (список)',
                   '5. Десерт (список)')

    columns = ['category', 'name', 'price', 'description',
               'calories', 'PFC', 'photo_name', 'amount']
    all_dishes = pd.DataFrame(columns=columns)

    lister = drive.ListFile({
        'q': f"'{menu_folder_id}' in parents and trashed=false"
    }).GetList()
    for file in lister:
        if file['title'] in menu_sheets:
            all_dishes = pd.concat([all_dishes, get_sheet_content(file)],
                                  ignore_index=True
                                  )

        elif file['title'] == 'Меню на неделю':
            week_menu = get_sheet_content(file)

        elif file['title'] == 'Меню фотографии':
            pass
            # lister = drive.ListFile({
            # 'q': f"'{file['id']}' in parents and trashed=false"
            # }).GetList()
            # photos = []
            # i = 0
            # for file in lister:
            #     name = re.sub(r'\.\w+', '', file['title'])
            #     title = re.sub(r'.+\.', f'{i}.', file['title'])
            #     local_filename = LOCAL_IMAGES_FOLDER + title
            #     file.GetContentFile(filename=local_filename)
            #     photos.append(name)
            #     add_img_to_DB(name, local_filename)
            #     os.remove(local_filename)
            #     i += 1

    return (all_dishes, week_menu)


def add_data_to_db(all_dishes, week_menu):

    Session = sessionmaker(bind=ENGINE)
    session = Session()

    # Adding dates to database

    dates = list(week_menu['date'])
    dates.sort()
    all_dates = ', '.join(dates)
    sprint = Sprints(first_date=datetime.strptime(dates[0], '%Y-%m-%d'),
                     last_date=datetime.strptime(dates[-1], '%Y-%m-%d'),
                     all_dates=all_dates
                     )

    session.merge(sprint)

    # Adding dishes list to database

    # all_dishes.loc[(~all_dishes['photo_name'].isin(photos)), 'photo_name'] = 'default_photo' TODO

    menu = all_dishes.apply(
        lambda x: Dishes(description=x['description'],
                         name=x['name'],
                         photo_name=x['photo_name'],
                         calories=x['calories'],
                         price=x['price'],
                         amount=x['amount'],
                         category=x['category'],
                         PFC=x['PFC']), axis=1)
    menu = list(menu)

    for item in menu:
        not_unique = session.scalars(
                     select(Dishes).where(Dishes.name == item.name)
                     ).all()
        for i in not_unique:
            session.delete(i)
            session.commit()
        session.merge(item)

    session.commit()

    # Adding week's menu to database

    dishes = session.query(Dishes).all()
    name_id = {i.name: i.idDishes for i in dishes}

    category_columns = list(week_menu.columns[3:])
    week_menu_dict = {i: week_menu[list(week_menu.columns[0:3]) + [j]]
                      for (i, j) in zip(range(1, 6), category_columns)}
    columns = list(week_menu.columns[0:3]) + ['Dish', 'category']
    dates_menu = pd.DataFrame(columns=columns)
    for i, val in week_menu_dict.items():
        val_1 = val.copy()
        val_1.rename(columns={f'Dish_{i}': 'Dish'}, inplace=True)
        val_1.insert(4, 'category', [i] * week_menu.shape[0], False)
        dates_menu = pd.concat([dates_menu, val_1])
    dates_menu['date'] = pd.to_datetime(dates_menu['date'])
    dates_menu['category'] = dates_menu['category'].astype(str)

    id_list = [name_id[i] for i in dates_menu['Dish']]
    dates_menu.rename(columns={f'Dish': 'id_dish'}, inplace=True)
    dates_menu['id_dish'] = id_list
    dates_menu_list = [DatesMenu(date=i.date, id_dish=i.id_dish,
                                 category=i.category) for i in
                       dates_menu.itertuples()]

    for item in dates_menu_list:
        not_unique = session.scalars(
                        select(DatesMenu).where(DatesMenu.date == item.date)
                            .where(
                                DatesMenu.category == item.category
                            )
                     ).all()
        for i in not_unique:
            session.delete(i)
            session.commit()
        session.merge(item)

    session.commit()
    session.close()


def download_menu():
    all_dishes, week_menu = get_data_from_google_drive()
    add_data_to_db(all_dishes, week_menu)


def upload(user_info, file_name):
        data_list = []
        for item in user_info:
            user_info_dict = item.__dict__
            user_info_dict.pop('_sa_instance_state', None)
            data_list.append(user_info_dict)

        lister = drive.ListFile({'q': f"'{MAMA_FOLDER_ID}'"
                                      f"in parents and "
                                      f"trashed=false"}).GetList()
        for file in lister:
            if file['title'] == file_name:
                file.Trash()
                break

        result = pd.DataFrame(data_list)

        my_file = drive.CreateFile({'title': file_name, 'mimeType':
            'text/csv', 'parents': [{'id': MAMA_FOLDER_ID}]})
        my_file.SetContentString(result.to_csv())
        my_file.Upload({'convert': True})


def upload_clients():
    Session = sessionmaker(bind=ENGINE)
    session = Session()

    user_info = session.scalars(select(Users)).all()

    session.close()

    if user_info:
        upload(user_info, 'База клиентов')
    else:
        return None


def upload_orders():
    Session = sessionmaker(bind=ENGINE)
    session = Session()

    last_sprint = session.query(Sprints).order_by(desc(
        Sprints.first_date)).first().first_date
    user_info = (
        session.query(Users.username_tg, Orders.Comment, Orders.order_date,)
        .join(Employee.department)
        .join(Address, Employee.id == Address.employee_id)
        .filter(Department.name == 'HR')
        .scalars()
        .all()
    )


    session.close()

    if user_info:
        upload(user_info, 'Актуальные заказы')
    else:
        return None


if __name__ == '__main__':
    upload()