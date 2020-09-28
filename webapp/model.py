from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    password = db.Column(db.String(128))
    role = db.Column(db.String())
    email = db.Column(db.String(), unique=True)
    phone = db.Column(db.Integer, unique=True)
    tag = db.Colomn(db.String(20))

    def __repr__(self):
        return'<User {}>'.format()
        # Пока не понятно, что из этого нам понадобится возвращать и куда?
        # и тут же появился вопрос, если мы что то хотим взять из БД
        # не можем ли мы просто залезть в неё и взять Или обязательно её значения надо возвращать?


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(), nullable=False)
    price = db.Column(db.Integer())
    deadline = db.Column(db.String()) # Не знаю есть ли тут формат даты
    # По идее мы всё остальное будем наследовать из другой Бд пока не знаю как это делается.

    def __repr__(self):
        return '<Task {}>'.format()
