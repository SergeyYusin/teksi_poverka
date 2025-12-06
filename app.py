from flask import Flask
from routes.main import main_bp
from routes.admin import admin_bp
from routes.api import api_bp
from models.database import init_db
import os


def create_app():
    app = Flask(__name__)
    app.secret_key = os.environ.get('SECRET_KEY', 'ваш-секретный-ключ-здесь')

    # Инициализация базы данных
    init_db()

    # Регистрация Blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(api_bp, url_prefix='/admin/api')

    return app


if __name__ == '__main__':
    app = create_app()
    print("=" * 50)
    print("🚀 Flask Site - Запуск приложения")
    print("=" * 50)
    print("🔧 Проверка базы данных...")
    print("✅ База данных готова")
    print(f"🌐 Сайт: http://localhost:5000")
    print(f"📋 Форма: http://localhost:5000/form")
    print(f"💰 Цены: http://localhost:5000/prices")
    print(f"👁 Админка: http://localhost:5000/admin/orders?password=alukard")
    print("=" * 50)
    app.run(debug=True, host='0.0.0.0', port=5000)