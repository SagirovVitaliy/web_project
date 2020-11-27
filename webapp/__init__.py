from flask import Flask, render_template, flash, redirect, url_for, request
from flask_migrate import Migrate
from flask_login import LoginManager

from webapp.db import db, User
from webapp.sign.views import blueprint as sign_blueprint
from webapp.customer.views import blueprint as customer_blueprint
from webapp.freelancer.views import blueprint as freelancer_blueprint
from webapp.task.views import blueprint as task_blueprint


def create_app():
    app = Flask(__name__)
    app.config.from_pyfile('config.py')
    db.init_app(app)
    migrate = Migrate(app, db, render_as_batch=True)

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'sign.sign_in'

    app.register_blueprint(sign_blueprint)
    app.register_blueprint(customer_blueprint)
    app.register_blueprint(freelancer_blueprint)
    app.register_blueprint(task_blueprint)


    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(user_id)

    return app
