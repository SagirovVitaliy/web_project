from flask import Blueprint, render_template, request, flash
from webapp.db import Task, TaskStatus, db, User
from webapp.customer.decorators import customer_required
from webapp.db import (CREATED, PUBLISHED, FREELANCERS_DETECTED, IN_WORK)

blueprint = Blueprint('customer', __name__, url_prefix='/customer')


@blueprint.route('/<int:user_id>/', methods=['GET', 'POST'])
@customer_required
def view_created_tasks(user_id):
    title = 'Все созданные заказы (статус created)'
    tasks = Task.query.filter(Task.customer == user_id, Task.status == CREATED).all()

    return render_template('customer/customer.html', title=title, tasks=tasks, user_id=user_id)


@blueprint.route('/<int:user_id>/published/', methods=['GET', 'POST'])
@customer_required
def view_published_tasks(user_id):
    title = 'Все опубликованные заказы (статус published)'
    tasks = Task.query.filter(Task.customer == user_id, Task.status == PUBLISHED).all()

    return render_template('customer/published.html', title=title, user_id=user_id, tasks=tasks)


@blueprint.route('/<int:user_id>/task/<int:task_id>/', methods=['GET', 'POST'])
@customer_required
def view_tasks(task_id, user_id):
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
        'customer/ct_task_information.html', title=title, task_id=task_id, task_name=task_name, user_id=user_id,
        description=description, price=price, deadline=deadline, task=task
        )


@blueprint.route('/<int:user_id>/freelancers_detected/', methods=['GET', 'POST'])
@customer_required
def view_freelancers_detected_task(user_id):
    title = 'Все заказы, на которые откликнулись'
    tasks = Task.query.filter(Task.customer == user_id, Task.status == FREELANCERS_DETECTED).all()

    return render_template('customer/freelancers_detected.html', title=title, user_id=user_id, tasks=tasks)


@blueprint.route('/<int:user_id>/ready_fl/<int:task_id>/', methods=['GET', 'POST'])
@customer_required
def view_ready_fl(user_id, task_id):
    title = 'Все откликнувшиеся на заказ'
    task = Task.query.get(task_id)
    freelancers = task.freelancers_who_responded.all()

    return render_template('customer/ready_fl.html', title=title, task_id=task_id, user_id=user_id, freelancers=freelancers)


@blueprint.route('/<int:user_id>/ready_fl/<int:task_id>/selected_fl/<int:fl_id>', methods=['GET','POST'])
@customer_required
def select_fl(user_id, task_id, fl_id):
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
        'customer/selected_fl.html', title=title, task_id=task_id, user_id=user_id,
        user_name =user_name, public_bio=public_bio, fl_id=fl_id
        )


@blueprint.route('/<int:user_id>/in_work/', methods=['GET', 'POST'])
@customer_required
def view_in_work_tasks(user_id):
    title = 'Все заказы в работе'
    tasks = Task.query.filter(Task.customer == user_id, Task.status == IN_WORK).all()

    return render_template('customer/in_work.html', title=title, tasks=tasks, user_id=user_id)
