from webapp import create_app
from webapp.model import db, Email, Phone, User_role, User, Tag, Task_status, Task
from dateparser import parse

import json

with open("fixtures.json", "r", encoding='utf-8') as read_file:
    data = json.load(read_file)


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
        task = Task(task_name=value['task_name'], description=value['description'], price=value['price'], deadline=parse(value['deadline']))
        db.session.add(task)
        db.session.commit()


app = create_app()
with app.app_context():
    get_data(data)
