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


class FreelancerForm(FlaskForm):
    tasks = SelectField('Выбрать заказ', choices=[])
    submit = SubmitField('Отликнутся')


class InWorkForm(FlaskForm):
    tasks = SelectField('Выбрать заказ', choices=[])
    submit = SubmitField('Выбрать')


class InWorkFormTwo(FlaskForm):
    freelancers = SelectField('Выбрать фрилансера', choices=[])
    submit = SubmitField('Выбрать')
