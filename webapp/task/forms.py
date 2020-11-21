from flask_wtf import FlaskForm
from wtforms import (
    BooleanField,
    DateField,
    IntegerField,
    PasswordField,
    SelectField,
    StringField,
    SubmitField,
    TextAreaField,
    )
from wtforms.validators import DataRequired


class CreateTaskForm(FlaskForm):
    task_name = StringField('Название проекта', validators=[DataRequired()])
    description = TextAreaField('Описание', validators=[DataRequired()])
    price = IntegerField('Цена', validators=[DataRequired()])
    deadline = DateField('дд.мм.гггг', format='%d.%m.%Y', validators=[DataRequired()])
    submit = SubmitField('Создать проект')


# TODO: check if it's even required.
class DismissFreelancerFromTaskForm(FlaskForm):
    task_id = SelectField('Выбрать задачу', choices=[], validators=[DataRequired()])
    user_id = SelectField('Выбрать Фрилансера', choices=[], validators=[DataRequired()])
    submit = SubmitField('Отцепить!')


class SimpleConfirmForm(FlaskForm):
    submit = SubmitField('Подтвердить')
