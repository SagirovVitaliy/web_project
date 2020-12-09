from flask import Blueprint, render_template, flash, redirect, url_for, request
from webapp.db import (
    db,
    freelancers_who_responded as freelancersWhoResponded,
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
from webapp.freelancer.decorators import freelancer_required
from flask_login import current_user

blueprint = Blueprint('freelancer', __name__, url_prefix='/freelancer')


@blueprint.route('/<int:user_id>', methods=['GET'])
@freelancer_required
def view_freelancer(user_id):
    if int(current_user.get_id()) != user_id:
        flash('Это не твой id')
        return redirect(url_for('sign.index'))
    title = 'Личный кабинет Фрилансера'
    
    task_tab = request.args.get('tab')
    allowed_tab_values = [
        'freelancer_may_respond',
        'freelancer_responded_and_is_waiting_for_approval',
        'in_work',
        'in_review',
        'done',
    ];
    if task_tab == None:
        task_tab = allowed_tab_values[0]
    
    tasks = []
    if task_tab == 'freelancer_may_respond':
        tasks_raw = Task.query.filter(
            Task.status.in_([PUBLISHED, FREELANCERS_DETECTED])
        ).all()
        for task in tasks_raw:
            responded_freelancers = task.freelancers_who_responded.filter(
                User.id == user_id
            ).all()
            if not responded_freelancers:
                tasks.append(task)
    if task_tab == 'freelancer_responded_and_is_waiting_for_approval':
        tasks_raw = Task.query.filter(
            Task.status.in_([PUBLISHED, FREELANCERS_DETECTED])
        ).all()
        for task in tasks_raw:
            responded_freelancers = task.freelancers_who_responded.filter(
                User.id == user_id
            ).all()
            if responded_freelancers:
                tasks.append(task)
    if task_tab == 'in_work':
        tasks = Task.query.filter(
            Task.freelancer == user_id,
            Task.status == IN_WORK
        ).all()
    if task_tab == 'in_review':
        tasks = Task.query.filter(
            Task.freelancer == user_id,
            Task.status == IN_REVIEW
        ).all()
    if task_tab == 'done':
        tasks = Task.query.filter(
            Task.freelancer == user_id,
            Task.status == DONE
        ).all()

    task_tabs = []
    def add_tab(param_value, label=None):
        task_tabs.append({
            'label': f'{label}',
            'url': url_for(
                'freelancer.view_freelancer',
                user_id=user_id,
                tab=param_value
                ),
            'is_selected': task_tab == param_value,
            })
    add_tab(
        label='Доступные для Участия',
        param_value='freelancer_may_respond'
        )
    add_tab(
        label='Ожидающие подтверждения Участия',
        param_value='freelancer_responded_and_is_waiting_for_approval'
        )
    add_tab(
        label=convert_task_status_id_to_label(
            IN_WORK,
            simple_form='сделанные'
            ),
        param_value='in_work'
        )
    add_tab(
        label=convert_task_status_id_to_label(
            IN_REVIEW,
            simple_form='сделанные'
            ),
        param_value='in_review'
        )
    add_tab(
        label=convert_task_status_id_to_label(
            DONE,
            simple_form='сделанные'
            ),
        param_value='done'
        )

    return render_template(
        'freelancer/freelancer.html',
        title=title,
        tasks=tasks,
        user_id=user_id,
        task_tabs=task_tabs
        )
