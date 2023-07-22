from flask import Flask

from src.website.views import views


def create_app():
    app = Flask(__name__)

    app.register_blueprint(views, url_prefix="/")

    return app


def run_website():
    app = create_app()
    app.run(debug=True)


if __name__ == '__main__':
    run_website()