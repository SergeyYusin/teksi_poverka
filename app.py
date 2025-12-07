from flask import Flask
from routes.main import main_bp
from routes.admin import admin_bp
from routes.api import api_bp
from models.database import init_db
import os
import sys


def create_app():
    app = Flask(__name__)

    # Конфигурация для продакшена
    app.config.update(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production'),
        SESSION_COOKIE_SECURE=True,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE='Lax',
        PERMANENT_SESSION_LIFETIME=3600,
        MAX_CONTENT_LENGTH=16 * 1024 * 1024,  # 16MB max upload
    )

    # Инициализация базы данных
    try:
        init_db()
        print("✅ База данных инициализирована")
    except Exception as e:
        print(f"⚠️ Ошибка инициализации БД: {e}")
        # Продолжаем работу без БД для отладки

    # Регистрация Blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(api_bp, url_prefix='/admin/api')

    # Обработчики ошибок
    @app.errorhandler(404)
    def not_found_error(error):
        return "Страница не найдена", 404

    @app.errorhandler(500)
    def internal_error(error):
        return "Внутренняя ошибка сервера", 500

    return app


# Создаем приложение для импорта
app = create_app()

if __name__ == '__main__':
    # Определяем порт из переменных окружения или используем 5000
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '0.0.0.0')

    print("=" * 50)
    print(f"🚀 Flask Site v1.0")
    print(f"🐍 Python {sys.version}")
    print(f"🌐 Запуск на {host}:{port}")
    print(f"🔧 Режим: {os.environ.get('FLASK_ENV', 'production')}")
    print("=" * 50)

    # Запускаем приложение
    app.run(
        host=host,
        port=port,
        debug=os.environ.get('FLASK_DEBUG', 'False').lower() == 'true',
        threaded=True
    )