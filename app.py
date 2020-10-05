import os
from datetime import datetime
from dotenv import load_dotenv

from flask import Flask, render_template, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_migrate import Migrate
from flask_login import LoginManager, UserMixin, current_user, login_user, logout_user

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

class CustomModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated

class CustomAdminIndexView(AdminIndexView):
    def is_accessible(self):
        return current_user.is_authenticated

    def inaccessible_callback(self, username, **kwargs):
        return redirect(url_for('login'))

admin = Admin(app, name='Flasky ADM', template_mode='bootstrap4', index_view=CustomAdminIndexView())
admin.add_view(CustomModelView(User, db.session))
admin.add_view(CustomModelView(Role, db.session))

@app.route('/')
def index():
    return render_template('index.html', current_time=datetime.utcnow())

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/blog')
def blog():
    return render_template('blog.html')

@app.route('/login')
def login():
    user = User.query.get(1)
    login_user(user)
    return render_template('login.html')

@app.route('/logout')
def logout():
    logout_user()
    return render_template('logout.html')

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
