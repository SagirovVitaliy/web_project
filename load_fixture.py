'''
    Ожидается что этот файл будет использоваться в коммандной строке в стиле:
    python3 load_fixture.py
    или
    python3 load_fixture.py abcd
    где вместо "abcd" надо присылать название файла фикстуры.

    Файл с фиктурой ищется в папке fixtures/__имя_файла__.json

    Для примера с abcd это будет fixtures/abcd.json

    python3 load_fixture.py
    - особый случай: будет подключаться фикстура по адресу fixtures/default.json
'''
from webapp import create_app
from webapp.model import (
    db, Email, Phone, UserRole, User, Tag, TaskStatus, Task,
    freelancers_who_responded
    )
from dateparser import parse
from sys import argv

import json


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


def push_table_row_to_db(model_class, table_row, conversion_rules={}):
    item = model_class()
    for prop_name in table_row:

        prop_value = table_row[prop_name]

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
    """Добавить в Базу Данных: Записи."""
    table_rows = data.get(table_name_in_data, []);
    for table_row in table_rows:
        push_table_row_to_db(
            model_class=model_class,
            table_row=table_row,
            conversion_rules=conversion_rules
        )


def push_m2m_relationship_to_db(
        model_class_a,
        model_class_a_prop_name_in_data,
        model_class_a_prop_name_in_class,
        model_class_a_relationship_in_class,
        
        model_class_b,
        model_class_b_prop_name_in_data,
        model_class_b_prop_name_in_class,
        
        table_row
    ):
    """Добавить в Базу Данных: одну Связь (между двумя предметами А и Б).

    Keyword arguments:

    model_class_a -- класс предмета А (без дефолта)
    model_class_a_prop_name_in_data -- имя свойства с id Предмета А в table_row.
    model_class_a_prop_name_in_class -- имя свойства с id Предмета А в классе А.
    model_class_a_relationship_in_class --

    model_class_b -- класс предмета Б (без дефолта)
    model_class_b_prop_name_in_data -- имя свойства с id Предмета Б в table_row.
    model_class_b_prop_name_in_class -- имя свойства с id Предмета Б в классе Б.

    table_row -- ряд таблицы, описывающий связь двух предметов; в ряду -
                 2 элемента - id Предмета A и id Предмета Б.
    """
    item_a = model_class_a.query.filter(
        getattr(model_class_a, model_class_a_prop_name_in_class) ==
        table_row[model_class_a_prop_name_in_data]
    ).first()
    
    item_b = model_class_b.query.filter(
        getattr(model_class_b, model_class_b_prop_name_in_class) ==
        table_row[model_class_b_prop_name_in_data]
    ).first()

    getattr(item_a, model_class_a_relationship_in_class).append(item_b)
    db.session.commit()
    pass


def push_m2m_relationships_to_db(
        data,
        table_name_in_data,
        
        model_class_a,
        model_class_a_prop_name_in_data,
        model_class_a_prop_name_in_class,
        model_class_a_relationship_in_class,
        
        model_class_b,
        model_class_b_prop_name_in_data,
        model_class_b_prop_name_in_class
    ):
    """Добавить в Базу Данных: Отношения многие-ко-многим."""
    table_rows = data.get(table_name_in_data, []);
    for table_row in table_rows:
        push_m2m_relationship_to_db(
            model_class_a=model_class_a,
            model_class_a_prop_name_in_data=model_class_a_prop_name_in_data,
            model_class_a_prop_name_in_class=model_class_a_prop_name_in_class,
            model_class_a_relationship_in_class=model_class_a_relationship_in_class,
            
            model_class_b=model_class_b,
            model_class_b_prop_name_in_data=model_class_b_prop_name_in_data,
            model_class_b_prop_name_in_class=model_class_b_prop_name_in_class,
            
            table_row=table_row
        )


def push_data_to_db(data):
    """Добавить в Базу Данных: Записи и Отношения многие-ко-многим.

    Это функция-клей.

    Эта функция - не общего назначения. В том виде как она записана сейчас, она
    не подойдёт другим сайтам. Она заточена под нашу структуру БД; и даже больше
    того - под конкретную миграцию. Она ожидает наши названия таблиц и модель.
    Подробней, про текущую структуру БД, смотрите файл webapp/model.py.

    Но хотя эта функция заточена под конкретный сайт и конкретную миграцию, её
    можно использовать как пример использования функций из этого модуля.
    """
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
        model_class=UserRole
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
        model_class=TaskStatus
    )
    push_table_to_db(
        data=data,
        table_name_in_data='task',
        model_class=Task,
        conversion_rules={
            'deadline': 'date_iso8601',
        }
    )

    # Связи Many-To-Many надо подгружать после всех push_table_to_db.
    push_m2m_relationships_to_db(
        data=data,
        table_name_in_data='m2m_freelancers_who_responded',
        model_class_a=User,
        model_class_a_prop_name_in_data='user_id',
        model_class_a_prop_name_in_class='id',
        model_class_a_relationship_in_class='responded_to_tasks',
        model_class_b=Task,
        model_class_b_prop_name_in_data='task_id',
        model_class_b_prop_name_in_class='id'
    )


app = create_app()
with app.app_context():
    fixture_file_name = get_fixture_file_name()
    data = get_data_from_file(file_name=fixture_file_name)
    push_data_to_db(data)

