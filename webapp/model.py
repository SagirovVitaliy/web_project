from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Email(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(), unique=True)


class Phone(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    phone = db.Column(db.Integer, unique=True)


class User_role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.String(), nullable=False)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    password = db.Column(db.String(128))
    public_bio = db.Column(db.String())

    role = db.Column(
        db.Integer(),
        db.ForeignKey('user_role.id', ondelete='CASCADE') 
        )

    email = db.Column(
        db.Integer(),
        db.ForeignKey('email.id', ondelete='CASCADE') 
        )

    phone = db.Column(
        db.Integer,
        db.ForeignKey('phone.id', ondelete='CASCADE')
        )

    tag = db.Column(
        db.Integer(),
        db.ForeignKey('user.id', ondelete='CASCADE')
        )

    def __repr__(self):
        return'<User {} {}>'.format(self.id, self.username)


class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tag = db.Column(db.String(20))


class Task_status(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(), nullable=False)


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task_name = db.Column(db.String())
    description = db.Column(db.String(), nullable=False)
    price = db.Column(db.Integer())
    deadline = db.Column(db.DateTime)
    status = db.Column(
        db.Integer(),
        db.ForeignKey('task_status.id', ondelete='CASCADE')
    ) 

    customer = db.Column(
        db.Integer(),
        db.ForeignKey('user.id', ondelete='CASCADE') 
        )

    freelancer = db.Column(
        db.Integer(),
        db.ForeignKey('user.id', ondelete='CASCADE') 
        )

    tag = db.Column(
        db.Integer(),
        db.ForeignKey('user.id', ondelete='CASCADE')
        )

    def __repr__(self):
        return '<Task {} {}>'.format(self.id, self.task_name)
