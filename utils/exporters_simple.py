# utils/exporters_simple.py
import csv
from io import BytesIO, StringIO
from datetime import datetime
import json
from models.application import Application


def export_to_simple_csv():
    """Упрощенный экспорт в CSV"""

    orders = Application.get_all()

    # Создаем CSV
    output = StringIO()

    # Пишем BOM для UTF-8
    output.write('\ufeff')

    writer = csv.writer(output, delimiter=';')

    # Заголовки
    writer.writerow(['ID', 'ФИО', 'Телефон', 'Адрес', 'Услуги', 'Сумма', 'Статус', 'Дата', 'Комментарий'])

    if orders:
        for order in orders:
            # Обрабатываем услуги
            works_text = ''
            try:
                works = json.loads(order.get('selected_works', '[]'))
                works_list = []
                for w in works:
                    works_list.append(f"{w.get('type', '')} {w.get('quantity', 0)} {w.get('unit', '')}")
                works_text = ', '.join(works_list)
            except:
                works_text = ''

            # Статус
            status_text = {
                'new': 'Новая',
                'in_progress': 'В работе',
                'completed': 'Выполнено',
                'cancelled': 'Отменено'
            }.get(order.get('status', ''), '')

            writer.writerow([
                order.get('id', ''),
                order.get('full_name', ''),
                order.get('phone', ''),
                order.get('address', ''),
                works_text,
                order.get('total_amount', 0),
                status_text,
                order.get('created_at', ''),
                order.get('comment', '')[:100] if order.get('comment') else ''
            ])

    # Конвертируем в байты
    content = output.getvalue().encode('utf-8-sig')

    bytes_io = BytesIO()
    bytes_io.write(content)
    bytes_io.seek(0)

    return bytes_io