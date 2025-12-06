import re


def validate_phone(phone):
    """Валидирует номер телефона"""
    # Убираем все нецифровые символы
    cleaned = re.sub(r'\D', '', phone)

    # Российские номера обычно 11 цифр (с кодом страны)
    if len(cleaned) == 11 and cleaned.startswith('7'):
        return True
    elif len(cleaned) == 10:
        return True

    return False


def validate_email(email):
    """Валидирует email"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_name(name):
    """Валидирует ФИО"""
    # Проверяем, что имя содержит только буквы, пробелы и дефисы
    pattern = r'^[а-яА-ЯёЁa-zA-Z\s\-]{2,100}$'
    return re.match(pattern, name) is not None