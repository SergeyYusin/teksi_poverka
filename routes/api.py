from flask import Blueprint, request, jsonify, send_file
from models.application import Application, ApplicationHistory
from utils.exporters import export_to_excel
from datetime import datetime

api_bp = Blueprint('api', __name__)


def check_auth():
    """Проверяет авторизацию"""
    password = request.args.get('password') or (request.json.get('password') if request.json else None)
    return password == 'alukard'


@api_bp.route('/order/<int:order_id>')
def get_order_details(order_id):
    if not check_auth():
        return jsonify({'error': 'Unauthorized'}), 403

    order = Application.get_by_id(order_id)
    if order:
        return jsonify(order)
    else:
        return jsonify({'error': 'Заявка не найдена'}), 404


@api_bp.route('/history/<int:order_id>')
def get_order_history(order_id):
    if not check_auth():
        return jsonify({'error': 'Unauthorized'}), 403

    history = ApplicationHistory.get_by_application_id(order_id)
    return jsonify(history)


@api_bp.route('/update-status', methods=['POST'])
def update_order_status():
    if not check_auth():
        return jsonify({'error': 'Unauthorized'}), 403

    data = request.get_json()
    order_id = data.get('order_id')
    new_status = data.get('status')

    if not order_id or not new_status:
        return jsonify({'error': 'Не указаны данные'}), 400

    old_status = Application.update_status(order_id, new_status)

    # Записываем в историю
    status_names = {
        'new': 'Новая',
        'in_progress': 'В работе',
        'completed': 'Выполнено',
        'cancelled': 'Отменено'
    }

    details = f"Статус изменен: {status_names.get(old_status, old_status)} → {status_names.get(new_status, new_status)}"
    ApplicationHistory.log(order_id, 'status_changed', details)

    return jsonify({'success': True})


@api_bp.route('/delete', methods=['POST'])
def delete_order():
    if not check_auth():
        return jsonify({'error': 'Unauthorized'}), 403

    data = request.get_json()
    order_id = data.get('order_id')

    if not order_id:
        return jsonify({'error': 'Не указан ID заявки'}), 400

    # Получаем данные перед удалением
    order = Application.get_by_id(order_id)

    if order:
        # Логируем удаление
        ApplicationHistory.log(order_id, 'deleted', f"Заявка удалена. Данные: {order}")

    # Удаляем заявку
    Application.delete(order_id)

    return jsonify({'success': True})


# В routes/api.py замените export_orders функцию:
@api_bp.route('/export')
def export_orders():
    if not check_auth():
        return jsonify({'error': 'Unauthorized'}), 403

    try:
        # Попробуем использовать pandas
        try:
            from utils.exporters import export_to_excel
            output = export_to_excel()
            filename = f"заявки_{datetime.now().strftime('%Y-%m-%d_%H-%M')}.xlsx"
            mimetype = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        except ImportError:
            # Если pandas не установлен, используем CSV
            from utils.exporters_light import export_to_csv
            output = export_to_csv()
            filename = f"заявки_{datetime.now().strftime('%Y-%m-%d_%H-%M')}.csv"
            mimetype = 'text/csv'

        return send_file(
            output,
            mimetype=mimetype,
            as_attachment=True,
            download_name=filename
        )

    except Exception as e:
        return jsonify({'error': str(e)}), 500