// static/js/notifications.js
let currentNotificationId = null;

document.addEventListener('DOMContentLoaded', function() {
    loadNotifications();
});

function loadNotifications() {
    fetch('/api/notifications/email')
        .then(response => response.json())
        .then(data => {
            displayNotifications(data);
        })
        .catch(error => {
            console.error('Erreur chargement notifications:', error);
            document.getElementById('notificationsTable').innerHTML =
                '<div class="error">Erreur de chargement des notifications</div>';
        });
}

function displayNotifications(notifications) {
    const tableContainer = document.getElementById('notificationsTable');

    if (notifications.length === 0) {
        tableContainer.innerHTML = '<div class="loading">Aucune notification configurée</div>';
        return;
    }

    let html = `
        <table class="notifications-table">
            <thead>
                <tr>
                    <th>Email</th>
                    <th>Type</th>
                    <th>Contenu</th>
                    <th>Statut</th>
                    <th>Dernier envoi</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
    `;

    notifications.forEach(notification => {
        const statusClass = notification.is_active ? 'status-active' : 'status-inactive';
        const statusText = notification.is_active ? 'Actif' : 'Inactif';
        const lastSent = notification.last_sent ?
            new Date(notification.last_sent).toLocaleDateString('fr-FR') : 'Jamais';

        const content = [];
        if (notification.include_detections) content.push('Détections');
        if (notification.include_alerts) content.push('Alertes');
        if (notification.include_presence) content.push('Présences');
        if (notification.include_compliance) content.push('Conformité');

        html += `
            <tr>
                <td>${notification.email_address}</td>
                <td>${getTypeLabel(notification.notification_type)}</td>
                <td>${content.join(', ')}</td>
                <td><span class="${statusClass}">${statusText}</span></td>
                <td>${lastSent}</td>
                <td class="action-buttons">
                    <button class="btn btn-sm btn-secondary" onclick="editNotification(${notification.id})">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn btn-sm btn-secondary" onclick="deleteNotification(${notification.id})">
                        <i class="fas fa-trash"></i>
                    </button>
                </td>
            </tr>
        `;
    });

    html += `
            </tbody>
        </table>
    `;

    tableContainer.innerHTML = html;
}

function getTypeLabel(type) {
    const labels = {
        'daily': 'Quotidien',
        'weekly': 'Hebdomadaire',
        'monthly': 'Mensuel'
    };
    return labels[type] || type;
}

function addNotification() {
    currentNotificationId = null;
    document.getElementById('notificationForm').reset();
    document.getElementById('emailAddress').value = '';
    document.getElementById('notificationType').value = 'daily';
    document.getElementById('includeDetections').checked = true;
    document.getElementById('includeAlerts').checked = true;
    document.getElementById('includePresence').checked = true;
    document.getElementById('includeCompliance').checked = true;
    document.getElementById('isActive').checked = true;

    new bootstrap.Modal(document.getElementById('notificationModal')).show();
}

function editNotification(id) {
    currentNotificationId = id;

    fetch(`/api/notifications/email/${id}`)
        .then(response => response.json())
        .then(notification => {
            document.getElementById('emailAddress').value = notification.email_address;
            document.getElementById('notificationType').value = notification.notification_type;
            document.getElementById('includeDetections').checked = notification.include_detections;
            document.getElementById('includeAlerts').checked = notification.include_alerts;
            document.getElementById('includePresence').checked = notification.include_presence;
            document.getElementById('includeCompliance').checked = notification.include_compliance;
            document.getElementById('isActive').checked = notification.is_active;

            new bootstrap.Modal(document.getElementById('notificationModal')).show();
        })
        .catch(error => {
            console.error('Erreur chargement notification:', error);
            alert('Erreur de chargement de la notification');
        });
}

