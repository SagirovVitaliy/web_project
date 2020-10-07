from flask import Flask, render_template, flash, redirect, url_for
from flask_migrate import Migrate
from webapp.model import db, Task, Task_status
from webapp.forms import Task_form
from dateparser import parse


def create_app():
    app = Flask(__name__)
    app.config.from_pyfile('config.py')
    db.init_app(app)
    migrate = Migrate(app, db)

    @app.route('/')
    def index():
        world = 'word'
        return render_template('hello_world.html', world=world)
    
    @app.route('/create_task')
    def create_task():
        title = 'Создание заказа'
        task_form = Task_form()
        return render_template('create_task.html', title=title, form=task_form)

    @app.route('/process_create_task', methods=['POST'])
    def process_create_task():
        task_form = Task_form()
        
        if task_form.validate_on_submit():
            task_name = Task(task_name=task_form.task_name.data, description=task_form.description.data, price=task_form.price.data, deadline=parse(task_form.deadline.data))
            db.session.add(task_name)
            db.session.commit()
            
            status = Task_status(status='created')
            db.session.add(status)
            db.session.commit()

            flash('Вы успешно создали заказ!')
            return redirect(url_for('personal_area_customer'))

        flash('Введите все данные!')
        return redirect(url_for('create_task'))

    @app.route('/personal_area_customer', methods=['GET', 'POST'])
    def personal_area_customer():
        title = 'Все заказы'
        task_name = Task.query.order_by(Task.id.desc()).all()
        task_form = Task_form()
        if task_form.validate_on_submit():

            status = Task_status(status='published')
            db.session.add(status)
            db.session.commit()

            flash('Заказ успешно опубликован')
            return redirect(url_for('personal_area_customer/published'))

        return render_template('personal_area_customer.html', title=title, task_name=task_name, form=task_form)

    @app.route('/personal_area_customer_published')
    def published():
        title = 'Опубликованные заказы'
        return render_template('personal_area_customer_published.html', title=title)

    return app
