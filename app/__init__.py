from flask import Flask
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_admin import Admin
from flask_admin.menu import MenuLink
from flask_ckeditor import CKEditor
from flask_wtf.csrf import CSRFProtect
from config import config

bootstrap = Bootstrap()
moment = Moment()
db = SQLAlchemy()
ckeditor = CKEditor()
csrf = CSRFProtect()

login_manager = LoginManager()
login_manager.login_view = 'login'


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    bootstrap.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    ckeditor.init_app(app)
    csrf.init_app(app)
    login_manager.init_app(app)

    if app.config['SSL_REDIRECT']:
        from flask_sslify import SSLify
        sslify = SSLify(app)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .models import User, Role, Post, Project
    from .main.views import CustomAdminIndexView, CustomModelView, PostView, ProjectView
    admin = Admin(app, name='Flaskp ADM', template_mode='bootstrap4', index_view=CustomAdminIndexView())
    admin.add_view(CustomModelView(User, db.session))
    admin.add_view(CustomModelView(Role, db.session))
    admin.add_view(PostView(Post, db.session, name="Post", endpoint="post"))
    admin.add_view(ProjectView(Project, db.session, name="Project", endpoint="project"))
    admin.add_link(MenuLink(name='Home', url='/', category='Live Site'))
    admin.add_link(MenuLink(name='About', url='/about', category='Live Site'))
    admin.add_link(MenuLink(name='Blog', url='/blog', category='Live Site'))
    admin.add_link(MenuLink(name='Projects', url='/projects', category='Live Site'))

    return app