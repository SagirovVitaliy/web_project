from flask import Blueprint, render_template, flash, redirect, url_for, request
from webapp.db import db, Task, User
from webapp.freelancer.decorators import freelancer_required
from webapp.db import PUBLISHED, FREELANCERS_DETECTED, IN_WORK

blueprint = Blueprint('freelancer', __name__, url_prefix='/freelancer')


@blueprint.route('/<int:user_id>/', methods=['GET', 'POST'])
@freelancer_required
def view_tasks_for_fl(user_id):
    title = 'Все актуальные заказы'
    tasks = Task.query.filter(Task.status.in_([PUBLISHED, FREELANCERS_DETECTED])).all()

    return render_template('freelancer/freelancer.html', title=title, tasks=tasks, user_id=user_id)


@blueprint.route('/<int:user_id>/fl_task/<int:task_id>', methods=['GET', 'POST'])
@freelancer_required
def view_task_information(user_id, task_id):
    title = 'Информация по заказы'
    task = Task.query.get(task_id)
    task_name = task.task_name
    description = task.description
    price = task.price
    deadline = task.deadline

    if request.method == 'POST':
        user = User.query.get(user_id)
        freelancers = task.freelancers_who_responded.all()
        if user in freelancers:
            flash('Вы уже откликнулись на эту задачу!')
        else:
            task.freelancers_who_responded.append(user)
            task.status = FREELANCERS_DETECTED
            db.session.commit()
            flash('Вы откликнулись на задачу, ждите решения заказчика')

    return render_template(
        'freelancer/fl_task_information.html', title=title, task_id=task_id, user_id=user_id, task_name=task_name, 
        description=description, price=price, deadline=deadline, task=task
        )


@blueprint.route('/<int:user_id>/fl_in_work/', methods=['GET', 'POST'])
@freelancer_required
def view_tasks_in_work(user_id):
    title = 'Все заказы в работе'
    tasks = Task.query.filter(Task.freelancer == user_id, Task.status == IN_WORK).all()

    if request.method == 'POST':

        if form.validate_on_submit():
            task_id = form.tasks.data
            return redirect(url_for('', task_id=task_id))

    return render_template('freelancer/fl_in_work.html', title=title, user_id=user_id, tasks=tasks )
