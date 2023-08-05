from os import getcwd

from flask import Blueprint, render_template, request, flash, redirect, \
    url_for, jsonify
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from datetime import datetime
import re

from src.bot.database import DB, Users, Images, Dishes, \
    DatesMenu, Sprints, Orders, OrderDishes, \
    ExtraWishes, MetaInfo, SpecialPermissions, ENGINE


views = Blueprint("views", __name__)

WEEK_DAYS = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница',
             'Суббота', 'Воскресенье']


def get_dates(result_str=False):
    Session = sessionmaker(bind=ENGINE)
    session = Session()
    dates = session.scalars(select(Sprints).order_by(
        Sprints.first_date.desc())).one().all_dates
    session.close()

    dates = dates.split(', ')
    dates = list(map(lambda x: datetime.strptime(x, '%Y-%m-%d'), dates))

    if result_str:
        dates = list(map(lambda x: x.strftime('%d.%m'), dates))

    return dates


def get_day_menu(date):
    Session = sessionmaker(bind=ENGINE)
    session = Session()
    day_menu = session.query(DatesMenu.category,
                             Dishes.description, Dishes.name,
                             Dishes.photo_name, Dishes.calories,
                             Dishes.price, Dishes.amount, Dishes.PFC
                             ).where(DatesMenu.date == date).join(Dishes).all()
    session.close()

    day_menu = [zip(item._fields, item) for item in day_menu]
    day_menu = [dict(item) for item in day_menu]

    week_day_num = date.weekday()
    day = {'date': date.strftime('%d.%m'), 'week_day': WEEK_DAYS[week_day_num]}

    return {'menu': day_menu, 'day': day}


def get_greetings_text_path():
    cwd = getcwd()
    if re.search('website', cwd):
        return "static/greetings_text.txt"
    else:
        return "website/static/greetings_text.txt"


@views.route("/")
def home():

    print(getcwd())
    dates = get_dates(result_str=True)

    greetings_text_path = get_greetings_text_path()
    with open(greetings_text_path, 'r', encoding='utf-8') as f:
        greetings_text = f.read()

    img_path = "../static/im_1.jpg"

    return render_template('front_page.html', dates=dates,
                           greetings_text=greetings_text, img_path=img_path)


@views.route("/day/<date>")
def day(date):
    img_path = "../static/im_1.jpg"
    # year = datetime.now().year TODO
    year = 2022
    date = date + '.' + str(year)
    date = datetime.strptime(date, '%d.%m.%Y').date()
    menu_day = get_day_menu(date)

    menu = menu_day['menu']
    day = menu_day['day']

    days = get_dates(result_str=True)
    if day['date'] == days[0]:
        next_day = days[1]
        prev_day = False
    elif day['date'] == days[-1]:
        next_day = False
        prev_day = days[-2]
    else:
        i = days.index(day['date'])
        next_day = days[i+1]
        prev_day = days[i-1]

    dates = get_dates(result_str=True)
    return render_template('day.html', menu=menu, day=day, days=days,
                           next_day=next_day, prev_day=prev_day, dates=dates,
                           img_path=img_path)


# @views.route("/add_dish/<date>/<category>/<amount>", methods=['Post'])
# def add_dish(date, category, amount):
#     return jsonify({"date": date, "category": category, "amount": amount})


@views.route("/user_info", methods=['GET', 'POST'])
def user_info():
    if request.method == 'POST':
        username_tg = 'username_tg' #TODO

        name = request.form.get('name')
        telephone = request.form.get('telephone')
        address = request.form.get('address')
        comment = request.form.get('comment')

        flash('Logged in!', category='success')

        Session = sessionmaker(bind=ENGINE)
        session = Session()

        user = session.scalars(
                     select(Users).where(Users.username_tg == username_tg)
                     ).first()

        if user:
            if telephone == '':
                telephone = user.telephone
            session.delete(user)

        user = Users(
                username_tg=username_tg,
                name=name,
                address=address,
                telephone=telephone
               )

        session.merge(user)
        session.commit()
        session.close()

        return redirect(url_for('views.home'))

    dates = get_dates(result_str=True)

    return render_template('collect_userinfo.html', dates=dates)


@views.route("/order_details")
def order_details():
    dates = get_dates(result_str=True)

    return render_template('order_details.html', dates=dates)


if __name__ == "__main__":
    import os
    content = os.listdir('static')
    print(content)
