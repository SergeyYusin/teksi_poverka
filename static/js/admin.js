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
        fetch(`/admin/api/update-status`, {
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



function showDetails(orderId) {
    fetch(`/admin/api/order/${orderId}?password=${PASSWORD}`)
        .then(response => response.json())
        .then(data => {
            document.getElementById('modalOrderId').textContent = orderId;
            let content = `
                <div style="margin-bottom: 20px;">
                    <h3>Контактная информация</h3>
                    <p><strong>ФИО:</strong> ${data.full_name}</p>
                    <p><strong>Телефон:</strong> <a href="tel:${data.phone}">${data.phone}</a></p>
                    <p><strong>Адрес:</strong> ${data.address}</p>
                    <p><strong>Дата создания:</strong> ${data.created_at}</p>
                    <p><strong>Статус:</strong> <span class="status status-${data.status}">${getStatusText(data.status)}</span></p>
                </div>

                <div style="margin-bottom: 20px;">
                    <h3>Выбранные услуги</h3>
                    <div id="worksList"></div>
                </div>

                <div style="margin-bottom: 20px;">
                    <h3>Комментарий</h3>
                    <p style="background: #f8f9fa; padding: 15px; border-radius: 8px;">${data.comment || 'Нет комментария'}</p>
                </div>

                <div>
                    <h3>Итоговая стоимость</h3>
                    <p style="font-size: 1.5rem; font-weight: 600; color: #27ae60;">${parseInt(data.total_amount || 0).toLocaleString('ru-RU')} ₽</p>
                </div>
            `;

            document.getElementById('modalContent').innerHTML = content;

            // Добавляем список услуг
            if (data.selected_works) {
                try {
                    const works = JSON.parse(data.selected_works);
                    let worksHtml = '';
                    works.forEach(work => {
                        const cost = (work.price || 0) * (work.quantity || 0);
                        worksHtml += `
                            <div class="work-item" style="margin-bottom: 10px;">
                                <div><strong>${work.type}</strong></div>
                                <div>Количество: ${work.quantity} ${work.unit}</div>
                                <div>Цена за единицу: ${work.price} ₽</div>
                                <div>Стоимость: ${cost} ₽</div>
                            </div>
                        `;
                    });
                    document.getElementById('worksList').innerHTML = worksHtml;
                } catch (e) {
                    document.getElementById('worksList').innerHTML = '<p>Ошибка загрузки данных об услугах</p>';
                }
            }

            document.getElementById('detailsModal').style.display = 'flex';
        })
        .catch(error => {
            alert('Ошибка загрузки данных: ' + error);
        });
}

function showHistory(orderId) {
    fetch(`/admin/api/history/${orderId}?password=${PASSWORD}`)
        .then(response => response.json())
        .then(data => {
            document.getElementById('historyOrderId').textContent = orderId;

            if (data.length === 0) {
                document.getElementById('historyContent').innerHTML = '<p>История изменений отсутствует</p>';
            } else {
                let historyHtml = '';
                data.forEach(item => {
                    historyHtml += `
                        <div class="history-item">
                            <div><strong>${item.action}</strong></div>
                            <div>${item.details}</div>
                            <div style="font-size: 0.9rem; color: #666; margin-top: 5px;">
                                ${item.changed_by} • ${item.created_at}
                            </div>
                        </div>
                    `;
                });
                document.getElementById('historyContent').innerHTML = historyHtml;
            }

            document.getElementById('historyModal').style.display = 'flex';
        })
        .catch(error => {
            alert('Ошибка загрузки истории: ' + error);
        });
}

function changeStatus(orderId, newStatus) {
    // Получаем текущий статус заявки
    fetch(`/admin/api/order/${orderId}?password=${PASSWORD}`)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert('Ошибка: ' + data.error);
                return;
            }

            showStatusModal(orderId, data.status);
        })
        .catch(error => {
            alert('Ошибка загрузки данных: ' + error);
        });
}

function deleteOrder(orderId) {
    if (confirm('Вы уверены, что хотите удалить эту заявку? Это действие нельзя отменить.')) {
        fetch(`/admin/api/delete`, {
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
                document.getElementById(`row-${orderId}`).remove();
                alert('Заявка удалена!');
            } else {
                alert('Ошибка: ' + (data.error || 'Неизвестная ошибка'));
            }
        })
        .catch(error => {
            alert('Ошибка сети: ' + error);
        });
    }
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'none';
        // Если это динамически созданное модальное окно, удаляем его
        if (modalId === 'statusModal') {
            setTimeout(() => {
                modal.remove();
            }, 300);
        }
    }
}

function getStatusText(status) {
    const statuses = {
        'new': 'Новая',
        'in_progress': 'В работе',
        'completed': 'Выполнено',
        'cancelled': 'Отменено'
    };
    return statuses[status] || status;
}

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

// admin.js - основные функции админки

// Показать детали заявки
function showDetails(orderId) {
    fetch(`/admin/api/order/${orderId}?password=${PASSWORD}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                document.getElementById('modalOrderId').textContent = orderId;
                document.getElementById('modalContent').innerHTML = `
                    <div class="modal-body">
                        <div class="info-grid">
                            <div class="info-item">
                                <strong>ФИО:</strong> ${data.order.full_name}
                            </div>
                            <div class="info-item">
                                <strong>Телефон:</strong> <a href="tel:${data.order.phone}">${data.order.phone}</a>
                            </div>
                            <div class="info-item">
                                <strong>Адрес:</strong> ${data.order.address}
                            </div>
                            <div class="info-item">
                                <strong>Дата:</strong> ${data.order.created_at}
                            </div>
                            <div class="info-item full-width">
                                <strong>Услуги:</strong><br>
                                ${data.order.works_html || 'Нет данных'}
                            </div>
                            <div class="info-item">
                                <strong>Сумма:</strong> ${data.order.total_amount} ₽
                            </div>
                            <div class="info-item">
                                <strong>Статус:</strong> <span class="status status-${data.order.status}">${data.order.status_text}</span>
                            </div>
                            <div class="info-item full-width">
                                <strong>Комментарий:</strong><br>
                                ${data.order.comment || 'Нет комментария'}
                            </div>
                        </div>
                    </div>
                `;
                openModal('detailsModal');
            }
        })
        .catch(error => console.error('Error:', error));
}

// Показать историю изменений
function showHistory(orderId) {
    document.getElementById('historyOrderId').textContent = orderId;
    document.getElementById('historyContent').innerHTML = '<p>Загрузка истории...</p>';
    openModal('historyModal');

    // Здесь можно добавить запрос к API для получения истории
}

// Удалить заявку
function deleteOrder(orderId) {
    if (confirm('Вы уверены, что хотите удалить эту заявку?')) {
        fetch(`/admin/api/order/${orderId}?password=${PASSWORD}`, {
            method: 'DELETE'
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                document.getElementById(`row-${orderId}`).remove();
                alert('Заявка удалена!');
            } else {
                alert('Ошибка при удалении: ' + data.error);
            }
        })
        .catch(error => console.error('Error:', error));
    }
}

// Модальные окна
function openModal(modalId) {
    document.getElementById(modalId).style.display = 'block';
}

function closeModal(modalId) {
    document.getElementById(modalId).style.display = 'none';
}

// Закрытие модальных окон при клике вне их
window.onclick = function(event) {
    const modals = document.querySelectorAll('.modal');
    modals.forEach(modal => {
        if (event.target === modal) {
            modal.style.display = 'none';
        }
    });
};