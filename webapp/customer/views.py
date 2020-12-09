from flask import Blueprint, render_template, request, flash, redirect, url_for
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
from webapp.customer.decorators import customer_required
from flask_login import current_user

blueprint = Blueprint('customer', __name__, url_prefix='/customer')


@blueprint.route('/<int:user_id>', methods=['GET', 'POST'])
@customer_required
def view_customer(user_id):
    if int(current_user.get_id()) != user_id:
        flash('Это не твой id')
        return redirect(url_for('sign.index'))
    title = 'Личный кабинет Заказчика'
    
    task_tab = request.args.get('tab')
    mapping = {
        'created': CREATED,
        'published': PUBLISHED,
        'freelancers_detected': FREELANCERS_DETECTED,
        'in_work': IN_WORK,
        'stopped': STOPPED,
        'in_review': IN_REVIEW,
        'done': DONE,
    }
    task_status_id = mapping.get(task_tab)
    if task_status_id == None:
        task_tab = 'created'
        task_status_id = CREATED
    
    tasks = Task.query.filter(
        Task.customer == user_id,
        Task.status == task_status_id
    ).all()
    
    task_tabs = []
    def add_tab(task_status_id, param_value, label=None):
        if not label == None:
            label = f'{label}'
        else:
            label = convert_task_status_id_to_label(
                task_status_id,
                simple_form='сделанные'
                )
        task_tabs.append({
            'label': label,
            'url': url_for(
                'customer.view_customer',
                user_id=user_id,
                tab=param_value
                ),
            'is_selected': task_tab == param_value,
            })
    add_tab(
        task_status_id=CREATED,
        param_value='created'
        )
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
        'customer/customer.html',
        title=title,
        tasks=tasks,
        user_id=user_id,
        task_tabs=task_tabs
        )
