from webapp import create_app
from webapp.model import db, Email, Phone, Role, User, Tag, Status, Task
from dateparser import parse
from sys import argv

import json


'''
    Ожидается что этот файл будет использоваться в коммандной строке в стиле:
    python3 load_fixture.py
    или
    python3 load_fixture.py abcd
    где вместо "abcd" надо присылать назваание файла фикстуры.

    Файл с фиктурой ищется в папке fixtures/__имя_файла__.json

    Для примера с abcd это будет fixtures/abcd.json

    python3 load_fixture.py
    - особый случай: будет подключаться фикстура по адресу fixtures/default.json
'''


def get_fixture_file_name():
    argument_list = argv
    fixture_file_name = 'default'

    if len(argument_list) > 1:
        fixture_file_name = f'{argv[1]}'

    return fixture_file_name


def get_data_from_file(file_name):
    fixture_folder = 'fixtures/'
    fixture_file_name = f'{file_name}'
    fixture_file_extension = '.json'
    fixture_path = fixture_folder + fixture_file_name + fixture_file_extension

    with open(fixture_path, "r", encoding='utf-8') as read_file:
        data = json.load(read_file)
    
    return data


def push_data_to_db(data):
    for value in data['email']:
        email = Email(email=value['email'])
        db.session.add(email)
        db.session.commit()
    
    for value in data['phone']:
        phone = Phone(phone=value['phone'])
        db.session.add(phone)
        db.session.commit()

    for value in data['user_role']:
        user_role = Role(role=value['role'])
        db.session.add(user_role)
        db.session.commit()
    
    for value in data['user']:
        user = User(username=value['username'], password=value['password'], public_bio=value['public_bio'])
        db.session.add(user)
        db.session.commit()

    for value in data['tag']:
        tag = Tag(tag=value['tag'])
        db.session.add(tag)
        db.session.commit()

    for value in data['task_status']:
        status = Status(status=value['status'])
        db.session.add(status)
        db.session.commit()

    for value in data['task']:
        task = Task(task_name=value['task_name'], description=value['description'], price=value['price'], deadline=parse(value['deadline']))
        db.session.add(task)
        db.session.commit()


app = create_app()
with app.app_context():
    fixture_file_name = get_fixture_file_name()
    data = get_data_from_file(file_name=fixture_file_name)
    push_data_to_db(data)
