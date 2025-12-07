#!/usr/bin/env python3
"""
WSGI точка входа для uWSGI
"""

import sys
import os

# Добавляем путь к проекту
project_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_path)

# Устанавливаем переменные окружения
os.environ.setdefault('FLASK_ENV', 'production')

# Импортируем и создаем приложение
from app import create_app

# Создаем приложение для uWSGI
application = create_app()

if __name__ == '__main__':
    # Для локального запуска
    application.run(host='0.0.0.0', port=5000)