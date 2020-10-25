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


def push_item_to_db(model_class, dictionary_item, conversion_rules={}):
    item = model_class()
    for prop_name in dictionary_item:

        prop_value = dictionary_item[prop_name]

        # В редких случаях могут прислать правила в формате который нельзя
        # посылать напрямую в db - например когда присылают дату в формате
        # '2020-10-10', а db ожидает объект даты. В таких случаях - присылайте
        # пометку о том что нужно сделать определённое преобразование.
        conversion_rule = conversion_rules.get(prop_name, None)
        if conversion_rule == 'date_iso8601':
            prop_value = parse(prop_value)

        setattr(item, prop_name, prop_value)
    print('New item:')
    print(item)
    db.session.add(item)
    db.session.commit()


def push_table_to_db(
        data,
        table_name_in_data,
        model_class,
        conversion_rules={}
    ):
    table_elements = data.get(table_name_in_data, []);
    for element in table_elements:
        push_item_to_db(
            model_class=model_class,
            dictionary_item=element,
            conversion_rules=conversion_rules
        )


def push_data_to_db(data):

    push_table_to_db(
        data=data,
        table_name_in_data='email',
        model_class=Email
    )
    push_table_to_db(
        data=data,
        table_name_in_data='phone',
        model_class=Phone
    )
    push_table_to_db(
        data=data,
        table_name_in_data='user_role',
        model_class=Role
    )
    push_table_to_db(
        data=data,
        table_name_in_data='user',
        model_class=User
    )
    push_table_to_db(
        data=data,
        table_name_in_data='tag',
        model_class=Tag
    )
    push_table_to_db(
        data=data,
        table_name_in_data='task_status',
        model_class=Status
    )
    push_table_to_db(
        data=data,
        table_name_in_data='task',
        model_class=Task,
        conversion_rules={
            'deadline': 'date_iso8601',
        }
    )


app = create_app()
with app.app_context():
    fixture_file_name = get_fixture_file_name()
    data = get_data_from_file(file_name=fixture_file_name)
    push_data_to_db(data)
