# utils/exporters_light.py
import csv
from io import StringIO, BytesIO
from datetime import datetime
import json


def export_to_csv():
    """Экспортирует заявки в CSV (без pandas)"""
    from models.application import Application

    # Получаем все заявки
    orders = Application.get_all()

    if not orders:
        # Создаем пустой CSV
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(['ID', 'ФИО', 'Телефон', 'Адрес', 'Сумма', 'Статус', 'Дата'])
        return BytesIO(output.getvalue().encode('utf-8'))

    # Создаем CSV
    output = StringIO()
    writer = csv.writer(output)

    # Заголовки
    writer.writerow(['ID', 'ФИО', 'Телефон', 'Адрес', 'Услуги', 'Сумма', 'Статус', 'Дата создания'])

    # Данные
    for order in orders:
        # Обрабатываем услуги
        works_text = ''
        try:
            works = json.loads(order['selected_works']) if order['selected_works'] else []
            works_text = '; '.join([f"{w.get('type', '')}: {w.get('quantity', 0)} {w.get('unit', '')}" for w in works])
        except:
            works_text = order.get('selected_works', '')

        writer.writerow([
            order['id'],
            order['full_name'],
            order['phone'],
            order['address'],
            works_text,
            order['total_amount'],
            order['status'],
            order['created_at']
        ])

    return BytesIO(output.getvalue().encode('utf-8'))