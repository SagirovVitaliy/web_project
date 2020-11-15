from flask import Flask, render_template, flash, redirect, url_for, request
from flask_migrate import Migrate
from flask_login import LoginManager, login_user, logout_user, current_user, login_required

from webapp.model import (
    db, Email, Phone, Task, TaskStatus, Tag, User, UserRole,
    freelancers_who_responded
    )
from webapp.forms import (
    RegistrationForm, LoginForm, CreateTaskForm, ChoiceFreelancerForm,
    ChangeTaskStatusForm, DismissFreelancerFromTaskForm, ViewTaskForm,
    )
from webapp.errors import ValidationError
import webapp.validators as validators
from webapp.model import (
    CUSTOMER,
    FREELANCER,

    CREATED,
    PUBLISHED,
    FREELANCERS_DETECTED,
    IN_WORK,
    STOPPED,
    IN_REVIEW,
    DONE,
    )


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

        return render_template('start_page/index.html', title=title)

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

        return render_template('start_page/registration.html', title=title, form=form)

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if current_user.is_authenticated:
            flash('Вы уже вошли')
            user = User.query.get(current_user.get_id())
            if user.role == CUSTOMER:
                return redirect(url_for('customer', user_id=user.id))
            elif user.role == FREELANCER:
                return redirect(url_for('freelancer', user_id=user.id))

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

        return render_template('start_page/login.html', title=title, form=form)

    @app.route('/logout')
    def logout():
        logout_user()
        flash('Вы успешно вышли')
        return redirect(url_for('index'))

    @app.route('/customer/<int:user_id>/', methods=['GET', 'POST'])
    @login_required
    def customer(user_id):
        title = 'Все созданные заказы (статус created)'
        tasks = Task.query.filter(Task.customer == user_id, Task.status == CREATED).all()

        return render_template('home_page/customer.html', title=title, tasks=tasks, user_id=user_id)

    @app.route('/customer/<int:user_id>/published/', methods=['GET', 'POST'])
    @login_required
    def published(user_id):
        title = 'Все опубликованные заказы (статус published)'
        tasks = Task.query.filter(Task.customer == user_id, Task.status == PUBLISHED).all()

        return render_template('home_page/published.html', title=title, user_id=user_id, tasks=tasks)

    @app.route('/customer/<int:user_id>/freelancers_detected/', methods=['GET', 'POST'])
    @login_required
    def freelancers_detected(user_id):
        title = 'Все заказы, на которые откликнулись'
        tasks = Task.query.filter(Task.customer == user_id, Task.status == FREELANCERS_DETECTED).all()

        return render_template('home_page/freelancers_detected.html', title=title, user_id=user_id, tasks=tasks)

    @app.route('/customer/<int:user_id>/in_work/', methods=['GET', 'POST'])
    @login_required
    def in_work(user_id):
        title = 'Все заказы в работе'
        tasks = Task.query.filter(Task.customer == user_id, Task.status == IN_WORK).all()

        return render_template('home_page/in_work.html', title=title, tasks=tasks, user_id=user_id)

    @app.route('/customer/<int:user_id>/ct_task/<int:task_id>/', methods=['GET', 'POST'])
    @login_required
    def ct_task(user_id, task_id):
        title = 'Информация по заказу (здесь мы можем менять с created на published)'
        task = Task.query.get(task_id)
        task_name = task.task_name
        description = task.description
        price = task.price
        deadline = task.deadline

        if request.method == 'POST':
            if task.status == 1:
                task.status = PUBLISHED
                db.session.commit()
                flash('Заказ опубликован')
            elif task.status == 2:
                task.status = CREATED
                db.session.commit()
                flash('Заказ снят с публикации')

        return render_template(
            'ct_task_information.html', title=title, task_id=task_id, user_id=user_id, task_name=task_name, 
            description=description, price=price, deadline=deadline, task=task
            )

    @app.route('/customer/<int:user_id>/ready_fl/<int:task_id>/', methods=['GET', 'POST'])
    @login_required
    def ready_fl(user_id, task_id):
        title = 'Все откликнувшиеся на заказ'
        task = Task.query.get(task_id)
        freelancers = task.freelancers_who_responded.all()

        return render_template('ready_fl.html', title=title, task_id=task_id, user_id=user_id, freelancers=freelancers)

    @app.route('/customer/<int:user_id>/ready_fl/<int:task_id>/selected_fl/<int:fl_id>', methods=['GET','POST'])
    @login_required
    def selected_fl(user_id, task_id, fl_id):
        title = 'Информация по фрилнсеру'
        freelancer = User.query.get(fl_id)
        user_name = freelancer.user_name
        public_bio = freelancer.public_bio

        if request.method == 'POST':
            task = Task.query.get(task_id)
            status = TaskStatus.query.filter(TaskStatus.id == IN_WORK).one()
            task.status = status.id
            task.freelancer = fl_id
            db.session.commit()
            flash('Теперь ваш заказ в работе')

        return render_template(
            'selected_fl.html', title=title, task_id=task_id, user_id=user_id,
            user_name = user_name, public_bio=public_bio, fl_id=fl_id
            )

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
        tasks = Task.query.filter(Task.status.in_([PUBLISHED, FREELANCERS_DETECTED])).all()

        return render_template('freelancer.html', title=title, tasks=tasks, user_id=user_id)

    @app.route('/freelancer/<int:user_id>/fl_task/<int:task_id>', methods=['GET', 'POST'])
    @login_required
    def fl_task(user_id, task_id):
        title = 'Информация по заказы'
        task = Task.query.get(task_id)
        task_name = task.task_name
        description = task.description
        price = task.price
        deadline = task.deadline

        if request.method == 'POST':
            user = User.query.get(user_id)
            freelancers = task.freelancers_who_responded.all()
            if user in freelancers:
                flash('Вы уже откликнулись на эту задачу!')
            else:
                task.freelancers_who_responded.append(user)
                task.status = FREELANCERS_DETECTED
                db.session.commit()
                flash('Вы откликнулись на задачу, ждите решения заказчика')

        return render_template(
            'fl_task_information.html', title=title, task_id=task_id, user_id=user_id, task_name=task_name, 
            description=description, price=price, deadline=deadline, task=task
            )

    @app.route('/freelancer/<int:user_id>/fl_in_work/', methods=['GET', 'POST'])
    @login_required
    def fl_in_work(user_id):
        title = 'Все заказы в работе'
        tasks = Task.query.filter(Task.freelancer == user_id, Task.status == IN_WORK).all()

        if request.method == 'POST':

            if form.validate_on_submit():
                task_id = form.tasks.data
                return redirect(url_for('', task_id=task_id))

        return render_template('fl_in_work.html', title=title, user_id=user_id, tasks=tasks )

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

        allowed_statuses = [ IN_REVIEW ]
        status_list = TaskStatus.query.filter(TaskStatus.id.in_(allowed_statuses))

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
                validators.validate_form(form)

                current_task_id = request.form.get('task_id');
                new_status_id = request.form.get('status');

                # Сделать свежий снимок Задачи для дебага.
                task_debug_info1 = (
                    Task
                    .query
                    .get(current_task_id)
                    .generate_level_2_debug_dictionary()
                )

                task = Task.query.get(current_task_id)
                validators.validate_task_existence(task)

                # Внести изменения в Задачу.
                task.status = new_status_id
                db.session.commit()

                # Сделать свежий снимок Задачи для дебага.
                task_debug_info2 = (
                    Task
                    .query
                    .get(current_task_id)
                    .generate_level_2_debug_dictionary()
                )
            except ValidationError as e:
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

        allowed_statuses = [ IN_WORK, DONE ]
        status_list = TaskStatus.query.filter(TaskStatus.id.in_(allowed_statuses))

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
                validators.validate_form(form)

                current_task_id = request.form.get('task_id');
                new_status_id = request.form.get('status');

                # Сделать свежий снимок Задачи для дебага.
                task_debug_info1 = (
                    Task
                    .query
                    .get(current_task_id)
                    .generate_level_2_debug_dictionary()
                )

                task = Task.query.get(current_task_id)
                validators.validate_task_existence(task)

                # Внести изменения в Задачу.
                task.status = new_status_id
                db.session.commit()

                # Сделать свежий снимок Задачи для дебага.
                task_debug_info2 = (
                    Task
                    .query
                    .get(current_task_id)
                    .generate_level_2_debug_dictionary()
                )
            except ValidationError as e:
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
                validators.validate_form(form)

                current_task_id = request.form.get('task_id');
                new_status_id = request.form.get('status');

                # Сделать свежий снимок Задачи для дебага.
                task_debug_info1 = (
                    Task
                    .query
                    .get(current_task_id)
                    .generate_level_2_debug_dictionary()
                )

                task = Task.query.get(current_task_id)
                validators.validate_task_existence(task)

                # Внести изменения в задачу.
                task.status = new_status_id
                db.session.commit()

                # Отцепить от Задачи: Фрилансера-Подтверждённого Исполнителя.
                user = User.query.get(task.freelancer)
                validators.validate_user_existence(user)
                validators.validate_if_user_is_freelancer(user)
                validators.is_user_connected_to_task_as_confirmed_freelancer(
                    user=user, task=task
                )

                # Отцепить от Задачи: всех Предваритально Откликнувшихся
                # Фрилансеров.
                freelancers = task.freelancers_who_responded.all()
                task.freelancers_who_responded = task.freelancers_who_responded.filter(
                    User.role != FREELANCER
                )
                db.session.commit()

                # Сделать свежий снимок Задачи для дебага.
                task_debug_info2 = (
                    Task
                    .query
                    .get(current_task_id)
                    .generate_level_2_debug_dictionary()
                )
            except ValidationError as e:
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
                validators.validate_form(form)

                current_task_id = request.form.get('task_id');
                current_user_id = request.form.get('user_id');

                task = Task.query.get(current_task_id)
                validators.validate_task_existence(task)

                user = User.query.get(current_user_id)
                validators.validate_user_existence(user)
                validators.validate_if_user_is_freelancer(user)
                validators.is_user_connected_to_task_as_confirmed_freelancer(
                    user=user, task=task
                )

                # Сделать свежий снимок Задачи для дебага.
                task_debug_info1 = (
                    Task
                    .query
                    .get(current_task_id)
                    .generate_level_2_debug_dictionary()
                )

                # Отцепить от Задачи: Фрилансера-Подтверждённого Исполнителя.
                task.freelancer = None
                if (
                        task.status == IN_WORK or
                        task.status == IN_REVIEW
                    ):
                    # Если это был удалён последний Фрилансер в списке; и
                    # если задача - в Статусе когда нельзя делать
                    # последующие шаги к Главной Цели, не имея Фрилансеров в
                    # этом списке, тогда надо перевести Задачу в Статус
                    # 'created'.
                    task.status = CREATED
                db.session.commit()

                # Сделать свежий снимок Задачи для дебага.
                task_debug_info2 = (
                    Task
                    .query
                    .get(current_task_id)
                    .generate_level_2_debug_dictionary()
                )
            except ValidationError as e:
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
                validators.validate_form(form)

                current_task_id = request.form.get('task_id');
                current_user_id = request.form.get('user_id');

                task = Task.query.get(current_task_id)
                validators.validate_task_existence(task)

                user = User.query.get(current_user_id)
                validators.validate_user_existence(user)
                validators.validate_if_user_is_freelancer(user)
                validators.is_user_connected_to_task_as_responded_freelancer(
                    user=user, task=task
                )

                # Сделать свежий снимок Задачи для дебага.
                task_debug_info1 = (
                    Task
                    .query
                    .get(current_task_id)
                    .generate_level_2_debug_dictionary()
                )

                # Отцепить от Задачи: Предваритально Откликнувшегося Фрилансера.
                freelancers = task.freelancers_who_responded.filter(
                    User.role == FREELANCER,
                    User.id != current_user_id
                )
                task.freelancers_who_responded = freelancers
                if task.status == FREELANCERS_DETECTED:
                    if not freelancers.count() > 0:
                        # Если это был удалён последний Фрилансер в списке; и
                        # если задача - в Статусе когда нельзя делать
                        # последующие шаги к Главной Цели, не имея Фрилансеров в
                        # этом списке, тогда надо перевести Задачу в Статус
                        # 'created'.
                        task.status = CREATED
                db.session.commit()

                # Сделать свежий снимок Задачи для дебага.
                task_debug_info2 = (
                    Task
                    .query
                    .get(current_task_id)
                    .generate_level_2_debug_dictionary()
                )
            except ValidationError as e:
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
                validators.validate_form(form)

                current_task_id = request.form.get('task_id');

                task = Task.query.get(current_task_id)
                validators.validate_task_existence(
                    task=task,
                    failure_feedback='Указанная в запросе Задача не существует. Попробуйте изменить критерий поиска и попровать снова.'
                )

                # Сделать свежий снимок Задачи для дебага.
                task_debug_info = (
                    Task
                    .query
                    .get(current_task_id)
                    .generate_level_2_debug_dictionary()
                )
            except ValidationError as e:
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
