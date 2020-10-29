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

    with open(fixture_path, 'r', encoding='utf-8') as read_file:
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
        model_class,
        conversion_rules={}
    ):
    '''Добавить в Базу Данных: Записи.'''
    table_name_in_data = model_class.__tablename__
    table_rows = data.get(table_name_in_data, []);
    for table_row in table_rows:
        push_table_row_to_db(
            model_class=model_class,
            table_row=table_row,
            conversion_rules=conversion_rules
        )


def push_m2m_relationship_to_db(
        a_class,
        a_relationship_prop_name,
        b_class,
        table_row
    ):
    '''Добавить в Базу Данных: одну Связь (между двумя предметами А и Б).

    Keyword arguments:

    a_class -- класс предмета А (без дефолта)
    a_relationship_prop_name -- имя свойства класса A, которое содержит
                                отношение (без дефолта).

    b_class -- класс предмета Б (без дефолта)

    table_row -- ряд таблицы, описывающий связь двух предметов; в ряду -
                 2 элемента - id Предмета A и id Предмета Б.
    '''
    def get_item(z_class):
        id_name_in_table_row = z_class.__tablename__ + '.id'
        id_name_in_class = 'id'

        z_item = z_class.query.filter(
            getattr(z_class, id_name_in_class) ==
            table_row[id_name_in_table_row]
        ).first()

        return z_item

    a_item = get_item(a_class)
    b_item = get_item(b_class)

    getattr(a_item, a_relationship_prop_name).append(b_item)
    db.session.commit()
    pass


def push_m2m_relationships_to_db(
        data,
        a_class,
        a_relationship_prop_name,
        b_class
    ):
    '''Добавить в Базу Данных: Отношения многие-ко-многим.

    Обычно вы прислаете в data - то что содержалось в JSON файле фикстуры.
    Ожидается что data - это словарь. data может содержать поле которое содержит
    данные для простой двусторонней связи двух сущностей по двум id. Название
    этого поля в data вычисляется на основе параметров которые вы прислали -
    a_class, a_relationship_prop_name.

    Если вы прислали класс a_class=SomeExampleClass и
    a_relationship_prop_name='some_example_field', то название поля на выходе
    этого алгоритма будет 'm2m.some_example_class.some_example_field'.

    По идее, точки в названии должны сделать невозможными коллизии если вы
    следуете обычным конвенциям для того чтобы называть классы и свойства даже
    если у вас есть класс 'm2m'.
    '''
    table_name_in_data = f'm2m.{a_class.__tablename__}.{a_relationship_prop_name}'
    table_rows = data.get(table_name_in_data, []);

    for table_row in table_rows:
        push_m2m_relationship_to_db(
            a_class=a_class,
            a_relationship_prop_name=a_relationship_prop_name,
            b_class=b_class,
            table_row=table_row
        )


def push_data_to_db(data):
    '''Добавить в Базу Данных: Записи и Отношения многие-ко-многим.

    Это функция-клей.

    Эта функция - не общего назначения. В том виде как она записана сейчас, она
    не подойдёт другим сайтам. Она заточена под нашу структуру БД; и даже больше
    того - под конкретную миграцию. Она ожидает наши названия таблиц и модель.
    Подробней, про текущую структуру БД, смотрите файл webapp/model.py.

    Но хотя эта функция заточена под конкретный сайт и конкретную миграцию, её
    можно использовать как пример использования функций из этого модуля.
    '''
    push_table_to_db(
        data=data,
        model_class=Email
    )
    push_table_to_db(
        data=data,
        model_class=Phone
    )
    push_table_to_db(
        data=data,
        model_class=UserRole
    )
    push_table_to_db(
        data=data,
        model_class=User
    )
    push_table_to_db(
        data=data,
        model_class=Tag
    )
    push_table_to_db(
        data=data,
        model_class=TaskStatus
    )
    push_table_to_db(
        data=data,
        model_class=Task,
        conversion_rules={
            'deadline': 'date_iso8601',
        }
    )

    # Связи Many-To-Many надо подгружать после всех push_table_to_db.
    push_m2m_relationships_to_db(
        data=data,
        a_class=User,
        a_relationship_prop_name='responded_to_tasks',
        b_class=Task
    )


app = create_app()
with app.app_context():
    fixture_file_name = get_fixture_file_name()
    data = get_data_from_file(file_name=fixture_file_name)
    push_data_to_db(data)

