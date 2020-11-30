import pytest
from webapp.db import User, Task, CUSTOMER

from webapp import create_app


@pytest.fixture(scope='module')
def new_user():
    user = User(
        user_name='Сергей Галицкий',
        public_bio='Сделаю из вашего бизнеса магнит',
        role=CUSTOMER,
        email='gal@mail.ru',
        phone=85557775466,
        tag='magnit'
        )

    password = '254565'
    user.set_password(password)

    return user


@pytest.fixture(scope='module')
def new_task():
    task = Task(
        task_name='Для теста',
        description='Это наша тестовая задача',
        price=3000,
        deadline='2020-10-21',
        status=4,
        customer=3,
        freelancer=6,
        tag='magnit'
        )

    return task


@pytest.fixture(scope='module')
def test_client():
    flask_app = create_app('config_test.py')

    with flask_app.test_client() as testing_client:
        with flask_app.app_context():
            yield testing_client


