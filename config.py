import os


class Config:
    """
    Set Flask configuration vars from .env file
    Always been using PostgreSQL, but for this project, I will use SQLite and see how it goes.
    I have to say that I am a little bit scared of the result...
    """
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv('SECRET_KEY')
    DB_NAME = os.getenv('DB_NAME') + '.db'
    MD_FOLDER = os.getenv('MD_FOLDER')
    MD_FOLDER_LOCATION = os.getenv('MD_FOLDER_LOCATION')
    REFRESH_KEY = os.getenv('REFRESH_KEY')
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{os.path.join(BASE_DIR, DB_NAME)}'
    DEBUG = os.getenv('DEBUG')
    HOST = os.getenv('HOST')
    PORT = os.getenv('PORT')
    HTTP_ADDR = os.getenv('HTTP_ADDR')
