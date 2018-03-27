import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'THISiSsUp3rSEvr3tKEY'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(
        os.path.dirname(__file__), './data-dev.sqlite3')
    SQLALCHEMY_TRACK_MODIFICATIONS = False



