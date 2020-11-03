from flask import Flask, render_template, flash, redirect, url_for, request
from flask_migrate import Migrate

from webapp.model import (
    db, Email, Phone, Task, TaskStatus, Tag, User, UserRole,
    freelancers_who_responded
    )
from webapp.forms import (
    TaskForm, ChoiseForm, FreelancerForm, InWorkForm, InWorkFormTwo,
    ChangeTaskStatusForm, DismissFreelancerFromTaskForm, ViewTaskForm
    )
from webapp.errors import LocalError


def create_app():
    app = Flask(__name__)
    app.config.from_pyfile('config.py')
    db.init_app(app)
    migrate = Migrate(app, db, render_as_batch=True)


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


    @app.route('/')
    def index():
        '''Задать маршрут по которому можно проверить что сервер работает.'''
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
            task = Task(
                task_name=task_form.task_name.data, 
                description=task_form.description.data,
                price=task_form.price.data,
                deadline=task_form.deadline.data, 
                status=status.id, 
                tag=tag.id, 
                freelancer=freelancer.id, 
                customer=customer.id
            )
            db.session.add(task)
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
