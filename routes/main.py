from flask import Blueprint, render_template, request, redirect, url_for, flash
from models.application import Application
import json
from datetime import datetime
import os

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    return render_template('index.html')


@main_bp.route('/form')
def form():
    return render_template('form.html')


@main_bp.route('/submit_application', methods=['POST'])
def submit_application():
    try:
        # Получаем данные
        name = request.form['full_name'].strip()
        address = request.form['address'].strip()
        phone = request.form['phone'].strip()
        comment = request.form.get('comment', '').strip()

        # Данные о работах
        works_json = request.form.get('selected_works_json', '[]')
        total = request.form.get('total_amount', '0')

        try:
            works = json.loads(works_json)
        except:
            works = []

        # Валидация
        if not name or not address or not phone:
            flash('❌ Заполните все обязательные поля', 'error')
            return redirect(url_for('main.form'))

        if not works:
            flash('❌ Выберите хотя бы один вид работ', 'error')
            return redirect(url_for('main.form'))

        # Создаем заявку
        app_data = {
            'full_name': name,
            'address': address,
            'phone': phone,
            'comment': comment,
            'selected_works': works_json,
            'total_amount': total
        }

        app_id = Application.create(app_data)

        # Сохраняем в файл для надежности
        os.makedirs('data', exist_ok=True)
        with open('data/orders_log.txt', 'a', encoding='utf-8') as f:
            f.write(f"{datetime.now()}: {name} | {phone} | {address} | {total} руб\n")

        flash(f'✅ Заявка #{app_id} принята! Мы свяжемся с вами по номеру {phone}', 'success')
        return redirect(url_for('main.prices'))

    except Exception as e:
        print(f"Ошибка: {e}")
        flash('⚠️ Произошла ошибка при сохранении', 'error')
        return redirect(url_for('main.form'))


@main_bp.route('/prices')
def prices():
    return render_template('prices.html')