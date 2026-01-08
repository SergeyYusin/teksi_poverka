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
    if any(filters.values()):  # Если есть какие-то фильтры
        stats = Application.get_stats_with_filters(filters)
    else:
        stats = Application.get_stats()  # Без фильтров - общая статистика

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


# ========== API ЭНДПОИНТЫ ==========

@admin_bp.route('/api/order/<int:order_id>')
def get_order_api(order_id):
    """API: Получает детали заявки"""
    password = request.args.get('password', '')
    if not check_auth(password):
        return jsonify({'error': 'Unauthorized'}), 403

    order = Application.get_by_id(order_id)
    if not order:
        return jsonify({'error': 'Order not found'}), 404

    # Форматируем статус
    status_map = {
        'new': 'Новая',
        'in_progress': 'В работе',
        'completed': 'Выполнено',
        'cancelled': 'Отменено'
    }
    order['status_text'] = status_map.get(order['status'], order['status'])

    return jsonify(order)


@admin_bp.route('/api/history/<int:order_id>')
def get_order_history_api(order_id):
    """API: Получает историю изменений заявки"""
    password = request.args.get('password', '')
    if not check_auth(password):
        return jsonify({'error': 'Unauthorized'}), 403

    history = ApplicationHistory.get_by_application_id(order_id)
    return jsonify(history)


@admin_bp.route('/api/update-status', methods=['POST'])
def update_order_status_api():
    """API: Обновляет статус заявки"""
    try:
        data = request.get_json()
        password = data.get('password', '')

        if not check_auth(password):
            return jsonify({'error': 'Unauthorized'}), 403

        order_id = data.get('order_id')
        new_status = data.get('status')

        if not order_id or not new_status:
            return jsonify({'error': 'Missing parameters'}), 400

        # Получаем старый статус
        old_status = Application.update_status(order_id, new_status)

        # Логируем изменение
        status_map = {
            'new': 'Новая',
            'in_progress': 'В работе',
            'completed': 'Выполнено',
            'cancelled': 'Отменено'
        }

        details = f"Статус изменен: {status_map.get(old_status, old_status)} → {status_map.get(new_status, new_status)}"
        ApplicationHistory.log(order_id, 'status_changed', details)

        return jsonify({'success': True, 'new_status': new_status})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/api/delete', methods=['POST'])
def delete_order_api():
    """API: Удаляет заявку"""
    try:
        data = request.get_json()
        password = data.get('password', '')

        if not check_auth(password):
            return jsonify({'error': 'Unauthorized'}), 403

        order_id = data.get('order_id')

        if not order_id:
            return jsonify({'error': 'Missing order_id'}), 400

        # Получаем данные перед удалением
        order = Application.get_by_id(order_id)
        if not order:
            return jsonify({'error': 'Order not found'}), 404

        # Логируем удаление
        ApplicationHistory.log(order_id, 'deleted', f'Заявка удалена: {order["full_name"]}, {order["phone"]}')

        # Удаляем
        deleted_order = Application.delete(order_id)

        return jsonify({
            'success': True,
            'message': f'Заявка #{order_id} удалена',
            'order': deleted_order
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ========== ЭКСПОРТ ==========

@admin_bp.route('/export2')
def export_orders_simple():
    """Экспорт в CSV с учетом фильтров"""
    password = request.args.get('password', '')
    if not check_auth(password):
        return jsonify({'error': 'Unauthorized'}), 403

    try:
        # Получаем параметры фильтрации из запроса
        filters = {
            'status': request.args.get('status', 'all'),
            'search': request.args.get('search', ''),
            'date_from': request.args.get('date_from', ''),
            'date_to': request.args.get('date_to', '')
        }

        # Используем функцию экспорта
        from utils.exporters import export_to_csv
        output = export_to_csv(filters)

        filename = f"applications_{datetime.now().strftime('%Y-%m-%d_%H-%M')}.csv"

        # Создаем ответ
        response = make_response(output.getvalue() if hasattr(output, 'getvalue') else output)
        response.headers['Content-Type'] = 'text/csv; charset=utf-8'
        response.headers['Content-Disposition'] = f'attachment; filename="{filename}"'

        return response

    except Exception as e:
        return f"Ошибка экспорта: {e}", 500


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

        response = make_response(output.getvalue() if hasattr(output, 'getvalue') else output)
        response.headers.set('Content-Type', 'text/csv; charset=utf-8')
        response.headers.set('Content-Disposition', 'attachment', filename=filename)
        return response

    except Exception as e:
        return jsonify({'error': str(e)}), 500