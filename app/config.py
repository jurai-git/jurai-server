import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    VAR_FOLDER = os.path.join(os.getcwd(), 'var/')
