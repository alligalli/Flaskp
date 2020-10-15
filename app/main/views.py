import os
from datetime import datetime
from slugify import slugify

from flask import render_template, redirect, url_for, request, flash, current_app, send_from_directory
from flask_login import current_user, login_user, logout_user, login_required
from flask_admin import AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_ckeditor import CKEditorField, upload_fail, upload_success

from . import main
from .forms import LoginForm
from ..models import User, Post, Project

@main.route('/')
def index():
    return render_template('index.html', current_time=datetime.utcnow())

@main.route('/about')
def about():
    return render_template('about.html')

@main.route('/blog')
def blog():
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(page, per_page=5)
    posts = pagination.items
    return render_template('blog.html', posts=posts, pagination=pagination)

@main.route('/blog/<slug>')
def post(slug):
    post = Post.query.filter_by(slug=slug).first()
    post_edit_url = url_for('post.edit_view', id=post.id)
    if post:
        return render_template("post.html", post=post, post_edit_url=post_edit_url)

@main.route('/projects')
def projects():
    page = request.args.get('page', 1, type=int)
    pagination = Project.query.order_by(Project.timestamp.desc()).paginate(page, per_page=5)
    projects = pagination.items
    return render_template('projects.html', projects=projects, pagination=pagination)

@main.route('/projects/<slug>')
def project(slug):
    project = Project.query.filter_by(slug=slug).first()
    project_edit_url = url_for('project.edit_view', id=project.id)
    if post:
        return render_template("project.html", project=project, project_edit_url=project_edit_url)

@main.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            next = request.args.get('next')
            if next is None or not next.startswith('/'):
                next = url_for('main.index')
            return redirect(next)
        flash('Invalid username or password.')
    return render_template('login.html', form=form)

@main.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.index'))

@main.route('/files/<filename>')
def uploaded_files(filename):
    path = current_app.config['UPLOADED_PATH']
    return send_from_directory(path, filename)

@main.route('/upload', methods=['POST'])
def upload():
    f = request.files.get('upload')
    extension = f.filename.split('.')[-1].lower()
    if extension not in ['jpg', 'gif', 'png', 'jpeg']:
        return upload_fail(message='Image only!')
    f.save(os.path.join(current_app.config['UPLOADED_PATH'], f.filename))
    url = url_for('main.uploaded_files', filename=f.filename)
    return upload_success(url=url)

class PostView(ModelView):
    form_overrides = dict(body=CKEditorField)
    create_template = 'admin/edit_page.html'
    edit_template = 'admin/edit_page.html'
    can_export = True
    column_default_sort = ('timestamp', True)

    def on_model_change(self, form, model, is_created):
        if is_created and not model.slug:
            model.slug = slugify(model.title)

    def is_accessible(self):
        return current_user.is_authenticated

class ProjectView(ModelView):
    form_overrides = dict(body=CKEditorField)
    create_template = 'admin/edit_page.html'
    edit_template = 'admin/edit_page.html'
    can_export = True
    column_default_sort = ('timestamp', True)

    def on_model_change(self, form, model, is_created):
        if is_created and not model.slug:
            model.slug = slugify(model.title)

    def is_accessible(self):
        return current_user.is_authenticated

class CustomModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated

class CustomAdminIndexView(AdminIndexView):
    def is_accessible(self):
        return current_user.is_authenticated

    def inaccessible_callback(self, username, **kwargs):
        return redirect(url_for('main.login'))
