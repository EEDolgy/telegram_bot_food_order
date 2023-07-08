from flask import Blueprint, render_template, request, flash, redirect, url_for
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from datetime import datetime

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


@views.route("/")
def home():
    dates = get_dates(result_str=True)

    return render_template('front_page.html', dates=dates)


@views.route("/day/<date>")
def day(date):
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

    return render_template('day.html', menu=menu, day=day, days=days,
                           next_day=next_day, prev_day=prev_day)


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

    return render_template('collect_userinfo.html')


@views.route("/order_details")
def order_details():



    return render_template('order_details.html')


# @app.route("/menu", methods=['GET', 'POST'])
# def first_date():
#     menu = get_actual_menu()
#     dates = list(menu.keys())
#     ln = len(dates)
#     if 'pg' in request.args:
#         page = request.args.get('pg')
#         dates_str = [menu[dt]['date'] for dt in dates]
#         if page == 'fst':
#             eggs = list(zip(dates_str, range(ln)))
#             dates_pages = {k: v for k, v in eggs}
#             return render_template('Front_page.html', dates_pages=dates_pages)
#         elif page == 'lst':
#             return render_template('Collect_userinfo.html')
#         elif page == 'view':
#             return render_template('Order_view.html')
#     elif 'i' in request.args:
#         i = int(request.args.get('i'))
#         menu_day = menu[dates[i]]
#         menu = [menu_day[str(i)] for i in range(1, 6)]
#         if i in range(1, ln-1):
#             return render_template('Order_day.html',
#                                    menu_day=menu_day,
#                                    next_page=f'{i+1}',
#                                    previous_page=f'{i-1}',
#                                    menu=menu)
#         elif i == 0:
#             return render_template('Order_day.html',
#                                    menu_day=menu_day,
#                                    next_page=f'{i+1}',
#                                    first_date=True,
#                                    menu=menu)
#         elif i == ln-1:
#             return render_template('Order_day.html',
#                                    menu_day=menu_day,
#                                    previous_page=f'{i-1}',
#                                    last_date=True,
#                                    menu=menu)
#
#
# if __name__ == "__main__":
#     app.run()
