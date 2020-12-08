from flask_wtf import FlaskForm
from wtforms import BooleanField, StringField, PasswordField, SubmitField, IntegerField, SelectField, TextAreaField
from wtforms.validators import DataRequired, EqualTo


class RegistrationForm(FlaskForm):
    user_name = StringField('Введите имя пользователя', validators=[DataRequired()])
    email = StringField('Введите Email', validators=[DataRequired()])
    phone = IntegerField('Введите телефон')
    role = SelectField('Выберите роль', choices=[])
    public_bio = TextAreaField('Расскажите о себе', validators=[DataRequired()])
    password1 = PasswordField('Введите пароль', validators=[DataRequired()])
    password2 = PasswordField('Повторите пароль', validators=[DataRequired(), EqualTo('password1')])
    submit = SubmitField('Зарегистрироваться', render_kw={'class': 'btn btn-dark'})


class LoginForm(FlaskForm):
    user_name = StringField('Имя пользователя', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня', default=True, render_kw={"class": "custom-control-input custom-control-input-black"})
    submit = SubmitField('Войти', render_kw={'class': 'btn btn-dark'})