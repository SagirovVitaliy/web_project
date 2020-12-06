from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from webapp.errors import OperationPermissionError, ValidationError
from webapp.db import (
    db,
    Task,
    TaskStatus,
    User,
    convert_task_status_id_to_label,

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
from webapp.task.forms import (
    CreateTaskForm,
    SimpleConfirmForm,
    ConfirmFreelancerFromTaskForm,
    DismissFreelancerFromTaskForm
    )

import webapp.task.access_rules as task_access_rules
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
    if int(current_user.get_id()) != user_id:
        flash('Это не твой id')
        return redirect(url_for('sign.index'))
    title = 'Создание заказа'
    form = CreateTaskForm()
    customer = User.query.get(user_id)

    if request.method == 'POST':
        if form.validate_on_submit():
            task = Task(
                task_name=form.task_name.data,
                description=form.description.data,
                price=form.price.data,
                deadline=form.deadline.data,
                status=CREATED,
                customer=customer.id
            )
            
            db.session.add(task)
            db.session.commit()

            flash('Вы успешно создали заказ!')
            return redirect(url_for('customer.view_created_tasks', user_id=user_id))

    return render_template(
        'task/create_task.html',
        title=title,
        form=form,
        user_id=user_id
        )


@blueprint.route('/tasks/add', methods=['GET', 'POST'])
@login_required
def add_task():
    '''Заказчик требует создать Задачу со статусом CREATED.'''
    title = 'Создать Задачу'
    form_url = url_for('task.add_task')

    form = CreateTaskForm()

    try:

        if request.method == 'GET':

            return render_template(
                'task/add_task.html',
                title=title,
                form=form,
                form_url=form_url,
                feedback_message='Создать задачу'
                )

        elif request.method == 'POST':

            try:
                validators.validate_form(form)

                task_access_rules.current_user_must_be_customer(
                    current_user=current_user
                    )

                task = Task(
                    task_name=form.task_name.data,
                    description=form.description.data,
                    price=form.price.data,
                    deadline=form.deadline.data,
                    status=CREATED,
                    customer=current_user.id
                )
                
                db.session.add(task)
                db.session.commit()
                db.session.refresh(task)

                task_id = task.id

                # DEBUG: Сделать свежий снимок Задачи для дебага.
                task_debug_info = get_task_debug_info(task_id)
            except:
                db.session.rollback()
                raise
            else:
                return redirect(url_for('task.view_task', task_id=task_id))

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
            'task/add_task.html',
            title=title,
            form=form,
            form_url=form_url,
            feedback_message=e.args[0]
            )
    pass


