from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField
from wtforms.validators import DataRequired


class User_form(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Отправить')


class Task_form(FlaskForm):
    task_name = StringField('Название проекта', validators=[DataRequired()])
    description = StringField('Описание', validators=[DataRequired()])
    price = IntegerField('Цена', validators=[DataRequired()])
    deadline = StringField('Дата завершения проекта')
    submit = SubmitField('Создать проект')
    submit_published = SubmitField('Опубликовать проект')