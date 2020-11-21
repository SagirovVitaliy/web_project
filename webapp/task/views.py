from flask import Blueprint, render_template, request, redirect, url_for, flash
from webapp.db import db, Task, TaskStatus, User
from flask_login import login_required
from webapp.task.forms import CreateTaskForm
from webapp.db import (
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
from webapp.errors import ValidationError
import webapp.validators as validators

blueprint = Blueprint('task', __name__)


@blueprint.route('/customer/<int:user_id>/create_task/', methods=['GET', 'POST'])
@login_required
def create_task(user_id):
    title = 'Создание заказа'
    form = CreateTaskForm()
    status = TaskStatus.query.filter(TaskStatus.id == CREATED).one()
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
            return redirect(url_for('customer.view_created_tasks', user_id=user_id))

    return render_template('task/create_task.html', title=title, form=form, user_id=user_id)


@blueprint.route('/tasks/<int:task_id>', methods=['GET'])
def view_task(task_id):
    '''Просмотреть состояние Задачи.'''
    title = 'Просматриваем состояние Задачи'

    try:
        task = Task.query.get(task_id)
        validators.validate_task_existence(
            task=task,
            failure_feedback='Указанная в запросе Задача не существует. Попробуйте изменить критерий поиска и попровать снова.'
        )

        # Сделать свежий снимок Задачи для дебага.
        task_debug_info = (
            Task
            .query
            .get(task_id)
            .generate_level_2_debug_dictionary()
        )
    except ValidationError as e:
        return render_template(
            'task/view_task.html',
            title=title,
            feedback_message=e.args[0]
        )
    else:
        return render_template(
            'task/view_task.html',
            title=title,
            task=task_debug_info
        )


@blueprint.route('/tasks/<int:task_id>/move_task_to_in_review', methods=['GET', 'POST'])
def move_task_to_in_review(task_id):
    '''Фрилансер двигает заказ со статуса 'in_work' на 'in_review'.'''
    title = 'Фрилансер двигает заказ со статуса in_work на in_review'

    form = SimpleSubmitForm()

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


@blueprint.route('/tasks/<int:task_id>/move_task_to_in_work', methods=['GET', 'POST'])
def move_task_to_in_work(task_id):
    '''Задать маршрут по которому можно тестировать логику.

    Здесь мы хотим тестировать логику:
    ----------------------------------

    Отрезок позитивного пути - Заказчик двигает заказ со статуса 'in_review'
    либо на 'in_work', либо на 'done'.
    '''
    title = 'Тестируем task.status: in_review -> (in_work|done)'
    form_url = url_for('task.move_task_to_in_work', task_id=task_id)

    allowed_statuses = [ IN_WORK ]
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


@blueprint.route('/tasks/<int:task_id>/move_task_to_done', methods=['GET', 'POST'])
def move_task_to_done(task_id):
    '''Задать маршрут по которому можно тестировать логику.

    Здесь мы хотим тестировать логику:
    ----------------------------------

    Отрезок позитивного пути - Заказчик двигает заказ со статуса 'in_review'
    либо на 'in_work', либо на 'done'.
    '''
    title = 'Тестируем task.status: in_review -> (in_work|done)'
    form_url = url_for('task.move_task_to_done', task_id=task_id)

    allowed_statuses = [ DONE ]
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


@blueprint.route('/tasks/<int:task_id>/cancel_task', methods=['GET', 'POST'])
def cancel_task(task_id):
    '''Задать маршрут по которому можно тестировать логику.

    Здесь мы хотим тестировать логику:
    ----------------------------------

    Отрезок негативного пути - Заказчик отменяет Задачу.
    '''
    title = 'Тестируем customer.cancel_task'
    form_url = url_for('task.cancel_task', task_id=task_id)

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


@blueprint.route('/tasks/<int:task_id>/dismiss_confirmed_freelancer_from_task', methods=['GET', 'POST'])
def dismiss_confirmed_freelancer_from_task():
    '''Задать маршрут по которому можно тестировать логику.

    Здесь мы хотим тестировать логику:
    ----------------------------------

    Отрезок негативного пути - Отцепляем от Задачи одного из предварительно
    Откликнувшихся Фрилансеров.
    '''
    title = 'Тестируем freelancer.dismiss_confirmed_freelancer_from_task'
    form_url = url_for('task.dismiss_confirmed_freelancer_from_task', task_id=task_id)

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


@blueprint.route('/tasks/<int:task_id>/dismiss_responded_freelancer_from_task', methods=['GET', 'POST'])
def dismiss_responded_freelancer_from_task(task_id):
    '''Задать маршрут по которому можно тестировать логику.

    Здесь мы хотим тестировать логику:
    ----------------------------------

    Отрезок негативного пути - Отцепляем от Задачи одного из предварительно
    Откликнувшихся Фрилансеров.
    '''
    title = 'Тестируем freelancer.dismiss_responded_freelancer_from_task'
    form_url = url_for('task.dismiss_responded_freelancer_from_task', task_id=task_id)

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
