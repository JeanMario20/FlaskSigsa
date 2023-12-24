import os 
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRE_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-know'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'app.db')