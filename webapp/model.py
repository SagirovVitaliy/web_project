from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Email(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(), unique=True)
    
    def __repr__(self):
        return'Email {}'.format(self.email)


class Phone(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    phone = db.Column(db.Integer, unique=True)
    
    def __repr__(self):
        return'Phone {}'.format(self.phone)


class UserRole(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.String(), nullable=False)
    
    def __repr__(self):
        return'Role {}'.format(self.role)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    password = db.Column(db.String(128))
    public_bio = db.Column(db.String())

    role = db.Column(
        db.Integer(),
        db.ForeignKey('userrole.id', ondelete='CASCADE') 
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
        db.ForeignKey('tag.id', ondelete='CASCADE')
        )

    def __repr__(self):
        return'<User {} {}>'.format(self.id, self.username)


class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tag = db.Column(db.String(20))
    
    def __repr__(self):
        return'Tag {}'.format(self.tag)


class TaskStatus(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(), nullable=False)

    def __repr__(self):
        return'Status {} {}'.format(self.status, self.id)


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task_name = db.Column(db.String())
    description = db.Column(db.String(), nullable=False)
    price = db.Column(db.Integer())
    status = db.Column(
        db.Integer(),
        db.ForeignKey('TaskStatus.id', ondelete='CASCADE')
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
        return '{} {} {} {}'.format(self.id, self.task_name, self.status, self.price)
