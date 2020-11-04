'''Несколько валидаторов чтобы сделать маршруты красивее.'''

from webapp.model import Task, User
from webapp.errors import ValidationError
from webapp.model import CUSTOMER, FREELANCER


def validate_form(
        form,
        failure_feedback='Некорректно заполнены поля формы.'
    ):
    if not form.validate_on_submit():
        raise ValidationError(failure_feedback)


def validate_task_existence(
        task,
        failure_feedback='Указанная в запросе Задача не существует. Попробуйте изменить критерий поиска и попровать снова.'
    ):
    if task == None:
        raise ValidationError(failure_feedback)


def validate_user_existence(
        user,
        failure_feedback='Операция не может быть выполнена, потому что указанный в запросе Пользователь не существует.'
    ):
    if user == None:
        raise ValidationError(failure_feedback)


def validate_if_user_is_customer(
        user,
        failure_feedback='Операция не может быть выполнена, потому что указанный в запросе пользователь не является Заказчиком.'
    ):
    if user.role != CUSTOMER:
        raise ValidationError(failure_feedback)


def validate_if_user_is_freelancer(
        user,
        failure_feedback='Операция не может быть выполнена, потому что указанный в запросе пользователь не является Фрилансером.'
    ):
    if user.role != FREELANCER:
        raise ValidationError(failure_feedback)


def is_user_connected_to_task_as_customer(
        user,
        task,
        failure_feedback='Операция не может быть выполнена, потому что указанный в запросе Пользователь не привязан к указанной Задаче как Заказчик.'
    ):
    if task.customer != user.id:
        raise ValidationError(failure_feedback)


def is_user_connected_to_task_as_confirmed_freelancer(
        user,
        task,
        failure_feedback='Операция не может быть выполнена, потому что указанный в запросе Пользователь не привязан к указанной Задаче как Предварительно Откликнувшийся Фрилансер.'
    ):
    if task.freelancer != user.id:
        raise ValidationError(failure_feedback)


def is_user_connected_to_task_as_responded_freelancer(
        user,
        task,
        failure_feedback='Операция не может быть выполнена, потому что указанный в запросе Пользователь не привязан к указанной Задаче как Предварительно Откликнувшийся Фрилансер.'
    ):
    user = task.freelancers_who_responded.filter(
        User.id == user.id
    ).first()
    if user == None:
        raise ValidationError(failure_feedback)