@blueprint.route('/tasks/<int:task_id>', methods=['GET'])
@login_required
def view_task(task_id):
    '''Просмотреть состояние Задачи.'''
    title = 'Просматриваем состояние Задачи'

    try:
        task = Task.query.get(task_id)
        validators.validate_task_existence(task=task)

        title = f'{task.task_name}' or title

        # Набираем информацию для темплайта.
        task_status_label = convert_task_status_id_to_label(task.status)

        def render_users_and_pack_to_group(users):
            '''Список пользователей обработать и ужать в группу

            Которая содержит только выжимку по релевантным данным, а лишнее -
            выкинуто.
            '''

            contains_current_user = False
            rendered_users = []

            for user in users:
                if not user == None:

                    is_current_user = False
                    if current_user.is_authenticated and current_user.is_active:
                        if user.id == current_user.id:
                            is_current_user = True
                            contains_current_user = True

                    rendered_users.append({
                        'id': f'{user.id}',
                        'label': f'{user.get_public_label()}',
                        'is_current_user': is_current_user,
                        })
            return {
                'contains_current_user': contains_current_user,
                'rendered_users': rendered_users,
                }

        user_groups = {}

        task_customer = User.query.get(task.customer)
        user_groups['task_customers'] = render_users_and_pack_to_group(
            users=[task_customer]
            )

        confirmed_freelancer = User.query.get(task.freelancer)
        user_groups['confirmed_freelancers'] = render_users_and_pack_to_group(
            users=[confirmed_freelancer]
            )

        responded_freelancers = task.freelancers_who_responded.filter(
            User.role == FREELANCER,
        ).all()
        user_groups['responded_freelancers'] = render_users_and_pack_to_group(
            users=responded_freelancers
            )

        # Ставим ограничение на пользователей которые имеют право смотреть
        # контент этой задачи.
        if (
                task.status == CREATED or
                task.status == IN_WORK or
                task.status == IN_REVIEW or
                task.status == DONE or
                task.status == STOPPED
            ):
            if not (
                    user_groups['task_customers']['contains_current_user'] or
                    user_groups['confirmed_freelancers']['contains_current_user'] or
                    user_groups['responded_freelancers']['contains_current_user']
                ):
                raise OperationPermissionError('Только участники этой Задачи имеют право для её просмотра')

        permitted_actions = {}

        if (
                task.status == CREATED and
                user_groups['task_customers']['contains_current_user']
            ):
            permitted_actions['publish_task'] = {
                'is_allowed': True,
                'form': SimpleConfirmForm()
                }

        if (
                (
                    task.status == PUBLISHED or
                    task.status == FREELANCERS_DETECTED
                ) and
                current_user.is_authenticated and
                current_user.is_active and
                current_user.role == FREELANCER
            ):
            permitted_actions['join_to_detected_freelancers_in_task'] = {
                'is_allowed': True,
                'form': SimpleConfirmForm()
                }

        if (
                task.status == FREELANCERS_DETECTED and
                user_groups['task_customers']['contains_current_user']
            ):
            permitted_actions['confirm_freelancer_and_move_task_to_in_work'] = {
                'is_allowed': True,
                'form': SimpleConfirmForm()
                }

        if (
                (
                    task.status == PUBLISHED or
                    task.status == FREELANCERS_DETECTED
                ) and
                current_user.is_authenticated and
                current_user.is_active and
                current_user.role == FREELANCER and
                not user_groups['responded_freelancers']['contains_current_user']
            ):
            permitted_actions['join_to_detected_freelancers'] = {
                'is_allowed': True,
                'form': SimpleConfirmForm()
                }

        if (
                task.status == IN_WORK and
                user_groups['confirmed_freelancers']['contains_current_user']
            ):
            permitted_actions['move_task_to_in_review'] = {
                'is_allowed': True,
                'form': SimpleConfirmForm()
                }

        if (
                task.status == IN_REVIEW and
                user_groups['task_customers']['contains_current_user']
            ):
            permitted_actions['move_task_to_in_work'] = {
                'is_allowed': True,
                'form': SimpleConfirmForm()
                }

        if (
                task.status == IN_REVIEW and
                user_groups['task_customers']['contains_current_user']
            ):
            permitted_actions['move_task_to_done'] = {
                'is_allowed': True,
                'form': SimpleConfirmForm()
                }

        if (
                task.status != STOPPED and
                user_groups['task_customers']['contains_current_user']
            ):
            permitted_actions['cancel_task'] = {
                'is_allowed': True,
                'form': SimpleConfirmForm()
                }

        if (
                user_groups['task_customers']['contains_current_user']
            ):
            permitted_actions['dismiss_confirmed_freelancer_from_task'] = {
                'is_allowed': True,
                'form': DismissFreelancerFromTaskForm()
                }

        if (
                user_groups['task_customers']['contains_current_user']
            ):
            permitted_actions['dismiss_responded_freelancer_from_task'] = {
                'is_allowed': True,
                'form': DismissFreelancerFromTaskForm()
                }

        # DEBUG: Сделать свежий снимок Задачи для дебага.
        task_debug_info = get_task_debug_info(task_id)
    except OperationPermissionError as e:
        db.session.rollback()
        return render_template(
            'task/access_denied.html',
            title=title,
            feedback_message=e.args[0]
            ), 403
    except ValidationError as e:
        return render_template(
            'task/view_task.html',
            title=title,
            feedback_message=e.args[0]
            ), 400
    else:
        return render_template(
            'task/view_task.html',
            title=title,
            task=task,
            task_status_label=task_status_label,
            user_groups=user_groups,
            permitted_actions=permitted_actions,
            task_debug_info=task_debug_info
        )


@blueprint.route('/tasks/<int:task_id>/publish', methods=['GET', 'POST'])
@login_required
def publish_task(task_id):
    '''Заказчик требует двинуть Задачу со статуса CREATED в PUBLISHED'''
    title = 'Опубликовать Задачу'
    form_url = url_for('task.publish_task', task_id=task_id)

    form = SimpleConfirmForm()

    try:
        task = Task.query.get(task_id)
        validators.validate_task_existence(task=task)

        task_access_rules.current_user_must_be_connected_to_task_as_customer(
            current_user=current_user,
            task=task
            )
        task_access_rules.task_must_be_in_one_of_statuses(
            task=task,
            task_status_ids = [CREATED]
            )

        if request.method == 'GET':

            return render_template(
                'task/change_task_status.form.html',
                title=title,
                form=form,
                form_url=form_url,
                feedback_message='Вы действительно хотите опуликовать эту Задачу?'
                )

        elif request.method == 'POST':

            try:
                validators.validate_form(form)

                # Внести изменения в Задачу.
                task.status = PUBLISHED
                db.session.commit()
            except:
                db.session.rollback()
                raise
            else:
                return redirect(url_for('task.view_task', task_id=task_id))

    except OperationPermissionError as e:
        db.session.rollback()
        return render_template(
            'task/access_denied.html',
            title=title,
            feedback_message=e.args[0]
            ), 403
    except ValidationError as e:
        db.session.rollback()
        return render_template(
            'task/change_task_status.form.html',
            title=title,
            form=form,
            form_url=form_url,
            feedback_message=e.args[0]
            ), 400


