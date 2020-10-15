from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from . import db, login_manager

class User(UserMixin, db.Model):
    __tablename__ = 'Users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.Unicode(64), unique=True, index=True)
    email = db.Column(db.Unicode(64))
    password_hash = db.Column(db.String(128))
    created_at = db.Column(db.DateTime, default=datetime.now)
    role_id = db.Column(db.Integer, db.ForeignKey('Roles.id'))
    post_author_id = db.relationship('Post', backref='post_author', lazy='dynamic')
    project_author_id = db.relationship('Project', backref='project_author', lazy='dynamic')

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __unicode__(self):
        return self.username
    
    def __repr__(self):
        return self.username

class Role(db.Model):
    __tablename__ = 'Roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode(64), unique=True)
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __unicode__(self):
        return self.name
    
    def __repr__(self):
        return self.name

class Post(db.Model):
    __tablename__ = 'Posts'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Unicode(64))
    body = db.Column(db.UnicodeText)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    post_author_id = db.Column(db.Integer, db.ForeignKey('Users.id'))
    slug = db.Column(db.String(80), unique=True)

    def __unicode__(self):
        return self.title

class Project(db.Model):
    __tablename__ = 'Projects'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Unicode(64))
    body = db.Column(db.UnicodeText)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    project_author_id = db.Column(db.Integer, db.ForeignKey('Users.id'))
    slug = db.Column(db.String(80), unique=True)

    def __unicode__(self):
        return self.title

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
