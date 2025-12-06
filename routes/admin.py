from flask import Blueprint, render_template, request, jsonify, send_file
from models.application import Application, ApplicationHistory
from utils.exporters import export_to_excel
import json
from io import BytesIO

admin_bp = Blueprint('admin', __name__)


def check_auth(password):
    """Проверяет авторизацию"""
    return password == 'alukard'


@admin_bp.route('/orders')
def admin_orders():
    """Расширенная админка для управления заявками"""

    password = request.args.get('password', '')
    if not check_auth(password):
        return render_template('admin/login.html')

    # Получаем параметры фильтрации
    filters = {
        'status': request.args.get('status', 'all'),
        'search': request.args.get('search', ''),
        'date_from': request.args.get('date_from', ''),
        'date_to': request.args.get('date_to', '')
    }

    # Получаем заявки с фильтрами
    orders = Application.get_all(filters)

    # Получаем статистику
    stats = Application.get_stats()

    # Получаем опции статусов
    status_options = Application.get_status_options()

    # Обработка данных для шаблона
    for order in orders:
        # Парсим JSON с услугами
        works_data = []
        try:
            works = json.loads(order['selected_works']) if order['selected_works'] else []
            for work in works:
                works_data.append(f"{work.get('type', '')}: {work.get('quantity', 0)} {work.get('unit', '')}")
        except:
            works_data = ["Ошибка загрузки данных"]

        order['works_data'] = works_data
        order['works_html'] = format_works_html(works_data)

        # Определяем текст статуса
        status_text = {
            'new': 'Новая',
            'in_progress': 'В работе',
            'completed': 'Выполнено',
            'cancelled': 'Отменено'
        }.get(order['status'], order['status'])
        order['status_text'] = status_text

    return render_template(
        'admin/orders.html',
        orders=orders,
        stats=stats,
        filters=filters,
        password=password,
        status_options=status_options
    )

def format_works_html(works_data):
    """Форматирует список услуг в HTML"""
    if not works_data:
        return '<div class="works-list"></div>'

    html = '<div class="works-list">'
    for work in works_data[:3]:
        html += f'<div class="work-item">{work}</div>'
    if len(works_data) > 3:
        html += f'<div class="work-item">...и еще {len(works_data) - 3}</div>'
    html += '</div>'

    return html