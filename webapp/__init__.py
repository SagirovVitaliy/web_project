from flask import Flask, render_template, flash, redirect, url_for
from flask_migrate import Migrate
from webapp.model import db, Task, Task_status
from webapp.forms import Task_form


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
            task_name = Task(task_name=task_form.task_name.data, description=task_form.description.data, 
            price=task_form.price.data, status=Task_status.query.filter(Task_status.status == 'created').one())
            db.session.add(task_name)
            db.session.commit()
            
            flash('Вы успешно создали заказ!')
            return redirect(url_for('personal_area_customer'))

        flash('Введите все данные!')
        return redirect(url_for('create_task'))

    @app.route('/personal_area_customer')
    def personal_area_customer():
        title = 'Все заказы'
        task_name = Task.query.all()
       
        return render_template('personal_area_customer.html', title=title, task_name=task_name)

    return app
