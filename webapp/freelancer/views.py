from flask import Blueprint, render_template, flash, redirect, url_for, request
from webapp.db import (
    db,
    Task,
    TaskStatus,
    User,
    convert_task_status_id_to_label,

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
    title = 'Фрилансер'
    
    task_status_tab = request.args.get('tab')
    mapping = {
        'created': CREATED,
        'published': PUBLISHED,
        'freelancers_detected': FREELANCERS_DETECTED,
        'in_work': IN_WORK,
        'stopped': STOPPED,
        'in_review': IN_REVIEW,
        'done': DONE,
    }
    task_status_id = mapping.get(task_status_tab)
    if task_status_id == None:
        task_status_tab = 'created'
        task_status_id = CREATED
    
    tasks = Task.query.filter(
        Task.freelancer == user_id,
        Task.status == task_status_id
    ).all()
    
    task_status_tabs = []
    def add_tab(task_status_id, param_value):
        task_status_tabs.append({
            "label": convert_task_status_id_to_label(
                task_status_id,
                simple_form='сделанные'
                ),
            "url": url_for(
                'freelancer.view_freelancer',
                user_id=user_id,
                tab=param_value
                ),
            "is_selected": task_status_tab == param_value,
            })
    add_tab(
        task_status_id=PUBLISHED,
        param_value='published'
        )
    add_tab(
        task_status_id=FREELANCERS_DETECTED,
        param_value='freelancers_detected'
        )
    add_tab(
        task_status_id=IN_WORK,
        param_value='in_work'
        )
    add_tab(
        task_status_id=IN_REVIEW,
        param_value='in_review'
        )
    add_tab(
        task_status_id=DONE,
        param_value='done'
        )
    add_tab(
        task_status_id=STOPPED,
        param_value='stopped'
        )

    return render_template(
        'freelancer/freelancer.html',
        title=title,
        tasks=tasks,
        user_id=user_id,
        task_status_tabs=task_status_tabs
        )
