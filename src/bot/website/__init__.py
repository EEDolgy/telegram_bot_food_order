from flask import Flask

from src.bot.website.views import views


def create_app():
    app = Flask(__name__)

    app.register_blueprint(views, url_prefix="/")

    return app


app = create_app()
app.run(debug=True)