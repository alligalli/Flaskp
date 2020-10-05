import os
from datetime import datetime
from dotenv import load_dotenv
from redis import Redis

from flask import Flask, render_template, request, redirect, url_for, flash
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.widgets import TextArea
from wtforms.validators import DataRequired, Length, Email
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin, AdminIndexView
from flask_admin.contrib import rediscli
from flask_admin.contrib.sqla import ModelView
from flask_migrate import Migrate
from flask_login import LoginManager, UserMixin, current_user, login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash

load_dotenv()

app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['FLASK_APP'] = os.getenv("FLASK_APP")
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = os.getenv("SQLALCHEMY_TRACK_MODIFICATIONS")
app.config['FLASK_ADMIN_SWATCH'] = os.getenv("FLASK_ADMIN_SWATCH")
app.config['FLASK_ADMIN_FLUID_LAYOUT'] = os.getenv("FLASK_ADMIN_FLUID_LAYOUT")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'flasky.sqlite')

bootstrap = Bootstrap(app)
moment = Moment(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(UserMixin, db.Model):
    __tablename__ = 'Users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.Unicode(64), unique=True, index=True)
    email = db.Column(db.Unicode(64))
    password_hash = db.Column(db.String(128))
    created_at = db.Column(db.DateTime, default=datetime.now)
    role_id = db.Column(db.Integer, db.ForeignKey('Roles.id'))
    author_id = db.relationship('Post', backref='author', lazy='dynamic')

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
    author_id = db.Column(db.Integer, db.ForeignKey('Users.id'))

    def __unicode__(self):
        return self.title

class CKTextAreaWidget(TextArea):
    def __call__(self, field, **kwargs):
        if kwargs.get('class'):
            kwargs['class'] += ' ckeditor'
        else:
            kwargs.setdefault('class', 'ckeditor')
        return super(CKTextAreaWidget, self).__call__(field, **kwargs)

class CKTextAreaField(TextAreaField):
    widget = CKTextAreaWidget()

class PostView(ModelView):
    form_overrides = {
        'body': CKTextAreaField
    }

    create_template = 'create_page.html'
    edit_template = 'edit_page.html'

    def is_accessible(self):
        return current_user.is_authenticated

class CustomModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated

class CustomAdminIndexView(AdminIndexView):
    def is_accessible(self):
        return current_user.is_authenticated

    def inaccessible_callback(self, username, **kwargs):
        return redirect(url_for('login'))

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(1, 64)])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Login')

admin = Admin(app, name='Flasky ADM', template_mode='bootstrap4', index_view=CustomAdminIndexView())
admin.add_view(CustomModelView(User, db.session))
admin.add_view(CustomModelView(Role, db.session))
admin.add_view(PostView(Post, db.session))
admin.add_view(rediscli.RedisCli(Redis()))


@app.route('/')
def index():
    return render_template('index.html', current_time=datetime.utcnow())

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/blog')
def blog():
    posts = Post.query.order_by(Post.timestamp.desc()).all()
    return render_template('blog.html', posts=posts)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            next = request.args.get('next')
            if next is None or not next.startswith('/'):
                next = url_for('index')
            return redirect(next)
        flash('Invalid username or password.')
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('index'))

@app.errorhandler(403)
def forbidden(e):
    return render_template('403.html'), 403

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, Role=Role)

@app.cli.command("test")
def test():
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)

if __name__ == '__main__':
    app.run(debug=True)
