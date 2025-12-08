# utils/exporters.py
import csv
from io import BytesIO, StringIO
from datetime import datetime
import json
from models.application import Application


def export_to_csv():
    """Экспортирует заявки в CSV с правильной кодировкой для Excel"""

    # Получаем все заявки
    orders = Application.get_all()

    # Создаем CSV в памяти
    output = StringIO()

    # Добавляем BOM для Excel (UTF-8 с BOM)
    output.write('\ufeff')

    writer = csv.writer(output, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)

    # Заголовки с русскими символами
    writer.writerow(['ID', 'ФИО', 'Телефон', 'Адрес', 'Услуги', 'Сумма', 'Статус', 'Дата создания', 'Комментарий'])

    # Если нет заявок
    if not orders:
        writer.writerow(['Нет данных', '', '', '', '', '', '', '', ''])
    else:
        # Данные
        for order in orders:
            # Обрабатываем услуги
            works_text = ''
            try:
                works = json.loads(order['selected_works']) if order['selected_works'] else []
                work_items = []
                for w in works:
                    work_type = w.get('type', '').replace(';', ',')
                    quantity = w.get('quantity', 0)
                    unit = w.get('unit', '').replace(';', ',')
                    work_items.append(f"{work_type}: {quantity} {unit}")
                works_text = ' | '.join(work_items)
            except Exception as e:
                works_text = str(order.get('selected_works', ''))

            # Форматируем статус
            status_map = {
                'new': 'Новая',
                'in_progress': 'В работе',
                'completed': 'Выполнено',
                'cancelled': 'Отменено'
            }
            status_text = status_map.get(order.get('status', ''), order.get('status', ''))

            # Получаем значения
            full_name = order.get('full_name', '')
            phone = order.get('phone', '')
            address = order.get('address', '')
            total_amount = order.get('total_amount', 0)
            created_at = order.get('created_at', '')
            comment = order.get('comment', '')

            # Экранируем строковые значения
            def escape(value):
                if value is None:
                    return ''
                value = str(value)
                # Если значение содержит разделитель или кавычки
                if ';' in value or '"' in value or '\n' in value:
                    value = value.replace('"', '""')
                    return f'"{value}"'
                return value

            # Записываем строку
            writer.writerow([
                order.get('id', ''),
                escape(full_name),
                escape(phone),
                escape(address),
                escape(works_text),
                total_amount,
                escape(status_text),
                escape(created_at),
                escape(comment)
            ])

    # Конвертируем в байты с UTF-8 BOM кодировкой
    content = output.getvalue().encode('utf-8-sig')

    # Создаем BytesIO объект
    bytes_io = BytesIO()
    bytes_io.write(content)
    bytes_io.seek(0)

    return bytes_io


# Алиас для обратной совместимости
def export_to_excel():
    """Алиас для export_to_csv (для обратной совместимости)"""
    return export_to_csv()