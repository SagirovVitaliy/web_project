
from flask import Flask, render_template


def create_app():
    app = Flask(__name__)
    app.config.from_pyfile('config.py')

    @app.route('/')
    def index():
        world = app.config['DEMO_WORLD']
        return render_template('hello_world.html', world=world);
    return app
