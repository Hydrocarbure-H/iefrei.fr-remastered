import os

class Config:
    """
    Set Flask configuration vars from .env file
    Always been using PostgreSQL, but for this project, I will use SQLite and see how it goes.
    I have to say that I am a little bit scared of the result...
    """
    SECRET_KEY = os.getenv('SECRET_KEY')
    DB_NAME = os.getenv('DB_NAME')
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{DB_NAME}.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
