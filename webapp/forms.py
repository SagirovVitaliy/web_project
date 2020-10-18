from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, DateField, SelectField, TextAreaField
from wtforms.validators import DataRequired


class UserForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Отправить')


class TaskForm(FlaskForm):
    task_name = StringField('Название проекта', validators=[DataRequired()])
    description = TextAreaField('Описание', validators=[DataRequired()])
    price = IntegerField('Цена', validators=[DataRequired()])
    deadline = DateField('Дата завершения проекта', format='%d.%m.%Y')
    submit = SubmitField('Создать проект')


class ChoiseForm(FlaskForm):
    status = SelectField('Выбрать статус', choices=[])
    submit = SubmitField('Сменить статус')


class ChangeTaskStatus(FlaskForm):
    task_id = SelectField('Выбрать задачу', choices=[], validators=[DataRequired()])
    status = SelectField('Новый статус', choices=[], validators=[DataRequired()])
    submit = SubmitField('Сменить статус')
