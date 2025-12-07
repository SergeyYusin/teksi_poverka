#!/usr/bin/env python3
"""
Проверка установленных зависимостей
"""

import pkg_resources
import sys

REQUIRED = {
    'Flask': '2.3.3',
    'pandas': '2.1.4',
    'openpyxl': '3.1.2',
    'python-dotenv': '1.0.0',
}

OPTIONAL = {
    'Werkzeug': '2.3.7',
    'Jinja2': '3.1.2',
    'itsdangerous': '2.1.2',
}


def check_dependencies():
    print("🔍 Проверка зависимостей...")
    print("=" * 50)

    installed = {pkg.key: pkg.version for pkg in pkg_resources.working_set}

    errors = []
    warnings = []

    # Проверяем обязательные зависимости
    print("\n📦 ОБЯЗАТЕЛЬНЫЕ ЗАВИСИМОСТИ:")
    for package, required_version in REQUIRED.items():
        if package.lower() in installed:
            installed_version = installed[package.lower()]
            status = "✅" if installed_version.startswith(required_version.split('.')[0]) else "⚠️"
            print(f"{status} {package}=={installed_version} (требуется: {required_version})")
            if not installed_version.startswith(required_version.split('.')[0]):
                warnings.append(f"{package}: установлена версия {installed_version}, рекомендуется {required_version}")
        else:
            print(f"❌ {package}=={required_version} - НЕ УСТАНОВЛЕН")
            errors.append(f"{package} не установлен")

    # Проверяем опциональные зависимости
    print("\n📦 ОПЦИОНАЛЬНЫЕ ЗАВИСИМОСТИ:")
    for package, recommended_version in OPTIONAL.items():
        if package.lower() in installed:
            installed_version = installed[package.lower()]
            print(f"✅ {package}=={installed_version}")
        else:
            print(f"⚠️ {package} - не установлен (рекомендуется)")

    # Вывод результатов
    print("\n" + "=" * 50)
    print("📊 РЕЗУЛЬТАТЫ:")

    if errors:
        print(f"❌ Ошибки: {len(errors)}")
        for error in errors:
            print(f"   • {error}")
        print("\n💡 Решение: установите отсутствующие пакеты:")
        print("   pip install -r requirements.txt")
    else:
        print("✅ Все обязательные зависимости установлены")

    if warnings:
        print(f"\n⚠️ Предупреждения: {len(warnings)}")
        for warning in warnings:
            print(f"   • {warning}")

    print("\n🚀 Приложение готово к запуску!" if not errors else "\n❌ Требуется установка зависимостей")


if __name__ == "__main__":
    check_dependencies()