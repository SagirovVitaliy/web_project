from flask_sqlalchemy import SQLAlchemy

# Задаём конвенции того как называть Constraints. Подробней зачем это нужно
# можно посмотреть тут:
# https://stackoverflow.com/questions/29153930/changing-constraint-naming-conventions-in-flask-sqlalchemy
# https://flask-sqlalchemy.palletsprojects.com/en/master/config/
from sqlalchemy import MetaData

metadata = MetaData(
  naming_convention={
    'pk': 'pk_%(table_name)s',
    'fk': 'fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s',
    'ix': 'ix_%(table_name)s_%(column_0_name)s',
    'uq': 'uq_%(table_name)s_%(column_0_name)s',
    'ck': 'ck_%(table_name)s_%(constraint_name)s',
    }
)
db = SQLAlchemy(metadata=metadata)


def prettify(class_label, prop_line_list):
    props = ' '.join(prop_line_list)
    return f'<{class_label}: {props}>'


class Email(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(), unique=True)
    
    def __repr__(self):
        return prettify(
            class_label='Email',
            prop_line_list=[
                f'id:{self.id}',
                f'email:{self.email}',
            ]
        )


class Phone(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    phone = db.Column(db.Integer, unique=True)
    
    def __repr__(self):
        return prettify(
            class_label='Phone',
            prop_line_list=[
                f'id:{self.id}',
                f'phone:{self.phone}',
            ]
        )


class UserRole(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.String(), nullable=False)
    
    def __repr__(self):
        return prettify(
            class_label='UserRole',
            prop_line_list=[
                f'id:{self.id}',
                f'role:{self.role}',
            ]
        )

freelancers_who_responded = db.Table('freelancers_who_responded',
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
    db.Column('task_id', db.Integer(), db.ForeignKey('task.id'))
)

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
        db.Integer(),
        db.ForeignKey('phone.id', ondelete='CASCADE')
        )

    tag = db.Column(
        db.Integer(),
        db.ForeignKey('tag.id', ondelete='CASCADE')
        )

    responded_to_tasks = db.relationship(
        'Task', secondary=freelancers_who_responded,
        backref=db.backref('freelancers_who_responded', lazy='dynamic'))

    def __repr__(self):
        return prettify(
            class_label='User',
            prop_line_list=[
                f'id:{self.id}',
                f'username:{self.username}',
                f'role:{self.role}',
                f'email:{self.email}',
                f'phone:{self.phone}',
                f'tag:{self.tag}',
                f'password:{self.password}',
                f'public_bio:{self.public_bio}',
            ]
        )


class TaskStatus(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(), nullable=False)

    def __repr__(self):
        return prettify(
            class_label='TaskStatus',
            prop_line_list=[
                f'id:{self.id}',
                f'status:{self.status}',
            ]
        )


class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tag = db.Column(db.String(20))

    def __repr__(self):
        return prettify(
            class_label='Tag',
            prop_line_list=[
                f'id:{self.id}',
                f'tag:{self.tag}',
            ]
        )


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task_name = db.Column(db.String())
    description = db.Column(db.String(), nullable=False)
    price = db.Column(db.Integer())
    deadline = db.Column(db.Date())
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
        db.ForeignKey('tag.id', ondelete='CASCADE')
        )

    def __repr__(self):
        return prettify(
            class_label='Task',
            prop_line_list=[
                f'id:{self.id}',
                f'price:{self.price}',
                f'deadline:{self.deadline}',
                f'status:{self.status}',
                f'customer:{self.customer}',
                f'freelancer:{self.freelancer}',
                f'tag:{self.tag}',
                f'task_name:{self.task_name}',
                f'description:{self.description}',
            ]
        )

      
class TaskComment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String())

    task = db.Column(
        db.Integer(),
        db.ForeignKey('task.id')
        )

    def __repr__(self):
        return prettify(
            class_label='TaskComment',
            prop_line_list=[
                f'id:{self.id}',
                f'content:{self.content}',
                f'task:{self.task}',
            ]
        )
