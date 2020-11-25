'''Валидаторы которые проверяют права доступа к маршрутам Task.'''

from webapp.db import CUSTOMER, FREELANCER
from webapp.errors import OperationPermissionError


def current_user_must_be_connected_to_task_as_customer(
        current_user,
        task
    ):
    '''Проверка прав доступа для выполнения действия.'''
    
    if current_user == None:
        raise OperationPermissionError(
            'Ваш аккаунт не существует'
            )
    if task == None:
        raise OperationPermissionError(
            'Задача не существует'
            )
    if not current_user.is_authenticated:
        raise OperationPermissionError(
            'Только залогиненные пользователи имеют право на эту операцию'
            )
    if not current_user.is_active:
        raise OperationPermissionError(
            'Вы используете заблокированный аккаунт'
            )
    if not current_user.id == task.customer:
        raise OperationPermissionError(
            'Только Заказчик поставивший эту Задачу имеет право на эту операцию'
            )
    if not current_user.role == CUSTOMER:
        raise OperationPermissionError(
            'Только Заказчики имеют право на эту операцию'
            )


def current_user_must_be_connected_to_task_as_confirmed_freelancer(
        current_user,
        task
    ):
    '''Проверка прав доступа для выполнения действия.'''
    
    if current_user == None:
        raise OperationPermissionError(
            'Ваш аккаунт не существует'
            )
    if task == None:
        raise OperationPermissionError(
            'Задача не существует'
            )
    if not current_user.is_authenticated:
        raise OperationPermissionError(
            'Только залогиненные пользователи имеют право на эту операцию'
            )
    if not current_user.is_active:
        raise OperationPermissionError(
            'Вы используете заблокированный аккаунт'
            )
    if not current_user.id == task.freelancer:
        raise OperationPermissionError(
            'Только Подтверждённый Исполнитель Задачи имеет право на эту операцию'
            )
    if not current_user.role == FREELANCER:
        raise OperationPermissionError(
            'Только Фрилансеры имеют право на эту операцию'
            )