@blueprint.route('/tasks/<int:task_id>/join_to_detected_freelancers', methods=['GET', 'POST'])
@login_required
def join_to_detected_freelancers(task_id):
    '''Фрилансер требует присоединиться к заказу в статусе PUBLISHED или FREELANCERS_DETECTED.'''
    title = 'Отклинкуться на Заказ'
    form_url = url_for('task.join_to_detected_freelancers', task_id=task_id)

    form = SimpleConfirmForm()

    try:
        task = Task.query.get(task_id)
        validators.validate_task_existence(task=task)

        task_access_rules.current_user_must_be_freelancer(
            current_user=current_user
            )
        task_access_rules.task_must_be_in_one_of_statuses(
            task=task,
            task_status_ids = [PUBLISHED, FREELANCERS_DETECTED]
            )

        if request.method == 'GET':

            return render_template(
                'task/change_task_status.form.html',
                title=title,
                form=form,
                form_url=form_url,
                feedback_message='Вы действительно хотите откликнуться на эту Задачу?'
                )

        elif request.method == 'POST':

            try:
                validators.validate_form(form)

                # Внести изменения в Задачу.
                task.freelancers_who_responded.append(current_user)
                task.status = FREELANCERS_DETECTED
                db.session.commit()
            except:
                db.session.rollback()
                raise
            else:
                return redirect(url_for('task.view_task', task_id=task_id))

    except OperationPermissionError as e:
        db.session.rollback()
        return render_template(
            'task/access_denied.html',
            title=title,
            feedback_message=e.args[0]
            ), 403
    except ValidationError as e:
        db.session.rollback()
        return render_template(
            'task/change_task_status.form.html',
            title=title,
            form=form,
            form_url=form_url,
            feedback_message=e.args[0]
            ), 400


