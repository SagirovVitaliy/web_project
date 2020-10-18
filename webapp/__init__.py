from flask import Flask, render_template, flash, redirect, url_for, request
from flask_migrate import Migrate
from webapp.model import db, Email, Phone, Task, TaskStatus, Tag, User, UserRole, freelancers_who_responded
from webapp.forms import TaskForm, ChoiseForm, FreelancerForm, InWorkForm, InWorkFormTwo


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
            status=status.id, 
            tag=tag.id, 
            freelancer=freelancer.id, 
            customer=customer.id)
            db.session.add(task_name)
            db.session.commit()
            
            flash('Вы успешно создали заказ!')
            return redirect(url_for('personal_area_customer'))

        flash('Введите все данные!')
        title = 'Создание заказа'
        return render_template('create_task.html', title=title, form=task_form)

    @app.route('/personal_area_customer')
    def personal_area_customer():
        title = 'Все заказы'
        tasks = Task.query.all()
        form = ChoiseForm()
        form.status.choices = [g.status for g in TaskStatus.query.all()[:2]]

        return render_template('personal_area_customer.html', title=title, tasks=tasks, form=form)

    @app.route('/update_status/<int:task_id>', methods=['POST'])
    def update_status(task_id):
        form = ChoiseForm()
        form.status.choices = [g.status for g in TaskStatus.query.all()[:2]]

        if form.validate_on_submit():
            status = form.status.data
            task = Task.query.get(task_id)
            task_status = TaskStatus.query.filter(TaskStatus.status == status).one()
            task.status = task_status.id
            db.session.commit()
                
        flash(f"Статус заказа изменён на {status}")
        return redirect(url_for('personal_area_customer'))

    @app.route('/personal_area_freelancer/<int:user_id>', methods=['GET', 'POST'])
    def personal_area_freelancer(user_id):
        title = 'Все заказы'
        form = FreelancerForm()
        form.tasks.choices = [task.id for task in Task.query.filter(Task.status.in_([2,3])).all()]

        if form.validate_on_submit():
            task = Task.query.get(form.tasks.data)
            user = User.query.get(user_id)
            task.freelancers_who_responded.append(user)
            status = TaskStatus.query.filter(TaskStatus.status == 'freelancers_detected').one()
            task.status = status.id
            db.session.commit()
            flash(f"Статус заказа изменён на {status}")

        return render_template('personal_area_freelancer.html', title=title, form=form)


    @app.route('/personal_area_customer_in_work/<int:customer_id>', methods=['GET', 'POST'])
    def personal_area_customer_in_work(customer_id):
        title = 'Все заказы'
        form = InWorkForm()
        tasks = Task.query.filter(Task.customer == customer_id, Task.status == 3).all()
        form.tasks.choices = [task.id for task in tasks]
        
        if request.method == 'POST':
            if form.validate_on_submit():
                task_id = form.tasks.data
                return redirect(url_for('personal_area_customer_in_work_two', task_id=task_id))
        
        return render_template('in_work.html', title=title, form=form)

    
    @app.route('/personal_area_customer_in_work_two/<int:task_id>', methods=['GET', 'POST'])
    def personal_area_customer_in_work_two(task_id):
        title = 'Все откликнувшиеся'
        form = InWorkFormTwo()
        task = Task.query.get(task_id)
        freelancers = task.freelancers_who_responded.all()
        
        form.freelancers.choices = [user.id for user in freelancers]

        if form.validate_on_submit():
            task = Task.query.get(task_id)
            status = TaskStatus.query.filter(TaskStatus.status == 'in_work').one()
            task.status = status.id
            task.freelancer = form.freelancers.data
            db.session.commit()
            flash(f"Статус заказа изменён на {status}")
        
        return render_template('in_work_two.html', title=title, form=form)

    return app
