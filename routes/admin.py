from flask import Blueprint, render_template, request, jsonify, send_file, make_response
from models.application import Application, ApplicationHistory
import json
from datetime import datetime
from io import BytesIO
import os
from dotenv import load_dotenv

load_dotenv()
admin_bp = Blueprint('admin', __name__)


def check_auth(password):
    """Проверяет авторизацию"""
    return password == os.getenv('ADMIN_PASSWORD', 'пароль')


# routes/admin.py
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

    # Создаем опции статусов для выпадающего меню
    status_options = [
        {'value': 'new', 'label': 'Новая', 'color': '#3498db'},
        {'value': 'in_progress', 'label': 'В работе', 'color': '#f39c12'},
        {'value': 'completed', 'label': 'Выполнено', 'color': '#27ae60'},
        {'value': 'cancelled', 'label': 'Отменено', 'color': '#e74c3c'}
    ]

    return render_template(
        'admin/orders.html',
        orders=orders,
        stats=stats,
        filters=filters,
        password=password,
        status_options=status_options  # Добавляем переменную
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


# routes/admin.py - обновите функцию export_orders_simple
@admin_bp.route('/export2')
def export_orders_simple():
    """Простой экспорт в CSV"""
    password = request.args.get('password', '')
    if not check_auth(password):
        return jsonify({'error': 'Unauthorized'}), 403

    try:
        # Используем ту же функцию, что и в API
        from utils.exporters import export_to_csv
        output = export_to_csv()

        filename = f"applications_{datetime.now().strftime('%Y-%m-%d_%H-%M')}.csv"

        # Создаем ответ
        response = make_response(output.getvalue() if hasattr(output, 'getvalue') else output)
        response.headers['Content-Type'] = 'text/csv; charset=utf-8'
        response.headers['Content-Disposition'] = f'attachment; filename="{filename}"'

        return response

    except Exception as e:
        return f"Ошибка экспорта: {e}", 500


# Также обновите старую функцию export_orders
@admin_bp.route('/export')
def export_orders():
    """Экспорт заявок (совместимая версия)"""
    password = request.args.get('password', '')
    if not check_auth(password):
        return jsonify({'error': 'Unauthorized'}), 403

    try:
        from utils.exporters import export_to_csv
        output = export_to_csv()

        filename = f"applications_{datetime.now().strftime('%Y-%m-%d_%H-%M')}.csv"

        # Альтернатива 1: Используем make_response
        response = make_response(output.getvalue() if hasattr(output, 'getvalue') else output)
        response.headers.set('Content-Type', 'text/csv; charset=utf-8')
        response.headers.set('Content-Disposition', 'attachment', filename=filename)
        return response

    except Exception as e:
        return jsonify({'error': str(e)}), 500