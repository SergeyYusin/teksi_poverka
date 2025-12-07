#!/usr/bin/env python3
"""
Скрипт для настройки проекта на хостинге
"""

import os
import shutil


def setup_hosting():
    print("🏗️ Настройка проекта для хостинга...")
    print("=" * 50)

    # Создаем необходимые папки
    folders = [
        'static/css',
        'static/js',
        'static/images',
        'templates/admin',
        'models',
        'routes',
        'utils',
        'data',
        'instance',
        'logs'
    ]

    for folder in folders:
        os.makedirs(folder, exist_ok=True)
        print(f"📁 Создана папка: {folder}")

    # Создаем пустые файлы изображений
    image_files = ['service1.jpg', 'service2.jpg', 'service3.jpg']
    for image in image_files:
        image_path = f'static/images/{image}'
        if not os.path.exists(image_path):
            with open(image_path, 'wb') as f:
                # Создаем минимальный корректный JPEG
                f.write(
                    b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.\' ",#\x1c\x1c(7),01444\x1f\'9=82<.342\xff\xc0\x00\x0b\x08\x00\x01\x00\x01\x01\x01\x11\x00\xff\xc4\x00\x14\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x03\xff\xc4\x00\x14\x10\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xda\x00\x08\x01\x01\x00\x00?8\x00\xff\xd9')
            print(f"🖼️ Создано изображение: {image_path}")

    # Создаем файл .env если его нет
    env_example = '.env.example'
    env_file = '.env'

    if not os.path.exists(env_file) and os.path.exists(env_example):
        shutil.copy(env_example, env_file)
        print(f"📄 Создан файл: {env_file} (на основе {env_example})")
        print("⚠️ Не забудьте изменить SECRET_KEY в .env файле!")

    # Создаем базу данных
    print("🗄️ Инициализация базы данных...")
    try:
        from models.database import init_db
        init_db()
        print("✅ База данных инициализирована")
    except Exception as e:
        print(f"⚠️ Не удалось инициализировать БД: {e}")
        print("📋 Создайте БД вручную после запуска приложения")

    # Проверяем структуру проекта
    print("\n📁 Проверка структуры проекта...")
    required_files = [
        'app.py',
        'requirements.txt',
        'static/css/style.css',
        'static/css/admin.css',
        'static/js/admin.js',
        'templates/base.html',
        'templates/index.html',
        'templates/form.html',
        'templates/prices.html',
        'templates/admin/login.html',
        'templates/admin/orders.html',
        'models/__init__.py',
        'models/database.py',
        'models/application.py',
        'routes/__init__.py',
        'routes/main.py',
        'routes/admin.py',
        'routes/api.py',
        'utils/__init__.py',
        'utils/exporters.py'
    ]

    missing_files = []
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            print(f"❌ {file} - ОТСУТСТВУЕТ")
            missing_files.append(file)

    if missing_files:
        print(f"\n⚠️ Отсутствует {len(missing_files)} файлов")
    else:
        print("\n✅ Все файлы на месте")

    print("=" * 50)
    print("🎉 Настройка завершена!")
    print("📋 Следующие шаги:")
    print("1. Установите зависимости: pip install -r requirements.txt")
    print("2. Настройте .env файл (особенно SECRET_KEY)")
    print("3. Запустите приложение: python app.py")
    print("4. Проверьте доступность по адресу: http://localhost:5000")


if __name__ == "__main__":
    setup_hosting()