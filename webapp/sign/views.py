from flask import Blueprint, render_template, flash, redirect, url_for, request
from webapp.sign.forms import LoginForm, RegistrationForm
from webapp.db import db, User, UserRole
from flask_login import login_user, logout_user, current_user
from webapp.db import (CUSTOMER, FREELANCER)

blueprint = Blueprint('sign', __name__)


@blueprint.route('/sign_up', methods=['GET', 'POST'])
def sign_up():
    title = 'Регистрация пользователя'
    form = RegistrationForm()
    form.role.choices = [(role.id, role.role) for role in UserRole.query.all()]

    if request.method == 'POST':
        if form.validate_on_submit():
            user_name = form.user_name.data
            if User.query.filter(User.user_name == user_name).count():
                flash('Пользователь с таким именем уже существует')
            
            password1 = form.password1.data
            password2 = form.password2.data

            if not password1 == password2:
                flash('Пароли не совпадают')

            user = User(
                user_name=user_name,
                public_bio=form.public_bio.data,
                role=form.role.data,
                email=form.email.data,
                phone=form.phone.data,
            )
            user.set_password(password1)

            db.session.add(user)
            db.session.commit()
            flash('Вы успешно зарегистрированы!')
            return redirect(url_for('sign.sign_in'))

    return render_template('sign/sign_up.html', title=title, form=form)


@blueprint.route('/sign_in', methods=['GET', 'POST'])
def sign_in():
    if current_user.is_authenticated:
        flash('Вы уже вошли')
        user = User.query.get(current_user.get_id())
        if user.role == CUSTOMER:
            return redirect(url_for('customer.view_created_tasks', user_id=user.id))
        elif user.role == FREELANCER:
            return redirect(url_for('freelancer.view_tasks_for_fl', user_id=user.id))

    title = 'Вход'
    form = LoginForm()

    if request.method == 'POST':
        if form.validate_on_submit():
            user = User.query.filter(User.user_name == form.user_name.data).first()
            if user and user.check_password(form.password.data):
                login_user(user, remember=form.remember_me.data)
                flash('Вы успешно зашли на сайт')
                user_id = user.id
                if user.role == CUSTOMER:
                    return redirect(url_for('customer.view_created_tasks', user_id=user_id))
                elif user.role == FREELANCER:
                    return redirect(url_for('freelancer.view_tasks_for_fl', user_id=user_id))
                else:
                    flash('Неправильное имя или пароль')
                    return render_template('sign/sign_in.html', title=title, form=form)

    return render_template('sign/sign_in.html', title=title, form=form)


@blueprint.route('/sign_out')
def sign_out():
    logout_user()
    flash('Вы успешно вышли')
    return redirect(url_for('sign.index'))


@blueprint.route('/', methods=['GET', 'POST'])
def index():
    title = 'Главная страница'
    demo_links = [
        {
            'url': url_for('sign.sign_up'),
            'label': '〰😶 Регистрация.',
        },
        {
            'url': url_for('sign.sign_in'),
            'label': '〰😶 Войти.',
        },
        {
            'url': url_for('sign.sign_out'),
            'label': '〰😶 Выйти.',
        },
        {
            'url': url_for('task.view_task', task_id=2),
            'label': '〰😶 Просмотреть Задачу номер 2.',
        },
        {
            'url': url_for('task.view_task', task_id=3),
            'label': '〰😶 Просмотреть Задачу номер 3.',
        },
        {
            'url': url_for('task.dismiss_responded_freelancer_from_task', task_id=3),
            'label': '➖💀 Отцепить от Задачи номер 3, Предварительно Откликнувшегося Фрилансера номер...',
        },
        {
            'url': url_for('task.view_task', task_id=4),
            'label': '〰😶 Просмотреть Задачу номер 4.',
        },
        {
            'url': url_for('task.move_task_to_in_work', task_id=4),
            'label': '➕😁 Двинуть Задачу номер 4 в статус in_work.',
        },
        {
            'url': url_for('task.move_task_to_in_review', task_id=4),
            'label': '➕😁 Двинуть Задачу номер 4 в статус in_review.',
        },
        {
            'url': url_for('task.move_task_to_done', task_id=4),
            'label': '➕😁 Двинуть Задачу номер 4 в статус done.',
        },
        {
            'url': url_for('task.cancel_task', task_id=4),
            'label': '➖💀 Отменить Задачу номер 4.',
        },
        {
            'url': url_for('task.dismiss_confirmed_freelancer_from_task', task_id=4),
            'label': '➖💀 Отцепить от Задачи номер 4, Фрилансера-Исполнителя номер...',
        },
        {
            'url': url_for('task.view_task', task_id=5),
            'label': '〰😶 Просмотреть Задачу номер 5.',
        },
        {
            'url': url_for('task.move_task_to_in_work', task_id=5),
            'label': '➕😁 Двинуть Задачу номер 5 в статус in_work.',
        },
        {
            'url': url_for('task.move_task_to_in_review', task_id=5),
            'label': '➕😁 Двинуть Задачу номер 5 в статус in_review.',
        },
        {
            'url': url_for('task.move_task_to_done', task_id=5),
            'label': '➕😁 Двинуть Задачу номер 5 в статус done.',
        },
        {
            'url': url_for('task.cancel_task', task_id=5),
            'label': '➖💀 Отменить Задачу номер 5.',
        },
        {
            'url': url_for('task.dismiss_confirmed_freelancer_from_task', task_id=5),
            'label': '➖💀 Отцепить от Задачи номер 5, Фрилансера-Исполнителя номер...',
        },
    ]

    return render_template(
        'sign/index.html',
        title=title,
        demo_links=demo_links
        )