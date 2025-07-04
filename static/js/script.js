// Global variables
let currentUser = null;
let currentSessionId = null;
let currentTab = 'chat';

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    checkAuth();
    setupEventListeners();
});

// Setup event listeners
function setupEventListeners() {
    // Enter key for message input
    document.getElementById('message-input').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });
    
    // Enter key for login
    document.getElementById('password').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            login();
        }
    });
}

// Authentication functions
async function checkAuth() {
    try {
        const response = await fetch('/api/auth/check-auth');
        const data = await response.json();
        
        if (data.authenticated) {
            currentUser = data.user;
            showChatSection();
        } else {
            showAuthSection();
        }
    } catch (error) {
        console.error('Auth check error:', error);
        showAuthSection();
    }
}

async function login() {
    const username = document.getElementById('username').value.trim();
    const password = document.getElementById('password').value;
    
    if (!username || !password) {
        showAlert('Please enter both username and password', 'error');
        return;
    }
    
    try {
        const response = await fetch('/api/auth/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ username, password })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            currentUser = data.user;
            showChatSection();
            showAlert('Login successful!', 'success');
        } else {
            showAlert(data.error || 'Login failed', 'error');
        }
    } catch (error) {
        console.error('Login error:', error);
        showAlert('Login failed. Please try again.', 'error');
    }
}

async function register() {
    const username = document.getElementById('reg-username').value.trim();
    const email = document.getElementById('reg-email').value.trim();
    const password = document.getElementById('reg-password').value;
    const firstName = document.getElementById('reg-firstname').value.trim();
    const lastName = document.getElementById('reg-lastname').value.trim();
    const gradeLevel = document.getElementById('reg-grade').value.trim();
    
    if (!username || !email || !password || !firstName || !lastName) {
        showAlert('Please fill in all required fields', 'error');
        return;
    }
    
    try {
        const response = await fetch('/api/auth/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                username,
                email,
                password,
                first_name: firstName,
                last_name: lastName,
                grade_level: gradeLevel || null
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showAlert('Registration successful! Please login.', 'success');
            toggleAuthForm();
            // Clear form
            document.getElementById('reg-username').value = '';
            document.getElementById('reg-email').value = '';
            document.getElementById('reg-password').value = '';
            document.getElementById('reg-firstname').value = '';
            document.getElementById('reg-lastname').value = '';
            document.getElementById('reg-grade').value = '';
        } else {
            showAlert(data.error || 'Registration failed', 'error');
        }
    } catch (error) {
        console.error('Registration error:', error);
        showAlert('Registration failed. Please try again.', 'error');
    }
}

async function logout() {
    try {
        await fetch('/api/auth/logout', { method: 'POST' });
        currentUser = null;
        currentSessionId = null;
        showAuthSection();
        showAlert('Logged out successfully', 'info');
    } catch (error) {
        console.error('Logout error:', error);
    }
}

// UI functions
function showAuthSection() {
    document.getElementById('auth-section').classList.remove('hidden');
    document.getElementById('chat-section').classList.add('hidden');
}

function showChatSection() {
    document.getElementById('auth-section').classList.add('hidden');
    document.getElementById('chat-section').classList.remove('hidden');
    document.getElementById('user-name').textContent = currentUser.first_name + ' ' + currentUser.last_name;
    
    // Load initial data
    loadChatHistory();
    showTab('chat');
}

function toggleAuthForm() {
    const loginForm = document.getElementById('login-form');
    const registerForm = document.getElementById('register-form');
    
    loginForm.classList.toggle('hidden');
    registerForm.classList.toggle('hidden');
}

function showTab(tabName) {
    // Hide all tabs
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.add('hidden');
    });
    
    // Remove active class from all menu buttons
    document.querySelectorAll('.menu button').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Show selected tab
    document.getElementById(tabName + '-tab').classList.remove('hidden');
    
    // Add active class to selected button
    event.target.classList.add('active');
    
    currentTab = tabName;
    
    // Load tab-specific data
    switch(tabName) {
        case 'notes':
            loadNotes();
            break;
        case 'schedule':
            loadSchedule();
            break;
        case 'reminders':
            loadReminders();
            break;
    }
}

