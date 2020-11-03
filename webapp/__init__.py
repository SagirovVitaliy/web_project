from flask import Flask, render_template, flash, redirect, url_for, request
from flask_migrate import Migrate
from flask_login import LoginManager, login_user, logout_user, current_user, login_required

from webapp.model import db, Email, Phone, Task, TaskStatus, Tag, User, UserRole, freelancers_who_responded
from webapp.forms import (
    IndexForm, RegistrationForm, LoginForm, ChoiceTaskForm, ChangePageForm,
    ChangeTaskStatusForm1, CreateTaskForm, ChoiceFreelancerForm,
    ChangeTaskStatusForm
    )


FREELANCER = 1
CUSTOMER = 2

CREATED = 1
PUBLISHED = 2
FREELANCERS_DETECTED = 3
IN_WORK = 4
STOPPED = 5
IN_REVIEW = 6
DONE = 7


def create_app():
    app = Flask(__name__)
    app.config.from_pyfile('config.py')
    db.init_app(app)
    migrate = Migrate(app, db, render_as_batch=True)

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(user_id)

    @app.route('/', methods=['GET', 'POST'])
    def index():
        title = 'Главная страница'
        form = IndexForm()

        if request.method == 'POST':
            if form.validate_on_submit():
                if form.submit_for_signin.data:
                    return redirect(url_for('login'))
                if form.submit_for_signup.data:
                    return redirect(url_for('registration'))
            else:
                flash('Что-то пошло не так')
                return render_template('index.html', title=title, form=form)

        return render_template('index.html', title=title, form=form)

    @app.route('/registration', methods=['GET', 'POST'])
    def registration():
        title = 'Регистрация пользователя'
        form = RegistrationForm()
        form.role.choices = [(role.id, role.role) for role in UserRole.query.all()]

        if request.method == 'POST':
            if form.validate_on_submit():
                user_name = form.user_name.data
                if User.query.filter(User.user_name == user_name).count():
                    flash('Пользователь с таким именем уже существует')
                
                password1 = form.password1.data
                password2 = form.password2.data

                if not password1 == password2:
                    flash('Пароли не совпадают')

                user = User(
                    user_name=user_name,
                    public_bio=form.public_bio.data,
                    role=form.role.data,
                    email=form.email.data,
                    phone=form.phone.data,
                )
                user.set_password(password1)

                db.session.add(user)
                db.session.commit()
                flash('Вы успешно зарегистрированы!')
                return redirect(url_for('login'))

        return render_template('registration.html', title=title, form=form)

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if current_user.is_authenticated:
            flash('Вы уже вошли')
            return redirect(url_for('index'))

        title = 'login'
        form = LoginForm()

        if request.method == 'POST':
            if form.validate_on_submit():
                user = User.query.filter(User.user_name == form.user_name.data).first()
                if user and user.check_password(form.password.data):
                    login_user(user)
                    flash('Вы успешно зашли на сайт')
                    user_id = user.id
                    if user.role == CUSTOMER:
                        return redirect(url_for('customer', user_id=user_id))
                    elif user.role == FREELANCER:
                        return redirect(url_for('freelancer', user_id=user_id))
                    else:
                        flash('Неправильное имя или пароль')
                        return render_template('login.html', title=title, form=form)

        return render_template('login.html', title=title, form=form)

    @app.route('/logout')
    def logout():
        logout_user()
        flash('Вы успешно вышли')
        return redirect(url_for('index'))

    @app.route('/customer/<int:user_id>/', methods=['GET', 'POST'])
    def customer(user_id):
        title = 'Все созданные заказы (статус created)'
        form = ChoiceTaskForm()
        tasks = Task.query.filter(Task.customer == user_id, Task.status == 1).all()
        form.tasks.choices = [(task.id, task.task_name) for task in tasks]
        form_change_page = ChangePageForm()

        if request.method == 'POST':

            if form_change_page.validate_on_submit() and form_change_page.logout.data:
                return redirect(url_for('logout'))

            elif form_change_page.validate_on_submit() and form_change_page.create.data:
                return redirect(url_for('create_task', user_id=user_id))

            elif form_change_page.validate_on_submit() and form_change_page.created.data:
                return redirect(url_for('customer', user_id=user_id))

            elif form_change_page.validate_on_submit() and form_change_page.published.data:
                return redirect(url_for('published', user_id=user_id))

            elif form_change_page.validate_on_submit() and form_change_page.freelancers_detected.data:
                return redirect(url_for('freelancers_detected', user_id=user_id))

            elif form_change_page.validate_on_submit() and form_change_page.in_work.data:
                return redirect(url_for('in_work', user_id=user_id))

            elif form.validate_on_submit():
                task_id = form.tasks.data
                return redirect(url_for('task', task_id=task_id, user_id=user_id))

        return render_template('customer.html', title=title, form=form, user_id=user_id, form_change_page=form_change_page)

    @app.route('/customer/<int:user_id>/published/', methods=['GET', 'POST'])
    def published(user_id):
        title = 'Все опубликованные заказы (статус published)'
        form = ChoiceTaskForm()
        tasks = Task.query.filter(Task.customer == user_id, Task.status == 2).all()
        form.tasks.choices = [(task.id, task.task_name) for task in tasks]
        form_change_page = ChangePageForm()

        if request.method == 'POST':

            if form_change_page.validate_on_submit() and form_change_page.logout.data:
                return redirect(url_for('logout'))

            elif form_change_page.validate_on_submit() and form_change_page.create.data:
                return redirect(url_for('create_task', user_id=user_id))

            elif form_change_page.validate_on_submit() and form_change_page.created.data:
                return redirect(url_for('customer', user_id=user_id))

            elif form_change_page.validate_on_submit() and form_change_page.published.data:
                return redirect(url_for('published', user_id=user_id))

            elif form_change_page.validate_on_submit() and form_change_page.freelancers_detected.data:
                return redirect(url_for('freelancers_detected', user_id=user_id))

            elif form_change_page.validate_on_submit() and form_change_page.in_work.data:
                return redirect(url_for('in_work', user_id=user_id))

            elif form.validate_on_submit():
                task_id = form.tasks.data
                return redirect(url_for('task', task_id=task_id))

        return render_template('published.html', title=title, form=form, user_id=user_id, form_change_page=form_change_page)

    @app.route('/customer/<int:user_id>/freelancers_detected/', methods=['GET', 'POST'])
    def freelancers_detected(user_id):
        title = 'Все заказы, на которые откликнулись'
        form = ChoiceTaskForm()
        tasks = Task.query.filter(Task.customer == user_id, Task.status == 3).all()
        form.tasks.choices = [(task.id, task.task_name) for task in tasks]
        form_change_page = ChangePageForm()

        if request.method == 'POST':

            if form_change_page.validate_on_submit() and form_change_page.logout.data:
                return redirect(url_for('logout'))

            elif form_change_page.validate_on_submit() and form_change_page.create.data:
                return redirect(url_for('create_task', user_id=user_id))

            elif form_change_page.validate_on_submit() and form_change_page.created.data:
                return redirect(url_for('customer', user_id=user_id))

            elif form_change_page.validate_on_submit() and form_change_page.published.data:
                return redirect(url_for('published', user_id=user_id))

            elif form_change_page.validate_on_submit() and form_change_page.freelancers_detected.data:
                return redirect(url_for('freelancers_detected', user_id=user_id))

            elif form_change_page.validate_on_submit() and form_change_page.in_work.data:
                return redirect(url_for('in_work', user_id=user_id))

            elif form.validate_on_submit():
                task_id = form.tasks.data
                return redirect(url_for('task_in_work', task_id=task_id, user_id=user_id))

        return render_template('freelancers_detected.html', title=title, form=form, user_id=user_id, form_change_page=form_change_page)

    @app.route('/customer/<int:user_id>/in_work/', methods=['GET', 'POST'])
    def in_work(user_id):
        title = 'Все заказы в работе'
        form = ChoiceTaskForm()
        tasks = Task.query.filter(Task.customer == user_id, Task.status == 4).all()
        form.tasks.choices = [(task.id, task.task_name) for task in tasks]
        form_change_page = ChangePageForm()

        if request.method == 'POST':

            if form_change_page.validate_on_submit() and form_change_page.logout.data:
                return redirect(url_for('logout'))

            elif form_change_page.validate_on_submit() and form_change_page.create.data:
                return redirect(url_for('create_task', user_id=user_id))

            elif form_change_page.validate_on_submit() and form_change_page.created.data:
                return redirect(url_for('customer', user_id=user_id))

            elif form_change_page.validate_on_submit() and form_change_page.published.data:
                return redirect(url_for('published', user_id=user_id))

            elif form_change_page.validate_on_submit() and form_change_page.freelancers_detected.data:
                return redirect(url_for('freelancers_detected', user_id=user_id))

            elif form_change_page.validate_on_submit() and form_change_page.in_work.data:
                return redirect(url_for('in_work', user_id=user_id))

            elif form.validate_on_submit():
                task_id = form.tasks.data
                return redirect(url_for('task_in_work', task_id=task_id))

        return render_template('in_work.html', title=title, form=form, user_id=user_id, form_change_page=form_change_page)

    @app.route('/customer/<int:user_id>/task/<int:task_id>/', methods=['GET', 'POST'])
    def task(user_id, task_id):
        title = 'Информация по заказу (здесь мы можем менять с created на published)'
        form = ChangeTaskStatusForm1()
        form.status.choices = [(status.id, status.status) for status in TaskStatus.query.all()[:2]]
        form_change_page = ChangePageForm()

        if request.method == 'POST':
            if form_change_page.validate_on_submit() and form_change_page.logout.data:
                return redirect(url_for('logout'))

            elif form_change_page.validate_on_submit() and form_change_page.create.data:
                return redirect(url_for('create_task', user_id=user_id))

            elif form_change_page.validate_on_submit() and form_change_page.created.data:
                return redirect(url_for('customer', user_id=user_id))

            elif form_change_page.validate_on_submit() and form_change_page.published.data:
                return redirect(url_for('published', user_id=user_id))

            elif form_change_page.validate_on_submit() and form_change_page.freelancers_detected.data:
                return redirect(url_for('freelancers_detected', user_id=user_id))

            elif form_change_page.validate_on_submit() and form_change_page.in_work.data:
                return redirect(url_for('in_work', user_id=user_id))

            if form.validate_on_submit():
                status_id = form.status.data
                task = Task.query.get(task_id)
                task.status = status_id
                db.session.commit()

                flash(f"Статус заказа изменён на {status_id}")
                return render_template('customer_task.html', title=title, form=form,
                form_change_page=form_change_page, task_id=task_id, user_id=user_id)

        return render_template('customer_task.html', title=title, form=form, form_change_page=form_change_page,
            task_id=task_id, user_id=user_id)

    @app.route('/customer/<int:user_id>/task_in_work/<int:task_id>/', methods=['GET', 'POST'])
    def task_in_work(user_id, task_id):
        title = 'Все откликнувшиеся на заказ'
        form = ChoiceFreelancerForm()
        task = Task.query.get(task_id)
        freelancers = task.freelancers_who_responded.all()
        form.freelancers.choices = [(user.id, user.user_name) for user in freelancers]
        form_change_page = ChangePageForm()

        if request.method == 'POST':

            if form_change_page.validate_on_submit() and form_change_page.logout.data:
                return redirect(url_for('logout'))

            elif form_change_page.validate_on_submit() and form_change_page.create.data:
                return redirect(url_for('create_task', user_id=user_id))

            elif form_change_page.validate_on_submit() and form_change_page.created.data:
                return redirect(url_for('customer', user_id=user_id))

            elif form_change_page.validate_on_submit() and form_change_page.published.data:
                return redirect(url_for('published', user_id=user_id))

            elif form_change_page.validate_on_submit() and form_change_page.freelancers_detected.data:
                return redirect(url_for('freelancers_detected', user_id=user_id))

            elif form_change_page.validate_on_submit() and form_change_page.in_work.data:
                return redirect(url_for('in_work', user_id=user_id))

            if form.validate_on_submit():
                task = Task.query.get(task_id)
                status = TaskStatus.query.filter(TaskStatus.status == 'in_work').one()
                task.status = status.id
                task.freelancer = form.freelancers.data
                db.session.commit()

                flash(f"Статус заказа изменён на {status}")
                return render_template('task_in_work.html', title=title, form=form, task_id=task_id, form_change_page=form_change_page, user_id=user_id)

        return render_template('task_in_work.html', title=title, form=form, task_id=task_id, form_change_page=form_change_page, user_id=user_id)

    @app.route('/customer/<int:user_id>/create_task/', methods=['GET', 'POST'])
    def create_task(user_id):
        title = 'Создание заказа'
        form = CreateTaskForm()
        status = TaskStatus.query.filter(TaskStatus.status == 'created').one()
        customer = User.query.get(user_id)

        if request.method == 'POST':
            if form.validate_on_submit():
                task = Task(
                    task_name=form.task_name.data,
                    description=form.description.data,
                    price=form.price.data,
                    deadline=form.deadline.data,
                    status=status.id,
                    customer=customer.id
                )
                db.session.add(task)
                db.session.commit()

                flash('Вы успешно создали заказ!')
                return redirect(url_for('customer', user_id=user_id))

        return render_template('create_task.html', title=title, form=form, user_id=user_id)

    @app.route('/freelancer/<int:user_id>/', methods=['GET', 'POST'])
    def freelancer(user_id):
        title = 'Все актуальные заказы'
        form = ChoiceTaskForm()
        tasks = Task.query.filter(Task.status.in_([2,3])).all()
        form.tasks.choices = [(task.id, task.task_name) for task in tasks]
        form_change_page = ChangePageForm()
        
        if request.method == 'POST':
            
            if form_change_page.validate_on_submit() and form_change_page.logout.data:
                return redirect(url_for('logout'))
            
            if form.validate_on_submit():
                task = Task.query.get(form.tasks.data)
                user = User.query.get(user_id)
                task.freelancers_who_responded.append(user)
                status = TaskStatus.query.filter(TaskStatus.status == 'freelancers_detected').one()
                task.status = status.id
                db.session.commit()

                flash(f"Статус заказа изменён на {status}")
                return render_template(
                    'freelancer.html', title=title, form=form,
                    form_change_page=form_change_page, user_id=user_id
                    )

        return render_template('freelancer.html', title=title, form=form, form_change_page=form_change_page, user_id=user_id)

    @app.route('/change_task_status_from_in_work', methods=['GET', 'POST'])
    def change_task_status_from_in_work():

        title = 'Тестируем task.status: in_work -> in_review'
        form_url = url_for('change_task_status_from_in_work')

        allowed_status_codes = [ 'in_review' ]
        status_list = TaskStatus.query.filter(TaskStatus.status.in_(allowed_status_codes))

        form = ChangeTaskStatusForm()
        form.task_id.choices = [(g.id, g.task_name) for g in Task.query.all()]
        form.status.choices = [(g.id, g.status) for g in status_list]

        if request.method == 'GET':

            title += ' GET'
            return render_template(
                'change_task_status.form.html',
                title=title,
                form=form,
                form_url=form_url
            )

        elif request.method == 'POST':
            
            title += ' POST'
            if form.validate_on_submit():

                current_task = request.form.get('task_id');
                new_status = request.form.get('status');

                task = Task.query.get(current_task)
                task.status = new_status
                db.session.commit()

                title += ' SUCCESS'
                task = Task.query.get(current_task)
                return render_template(
                    'change_task_status.success.html',
                    title=title,
                    task=task.__dict__
                )

            return render_template(
                'change_task_status.form.html',
                title=title,
                form=form,
                form_url=form_url
            )

    @app.route('/change_task_status_from_in_review', methods=['GET', 'POST'])
    def change_task_status_from_in_review():

        title = 'Тестируем task.status: in_review -> (in_work|done)'
        form_url = url_for('change_task_status_from_in_review')

        allowed_status_codes = [ 'in_work', 'done' ]
        status_list = TaskStatus.query.filter(TaskStatus.status.in_(allowed_status_codes))

        form = ChangeTaskStatusForm()
        form.task_id.choices = [(g.id, g.task_name) for g in Task.query.all()]
        form.status.choices = [(g.id, g.status) for g in status_list]

        if request.method == 'GET':

            title += ' GET'
            return render_template(
                'change_task_status.form.html',
                title=title,
                form=form,
                form_url=form_url
            )

        elif request.method == 'POST':
            
            title += ' POST'
            if form.validate_on_submit():

                current_task = request.form.get('task_id');
                new_status = request.form.get('status');

                task = Task.query.get(current_task)
                task.status = new_status
                db.session.commit()

                title += ' SUCCESS'
                task = Task.query.get(current_task)
                return render_template(
                    'change_task_status.success.html',
                    title=title,
                    task=task.__dict__
                )

            return render_template(
                'change_task_status.form.html',
                title=title,
                form=form,
                form_url=form_url
            )

    return app
