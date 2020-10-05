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
            task_name = Task(task_name=task_form.task_name.data)
            db.session.add(task_name)
            db.session.commit()

            description = Task(description=task_form.description.data)
            db.session.add(description)
            db.session.commit()

            price = Task(price=task_form.price.data)
            db.session.add(price)
            db.session.commit()
            
            deadline = Task(deadline=parse(task_form.deadline.data))
            db.session.add(deadline)
            db.session.commit()
            
            status = Task_status(status='created')
            db.session.add(status)
            db.session.commit()

            flash('Вы успешно создали заказ!')
            return redirect(url_for('index'))
        
        flash('Введите все данные!')
        return redirect(url_for('create_task'))

    return app
