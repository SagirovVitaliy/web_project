
from flask import Flask, render_template


def create_app():
    app = Flask(__name__)

    @app.route('/')
    def index():
        world = 'ZA WARUDO'
        return render_template('hello_world.html', world=world);
    return app
