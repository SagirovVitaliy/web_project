from flask import Blueprint, render_template, request, redirect, url_for, flash
from webapp.db import db, Task, TaskStatus, User
from flask_login import login_required, current_user
import webapp.task.access_rules as task_access_rules
from webapp.task.forms import (
    CreateTaskForm,
    SimpleConfirmForm,
    DismissFreelancerFromTaskForm
    )
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
from webapp.errors import OperationPermissionError, ValidationError 
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
        validators.validate_task_existence(task=task)

        # DEBUG: Сделать свежий снимок Задачи для дебага.
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
    title = 'Передать заказ на ревью Заказчику'
    form_url = url_for('task.move_task_to_in_review', task_id=task_id)

    form = SimpleConfirmForm()

    try:
        task = Task.query.get(task_id)
        validators.validate_task_existence(task=task)

        task_access_rules.current_user_must_be_connected_to_task_as_confirmed_freelancer(
            current_user=current_user,
            task=task
            )
        if not task.status == IN_WORK:
            raise OperationPermissionError(
                'Эту операцию можно применять только к Задачам ' +
                'со статусом "В Работе"'
                )

        if request.method == 'GET':

            return render_template(
                'task/change_task_status.form.html',
                title=title,
                form=form,
                form_url=form_url,
                feedback_message='Вы действительно хотите передать эту Задачу на ревью?'
                )

        elif request.method == 'POST':

            try:
                validators.validate_form(form)

                # DEBUG: Сделать свежий снимок Задачи для дебага.
                task_debug_info1 = get_task_debug_info(task_id)

                status_id = IN_REVIEW;

                # Внести изменения в Задачу.
                task.status = status_id
                db.session.commit()

                # DEBUG: Сделать свежий снимок Задачи для дебага.
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

    except OperationPermissionError as e:
        db.session.rollback()
        return render_template(
            'task/access_denied.html',
            title=title,
            feedback_message=e.args[0]
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
    title = 'Передать Задачу назад на доработку к Фрилансеру'
    form_url = url_for('task.move_task_to_in_work', task_id=task_id)

    form = SimpleConfirmForm()

    try:
        task = Task.query.get(task_id)
        validators.validate_task_existence(task=task)

        task_access_rules.current_user_must_be_connected_to_task_as_customer(
            current_user=current_user,
            task=task
            )
        if not task.status == IN_REVIEW:
            raise OperationPermissionError(
                'Эту операцию можно применять только к Задачам ' +
                'со статусом "В Ревью"'
                )

        if request.method == 'GET':

            return render_template(
                'task/change_task_status.form.html',
                title=title,
                form=form,
                form_url=form_url,
                feedback_message='Вы действительно хотите передать эту Задачу назад на доработку?'
                )

        elif request.method == 'POST':

            try:
                validators.validate_form(form)

                # DEBUG: Сделать свежий снимок Задачи для дебага.
                task_debug_info1 = get_task_debug_info(task_id)

                # Внести изменения в Задачу.
                task.status = IN_WORK
                db.session.commit()

                # DEBUG: Сделать свежий снимок Задачи для дебага.
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

    except OperationPermissionError as e:
        db.session.rollback()
        return render_template(
            'task/access_denied.html',
            title=title,
            feedback_message=e.args[0]
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
    title = 'Закочить Задачу как успешно завершённую'
    form_url = url_for('task.move_task_to_done', task_id=task_id)

    form = SimpleConfirmForm()

    try:
        task = Task.query.get(task_id)
        validators.validate_task_existence(task=task)

        task_access_rules.current_user_must_be_connected_to_task_as_customer(
            current_user=current_user,
            task=task
            )
        if not task.status == IN_REVIEW:
            raise OperationPermissionError(
                'Эту операцию можно применять только к Задачам ' +
                'со статусом "В Ревью"'
                )

        if request.method == 'GET':

            return render_template(
                'task/change_task_status.form.html',
                title=title,
                form=form,
                form_url=form_url,
                feedback_message='Вы действительно хотите закончить эту Задачу как успешно завершённую?'
                )

        elif request.method == 'POST':

            try:
                validators.validate_form(form)

                # DEBUG: Сделать свежий снимок Задачи для дебага.
                task_debug_info1 = get_task_debug_info(task_id)

                # Внести изменения в Задачу.
                task.status = DONE
                db.session.commit()

                # DEBUG: Сделать свежий снимок Задачи для дебага.
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

    except OperationPermissionError as e:
        db.session.rollback()
        return render_template(
            'task/access_denied.html',
            title=title,
            feedback_message=e.args[0]
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
    title = 'Отменить Задачу'
    form_url = url_for('task.cancel_task', task_id=task_id)

    form = SimpleConfirmForm()

    try:
        task = Task.query.get(task_id)
        validators.validate_task_existence(task=task)

        task_access_rules.current_user_must_be_connected_to_task_as_customer(
            current_user=current_user,
            task=task
            )
        if task.status == STOPPED:
            raise OperationPermissionError(
                'Эту операцию нельзя применять к Задачам ' +
                'со статусом "Остановленная"'
                )

        if request.method == 'GET':

            return render_template(
                'task/change_task_status.form.html',
                title=title,
                form=form,
                form_url=form_url,
                feedback_message='Вы действительно хотите отменить эту Задачу?'
            )

        elif request.method == 'POST':

            try:
                validators.validate_form(form)

                # DEBUG: Сделать свежий снимок Задачи для дебага.
                task_debug_info1 = get_task_debug_info(task_id)

                # Внести изменения в задачу.
                task.status = STOPPED
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

                # DEBUG: Сделать свежий снимок Задачи для дебага.
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

    except OperationPermissionError as e:
        db.session.rollback()
        return render_template(
            'task/access_denied.html',
            title=title,
            feedback_message=e.args[0]
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
def dismiss_confirmed_freelancer_from_task(task_id):
    '''Заказчик требует отцепить Фрилансера-Исполнителя от Задачи'''
    title = 'Отцепить Фрилансера-Исполнителя от Задачи'
    form_url = url_for('task.dismiss_confirmed_freelancer_from_task', task_id=task_id)
    call_to_action_text = 'Выберите Предварительно Откликнувшихся Фрилансера которого вы хотите отцепить от Задачи'

    form = SimpleConfirmForm()
    freelancer_choices = []

    try:
        task = Task.query.get(task_id)
        validators.validate_task_existence(task=task)

        task_access_rules.current_user_must_be_connected_to_task_as_customer(
            current_user=current_user,
            task=task
            )

        # Подготовить form.user_id.choices.
        user_id = task.freelancer;
        user = User.query.get(user_id)
        if not user == None:
            freelancer_choices = [user]

        if request.method == 'GET':

            return render_template(
                'task/dismiss_freelancer_from_task.form.html',
                title=title,
                call_to_action_text=call_to_action_text,
                form=form,
                form_url=form_url,
                freelancer_choices=freelancer_choices
                )

        elif request.method == 'POST':

            try:
                validators.validate_form(form)

                user_id = request.form.get('user_id');

                user = User.query.get(user_id)
                validators.validate_user_existence(user)
                validators.validate_if_user_is_freelancer(user)
                validators.is_user_connected_to_task_as_confirmed_freelancer(
                    user=user, task=task
                    )

                # DEBUG: Сделать свежий снимок Задачи для дебага.
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
                    # PUBLISHED.
                    task.status = PUBLISHED
                db.session.commit()

                # DEBUG: Сделать свежий снимок Задачи для дебага.
                task_debug_info2 = get_task_debug_info(task_id)
            except:
                db.session.rollback()
                raise
            else:
                return render_template(
                    'task/dismiss_freelancer_from_task.success.html',
                    title=title,
                    call_to_action_text=call_to_action_text,
                    task_before=task_debug_info1,
                    task_after=task_debug_info2
                    )

    except OperationPermissionError as e:
        db.session.rollback()
        return render_template(
            'task/access_denied.html',
            title=title,
            feedback_message=e.args[0]
            )
    except ValidationError as e:
        db.session.rollback()
        return render_template(
            'task/dismiss_freelancer_from_task.form.html',
            title=title,
            call_to_action_text=call_to_action_text,
            form=form,
            form_url=form_url,
            freelancer_choices=freelancer_choices,
            feedback_message=e.args[0]
            )


@blueprint.route('/tasks/<int:task_id>/dismiss_responded_freelancer_from_task', methods=['GET', 'POST'])
def dismiss_responded_freelancer_from_task(task_id):
    '''Заказчик требует отцепить Предв. Отклик. Фрилансера от Задачи
    
    Заказчик требует отцепить Предварительно Откликнувшихся Фрилансеров от Задачи
    '''

    title = 'Отцепить Предварительно Откликнувшихся Фрилансеров от Задачи'
    form_url = url_for('task.dismiss_responded_freelancer_from_task', task_id=task_id)
    call_to_action_text = 'Выберите Предварительно Откликнувшихся Фрилансера которого вы хотите отцепить от Задачи'

    form = SimpleConfirmForm()
    freelancer_choices = []

    try:
        task = Task.query.get(task_id)
        validators.validate_task_existence(task=task)

        task_access_rules.current_user_must_be_connected_to_task_as_customer(
            current_user=current_user,
            task=task
            )

        freelancer_choices = task.freelancers_who_responded.filter(
            User.role == FREELANCER,
        ).all()

        if request.method == 'GET':

            return render_template(
                'task/dismiss_freelancer_from_task.form.html',
                title=title,
                call_to_action_text=call_to_action_text,
                form=form,
                form_url=form_url,
                freelancer_choices=freelancer_choices
                )

        elif request.method == 'POST':

            try:
                validators.validate_form(form)

                user_id = request.form.get('user_id');

                user = User.query.get(user_id)
                validators.validate_user_existence(user)
                validators.validate_if_user_is_freelancer(user)
                validators.is_user_connected_to_task_as_responded_freelancer(
                    user=user, task=task
                    )

                # DEBUG: Сделать свежий снимок Задачи для дебага.
                task_debug_info1 = get_task_debug_info(task_id)

                # Отцепить от Задачи: Предваритально Откликнувшегося Фрилансера.
                freelancers = task.freelancers_who_responded.filter(
                    User.role == FREELANCER,
                    User.id != user_id
                    )
                task.freelancers_who_responded = freelancers
                if task.status == FREELANCERS_DETECTED:
                    if not freelancers.count() > 0:
                        # Если это был удалён последний Фрилансер в списке; и
                        # если задача - в Статусе когда нельзя делать
                        # последующие шаги к Главной Цели, не имея Фрилансеров в
                        # этом списке, тогда надо перевести Задачу в Статус
                        # PUBLISHED.
                        task.status = PUBLISHED
                db.session.commit()

                # DEBUG: Сделать свежий снимок Задачи для дебага.
                task_debug_info2 = get_task_debug_info(task_id)
            except:
                db.session.rollback()
                raise
            else:
                return render_template(
                    'task/dismiss_freelancer_from_task.success.html',
                    title=title,
                    call_to_action_text=call_to_action_text,
                    task_before=task_debug_info1,
                    task_after=task_debug_info2
                    )

    except OperationPermissionError as e:
        db.session.rollback()
        return render_template(
            'task/access_denied.html',
            title=title,
            feedback_message=e.args[0]
            )
    except ValidationError as e:
        db.session.rollback()
        return render_template(
            'task/dismiss_freelancer_from_task.form.html',
            title=title,
            call_to_action_text=call_to_action_text,
            form=form,
            form_url=form_url,
            freelancer_choices=freelancer_choices,
            feedback_message=e.args[0]
            )