// Chat functions
async function sendMessage() {
    const messageInput = document.getElementById('message-input');
    const message = messageInput.value.trim();
    
    if (!message) return;
    
    // Clear input
    messageInput.value = '';
    
    // Add user message to chat
    addMessageToChat(message, 'user');
    
    // Show typing indicator
    const typingId = addTypingIndicator();
    
    try {
        const response = await fetch('/api/chat/message', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: message,
                session_id: currentSessionId
            })
        });
        
        const data = await response.json();
        
        // Remove typing indicator
        removeTypingIndicator(typingId);
        
        if (response.ok) {
            currentSessionId = data.session_id;
            addMessageToChat(data.response, 'bot');
        } else {
            addMessageToChat('Sorry, I encountered an error. Please try again.', 'bot');
        }
    } catch (error) {
        console.error('Message error:', error);
        removeTypingIndicator(typingId);
        addMessageToChat('Sorry, I encountered an error. Please try again.', 'bot');
    }
}

function addMessageToChat(message, sender) {
    const messagesContainer = document.getElementById('chat-messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}`;
    
    const messageContent = document.createElement('div');
    messageContent.textContent = message;
    
    const messageTime = document.createElement('div');
    messageTime.className = 'message-time';
    messageTime.textContent = new Date().toLocaleTimeString();
    
    messageDiv.appendChild(messageContent);
    messageDiv.appendChild(messageTime);
    messagesContainer.appendChild(messageDiv);
    
    // Scroll to bottom
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

function addTypingIndicator() {
    const messagesContainer = document.getElementById('chat-messages');
    const typingDiv = document.createElement('div');
    const typingId = 'typing-' + Date.now();
    typingDiv.id = typingId;
    typingDiv.className = 'message bot';
    typingDiv.innerHTML = '<div class="loading"></div><div class="message-time">Typing...</div>';
    
    messagesContainer.appendChild(typingDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
    
    return typingId;
}

function removeTypingIndicator(typingId) {
    const typingDiv = document.getElementById(typingId);
    if (typingDiv) {
        typingDiv.remove();
    }
}

async function loadChatHistory() {
    try {
        const response = await fetch('/api/chat/history?limit=20');
        const data = await response.json();
        
        if (response.ok) {
            const messagesContainer = document.getElementById('chat-messages');
            messagesContainer.innerHTML = '';
            
            data.history.forEach(chat => {
                addMessageToChat(chat.message, 'user');
                addMessageToChat(chat.response, 'bot');
            });
        }
    } catch (error) {
        console.error('Chat history error:', error);
    }
}

// Notes functions
async function loadNotes() {
    try {
        const response = await fetch('/api/chat/notes');
        const data = await response.json();
        
        if (response.ok) {
            displayNotes(data.notes);
        }
    } catch (error) {
        console.error('Notes loading error:', error);
    }
}

function displayNotes(notes) {
    const notesList = document.getElementById('notes-list');
    notesList.innerHTML = '';
    
    if (notes.length === 0) {
        notesList.innerHTML = '<p class="text-center">No notes yet. Create your first note!</p>';
        return;
    }
    
    notes.forEach(note => {
        const noteCard = document.createElement('div');
        noteCard.className = 'item-card';
        noteCard.innerHTML = `
            <h3>${note.topic}</h3>
            <p><strong>Subject:</strong> ${note.subject}</p>
            <p>${note.note_content}</p>
            <div class="item-meta">
                Created: ${new Date(note.created_at).toLocaleDateString()}
            </div>
        `;
        notesList.appendChild(noteCard);
    });
}

function showNewNoteForm() {
    const modalForm = document.getElementById('modal-form');
    modalForm.innerHTML = `
        <h2>New Note</h2>
        <div class="form-group">
            <label>Subject:</label>
            <input type="text" id="note-subject" required>
        </div>
        <div class="form-group">
            <label>Topic:</label>
            <input type="text" id="note-topic" required>
        </div>
        <div class="form-group">
            <label>Content:</label>
            <textarea id="note-content" required></textarea>
        </div>
        <div class="form-actions">
            <button class="btn btn-secondary" onclick="closeModal()">Cancel</button>
            <button class="btn btn-primary" onclick="saveNote()">Save Note</button>
        </div>
    `;
    showModal();
}

async function saveNote() {
    const subject = document.getElementById('note-subject').value.trim();
    const topic = document.getElementById('note-topic').value.trim();
    const content = document.getElementById('note-content').value.trim();
    
    if (!subject || !topic || !content) {
        showAlert('Please fill in all fields', 'error');
        return;
    }
    
    try {
        const response = await fetch('/api/chat/notes', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ subject, topic, content })
        });
        
        if (response.ok) {
            closeModal();
            loadNotes();
            showAlert('Note saved successfully!', 'success');
        } else {
            const data = await response.json();
            showAlert(data.error || 'Failed to save note', 'error');
        }
    } catch (error) {
        console.error('Save note error:', error);
        showAlert('Failed to save note', 'error');
    }
}

