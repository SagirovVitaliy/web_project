'''Валидаторы которые проверяют права доступа к маршрутам Task.'''

from webapp.db import (
    CUSTOMER,
    FREELANCER,
    convert_task_status_id_to_label,
)
from webapp.errors import OperationPermissionError


def current_user_must_be_customer(
        current_user
    ):
    '''Проверка прав доступа для выполнения действия.'''
    
    if current_user == None:
        raise OperationPermissionError(
            'Ваш аккаунт не существует'
            )
    if not current_user.is_authenticated:
        raise OperationPermissionError(
            'Только залогиненные пользователи имеют право на эту операцию'
            )
    if not current_user.is_active:
        raise OperationPermissionError(
            'Вы используете заблокированный аккаунт'
            )
    if not current_user.role == CUSTOMER:
        raise OperationPermissionError(
            'Только Заказчики имеют право на эту операцию'
            )


def current_user_must_be_freelancer(
        current_user
    ):
    '''Проверка прав доступа для выполнения действия.'''
    
    if current_user == None:
        raise OperationPermissionError(
            'Ваш аккаунт не существует'
            )
    if not current_user.is_authenticated:
        raise OperationPermissionError(
            'Только залогиненные пользователи имеют право на эту операцию'
            )
    if not current_user.is_active:
        raise OperationPermissionError(
            'Вы используете заблокированный аккаунт'
            )
    if not current_user.role == FREELANCER:
        raise OperationPermissionError(
            'Только Фрилансеры имеют право на эту операцию'
            )


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


def task_must_be_in_one_of_statuses(task, task_status_ids):
    if not task.status in task_status_ids:
        
        task_status_labels = []
        for task_status_id in task_status_ids:
            task_status_labels.append(
                f'"{convert_task_status_id_to_label(task_status_id)}"'
                )
        message = (
            'Эту операцию можно применять только к Задачам ' +
            ('со статусами ' if len(task_status_ids) > 1 else 'со статусом ') +
            ', '.join(task_status_labels)
            )
        raise OperationPermissionError(message)


def task_must_not_be_in_one_of_statuses(task, task_status_ids):
    if task.status in task_status_ids:
        
        task_status_labels = []
        for task_status_id in task_status_ids:
            task_status_labels.append(
                f'"{convert_task_status_id_to_label(task_status_id)}"'
                )
        message = (
            'Эту операцию нельзя применять к Задачам ' +
            ('со статусами ' if len(task_status_ids) > 1 else 'со статусом ') +
            ', '.join(task_status_labels)
            )
        raise OperationPermissionError(message)
