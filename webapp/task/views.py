from flask import Blueprint, render_template, request, redirect, url_for, flash
from webapp.db import db, Task, TaskStatus, User
from flask_login import login_required
from webapp.task.forms import CreateTaskForm, SimpleConfirmForm
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


def get_task_debug_info(task_id):
    '''Получить снимок Задачи для дебага.'''
    task = Task.query.get(task_id)
    if task == None:
        return None;
    return task.generate_level_2_debug_dictionary()


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
        task_debug_info = get_task_debug_info(task_id)
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
    '''Фрилансер требует двинуть заказ со статуса IN_WORK на IN_REVIEW.'''
    title = 'Фрилансер требует передать заказ на ревью Заказчику'
    form_url = url_for('task.move_task_to_in_review', task_id=task_id)

    form = SimpleConfirmForm()

    try:
        task = Task.query.get(task_id)
        validators.validate_task_existence(
            task=task,
            failure_feedback='Указанная в запросе Задача не существует. Попробуйте изменить критерий поиска и попровать снова.'
        )

        if request.method == 'GET':

            return render_template(
                'task/change_task_status.form.html',
                title=title,
                form=form,
                form_url=form_url,
                feedback_message='Вы действительно хотите передать эту задачу на ревью?'
            )

        elif request.method == 'POST':

            try:
                validators.validate_form(form)

                # Сделать свежий снимок Задачи для дебага.
                task_debug_info1 = get_task_debug_info(task_id)

                status_id = IN_REVIEW;

                # Внести изменения в Задачу.
                task.status = status_id
                db.session.commit()

                # Сделать свежий снимок Задачи для дебага.
                task_debug_info2 = get_task_debug_info(task_id)
            except:
                db.session.rollback()
                raise
            else:
                return render_template(
                    'task/change_task_status.success.html',
                    title=title,
                    task_before=task_debug_info1,
                    task_after=task_debug_info2
                )
    except ValidationError as e:
        db.session.rollback()
        return render_template(
            'task/change_task_status.form.html',
            title=title,
            form=form,
            form_url=form_url,
            feedback_message=e.args[0]
        )


@blueprint.route('/tasks/<int:task_id>/move_task_to_in_work', methods=['GET', 'POST'])
def move_task_to_in_work(task_id):
    '''Заказчик требует двинуть Задачу со статуса IN_REVIEW в IN_WORK'''
    title = 'Заказчик требует передать Задачу назад на доработку к Фрилансеру'
    form_url = url_for('task.move_task_to_in_work', task_id=task_id)

    form = SimpleConfirmForm()

    try:
        task = Task.query.get(task_id)
        validators.validate_task_existence(
            task=task,
            failure_feedback='Указанная в запросе Задача не существует. Попробуйте изменить критерий поиска и попровать снова.'
        )

        if request.method == 'GET':

            return render_template(
                'task/change_task_status.form.html',
                title=title,
                form=form,
                form_url=form_url,
                feedback_message='Вы действительно хотите передать эту задачу назад на доработку?'
            )

        elif request.method == 'POST':

            try:
                validators.validate_form(form)

                # Сделать свежий снимок Задачи для дебага.
                task_debug_info1 = get_task_debug_info(task_id)

                status_id = IN_WORK;

                # Внести изменения в Задачу.
                task.status = status_id
                db.session.commit()

                # Сделать свежий снимок Задачи для дебага.
                task_debug_info2 = get_task_debug_info(task_id)
            except:
                db.session.rollback()
                raise
            else:
                return render_template(
                    'task/change_task_status.success.html',
                    title=title,
                    task_before=task_debug_info1,
                    task_after=task_debug_info2
                )
    except ValidationError as e:
        db.session.rollback()
        return render_template(
            'task/change_task_status.form.html',
            title=title,
            form=form,
            form_url=form_url,
            feedback_message=e.args[0]
        )


