/**
 * Dashboard.js
 * Handles real-time updates for the Instagram Bot Dashboard.
 * Manages polling for stats and logs, and handles start/stop actions.
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initial fetch of data
    updateDashboard();
    updateLogs();

    // Set up auto-refresh timers (10 seconds for stats, 5 seconds for logs)
    const statsInterval = setInterval(updateDashboard, 10000);
    const logsInterval = setInterval(updateLogs, 5000);

    // Event Listener for the Start Bot form
    const startForm = document.getElementById('start-bot-form');
    if (startForm) {
        startForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const targetInput = document.getElementById('target-username');
            const target = targetInput.value.trim();

            if (!target) {
                alert("Please enter a target Instagram username.");
                return;
            }

            startBot(target);
        });
    }

    // Event Listener for the Stop Bot button
    const stopBtn = document.getElementById('stop-bot-btn');
    if (stopBtn) {
        stopBtn.addEventListener('click', function() {
            stopBot();
        });
    }
});

/**
 * Updates the dashboard UI with data from the /api/stats endpoint.
 */
function updateDashboard() {
    fetch('/api/stats')
        .then(response => {
            if (!response.ok) throw new Error('Network response was not ok');
            return response.json();
        })
        .then(data => {
            // Update Status Badge
            const statusBadge = document.getElementById('bot-status');
            if (statusBadge) {
                statusBadge.textContent = data.bot_status;
                statusBadge.className = data.bot_status === 'Running' ? 'badge bg-success' : 'badge bg-danger';
            }

            // Update Statistics
            document.getElementById('stat-target').textContent = data.target_account || 'None';
            document.getElementById('stat-total-followed').textContent = data.total_followed;
            document.getElementById('stat-hourly').textContent = `${data.hourly_count} / ${data.hourly_limit}`;
            document.getElementById('stat-daily').textContent = `${data.daily_count} / ${data.daily_limit}`;
            document.getElementById('stat-reset').textContent = data.next_reset;

            // Toggle form visibility based on status
            const startBtn = document.querySelector('#start-bot-form button');
            const stopBtn = document.getElementById('stop-bot-btn');
            
            if (data.bot_status === 'Running') {
                if (startBtn) startBtn.disabled = true;
                if (stopBtn) stopBtn.disabled = false;
            } else {
                if (startBtn) startBtn.disabled = false;
                if (stopBtn) stopBtn.disabled = true;
            }
        })
        .catch(error => console.error('Error fetching stats:', error));
}

/**
 * Fetches the latest logs and updates the log container.
 */
function updateLogs() {
    fetch('/api/logs')
        .then(response => response.json())
        .then(data => {
            const logContainer = document.getElementById('log-container');
            if (logContainer && data.logs) {
                // Join logs with newlines and escape HTML to prevent XSS
                logContainer.innerHTML = data.logs
                    .map(log => `<div>${log}</div>`)
                    .join('');
                
                // Auto-scroll to bottom of logs
                logContainer.scrollTop = logContainer.scrollHeight;
            }
        })
        .catch(error => console.error('Error fetching logs:', error));
}

/**
 * Sends a request to start the bot.
 * @param {string} target - The target Instagram username.
 */
function startBot(target) {
    fetch('/start', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ target: target })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            updateDashboard();
            alert(data.message);
        } else {
            alert("Error: " + data.message);
        }
    })
    .catch(error => {
        console.error('Error starting bot:', error);
        alert("Failed to connect to server.");
    });
}

/**
 * Sends a request to stop the bot.
 */
function stopBot() {
    fetch('/stop', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            updateDashboard();
            alert(data.message);
        } else {
            alert("Error: " + data.message);
        }
    })
    .catch(error => {
        console.error('Error stopping bot:', error);
        alert("Failed to connect to server.");
    });
}