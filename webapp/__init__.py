from flask import Flask, render_template, flash, redirect, url_for
from flask_migrate import Migrate
from webapp.model import db, Email, Phone, Task, Status, Tag, User, Role
from webapp.forms import TaskForm, ChoiseForm


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
        task_form = TaskForm()
        return render_template('create_task.html', title=title, form=task_form)

    @app.route('/process_create_task', methods=['POST'])
    def process_create_task():
        task_form = TaskForm()
        status = Status.query.filter(Status.status == 'created').one()
        tag = Tag.query.filter(Tag.tag == 'Разведение ежей').one()
        freelancer = Role.query.filter(Role.role == 'freelancer').one()
        customer = Role.query.filter(Role.role == 'customer').one()

        if task_form.validate_on_submit():
            task_name = Task(
            task_name=task_form.task_name.data, 
            description=task_form.description.data,
            price=task_form.price.data,
            deadline=task_form.deadline.data, 
            status=status.id, 
            tag=tag.id, 
            freelancer=freelancer.id, 
            customer=customer.id)
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
        form = ChoiseForm()
        form.status.choices = [g.status for g in Status.query.all()[:2]]

        return render_template('personal_area_customer.html', title=title, task_name=task_name, form=form)

    @app.route('/update_status/<int:task_id>', methods=['POST'])
    def update_status(task_id):
        form = ChoiseForm()
        form.status.choices = [g.status for g in Status.query.all()[:2]]

        if form.validate_on_submit():
            status = form.status.data
            task = Task.query.get(task_id)
            task_status = Status.query.filter(Status.status == status).one()
            task.status = task_status.id
            db.session.commit()
                
        flash(f"Статус заказа изменён на {status}")
        return redirect(url_for('personal_area_customer'))

    return app