// Schedule functions
async function loadSchedule() {
    try {
        const response = await fetch('/api/chat/schedule');
        const data = await response.json();
        
        if (response.ok) {
            displaySchedule(data.schedules);
        }
    } catch (error) {
        console.error('Schedule loading error:', error);
    }
}

function displaySchedule(schedules) {
    const scheduleList = document.getElementById('schedule-list');
    scheduleList.innerHTML = '';
    
    if (schedules.length === 0) {
        scheduleList.innerHTML = '<p class="text-center">No scheduled study sessions. Create your first schedule!</p>';
        return;
    }
    
    schedules.forEach(schedule => {
        const scheduleCard = document.createElement('div');
        scheduleCard.className = 'item-card';
        scheduleCard.innerHTML = `
            <h3>${schedule.subject} - ${schedule.topic}</h3>
            <p><strong>Date:</strong> ${schedule.scheduled_date}</p>
            <p><strong>Time:</strong> ${schedule.scheduled_time}</p>
            <p><strong>Duration:</strong> ${schedule.duration_minutes} minutes</p>
            <p><strong>Status:</strong> ${schedule.status}</p>
            ${schedule.notes ? `<p><strong>Notes:</strong> ${schedule.notes}</p>` : ''}
        `;
        scheduleList.appendChild(scheduleCard);
    });
}

function showNewScheduleForm() {
    const modalForm = document.getElementById('modal-form');
    modalForm.innerHTML = `
        <h2>New Study Schedule</h2>
        <div class="form-group">
            <label>Subject:</label>
            <input type="text" id="schedule-subject" required>
        </div>
        <div class="form-group">
            <label>Topic:</label>
            <input type="text" id="schedule-topic" required>
        </div>
        <div class="form-group">
            <label>Date:</label>
            <input type="date" id="schedule-date" required>
        </div>
        <div class="form-group">
            <label>Time:</label>
            <input type="time" id="schedule-time" required>
        </div>
        <div class="form-group">
            <label>Duration (minutes):</label>
            <input type="number" id="schedule-duration" value="60" min="15" max="480">
        </div>
        <div class="form-group">
            <label>Notes:</label>
            <textarea id="schedule-notes"></textarea>
        </div>
        <div class="form-actions">
            <button class="btn btn-secondary" onclick="closeModal()">Cancel</button>
            <button class="btn btn-primary" onclick="saveSchedule()">Save Schedule</button>
        </div>
    `;
    showModal();
}

async function saveSchedule() {
    const subject = document.getElementById('schedule-subject').value.trim();
    const topic = document.getElementById('schedule-topic').value.trim();
    const date = document.getElementById('schedule-date').value;
    const time = document.getElementById('schedule-time').value;
    const duration = parseInt(document.getElementById('schedule-duration').value);
    const notes = document.getElementById('schedule-notes').value.trim();
    
    if (!subject || !topic || !date || !time) {
        showAlert('Please fill in all required fields', 'error');
        return;
    }
    
    try {
        const response = await fetch('/api/chat/schedule', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                subject,
                topic,
                scheduled_date: date,
                scheduled_time: time,
                duration_minutes: duration,
                notes: notes || null
            })
        });
        
        if (response.ok) {
            closeModal();
            loadSchedule();
            showAlert('Schedule created successfully!', 'success');
        } else {
            const data = await response.json();
            showAlert(data.error || 'Failed to create schedule', 'error');
        }
    } catch (error) {
        console.error('Save schedule error:', error);
        showAlert('Failed to create schedule', 'error');
    }
}

