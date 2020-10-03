import os
from datetime import datetime
from dotenv import load_dotenv

from flask import Flask, render_template
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import flask_admin as admin
from flask_admin.contrib.sqla import ModelView
from flask_migrate import Migrate

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

admin = admin.Admin(app, name='Flasky ADM', template_mode='bootstrap4')

class User(db.Model):
    __tablename__ = 'Users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.Unicode(64), unique=True, index=True)
    email = db.Column(db.Unicode(64))
    created_at = db.Column(db.DateTime, default=datetime.now)
    role_id = db.Column(db.Integer, db.ForeignKey('Roles.id'))

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

admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(Role, db.session))

@app.route('/')
def index():
    return render_template('index.html', current_time=datetime.utcnow())

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/blog')
def blog():
    return render_template('blog.html')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, Role=Role)

if __name__ == '__main__':
    app.run(debug=True)
