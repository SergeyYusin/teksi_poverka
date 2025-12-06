import pandas as pd
from io import BytesIO
from models.application import Application
import json


def export_to_excel():
    """Экспортирует заявки в Excel"""

    # Получаем все заявки
    orders = Application.get_all()

    if not orders:
        # Создаем пустой DataFrame
        df = pd.DataFrame(
            columns=['ID', 'ФИО', 'Телефон', 'Адрес', 'Комментарий', 'Услуги', 'Сумма', 'Статус', 'Дата создания'])
    else:
        # Преобразуем в DataFrame
        df = pd.DataFrame(orders)

        # Переименовываем колонки
        df = df.rename(columns={
            'id': 'ID',
            'full_name': 'ФИО',
            'phone': 'Телефон',
            'address': 'Адрес',
            'comment': 'Комментарий',
            'selected_works': 'Услуги',
            'total_amount': 'Сумма',
            'status': 'Статус',
            'created_at': 'Дата создания'
        })

        # Обрабатываем JSON с услугами
        def parse_works(works_json):
            if not works_json:
                return ''
            try:
                works = json.loads(works_json)
                return '; '.join([f"{w.get('type', '')}: {w.get('quantity', 0)} {w.get('unit', '')}" for w in works])
            except:
                return works_json

        df['Услуги'] = df['Услуги'].apply(parse_works)

        # Форматируем статусы
        status_map = {
            'new': 'Новая',
            'in_progress': 'В работе',
            'completed': 'Выполнено',
            'cancelled': 'Отменено'
        }
        df['Статус'] = df['Статус'].map(status_map).fillna(df['Статус'])

    # Создаем Excel файл в памяти
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Заявки', index=False)

        # Добавляем лист со статистикой
        stats = Application.get_stats()
        stats_df = pd.DataFrame([{
            'Всего заявок': stats.get('total', 0),
            'Новые': stats.get('new_count', 0),
            'В работе': stats.get('in_progress_count', 0),
            'Выполнено': stats.get('completed_count', 0),
            'Отменено': stats.get('cancelled_count', 0),
            'Общая сумма': stats.get('total_amount', 0)
        }])
        stats_df.to_excel(writer, sheet_name='Статистика', index=False)

    output.seek(0)
    return output