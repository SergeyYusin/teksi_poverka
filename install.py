#!/usr/bin/env python3
"""
Скрипт для установки зависимостей проекта
"""

import subprocess
import sys


def install_requirements():
    print("🔧 Установка зависимостей проекта...")
    print("=" * 50)

    # Обновляем pip
    print("📦 Обновление pip...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])

    # Устанавливаем зависимости
    print("📦 Установка зависимостей из requirements.txt...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

    # Проверяем установку
    print("✅ Проверка установленных пакетов...")
    result = subprocess.run([sys.executable, "-m", "pip", "list"], capture_output=True, text=True)
    print(result.stdout)

    print("=" * 50)
    print("🎉 Все зависимости успешно установлены!")
    print("🚀 Запустите приложение командой: python app.py")


if __name__ == "__main__":
    try:
        install_requirements()
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка установки: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {e}")
        sys.exit(1)