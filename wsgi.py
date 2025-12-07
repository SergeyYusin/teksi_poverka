import sys
import os

# Добавляем путь к проекту
sys.path.insert(0, os.path.dirname(__file__))

# Импортируем Flask приложение
from app import create_app

application = create_app()

if __name__ == "__main__":
    application.run()