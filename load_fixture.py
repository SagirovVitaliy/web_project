from webapp import create_app
from webapp.model import db, Email, Phone, User_role, User, Tag, Task_status, Task


def get_data(data):
    for value in data['email']:
        email = Email(email=value['email'])
        db.session.add(email)
        db.session.commit()
    
    for value in data['phone']:
        phone = Phone(phone=value['phone'])
        db.session.add(phone)
        db.session.commit()

    for value in data['user_role']:
        user_role = User_role(role=value['role'])
        db.session.add(user_role)
        db.session.commit()
    
    for value in data['user']:
        user = User(username=value['username'], password=value['password'], public_bio=value['public_bio'] )
        db.session.add(user)
        db.session.commit()

    for value in data['tag']:
        tag = Tag(tag=value['tag'])
        db.session.add(tag)
        db.session.commit()

    for value in data['task_status']:
        status = Task_status(status=value['status'])
        db.session.add(status)
        db.session.commit()

    for value in data['task']:
        task = Task(task_name=value['task_name'], description=value['description'], price=value['price'], deadline=value['deadline'])
        db.session.add(task)
        db.session.commit()


data = {
    'email': [
        {
            'email': 'ww@mail.ru'
        },
        {
            'email': 'dkwjed@mail.ru'
        }
    ],
    'phone': [
        {
            'phone': '79828762465'
        },
        {
            'phone': '89651933244'
        }
    ],
    'user_role': [
        {
            'role': 'freelancer'
        },
        {
            'role': 'customer'
        }
    ],
    'user': [
        {
            'username': 'alex_syystem',
            'password': 'lcasdnjkncadkc',
            'public_bio': 'профессионально изготавливаю злых ежей'
        },
        {
            'username': 'german_gref',
            'password': 'mprewvewjgrn',
            'public_bio': 'Компания с тысячелетней историей поставки злых ежей'
        }
    ],
    'tag': [
        {
            'tag': 'Разведение ежей'
        },
        {
            'tag': 'Изготовление сайта'
        }
    ],
    'task_status': [
        {
            'status': 'created'
        },
        {
            'status': 'published'
        },
        {
            'status': 'freelancers_detected'
        },
        {
            'status': 'in_work'
        },
        {
            'status': 'stopped'
        },
        {
            'status': 'in_review'
        },
        {
            'status': 'done'
        }
    ],
    'task': [
        {
            'task_name': 'изготовление ежей',
            'description': 'надо изготовить злых ежей',
            'price': 20000,
            'deadline': '2020-10-14'
        },
        {
            'task_name': 'Сделать сайт',
            'description': 'Полная разработка сайта',
            'price': 500000,
            'deadline': '2020-10-31'
        },
    ]
}

app = create_app()
with app.app_context():
    get_data(data)
