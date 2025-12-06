import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'ваш-секретный-ключ-здесь')
    DATABASE_PATH = os.getenv('DATABASE_PATH', 'data/applications.db')


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False
    DATABASE_PATH = '/var/data/applications.db'