function saveNotification() {
    const formData = {
        email_address: document.getElementById('emailAddress').value,
        notification_type: document.getElementById('notificationType').value,
        include_detections: document.getElementById('includeDetections').checked,
        include_alerts: document.getElementById('includeAlerts').checked,
        include_presence: document.getElementById('includePresence').checked,
        include_compliance: document.getElementById('includeCompliance').checked,
        is_active: document.getElementById('isActive').checked
    };

    if (!formData.email_address) {
        alert('Veuillez saisir une adresse email');
        return;
    }

    const url = currentNotificationId ?
        `/api/notifications/email/${currentNotificationId}` :
        '/api/notifications/email';

    const method = currentNotificationId ? 'PUT' : 'POST';

    fetch(url, {
        method: method,
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert('Erreur: ' + data.error);
        } else {
            bootstrap.Modal.getInstance(document.getElementById('notificationModal')).hide();
            loadNotifications();
            alert(currentNotificationId ? 'Notification mise à jour' : 'Notification ajoutée');
        }
    })
    .catch(error => {
        console.error('Erreur sauvegarde:', error);
        alert('Erreur de sauvegarde');
    });
}

function deleteNotification(id) {
    if (!confirm('Êtes-vous sûr de vouloir supprimer cette notification ?')) {
        return;
    }

    fetch(`/api/notifications/email/${id}`, {
        method: 'DELETE'
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert('Erreur: ' + data.error);
        } else {
            loadNotifications();
            alert('Notification supprimée');
        }
    })
    .catch(error => {
        console.error('Erreur suppression:', error);
        alert('Erreur de suppression');
    });
}

function sendTestEmail() {
    const email = document.getElementById('testEmail').value;

    if (!email) {
        alert('Veuillez saisir une adresse email de test');
        return;
    }

    fetch('/api/notifications/send-test', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email: email })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert('Erreur: ' + data.error);
        } else {
            alert('Email de test envoyé avec succès');
        }
    })
    .catch(error => {
        console.error('Erreur envoi test:', error);
        alert('Erreur d\'envoi du test');
    });
}

function sendScheduledNotifications() {
    if (!confirm('Envoyer maintenant toutes les notifications programmées ?')) {
        return;
    }

    fetch('/api/notifications/send-scheduled', {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert('Erreur: ' + data.error);
        } else {
            alert('Notifications programmées envoyées');
            loadNotifications(); // Recharger pour mettre à jour les dates d'envoi
        }
    })
    .catch(error => {
        console.error('Erreur envoi programmé:', error);
        alert('Erreur d\'envoi des notifications programmées');
    });
}

function saveSmtpConfig() {
    const config = {
        smtp_server: document.getElementById('smtpServer').value,
        smtp_port: document.getElementById('smtpPort').value,
        sender_email: document.getElementById('senderEmail').value,
        sender_password: document.getElementById('senderPassword').value
    };

    // Pour l'instant, afficher juste un message
    // Dans un vrai système, cela serait sauvegardé dans la BD ou config
    alert('Configuration SMTP sauvegardée (simulation)\\n' +
          'Serveur: ' + config.smtp_server + '\\n' +
          'Port: ' + config.smtp_port + '\\n' +
          'Email: ' + config.sender_email);

    // Ici, on pourrait envoyer à une API pour sauvegarder la config
}

function exportPresencePDF() {
    // Demander les dates à l'utilisateur
    const startDate = prompt('Date de début (YYYY-MM-DD) ou laissez vide pour 7 derniers jours:', '');
    const endDate = prompt('Date de fin (YYYY-MM-DD) ou laissez vide pour aujourd\'hui:', '');
    
    // Construire l'URL
    let url = '/api/export/presence-pdf';
    const params = [];
    
    if (startDate) params.push(`start_date=${startDate}`);
    if (endDate) params.push(`end_date=${endDate}`);
    
    if (params.length > 0) {
        url += '?' + params.join('&');
    }
    
    // Ouvrir dans un nouvel onglet pour déclencher le téléchargement
    window.open(url, '_blank');
}</content>
<parameter name="filePath">D:\projet\EPI-DETECTION-PROJECT\static\js\notifications.js