from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, DateField, SelectField, TextAreaField
from wtforms.validators import DataRequired, EqualTo


class IndexForm(FlaskForm):
    submit_for_signin = SubmitField('Войти')
    submit_for_signup = SubmitField('Зарегистрироваться')


class RegistrationForm(FlaskForm):
    username = StringField('Введите имя пользователя', validators=[DataRequired()])
    email = StringField('Введите Email', validators=[DataRequired()])
    phone = IntegerField('Введите телефон')
    role = SelectField('Выберите роль', choices=[])
    public_bio = TextAreaField('Расскажите о себе', validators=[DataRequired()])
    password1 = PasswordField('Введите пароль', validators=[DataRequired()])
    password2 = PasswordField('Повторите пароль', validators=[DataRequired(), EqualTo('password1')])
    submit = SubmitField('Зарегистрироваться')


class LoginForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Войти')


class LogoutForm(FlaskForm):
    submit = SubmitField('Выйти')


class ChoiceTaskForm(FlaskForm):
    tasks = SelectField('Список заказов', choices=[])
    submit = SubmitField('Выбрать заказ')


class SubmitForCreateTaskForm(FlaskForm):
    submit = SubmitField('Создать заказ')


class ChangeTaskStatusForm1(FlaskForm):
    status = SelectField('Выбрать статус', choices=[], validators=[DataRequired()])
    submit = SubmitField('Сменить статус')


class CreateTaskForm(FlaskForm):
    task_name = StringField('Название проекта', validators=[DataRequired()])
    description = TextAreaField('Описание', validators=[DataRequired()])
    price = IntegerField('Цена', validators=[DataRequired()])
    deadline = DateField('Дата завершения проекта', format='%d.%m.%Y', validators=[DataRequired()])
    submit = SubmitField('Создать проект')


class TaskStatusForm(FlaskForm):
    status = SelectField('Выбрать статус', choices=[])
    submit = SubmitField('Сменить статус')


class ChoiceFreelancerForm(FlaskForm):
    freelancers = SelectField('Выбрать фрилансера', choices=[])
    submit = SubmitField('Выбрать')


class ChangeTaskStatusForm(FlaskForm):
    task_id = SelectField('Выбрать задачу', choices=[], validators=[DataRequired()])
    status = SelectField('Новый статус', choices=[], validators=[DataRequired()])
    submit = SubmitField('Сменить статус')