

def test_new_user_with_fixture(new_user):
    '''
    GIVEN User model
    WHEN a new User creating
    THEN check the User fields are defined correct
    '''
    assert new_user.user_name == 'Сергей Галицкий'
    assert new_user.public_bio == 'Сделаю из вашего бизнеса магнит'
    assert new_user.role == 1
    assert new_user.email == 'gal@mail.ru'
    assert new_user.phone == 85557775466
    assert new_user.tag == 'magnit'
    assert new_user.password != '254565'


def test_new_task_with_fixture(new_task):
    '''
    GIVEN Task model
    WHEN a new Task creating
    THEN check the Task fields are defined correct
    '''
    assert new_task.task_name == 'Для теста'
    assert new_task.description == 'Это наша тестовая задача'
    assert new_task.price == 3000
    assert new_task.deadline == '2020-10-21'
    assert new_task.status == 4
    assert new_task.customer == 3
    assert new_task.freelancer == 6
    assert new_task.tag == 'magnit'

