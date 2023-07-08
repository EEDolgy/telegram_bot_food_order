# from src.bot import run_bot


if __name__ == '__main__':
    # run_bot()

    from src.bot.database import add_meta_info, get_users_orders
    # add_meta_info('bot/user_data/hello_text.txt')
    print(get_users_orders('username_tg'))