# app.py
from flask import Flask
import os
import sys


def create_app():
    # Для Flask 2.2.5 и ниже немного другой синтаксис
    app = Flask(__name__)

    # Простая конфигурация для старых версий
    app.secret_key = os.environ.get('SECRET_KEY', 'dev-key-change-me')
    app.config['SESSION_COOKIE_SECURE'] = False  # Для старых версий
    app.config['PERMANENT_SESSION_LIFETIME'] = 3600

    # Инициализируем базу данных
    from models.database import init_db
    init_db()

    # Регистрируем blueprint'ы
    from routes.main import main_bp
    from routes.admin import admin_bp
    from routes.api import api_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(api_bp, url_prefix='/admin/api')

    return app


app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)