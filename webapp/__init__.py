from flask import Flask, render_template, flash, redirect, url_for
from flask_migrate import Migrate
from webapp.model import db, Task, TaskStatus, Tag, User, UserRole
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
        status = TaskStatus.query.filter(TaskStatus.status == 'created').one()
        tag = Tag.query.filter(Tag.tag == 'Разведение ежей').one()
        freelancer = UserRole.query.filter(UserRole.role == 'freelancer').one()
        customer = UserRole.query.filter(UserRole.role == 'customer').one()

        if task_form.validate_on_submit():
            task_name = Task(
            task_name=task_form.task_name.data, 
            description=task_form.description.data,
            price=task_form.price.data,
            deadline=task_form.deadline.data, 
            status=status.id, tag=tag.id, 
            freelancer=freelancer.id, 
            customer=customer.id)
            db.session.add(task_name)
            db.session.commit()
            
            flash('Вы успешно создали заказ!')
            return redirect(url_for('personal_area_customer'))

        flash('Введите все данные!')
        return redirect(url_for('create_task'))

    @app.route('/personal_area_customer', methods=['GET', 'POST'])
    def personal_area_customer():
        title = 'Все заказы'
        task_name = Task.query.all()
        form = ChoiseForm()
        form.status.choices = [g.status for g in TaskStatus.query.all()]

        if form.validate_on_submit():
            if form.status.data == 'created':
                status = TaskStatus.query.filter(TaskStatus.status == 'created').one()
                status = Task(status=status.id)
                db.session.add(status)
                db.session.commit()
                
                flash('Статус заказа изменён на created')

            if form.status.data == 'published':
                status = TaskStatus.query.filter(TaskStatus.status == 'published').one()
                status = Task(status=status.id)
                db.session.add(status)
                db.session.commit()
                
                flash('Статус заказа изменён на published')

            if form.status.data == 'freelancers_detected':
                status = TaskStatus.query.filter(TaskStatus.status == 'freelancers_detected').one()
                status = Task(status=status.id)
                db.session.add(status)
                db.session.commit()
                
                flash('Статус заказа изменён на freelancers_detected')

             if form.status.data == 'in_work':
                status = TaskStatus.query.filter(TaskStatus.status == 'in_work').one()
                status = Task(status=status.id)
                db.session.add(status)
                db.session.commit()
                
                flash('Статус заказа изменён на in_work')

             if form.status.data == 'stopped':
                status = TaskStatus.query.filter(TaskStatus.status == 'stopped').one()
                status = Task(status=status.id)
                db.session.add(status)
                db.session.commit()
                
                flash('Статус заказа изменён на stopped')

             if form.status.data == 'in_review':
                status = TaskStatus.query.filter(TaskStatus.status == 'in_review').one()
                status = Task(status=status.id)
                db.session.add(status)
                db.session.commit()
                
                flash('Статус заказа изменён на in_review')

            if form.status.data == 'done':
                status = TaskStatus.query.filter(TaskStatus.status == 'done').one()
                status = Task(status=status.id)
                db.session.add(status)
                db.session.commit()
                
                flash('Статус заказа изменён на done')
            

        return render_template('personal_area_customer.html', title=title, task_name=task_name, form=form)

    return app
