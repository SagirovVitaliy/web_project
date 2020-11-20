from flask import Blueprint, render_template, request, redirect, url_for, flash
from webapp.db import db, Task, TaskStatus, User
from flask_login import login_required
from webapp.task.forms import CreateTaskForm
from webapp.db import CREATED

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
