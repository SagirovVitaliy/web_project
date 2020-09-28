from flask_migrate import Migrate
from flask import Flask, render_template
from webapp.model import db


def create_app():
    app = Flask(__name__)
    app.config.from_pyfile('config.py')
    db.init_app(app)
    migrate = Migrate(app, db)

    @app.route('/')
    def index():
        world = app.config['DEMO_WORLD']
        return render_template('hello_world.html', world=world)
    return app
