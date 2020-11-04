from flask import Flask, render_template, flash, redirect, url_for, request
from flask_migrate import Migrate
from flask_login import LoginManager, login_user, logout_user, current_user, login_required

from webapp.model import (
    db, Email, Phone, Task, TaskStatus, Tag, User, UserRole,
    freelancers_who_responded
    )
from webapp.forms import (
    IndexForm, RegistrationForm, LoginForm, ChoiceTaskForm, ChangePageForm,
    ChangeTaskStatusForm1, CreateTaskForm, ChoiceFreelancerForm,
    ChangeTaskStatusForm, DismissFreelancerFromTaskForm, ViewTaskForm
    )
from webapp.errors import LocalError


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
    
    def get_task_status_id(code):
        '''Получить по текстовому коду, id для task_status.'''
        task_status = TaskStatus.query.filter(
            TaskStatus.status == f'{code}'
        ).first()
        if task_status == None:
            raise Exception(f'Database does not have TaskStatus "{code}"')
        return task_status.id

    def get_user_role_id(code):
        '''Получить по текстовому коду, id для user_role.'''
        user_role = UserRole.query.filter(
            UserRole.role == f'{code}'
        ).first()
        if user_role == None:
            raise Exception(f'Database does not have TaskStatus "{code}"')
        return user_role.id


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

        title = 'Вход'
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
    @login_required
    def customer(user_id):
        title = 'Все созданные заказы (статус created)'
        form = ChoiceTaskForm()
        tasks = Task.query.filter(Task.customer == user_id, Task.status == CREATED).all()
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
    @login_required
    def published(user_id):
        title = 'Все опубликованные заказы (статус published)'
        form = ChoiceTaskForm()
        tasks = Task.query.filter(Task.customer == user_id, Task.status == PUBLISHED).all()
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
                return redirect(url_for('task', user_id=user_id, task_id=task_id))

        return render_template('published.html', title=title, form=form, user_id=user_id, form_change_page=form_change_page)

    @app.route('/customer/<int:user_id>/freelancers_detected/', methods=['GET', 'POST'])
    @login_required
    def freelancers_detected(user_id):
        title = 'Все заказы, на которые откликнулись'
        form = ChoiceTaskForm()
        tasks = Task.query.filter(Task.customer == user_id, Task.status == FREELANCERS_DETECTED).all()
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
    @login_required
    def in_work(user_id):
        title = 'Все заказы в работе'
        form = ChoiceTaskForm()
        tasks = Task.query.filter(Task.customer == user_id, Task.status == IN_WORK).all()
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
    @login_required
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

        return render_template('customer_task.html', title=title, form=form, form_change_page=form_change_page,
            task_id=task_id, user_id=user_id)

    @app.route('/customer/<int:user_id>/task_in_work/<int:task_id>/', methods=['GET', 'POST'])
    @login_required
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

    @app.route('/customer/<int:user_id>/create_task/', methods=['GET', 'POST'])
    @login_required
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
    @login_required
    def freelancer(user_id):
        title = 'Все актуальные заказы'
        form = ChoiceTaskForm()
        tasks = Task.query.filter(Task.status.in_([PUBLISHED, FREELANCERS_DETECTED])).all()
        form.tasks.choices = [(task.id, task.task_name) for task in tasks]
        form_change_page = ChangePageForm()
        
        if request.method == 'POST':
            
            if form_change_page.validate_on_submit() and form_change_page.logout.data:
                return redirect(url_for('logout'))

            elif form_change_page.validate_on_submit() and form_change_page.actual.data:
                return redirect(url_for('freelancer', user_id=user_id))

            elif form_change_page.validate_on_submit() and form_change_page.in_work.data:
                return redirect(url_for('fl_in_work', user_id=user_id))

            elif form_change_page.validate_on_submit() and form_change_page.in_review.data:
                return redirect(url_for('', user_id=user_id))
            
            if form.validate_on_submit():
                task = Task.query.get(form.tasks.data)
                user = User.query.get(user_id)
                freelancers = task.freelancers_who_responded.all()
                if user in freelancers:
                    flash('Вы уже откликнулись на эту задачу!')
                else:
                    task.freelancers_who_responded.append(user)
                    status = TaskStatus.query.filter(TaskStatus.status == 'freelancers_detected').one()
                    task.status = status.id
                    db.session.commit()
                    flash(f"Статус заказа изменён на {status}")

        return render_template('freelancer.html', title=title, form=form, form_change_page=form_change_page, user_id=user_id)

    @app.route('/freelancer/<int:user_id>/fl_in_work/', methods=['GET', 'POST'])
    @login_required
    def fl_in_work(user_id):
        title = 'Все заказы в работе'
        form = ChoiceTaskForm()
        tasks = Task.query.filter(Task.freelancer == user_id, Task.status == IN_WORK).all()
        form.tasks.choices = [(task.id, task.task_name) for task in tasks]
        form_change_page = ChangePageForm()

        if request.method == 'POST':

            if form_change_page.validate_on_submit() and form_change_page.logout.data:
                return redirect(url_for('logout'))

            elif form_change_page.validate_on_submit() and form_change_page.actual.data:
                return redirect(url_for('freelancer', user_id=user_id))

            elif form_change_page.validate_on_submit() and form_change_page.in_work.data:
                return redirect(url_for('fl_in_work', user_id=user_id))

            elif form_change_page.validate_on_submit() and form_change_page.in_review.data:
                return redirect(url_for('', user_id=user_id))

            elif form.validate_on_submit():
                task_id = form.tasks.data
                return redirect(url_for('', task_id=task_id))

        return render_template('fl_in_work.html', title=title, form=form, user_id=user_id, form_change_page=form_change_page)

    @app.route('/change_task_status_from_in_work', methods=['GET', 'POST'])
    def change_task_status_from_in_work():
        '''Задать маршрут по которому можно тестировать логику.

        Здесь мы хотим тестировать логику:
        ----------------------------------

        Отрезок позитивного пути - Фрилансер двигает заказ со статуса 'in_work'
        mна 'in_review'.
        '''
        title = 'Тестируем task.status: in_work -> in_review'
        form_url = url_for('change_task_status_from_in_work')

        allowed_status_codes = [ 'in_review' ]
        status_list = TaskStatus.query.filter(TaskStatus.status.in_(allowed_status_codes))

        form = ChangeTaskStatusForm()
        form.task_id.choices = [(g.id, g.task_name) for g in Task.query.all()]
        form.status.choices = [(g.id, g.status) for g in status_list]

        if request.method == 'GET':

            return render_template(
                'change_task_status.form.html',
                title=title,
                form=form,
                form_url=form_url
            )

        elif request.method == 'POST':

            try:
                if not form.validate_on_submit():
                    raise LocalError('Некорректно заполнены поля формы.')

                current_task_id = request.form.get('task_id');
                new_status_id = request.form.get('status');

                # На время тестов собираем свежие снимки данных.
                task_debug_info1 = (
                    Task
                    .query
                    .get(current_task_id)
                    .generate_level_2_debug_dictionary()
                )

                # Проверяем - все ли входные данные адекватны.
                task = Task.query.get(current_task_id)
                if task == None:
                    raise LocalError('Операция не может быть выполнена, потому что указанная в запросе Задача не существует.')

                task.status = new_status_id
                db.session.commit()

                # На время тестов собираем свежие снимки данных.
                task_debug_info2 = (
                    Task
                    .query
                    .get(current_task_id)
                    .generate_level_2_debug_dictionary()
                )
            except LocalError as e:
                db.session.rollback()
                return render_template(
                    'change_task_status.form.html',
                    title=title,
                    form=form,
                    form_url=form_url,
                    feedback_message=e.args[0]
                )
            except:
                db.session.rollback()
                raise
            else:
                return render_template(
                    'change_task_status.success.html',
                    title=title,
                    task_before=task_debug_info1,
                    task_after=task_debug_info2
                )

    @app.route('/change_task_status_from_in_review', methods=['GET', 'POST'])
    def change_task_status_from_in_review():
        '''Задать маршрут по которому можно тестировать логику.

        Здесь мы хотим тестировать логику:
        ----------------------------------

        Отрезок позитивного пути - Заказчик двигает заказ со статуса 'in_review'
        либо на 'in_work', либо на 'done'.
        '''
        title = 'Тестируем task.status: in_review -> (in_work|done)'
        form_url = url_for('change_task_status_from_in_review')

        allowed_status_codes = [ 'in_work', 'done' ]
        status_list = TaskStatus.query.filter(TaskStatus.status.in_(allowed_status_codes))

        form = ChangeTaskStatusForm()
        form.task_id.choices = [(g.id, g.task_name) for g in Task.query.all()]
        form.status.choices = [(g.id, g.status) for g in status_list]

        if request.method == 'GET':

            return render_template(
                'change_task_status.form.html',
                title=title,
                form=form,
                form_url=form_url
            )

        elif request.method == 'POST':

            try:
                if not form.validate_on_submit():
                    raise LocalError('Некорректно заполнены поля формы.')

                current_task_id = request.form.get('task_id');
                new_status_id = request.form.get('status');

                # На время тестов собираем свежие снимки данных.
                task_debug_info1 = (
                    Task
                    .query
                    .get(current_task_id)
                    .generate_level_2_debug_dictionary()
                )

                # Проверяем - все ли входные данные адекватны.
                task = Task.query.get(current_task_id)
                if task == None:
                    raise LocalError('Операция не может быть выполнена, потому что указанная в запросе Задача не существует.')

                task.status = new_status_id
                db.session.commit()

                # На время тестов собираем свежие снимки данных.
                task_debug_info2 = (
                    Task
                    .query
                    .get(current_task_id)
                    .generate_level_2_debug_dictionary()
                )
            except LocalError as e:
                db.session.rollback()
                return render_template(
                    'change_task_status.form.html',
                    title=title,
                    form=form,
                    form_url=form_url,
                    feedback_message=e.args[0]
                )
            except:
                db.session.rollback()
                raise
            else:
                return render_template(
                    'change_task_status.success.html',
                    title=title,
                    task_before=task_debug_info1,
                    task_after=task_debug_info2
                )

    @app.route('/cancel_task', methods=['GET', 'POST'])
    def cancel_task():
        '''Задать маршрут по которому можно тестировать логику.

        Здесь мы хотим тестировать логику:
        ----------------------------------

        Отрезок негативного пути - Заказчик отменяет Задачу.
        '''
        title = 'Тестируем customer.cancel_task'
        form_url = url_for('cancel_task')

        allowed_status_codes = [ 'stopped' ]
        status_list = TaskStatus.query.filter(TaskStatus.status.in_(allowed_status_codes))

        form = ChangeTaskStatusForm()
        form.task_id.choices = [(g.id, g.task_name) for g in Task.query.all()]
        form.status.choices = [(g.id, g.status) for g in status_list]

        if request.method == 'GET':

            return render_template(
                'change_task_status.form.html',
                title=title,
                form=form,
                form_url=form_url
            )

        elif request.method == 'POST':

            try:
                if not form.validate_on_submit():
                    raise LocalError('Некорректно заполнены поля формы.')

                current_task_id = request.form.get('task_id');
                new_status_id = request.form.get('status');

                freelancer_role = get_user_role_id(code='freelancer')

                # На время тестов собираем свежие снимки данных.
                task_debug_info1 = (
                    Task
                    .query
                    .get(current_task_id)
                    .generate_level_2_debug_dictionary()
                )

                # Поставить Задаче новый Статус.
                task = Task.query.get(current_task_id)
                task.status = new_status_id
                db.session.commit()

                # Отцепить от Задачи - Фрилансера-подтверждённого исполнителя.
                freelancer = User.query.filter(
                    User.role == freelancer_role,
                    User.id == task.freelancer
                ).first()
                if freelancer != None:
                    task.freelancer = None
                    db.session.commit()

                # Отцепить от Задачи - Предваритально Откликнувшихся
                # Фрилансеров.
                freelancers = task.freelancers_who_responded.all()
                task.freelancers_who_responded = task.freelancers_who_responded.filter(
                    User.role != freelancer_role
                )
                db.session.commit()

                # На время тестов собираем свежие снимки данных.
                task_debug_info2 = (
                    Task
                    .query
                    .get(current_task_id)
                    .generate_level_2_debug_dictionary()
                )
            except LocalError as e:
                db.session.rollback()
                return render_template(
                    'change_task_status.form.html',
                    title=title,
                    form=form,
                    form_url=form_url,
                    feedback_message=e.args[0]
                )
            except:
                db.session.rollback()
                raise
            else:
                return render_template(
                    'change_task_status.success.html',
                    title=title,
                    task_before=task_debug_info1,
                    task_after=task_debug_info2
                )

    @app.route('/dismiss_confirmed_freelancer_from_task', methods=['GET', 'POST'])
    def dismiss_confirmed_freelancer_from_task():
        '''Задать маршрут по которому можно тестировать логику.

        Здесь мы хотим тестировать логику:
        ----------------------------------

        Отрезок негативного пути - Отцепляем от Задачи одного из предварительно
        Откликнувшихся Фрилансеров.
        '''
        title = 'Тестируем freelancer.dismiss_confirmed_freelancer_from_task'
        form_url = url_for('dismiss_confirmed_freelancer_from_task')

        form = DismissFreelancerFromTaskForm()
        form.task_id.choices = [(g.id, g.task_name) for g in Task.query.all()]
        form.user_id.choices = [(g.id, g.user_name) for g in User.query.all()]

        if request.method == 'GET':

            return render_template(
                'dismiss_freelancer_from_task.form.html',
                title=title,
                form=form,
                form_url=form_url
            )

        elif request.method == 'POST':

            try:
                if not form.validate_on_submit():
                    raise LocalError('Некорректно заполнены поля формы.')

                current_task_id = request.form.get('task_id');
                current_user_id = request.form.get('user_id');

                # Проверяем - все ли входные данные адекватны.
                status_created   = get_task_status_id(code='created');
                status_in_work   = get_task_status_id(code='in_work');
                status_in_review = get_task_status_id(code='in_review');

                freelancer_role = get_user_role_id(code='freelancer')

                task = Task.query.get(current_task_id)
                if task == None:
                    raise LocalError('Операция не может быть выполнена, потому что указанная в запросе Задача не существует.')

                freelancer = User.query.filter(
                    User.id == current_user_id
                ).first()
                if freelancer == None:
                    raise LocalError('Операция не может быть выполнена, потому что указанный в запросе Фрилансер не существует.')
                if freelancer.role != freelancer_role:
                    raise LocalError('Операция не может быть выполнена, потому что указанный в запросе пользователь не является Фрилансером.')
                if task.freelancer != freelancer.id:
                    raise LocalError('Операция не может быть выполнена, потому что указанный в запросе Фрилансер не привязан к указанной Задаче как Предварительно Откликнувшийся Фрилансер.')

                # На время тестов собираем свежие снимки данных.
                task_debug_info1 = (
                    Task
                    .query
                    .get(current_task_id)
                    .generate_level_2_debug_dictionary()
                )

                # Отцепить от Задачи - Фрилансера-подтверждённого исполнителя.
                task.freelancer = None
                if (
                        task.status == status_in_work or
                        task.status == status_in_review
                    ):
                    # Если это был удалён последний Фрилансер в списке; и
                    # если задача - в Статусе когда нельзя делать
                    # последующие шаги к Главной Цели, не имея Фрилансеров в
                    # этом списке, тогда надо перевести Задачу в Статус
                    # 'created'.
                    task.status = status_created
                db.session.commit()

                # На время тестов собираем свежие снимки данных.
                task_debug_info2 = (
                    Task
                    .query
                    .get(current_task_id)
                    .generate_level_2_debug_dictionary()
                )
            except LocalError as e:
                db.session.rollback()
                return render_template(
                    'dismiss_freelancer_from_task.form.html',
                    title=title,
                    form=form,
                    form_url=form_url,
                    feedback_message=e.args[0]
                )
            except:
                db.session.rollback()
                raise
            else:
                return render_template(
                    'dismiss_freelancer_from_task.success.html',
                    title=title,
                    task_before=task_debug_info1,
                    task_after=task_debug_info2
                )

    @app.route('/dismiss_responded_freelancer_from_task', methods=['GET', 'POST'])
    def dismiss_responded_freelancer_from_task():
        '''Задать маршрут по которому можно тестировать логику.

        Здесь мы хотим тестировать логику:
        ----------------------------------

        Отрезок негативного пути - Отцепляем от Задачи одного из предварительно
        Откликнувшихся Фрилансеров.
        '''
        title = 'Тестируем freelancer.dismiss_responded_freelancer_from_task'
        form_url = url_for('dismiss_responded_freelancer_from_task')

        form = DismissFreelancerFromTaskForm()
        form.task_id.choices = [(g.id, g.task_name) for g in Task.query.all()]
        form.user_id.choices = [(g.id, g.user_name) for g in User.query.all()]

        if request.method == 'GET':

            return render_template(
                'dismiss_freelancer_from_task.form.html',
                title=title,
                form=form,
                form_url=form_url
            )

        elif request.method == 'POST':

            try:
                if not form.validate_on_submit():
                    raise LocalError('Некорректно заполнены поля формы.')

                current_task_id = request.form.get('task_id');
                current_user_id = request.form.get('user_id');

                # Проверяем - все ли входные данные адекватны.
                status_created              = get_task_status_id(code='created');
                status_freelancers_detected = get_task_status_id(code='freelancers_detected');

                freelancer_role = get_user_role_id(code='freelancer')

                task = Task.query.get(current_task_id)
                if task == None:
                    raise LocalError('Операция не может быть выполнена, потому что указанная в запросе Задача не существует.')

                freelancer = User.query.filter(
                    User.id == current_user_id
                ).first()
                if freelancer == None:
                    raise LocalError('Операция не может быть выполнена, потому что указанный в запросе Фрилансер не существует.')
                if freelancer.role != freelancer_role:
                    raise LocalError('Операция не может быть выполнена, потому что указанный в запросе пользователь не является Фрилансером.')

                freelancer = task.freelancers_who_responded.filter(
                    User.id == current_user_id
                ).first()
                if freelancer == None:
                    raise LocalError('Операция не может быть выполнена, потому что указанный в запросе Фрилансер не привязан к указанной Задаче как Предварительно Откликнувшийся Фрилансер.')

                # На время тестов собираем свежие снимки данных.
                task_debug_info1 = (
                    Task
                    .query
                    .get(current_task_id)
                    .generate_level_2_debug_dictionary()
                )

                # Отцепить от Задачи - Конкретного Предваритально
                # Откликнувшегося Фрилансера.
                freelancers = task.freelancers_who_responded.filter(
                    User.role == freelancer_role,
                    User.id != current_user_id
                )
                task.freelancers_who_responded = freelancers
                if task.status == status_freelancers_detected:
                    if not freelancers.count() > 0:
                        # Если это был удалён последний Фрилансер в списке; и
                        # если задача - в Статусе когда нельзя делать
                        # последующие шаги к Главной Цели, не имея Фрилансеров в
                        # этом списке, тогда надо перевести Задачу в Статус
                        # 'created'.
                        task.status = status_created
                db.session.commit()

                # На время тестов собираем свежие снимки данных.
                task_debug_info2 = (
                    Task
                    .query
                    .get(current_task_id)
                    .generate_level_2_debug_dictionary()
                )
            except LocalError as e:
                db.session.rollback()
                return render_template(
                    'dismiss_freelancer_from_task.form.html',
                    title=title,
                    form=form,
                    form_url=form_url,
                    feedback_message=e.args[0]
                )
            except:
                db.session.rollback()
                raise
            else:
                return render_template(
                    'dismiss_freelancer_from_task.success.html',
                    title=title,
                    task_before=task_debug_info1,
                    task_after=task_debug_info2
                )

    @app.route('/view_task', methods=['GET', 'POST'])
    def view_task():
        '''Задать маршрут по которому можно просмотреть состояние Задачи.'''
        title = 'Просматриваем состояние Задачи'
        form_url = url_for('view_task')

        form = ViewTaskForm()
        form.task_id.choices = [(g.id, g.task_name) for g in Task.query.all()]

        if request.method == 'GET':

            return render_template(
                'view_task.form.html',
                title=title,
                form=form,
                form_url=form_url
            )

        elif request.method == 'POST':

            try:
                if not form.validate_on_submit():
                    raise LocalError('Некорректно заполнены поля формы.')

                current_task_id = request.form.get('task_id');

                # Проверяем - все ли входные данные адекватны.
                task = Task.query.get(current_task_id)
                if task == None:
                    raise LocalError('Указанная в запросе Задача не существует.. Попробуйте изменить критерий поиска и попровать снова.')

                # На время тестов собираем свежие снимки данных.
                task_debug_info = (
                    Task
                    .query
                    .get(current_task_id)
                    .generate_level_2_debug_dictionary()
                )
            except LocalError as e:
                return render_template(
                    'view_task.form.html',
                    title=title,
                    form=form,
                    form_url=form_url,
                    feedback_message=e.args[0]
                )
            else:
                return render_template(
                    'view_task.success.html',
                    title=title,
                    task=task_debug_info
                )

    return app