@blueprint.route('/tasks/<int:task_id>/move_task_to_done', methods=['GET', 'POST'])
def move_task_to_done(task_id):
    '''Заказчик требует двинуть Задачу со статуса IN_REVIEW в DONE'''
    title = 'Заказчик требует закочить Задачу как успешно завершённую'
    form_url = url_for('task.move_task_to_done', task_id=task_id)

    form = SimpleConfirmForm()

    try:
        task = Task.query.get(task_id)
        validators.validate_task_existence(
            task=task,
            failure_feedback='Указанная в запросе Задача не существует. Попробуйте изменить критерий поиска и попровать снова.'
        )

        if request.method == 'GET':

            return render_template(
                'task/change_task_status.form.html',
                title=title,
                form=form,
                form_url=form_url,
                feedback_message='Вы действительно хотите закончить эту задачу как успешно завершённую?'
            )

        elif request.method == 'POST':

            try:
                validators.validate_form(form)

                # Сделать свежий снимок Задачи для дебага.
                task_debug_info1 = get_task_debug_info(task_id)

                status_id = DONE;

                # Внести изменения в Задачу.
                task.status = status_id
                db.session.commit()

                # Сделать свежий снимок Задачи для дебага.
                task_debug_info2 = get_task_debug_info(task_id)
            except:
                db.session.rollback()
                raise
            else:
                return render_template(
                    'task/change_task_status.success.html',
                    title=title,
                    task_before=task_debug_info1,
                    task_after=task_debug_info2
                )
    except ValidationError as e:
        db.session.rollback()
        return render_template(
            'task/change_task_status.form.html',
            title=title,
            form=form,
            form_url=form_url,
            feedback_message=e.args[0]
        )


@blueprint.route('/tasks/<int:task_id>/cancel_task', methods=['GET', 'POST'])
def cancel_task(task_id):
    '''Заказчик требует двинуть Задачу в статус STOPPED'''
    title = 'Заказчик требует отменить Задачу'
    form_url = url_for('task.cancel_task', task_id=task_id)

    form = SimpleConfirmForm()

    try:
        task = Task.query.get(task_id)
        validators.validate_task_existence(
            task=task,
            failure_feedback='Указанная в запросе Задача не существует. Попробуйте изменить критерий поиска и попровать снова.'
        )

        if request.method == 'GET':

            return render_template(
                'task/change_task_status.form.html',
                title=title,
                form=form,
                form_url=form_url,
                feedback_message='Вы действительно хотите отменить эту задачу?'
            )

        elif request.method == 'POST':

            try:
                validators.validate_form(form)

                status_id = STOPPED;

                # Сделать свежий снимок Задачи для дебага.
                task_debug_info1 = get_task_debug_info(task_id)

                # Внести изменения в задачу.
                task.status = status_id
                db.session.commit()

                # Отцепить от Задачи: Фрилансера-Подтверждённого Исполнителя.
                task.freelancer = None

                # Отцепить от Задачи: всех Предваритально Откликнувшихся
                # Фрилансеров.
                freelancers = task.freelancers_who_responded.all()
                task.freelancers_who_responded = task.freelancers_who_responded.filter(
                    User.role != FREELANCER
                )
                db.session.commit()

                # Сделать свежий снимок Задачи для дебага.
                task_debug_info2 = get_task_debug_info(task_id)
            except:
                db.session.rollback()
                raise
            else:
                return render_template(
                    'task/change_task_status.success.html',
                    title=title,
                    task_before=task_debug_info1,
                    task_after=task_debug_info2
                )
    except ValidationError as e:
        db.session.rollback()
        return render_template(
            'task/change_task_status.form.html',
            title=title,
            form=form,
            form_url=form_url,
            feedback_message=e.args[0]
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
            task_debug_info1 = get_task_debug_info(task_id)

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
            task_debug_info2 = get_task_debug_info(task_id)
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
            task_debug_info1 = get_task_debug_info(task_id)

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
            task_debug_info2 = get_task_debug_info(task_id)
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