@blueprint.route('/tasks/<int:task_id>/confirm_freelancer_and_move_task_to_in_work', methods=['GET', 'POST'])
@login_required
def confirm_freelancer_and_move_task_to_in_work(task_id):
    '''Заказчик требует двинуть Задачу со статуса FREELANCERS_DETECTED в IN_WORK'''
    title = 'Выбрать Фрилансера'
    form_url = url_for('task.confirm_freelancer_and_move_task_to_in_work', task_id=task_id)
    call_to_action_text = 'Выберите Предварительно Откликнувшихся Фрилансера которого вы хотите выбрать как Исполнителя Задачи'

    form = SimpleConfirmForm()
    freelancer_choices = []

    try:
        task = Task.query.get(task_id)
        validators.validate_task_existence(task=task)

        task_access_rules.current_user_must_be_connected_to_task_as_customer(
            current_user=current_user,
            task=task
            )
        task_access_rules.task_must_be_in_one_of_statuses(
            task=task,
            task_status_ids = [FREELANCERS_DETECTED]
            )

        freelancer_choices = task.freelancers_who_responded.filter(
            User.role == FREELANCER,
        ).all()

        if request.method == 'GET':

            return render_template(
                'task/choose_freelancer_from_task.form.html',
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

                # Внести изменения в Задачу.

                task.freelancer = user.id
                task.status = IN_WORK

                # Отцепить от Задачи: Предваритально Откликнувшегося Фрилансера.
                freelancers = task.freelancers_who_responded.filter(
                    False
                    )
                task.freelancers_who_responded = freelancers
                db.session.commit()
            except:
                db.session.rollback()
                raise
            else:
                return redirect(url_for('task.view_task', task_id=task_id))

    except OperationPermissionError as e:
        db.session.rollback()
        return render_template(
            'task/access_denied.html',
            title=title,
            feedback_message=e.args[0]
            ), 403
    except ValidationError as e:
        db.session.rollback()
        return render_template(
            'task/choose_freelancer_from_task.form.html',
            title=title,
            call_to_action_text=call_to_action_text,
            form=form,
            form_url=form_url,
            freelancer_choices=freelancer_choices,
            feedback_message=e.args[0]
            ), 400


@blueprint.route('/tasks/<int:task_id>/move_task_to_in_review', methods=['GET', 'POST'])
@login_required
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
        task_access_rules.task_must_be_in_one_of_statuses(
            task=task,
            task_status_ids = [IN_WORK]
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

                # Внести изменения в Задачу.
                task.status = IN_REVIEW
                db.session.commit()
            except:
                db.session.rollback()
                raise
            else:
                return redirect(url_for('task.view_task', task_id=task_id))

    except OperationPermissionError as e:
        db.session.rollback()
        return render_template(
            'task/access_denied.html',
            title=title,
            feedback_message=e.args[0]
            ), 403
    except ValidationError as e:
        db.session.rollback()
        return render_template(
            'task/change_task_status.form.html',
            title=title,
            form=form,
            form_url=form_url,
            feedback_message=e.args[0]
            ), 400


@blueprint.route('/tasks/<int:task_id>/move_task_to_in_work', methods=['GET', 'POST'])
@login_required
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
        task_access_rules.task_must_be_in_one_of_statuses(
            task=task,
            task_status_ids = [IN_REVIEW]
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

                # Внести изменения в Задачу.
                task.status = IN_WORK
                db.session.commit()
            except:
                db.session.rollback()
                raise
            else:
                return redirect(url_for('task.view_task', task_id=task_id))

    except OperationPermissionError as e:
        db.session.rollback()
        return render_template(
            'task/access_denied.html',
            title=title,
            feedback_message=e.args[0]
            ), 403
    except ValidationError as e:
        db.session.rollback()
        return render_template(
            'task/change_task_status.form.html',
            title=title,
            form=form,
            form_url=form_url,
            feedback_message=e.args[0]
            ), 400


@blueprint.route('/tasks/<int:task_id>/move_task_to_done', methods=['GET', 'POST'])
@login_required
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
        task_access_rules.task_must_be_in_one_of_statuses(
            task=task,
            task_status_ids = [IN_REVIEW]
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

                # Внести изменения в Задачу.
                task.status = DONE
                db.session.commit()
            except:
                db.session.rollback()
                raise
            else:
                return redirect(url_for('task.view_task', task_id=task_id))

    except OperationPermissionError as e:
        db.session.rollback()
        return render_template(
            'task/access_denied.html',
            title=title,
            feedback_message=e.args[0]
            ), 403
    except ValidationError as e:
        db.session.rollback()
        return render_template(
            'task/change_task_status.form.html',
            title=title,
            form=form,
            form_url=form_url,
            feedback_message=e.args[0]
            ), 400


@blueprint.route('/tasks/<int:task_id>/cancel_task', methods=['GET', 'POST'])
@login_required
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
        task_access_rules.task_must_not_be_in_one_of_statuses(
            task=task,
            task_status_ids = [STOPPED]
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
            except:
                db.session.rollback()
                raise
            else:
                return redirect(url_for('task.view_task', task_id=task_id))

    except OperationPermissionError as e:
        db.session.rollback()
        return render_template(
            'task/access_denied.html',
            title=title,
            feedback_message=e.args[0]
            ), 403
    except ValidationError as e:
        db.session.rollback()
        return render_template(
            'task/change_task_status.form.html',
            title=title,
            form=form,
            form_url=form_url,
            feedback_message=e.args[0]
            ), 400


@blueprint.route('/tasks/<int:task_id>/dismiss_confirmed_freelancer_from_task', methods=['GET', 'POST'])
@login_required
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

                # Отцепить от Задачи: Фрилансера-Подтверждённого Исполнителя.
                task.freelancer = None
                if (
                        task.status == PUBLISHED or
                        task.status == FREELANCERS_DETECTED or
                        task.status == IN_WORK or
                        task.status == IN_REVIEW
                    ):
                    # Если это был удалён последний Фрилансер-Исполнитель; и
                    # если задача - в Статусе когда нельзя делать
                    # последующие шаги к Главной Цели, не имея Фрилансеров в
                    # этом списке, тогда надо перевести Задачу в Статус
                    # либо PUBLISHED либо FREELANCERS_DETECTED.
                    freelancers = task.freelancers_who_responded.filter(
                        User.role == FREELANCER,
                        User.id != user_id
                        )
                    if freelancers.count() > 0:
                        task.status = FREELANCERS_DETECTED
                    else:
                        task.status = PUBLISHED
                db.session.commit()
            except:
                db.session.rollback()
                raise
            else:
                return redirect(url_for('task.view_task', task_id=task_id))

    except OperationPermissionError as e:
        db.session.rollback()
        return render_template(
            'task/access_denied.html',
            title=title,
            feedback_message=e.args[0]
            ), 403
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
            ), 400


@blueprint.route('/tasks/<int:task_id>/dismiss_responded_freelancer_from_task', methods=['GET', 'POST'])
@login_required
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
            except:
                db.session.rollback()
                raise
            else:
                return redirect(url_for('task.view_task', task_id=task_id))

    except OperationPermissionError as e:
        db.session.rollback()
        return render_template(
            'task/access_denied.html',
            title=title,
            feedback_message=e.args[0]
            ), 403
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
            ), 400
