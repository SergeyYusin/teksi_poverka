// static/js/admin.js

const PASSWORD = '{{ password }}' || window.PASSWORD;

function getStatusText(status) {
    const statuses = {
        'new': 'Новая',
        'in_progress': 'В работе',
        'completed': 'Выполнено',
        'cancelled': 'Отменено'
    };
    return statuses[status] || status;
}

function showDetails(orderId) {
    fetch(`/admin/api/order/${orderId}?password=${PASSWORD}`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.error) {
                alert('Ошибка: ' + data.error);
                return;
            }

            document.getElementById('modalOrderId').textContent = orderId;

            // Форматируем данные для отображения
            let html = `
                <div class="order-details">
                    <div class="detail-row">
                        <strong>ФИО:</strong> ${data.full_name || ''}
                    </div>
                    <div class="detail-row">
                        <strong>Телефон:</strong> <a href="tel:${data.phone || ''}">${data.phone || ''}</a>
                    </div>
                    <div class="detail-row">
                        <strong>Адрес:</strong> ${data.address || ''}
                    </div>
                    <div class="detail-row">
                        <strong>Статус:</strong> <span class="status status-${data.status}">${data.status_text || getStatusText(data.status)}</span>
                    </div>
                    <div class="detail-row">
                        <strong>Сумма:</strong> ${data.total_amount || 0} ₽
                    </div>
                    <div class="detail-row">
                        <strong>Дата создания:</strong> ${data.created_at || ''}
                    </div>
            `;

            // Добавляем услуги, если есть
            if (data.selected_works) {
                try {
                    const works = JSON.parse(data.selected_works);
                    html += `<div class="detail-row"><strong>Услуги:</strong></div>`;
                    works.forEach(work => {
                        html += `<div class="work-item">• ${work.type || ''}: ${work.quantity || 0} ${work.unit || ''} (${work.price || 0} ₽ за ед.)</div>`;
                    });
                } catch (e) {
                    html += `<div class="detail-row"><strong>Услуги:</strong> ${data.selected_works}</div>`;
                }
            }

            // Добавляем комментарий, если есть
            if (data.comment) {
                html += `<div class="detail-row"><strong>Комментарий:</strong><br>${data.comment}</div>`;
            }

            html += `</div>`;

            document.getElementById('modalContent').innerHTML = html;
            document.getElementById('detailsModal').style.display = 'block';
        })
        .catch(error => {
            alert('Ошибка загрузки данных: ' + error.message);
            console.error('Error:', error);
        });
}

