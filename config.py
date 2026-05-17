from os import path, environ
from flask import Flask
from dotenv import load_dotenv

load_dotenv()

BASE_DIR : str = path.abspath(path.dirname('__file__'))

class Config:

    SECRET_KEY : str = environ.get('SECRET_KEY')
    ADM_EMAIL : str = environ.get('ADM_EMAIL')
    APP_TITLE : str = environ.get('APP_TITLE')
    SQLALCHEMY_DATABASE_URI : str = 'sqlite:///' + path.join(BASE_DIR, environ.get('DATABASE_PATH'))
    SQLALCHEMY_TRACK_MODIFICATIONS : bool = environ.get('SQLALCHEMT_TRACK_MODIFICATIONS')

    def init_app (self, app : Flask) -> None: app.config.from_object(self)