// Reminders functions
async function loadReminders() {
    try {
        const response = await fetch('/api/chat/reminders');
        const data = await response.json();
        
        if (response.ok) {
            displayReminders(data.reminders);
        }
    } catch (error) {
        console.error('Reminders loading error:', error);
    }
}

function displayReminders(reminders) {
    const remindersList = document.getElementById('reminders-list');
    remindersList.innerHTML = '';
    
    if (reminders.length === 0) {
        remindersList.innerHTML = '<p class="text-center">No reminders set. Create your first reminder!</p>';
        return;
    }
    
    reminders.forEach(reminder => {
        const reminderCard = document.createElement('div');
        reminderCard.className = 'item-card';
        reminderCard.innerHTML = `
            <h3>${reminder.title}</h3>
            <p><strong>Date:</strong> ${reminder.reminder_date}</p>
            <p><strong>Time:</strong> ${reminder.reminder_time}</p>
            ${reminder.description ? `<p><strong>Description:</strong> ${reminder.description}</p>` : ''}
            <p><strong>Status:</strong> ${reminder.is_completed ? 'Completed' : 'Pending'}</p>
        `;
        remindersList.appendChild(reminderCard);
    });
}

function showNewReminderForm() {
    const modalForm = document.getElementById('modal-form');
    modalForm.innerHTML = `
        <h2>New Reminder</h2>
        <div class="form-group">
            <label>Title:</label>
            <input type="text" id="reminder-title" required>
        </div>
        <div class="form-group">
            <label>Description:</label>
            <textarea id="reminder-description"></textarea>
        </div>
        <div class="form-group">
            <label>Date:</label>
            <input type="date" id="reminder-date" required>
        </div>
        <div class="form-group">
            <label>Time:</label>
            <input type="time" id="reminder-time" required>
        </div>
        <div class="form-actions">
            <button class="btn btn-secondary" onclick="closeModal()">Cancel</button>
            <button class="btn btn-primary" onclick="saveReminder()">Save Reminder</button>
        </div>
    `;
    showModal();
}

async function saveReminder() {
    const title = document.getElementById('reminder-title').value.trim();
    const description = document.getElementById('reminder-description').value.trim();
    const date = document.getElementById('reminder-date').value;
    const time = document.getElementById('reminder-time').value;
    
    if (!title || !date || !time) {
        showAlert('Please fill in all required fields', 'error');
        return;
    }
    
    try {
        const response = await fetch('/api/chat/reminders', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                title,
                description: description || null,
                reminder_date: date,
                reminder_time: time
            })
        });
        
        if (response.ok) {
            closeModal();
            loadReminders();
            showAlert('Reminder created successfully!', 'success');
        } else {
            const data = await response.json();
            showAlert(data.error || 'Failed to create reminder', 'error');
        }
    } catch (error) {
        console.error('Save reminder error:', error);
        showAlert('Failed to create reminder', 'error');
    }
}

// Modal functions
function showModal() {
    document.getElementById('modal').classList.remove('hidden');
}

function closeModal() {
    document.getElementById('modal').classList.add('hidden');
}

// Alert function
function showAlert(message, type) {
    // Remove existing alerts
    const existingAlerts = document.querySelectorAll('.alert');
    existingAlerts.forEach(alert => alert.remove());
    
    const alert = document.createElement('div');
    alert.className = `alert alert-${type}`;
    alert.textContent = message;
    
    // Insert at the top of the current visible section
    const authSection = document.getElementById('auth-section');
    const chatSection = document.getElementById('chat-section');
    
    if (!authSection.classList.contains('hidden')) {
        authSection.insertBefore(alert, authSection.firstChild);
    } else if (!chatSection.classList.contains('hidden')) {
        const mainContent = document.querySelector('.main-content');
        mainContent.insertBefore(alert, mainContent.firstChild);
    }
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        alert.remove();
    }, 5000);
}
