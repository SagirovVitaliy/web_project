from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

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

CUSTOMER = 1
FREELANCER = 2

CREATED = 1
PUBLISHED = 2
FREELANCERS_DETECTED = 3
IN_WORK = 4
STOPPED = 5
IN_REVIEW = 6
DONE = 7


def convert_task_status_id_to_label(task_status_id):
    return {
        CREATED: 'Создана',
        PUBLISHED: 'Опубликована',
        FREELANCERS_DETECTED: 'Заинтересовала Фрилансеров',
        IN_WORK: 'В работе',
        STOPPED: 'Остановлена',
        IN_REVIEW: 'В ревью',
        DONE: 'Успешно завершена',
    }.get(task_status_id, '')


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
    role = db.Column(db.String())
    
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


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(64), index=True, unique=True)
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
        'Task',
        secondary=freelancers_who_responded,
        backref=db.backref('freelancers_who_responded', lazy='dynamic')
        )

    def get_public_label(self):
        '''Вернуть строку в которой - то как представлять пользователя.
        
        Для других посетителей сайта.
        '''
        return f'{self.user_name}'

    def set_password(self, password):
        self.password = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password, password)

    @property
    def is_customer(self):
        return self.role == CUSTOMER

    @property
    def is_freelancer(self):
        return self.role == FREELANCER

    def __repr__(self):
        return prettify(
            class_label='User',
            prop_line_list=[
                f'id:{self.id}',
                f'user_name:{self.user_name}',
                f'role:{self.role}',
                f'email:{self.email}',
                f'phone:{self.phone}',
                f'tag:{self.tag}',
                f'password:{self.password}',
                f'public_bio:{self.public_bio}',
            ]
        )

    def generate_level_0_debug_dictionary(self):
        '''Собрать самые низкоуровневые свойства.'''
        return {
            '< class >': '< ' + self.__tablename__ + ' >',
            'id': self.id,
            'user_name': self.user_name,
            'role': self.role,
            'email': self.email,
            'phone': self.phone,
            'tag': self.tag,
            'password': self.password,
            'public_bio': self.public_bio,
        }

    def generate_level_1_debug_dictionary(self):
        '''Собрать связи о2о, о2м, которые задаются вручную.'''
        packet = self.generate_level_0_debug_dictionary()
        if packet['role'] != None:
            packet['role'] = UserRole.query.filter(
                UserRole.id == packet['role']
            ).first()
        if packet['email'] != None:
            packet['email'] = Email.query.filter(
                Email.id == packet['email']
            ).first()
        if packet['phone'] != None:
            packet['phone'] = Phone.query.filter(
                Phone.id == packet['phone']
            ).first()
        if packet['tag'] != None:
            packet['tag'] = Tag.query.filter(
                Tag.id == packet['tag']
            ).first()
        return packet

    def generate_level_2_debug_dictionary(self):
        '''Собрать связи которые задаются через SQLAlchemy.relationship.
        
        Внимание! Внутри этой функции запрещено у элементов других классов,
        которые прикреплены к этом объекту, запускать их имплементацию метода
        generate_level_2_debug_dictionary - это нужно чтобы гарантировать
        отсутствие петли взаимных запусков.
        '''
        packet = self.generate_level_1_debug_dictionary()
        packet['responded_to_tasks'] = self.responded_to_tasks
        return packet


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

    def generate_level_0_debug_dictionary(self):
        '''Собрать самые низкоуровневые свойства.'''
        return {
            '< class >': '< ' + self.__tablename__ + ' >',
            'id': self.id,
            'task_name': self.task_name,
            'description': self.description,
            'price': self.price,
            'deadline': self.deadline,
            'status': self.status,
            'customer': self.customer,
            'freelancer': self.freelancer,
            'tag': self.tag,
        }

    def generate_level_1_debug_dictionary(self):
        '''Собрать связи о2о, о2м, которые задаются вручную.'''
        packet = self.generate_level_0_debug_dictionary()
        if packet['status'] != None:
            packet['status'] = TaskStatus.query.filter(
                TaskStatus.id == packet['status']
            ).first()
        if packet['customer'] != None:
            packet['customer'] = User.query.filter(
                User.id == packet['customer']
            ).first()
        if packet['freelancer'] != None:
            packet['freelancer'] = User.query.filter(
                User.id == packet['freelancer']
            ).first()
        return packet

    def generate_level_2_debug_dictionary(self):
        '''Собрать связи которые задаются через SQLAlchemy.relationship.
        
        Внимание! Внутри этой функции запрещено у элементов других классов,
        которые прикреплены к этом объекту, запускать их имплементацию метода
        generate_level_2_debug_dictionary - это нужно чтобы гарантировать
        отсутствие петли взаимных запусков.
        '''
        packet = self.generate_level_1_debug_dictionary()
        if packet['customer'] != None:
            packet['customer'] = (
                packet['customer'].generate_level_1_debug_dictionary()
            )
        if packet['freelancer'] != None:
            packet['freelancer'] = (
                packet['freelancer'].generate_level_1_debug_dictionary()
            )
        packet['freelancers_who_responded'] = self.freelancers_who_responded.all()

        freelancers = []
        for user in packet['freelancers_who_responded']:
            freelancers.append(user.generate_level_1_debug_dictionary())
        packet['freelancers_who_responded'] = freelancers

        return packet


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