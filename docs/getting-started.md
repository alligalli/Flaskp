# Getting Started Guide

This guide will help you get started using **Flaskp**. For more information on what this project is, check out the [README](../README.md).

## Creating .env & .env-mysql files

To work properly first you have to provide the correct environment variables, add two files to the root of the project:

`.env`

``` sh
SECRET_KEY="verylongandsecretkey"
FLASK_APP=flaskp.py
FLASK_ENV=development
DATABASE_URL=mysql+pymysql://flaskp_db:flask_db_password@dbserver/flaskp_db
```

`.env-mysql`

``` sh
MYSQL_RANDOM_ROOT_PASSWORD=yes
MYSQL_DATABASE=flaskp_db
MYSQL_USER=flaskp_db
MYSQL_PASSWORD=flask_db_password
```

To use Docker you must change the value of FLASK_ENV in the `.env` file from development to docker, after that you will need to:

``` sh
docker-compose up -d --build
```

## Installing the project

Flaskp is a personal blog and portfolio web application made with [Flask](https://flask.palletsprojects.com). To install the app, use the following instructions:

``` sh
cd flaskp
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
flask run
```

## Creating a user to login

After activating the virtual environment you will need to add a User to the database in order to login:

``` sh
cd flaskp
source venv/bin/activate
flask shell
```

In the interactive python session create a user:

``` python
from app import db
from app.models import User
user = User(username="yourusername", password="yourpassword")
db.session.add(user)
db.session.commit()
```

You can now visit [localhost:5000](http://localhost:5000) to view the website.
