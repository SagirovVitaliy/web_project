from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, DateField, SelectField
from wtforms.validators import DataRequired


class UserForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Отправить')


class TaskForm(FlaskForm):
    task_name = StringField('Название проекта', validators=[DataRequired()])
    description = StringField('Описание', validators=[DataRequired()])
    price = IntegerField('Цена', validators=[DataRequired()])
    submit = SubmitField('Создать проект')


class ChoiseForm(FlaskForm):
    status = SelectField('Выбрать статус', choices=[('kek', 'lol'), ('lol', 'kek')])