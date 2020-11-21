from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, DateField, TextAreaField
from wtforms.validators import DataRequired


class SimpleConfirmForm(FlaskForm):
    submit = SubmitField('Подтвердить')


class CreateTaskForm(FlaskForm):
    task_name = StringField('Название проекта', validators=[DataRequired()])
    description = TextAreaField('Описание', validators=[DataRequired()])
    price = IntegerField('Цена', validators=[DataRequired()])
    deadline = DateField('дд.мм.гггг', format='%d.%m.%Y', validators=[DataRequired()])
    submit = SubmitField('Создать проект')
