from .database import get_db_connection
import json
from datetime import datetime


class Application:
    @staticmethod
    def create(data):
        """Создает новую заявку"""
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO applications (full_name, address, phone, comment, selected_works, total_amount, status)
            VALUES (?, ?, ?, ?, ?, ?, 'new')
        ''', (
            data['full_name'],
            data['address'],
            data['phone'],
            data.get('comment', ''),
            data.get('selected_works', '[]'),
            data.get('total_amount', 0)
        ))

        app_id = cursor.lastrowid
        conn.commit()
        conn.close()

        # Логируем создание
        ApplicationHistory.log(app_id, 'created', 'Новая заявка создана')

        return app_id

    @staticmethod
    def get_all(filters=None):
        """Получает все заявки с фильтрами"""
        conn = get_db_connection()
        cursor = conn.cursor()

        query = '''
            SELECT id, full_name, phone, address, comment, 
                   selected_works, total_amount, status, created_at
            FROM applications 
            WHERE 1=1
        '''
        params = []

        if filters:
            if filters.get('status') and filters['status'] != 'all':
                query += ' AND status = ?'
                params.append(filters['status'])

            if filters.get('search'):
                query += ' AND (full_name LIKE ? OR phone LIKE ? OR address LIKE ?)'
                search_term = f'%{filters["search"]}%'
                params.extend([search_term, search_term, search_term])

            if filters.get('date_from'):
                query += ' AND DATE(created_at) >= ?'
                params.append(filters['date_from'])

            if filters.get('date_to'):
                query += ' AND DATE(created_at) <= ?'
                params.append(filters['date_to'])

        query += ' ORDER BY created_at DESC'

        cursor.execute(query, params)
        orders = cursor.fetchall()
        conn.close()

        return [dict(order) for order in orders]

    @staticmethod
    def get_by_id(order_id):
        """Получает заявку по ID"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM applications WHERE id = ?', (order_id,))
        order = cursor.fetchone()
        conn.close()

        return dict(order) if order else None

    @staticmethod
    def update_status(order_id, new_status):
        """Обновляет статус заявки"""
        conn = get_db_connection()
        cursor = conn.cursor()

        # Получаем старый статус
        cursor.execute('SELECT status FROM applications WHERE id = ?', (order_id,))
        result = cursor.fetchone()
        old_status = result['status'] if result else 'new'

        # Обновляем статус
        cursor.execute('''
               UPDATE applications 
               SET status = ?, updated_at = CURRENT_TIMESTAMP 
               WHERE id = ?
           ''', (new_status, order_id))

        conn.commit()
        conn.close()

        return old_status

    @staticmethod
    def get_status_options():
        """Возвращает все возможные статусы"""
        return [
            {'value': 'new', 'label': 'Новая', 'color': '#3498db'},
            {'value': 'in_progress', 'label': 'В работе', 'color': '#f39c12'},
            {'value': 'completed', 'label': 'Выполнено', 'color': '#27ae60'},
            {'value': 'cancelled', 'label': 'Отменено', 'color': '#e74c3c'}
        ]

    @staticmethod
    def delete(order_id):
        """Удаляет заявку"""
        conn = get_db_connection()
        cursor = conn.cursor()

        # Получаем данные перед удалением
        cursor.execute('SELECT * FROM applications WHERE id = ?', (order_id,))
        order = cursor.fetchone()

        # Удаляем
        cursor.execute('DELETE FROM applications WHERE id = ?', (order_id,))

        conn.commit()
        conn.close()

        return dict(order) if order else None

    @staticmethod
    def get_stats():
        """Получает статистику по заявкам"""
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN status = 'new' THEN 1 ELSE 0 END) as new_count,
                SUM(CASE WHEN status = 'in_progress' THEN 1 ELSE 0 END) as in_progress_count,
                SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed_count,
                SUM(CASE WHEN status = 'cancelled' THEN 1 ELSE 0 END) as cancelled_count,
                SUM(total_amount) as total_amount
            FROM applications
        ''')

        stats = cursor.fetchone()
        conn.close()

        return dict(stats) if stats else {}

        # models/application.py - добавьте этот метод в класс Application

# models/application.py - добавьте этот метод в класс Application

    @staticmethod
    def get_stats_with_filters(filters=None):
        """Получает статистику по заявкам с учетом фильтров"""
        conn = get_db_connection()
        cursor = conn.cursor()

        # Базовый запрос
        query = '''
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN status = 'new' THEN 1 ELSE 0 END) as new_count,
                SUM(CASE WHEN status = 'in_progress' THEN 1 ELSE 0 END) as in_progress_count,
                SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed_count,
                SUM(CASE WHEN status = 'cancelled' THEN 1 ELSE 0 END) as cancelled_count,
                SUM(total_amount) as total_amount
            FROM applications
            WHERE 1=1
        '''
        params = []

        if filters:
            if filters.get('status') and filters['status'] != 'all':
                query += ' AND status = ?'
                params.append(filters['status'])

            if filters.get('search'):
                query += ' AND (full_name LIKE ? OR phone LIKE ? OR address LIKE ?)'
                search_term = f'%{filters["search"]}%'
                params.extend([search_term, search_term, search_term])

            if filters.get('date_from'):
                query += ' AND DATE(created_at) >= ?'
                params.append(filters['date_from'])

            if filters.get('date_to'):
                query += ' AND DATE(created_at) <= ?'
                params.append(filters['date_to'])

        cursor.execute(query, params)
        stats = cursor.fetchone()
        conn.close()

        return dict(stats) if stats else {
            'total': 0,
            'new_count': 0,
            'in_progress_count': 0,
            'completed_count': 0,
            'cancelled_count': 0,
            'total_amount': 0
        }


class ApplicationHistory:
    @staticmethod
    def log(application_id, action, details):
        """Записывает действие в историю"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO application_history (application_id, action, details)
                VALUES (?, ?, ?)
            ''', (application_id, action, details))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Ошибка записи в историю: {e}")

    @staticmethod
    def get_by_application_id(application_id):
        """Получает историю изменений заявки"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM application_history 
            WHERE application_id = ? 
            ORDER BY created_at DESC
        ''', (application_id,))
        history = cursor.fetchall()
        conn.close()

        return [dict(item) for item in history]