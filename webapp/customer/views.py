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
    title = 'Заказчик'
    
    task_status_tab = request.args.get('tab')
    mapping = [
        'created' => CREATED,
        'published' => PUBLISHED,
        'freelancers_detected' => FREELANCERS_DETECTED,
        'in_work' => IN_WORK,
        'stopped' => STOPPED,
        'in_review' => IN_REVIEW,
        'done' => DONE,
    ]
    task_status_id = mapping.get(task_status_tab)
    if task_status_id == None:
        task_status_tab = 'created'
        task_status_id = CREATED
    
    tasks = Task.query.filter(Task.customer == user_id, Task.status == CREATED).all()
    
    task_status_tabs = []
    def add_tab(task_status_id, param_value):
        task_status_tabs.append({
            "label": convert_task_status_id_to_label(task_status_id),
            "url": url_for('customer.view_customer', user_id=user_id, tab=param_value),
            "is_selected": task_status_tab == param_value,
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
        task_status_id=STOPPED,
        param_value='stopped'
        )
    add_tab(
        task_status_id=IN_REVIEW,
        param_value='in_review'
        )
    add_tab(
        task_status_id=DONE,
        param_value='done'
        )

    return render_template(
        'customer/customer.html',
        title=title,
        tasks=tasks,
        user_id=user_id,
        task_status_tabs=task_status_tabs
        )


@blueprint.route('/<int:user_id>/published', methods=['GET', 'POST'])
@customer_required
def view_published_tasks(user_id):
    if int(current_user.get_id()) != user_id:
        flash('Это не твой id')
        return redirect(url_for('sign.index'))
    title = 'Все опубликованные заказы (статус published)'
    tasks = Task.query.filter(Task.customer == user_id, Task.status == PUBLISHED).all()

    return render_template('customer/published.html', title=title, user_id=user_id, tasks=tasks)


@blueprint.route('/<int:user_id>/freelancers_detected', methods=['GET', 'POST'])
@customer_required
def view_freelancers_detected_task(user_id):
    if int(current_user.get_id()) != user_id:
        flash('Это не твой id')
        return redirect(url_for('sign.index'))
    title = 'Все заказы, на которые откликнулись'
    tasks = Task.query.filter(Task.customer == user_id, Task.status == FREELANCERS_DETECTED).all()

    return render_template('customer/freelancers_detected.html', title=title, user_id=user_id, tasks=tasks)


@blueprint.route('/<int:user_id>/in_work', methods=['GET', 'POST'])
@customer_required
def view_in_work_tasks(user_id):
    if int(current_user.get_id()) != user_id:
        flash('Это не твой id')
        return redirect(url_for('sign.index'))
    title = 'Все заказы в работе'
    tasks = Task.query.filter(Task.customer == user_id, Task.status == IN_WORK).all()

    return render_template('customer/in_work.html', title=title, tasks=tasks, user_id=user_id)