function showHistory(orderId) {
    fetch(`/admin/api/history/${orderId}?password=${PASSWORD}`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(history => {
            document.getElementById('historyOrderId').textContent = orderId;

            let html = '<div class="history-list">';

            if (history.length === 0) {
                html += '<div class="history-empty">История изменений отсутствует</div>';
            } else {
                history.forEach(item => {
                    html += `
                        <div class="history-item">
                            <div class="history-date">${item.created_at || ''}</div>
                            <div class="history-action">${item.details || item.action || ''}</div>
                            <div class="history-user">${item.changed_by || 'system'}</div>
                        </div>
                    `;
                });
            }

            html += '</div>';

            document.getElementById('historyContent').innerHTML = html;
            document.getElementById('historyModal').style.display = 'block';
        })
        .catch(error => {
            alert('Ошибка загрузки истории: ' + error.message);
            console.error('Error:', error);
        });
}

function showStatusModal(orderId, currentStatus) {
    const statuses = [
        { value: 'new', label: 'Новая', color: '#3498db', icon: '📋', desc: 'Новая заявка' },
        { value: 'in_progress', label: 'В работе', color: '#f39c12', icon: '⚡', desc: 'Работа начата' },
        { value: 'completed', label: 'Выполнено', color: '#27ae60', icon: '✅', desc: 'Работа завершена' },
        { value: 'cancelled', label: 'Отменено', color: '#e74c3c', icon: '❌', desc: 'Заявка отменена' }
    ];

    // Создаем модальное окно
    const modal = document.createElement('div');
    modal.className = 'modal';
    modal.id = 'statusModal';
    modal.innerHTML = `
        <div class="modal-content" style="max-width: 500px;">
            <div class="modal-header">
                <h2>Изменение статуса заявки #${orderId}</h2>
                <button onclick="closeModal('statusModal')">×</button>
            </div>
            <div class="status-modal">
                <p>Текущий статус: <span class="status status-${currentStatus}">${getStatusText(currentStatus)}</span></p>
                <p>Выберите новый статус:</p>
                <div class="status-options">
                    ${statuses.map(status => `
                        <div class="status-option" onclick="selectStatus('${status.value}', '${orderId}')"
                             style="border-color: ${status.value === currentStatus ? status.color : '#eee'};
                                    ${status.value === currentStatus ? 'background-color: #f0f8ff;' : ''}">
                            <div class="status-option-icon">${status.icon}</div>
                            <div class="status-option-label" style="color: ${status.color}">${status.label}</div>
                            <div class="status-option-desc">${status.desc}</div>
                        </div>
                    `).join('')}
                </div>
                <div class="modal-actions" style="margin-top: 20px;">
                    <button class="btn btn-secondary" onclick="closeModal('statusModal')">Отмена</button>
                </div>
            </div>
        </div>
    `;

    document.body.appendChild(modal);
    modal.style.display = 'flex';
}

function selectStatus(status, orderId) {
    if (confirm(`Изменить статус заявки #${orderId} на "${getStatusText(status)}"?`)) {
        fetch('/admin/api/update-status', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                order_id: orderId,
                status: status,
                password: PASSWORD
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Статус обновлен!');
                closeModal('statusModal');
                location.reload();
            } else {
                alert('Ошибка: ' + (data.error || 'Неизвестная ошибка'));
            }
        })
        .catch(error => {
            alert('Ошибка сети: ' + error);
        });
    }
}

function deleteOrder(orderId) {
    if (confirm(`Вы уверены, что хотите удалить заявку #${orderId}? Это действие нельзя отменить.`)) {
        fetch('/admin/api/delete', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                order_id: orderId,
                password: PASSWORD
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Удаляем строку из таблицы
                const row = document.getElementById(`row-${orderId}`);
                if (row) {
                    row.style.backgroundColor = '#fee';
                    setTimeout(() => row.remove(), 500);
                }
                alert('Заявка удалена!');

                // Обновляем счетчик
                updateStatsCount();
            } else {
                alert('Ошибка: ' + (data.error || 'Неизвестная ошибка'));
            }
        })
        .catch(error => {
            alert('Ошибка сети: ' + error);
        });
    }
}

function updateStatsCount() {
    // Обновляем общий счетчик заявок
    const totalElement = document.querySelector('.header p strong:first-child');
    if (totalElement) {
        const currentTotal = parseInt(totalElement.textContent) || 0;
        totalElement.textContent = Math.max(0, currentTotal - 1);
    }
}

// В admin.js оставьте только общие функции
function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'none';
        if (modalId === 'statusModal' && modal.parentNode) {
            setTimeout(() => modal.remove(), 300);
        }
    }
}

// ... остальные общие функции ...

// Закрытие модальных окон при клике вне их
window.onclick = function(event) {
    const modals = ['detailsModal', 'historyModal', 'statusModal'];
    modals.forEach(modalId => {
        const modal = document.getElementById(modalId);
        if (modal && event.target == modal) {
            closeModal(modalId);
        }
    });
};

// Закрытие модальных окон по клавише Escape
document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape') {
        closeModal('detailsModal');
        closeModal('historyModal');
        closeModal('statusModal');
    }
});

// Для совместимости с вашим HTML
window.showStatusModal = showStatusModal;
window.showDetails = showDetails;
window.showHistory = showHistory;
window.deleteOrder = deleteOrder;
window.closeModal = closeModal;