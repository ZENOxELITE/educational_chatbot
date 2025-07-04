-- Educational Chatbot Database Setup
-- Run this script in your MySQL database (via XAMPP phpMyAdmin or MySQL command line)

CREATE DATABASE IF NOT EXISTS educational_chatbot;
USE educational_chatbot;

-- Users table for authentication
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    grade_level VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP NULL,
    is_active BOOLEAN DEFAULT TRUE
);

-- Chat sessions table
CREATE TABLE IF NOT EXISTS chat_sessions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    session_start TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    session_end TIMESTAMP NULL,
    total_messages INT DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Chat history table
CREATE TABLE IF NOT EXISTS chat_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    session_id INT NOT NULL,
    user_id INT NOT NULL,
    message TEXT NOT NULL,
    response TEXT NOT NULL,
    message_type ENUM('question', 'study_tip', 'reminder', 'general') DEFAULT 'general',
    confidence_score DECIMAL(3,2) DEFAULT 0.00,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES chat_sessions(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Knowledge base table for educational content
CREATE TABLE IF NOT EXISTS knowledge_base (
    id INT AUTO_INCREMENT PRIMARY KEY,
    subject VARCHAR(50) NOT NULL,
    topic VARCHAR(100) NOT NULL,
    subtopic VARCHAR(100),
    content TEXT NOT NULL,
    keywords TEXT,
    difficulty_level ENUM('beginner', 'intermediate', 'advanced') DEFAULT 'beginner',
    grade_level VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- Study schedules table
CREATE TABLE IF NOT EXISTS study_schedules (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    subject VARCHAR(50) NOT NULL,
    topic VARCHAR(100) NOT NULL,
    scheduled_date DATE NOT NULL,
    scheduled_time TIME NOT NULL,
    duration_minutes INT DEFAULT 60,
    status ENUM('pending', 'completed', 'missed') DEFAULT 'pending',
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- User notes table
CREATE TABLE IF NOT EXISTS user_notes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    subject VARCHAR(50) NOT NULL,
    topic VARCHAR(100) NOT NULL,
    note_content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Reminders table
CREATE TABLE IF NOT EXISTS reminders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    title VARCHAR(100) NOT NULL,
    description TEXT,
    reminder_date DATE NOT NULL,
    reminder_time TIME NOT NULL,
    is_completed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Insert sample knowledge base data
INSERT INTO knowledge_base (subject, topic, subtopic, content, keywords, difficulty_level, grade_level) VALUES
('Mathematics', 'Algebra', 'Linear Equations', 'A linear equation is an equation that makes a straight line when graphed. It has the form y = mx + b, where m is the slope and b is the y-intercept.', 'linear equation, slope, y-intercept, graph', 'beginner', '9-12'),
('Mathematics', 'Geometry', 'Pythagorean Theorem', 'The Pythagorean theorem states that in a right triangle, the square of the hypotenuse equals the sum of squares of the other two sides: a² + b² = c²', 'pythagorean theorem, right triangle, hypotenuse', 'intermediate', '9-12'),
('Science', 'Physics', 'Newton''s Laws', 'Newton''s First Law: An object at rest stays at rest, and an object in motion stays in motion unless acted upon by an external force.', 'newton laws, motion, force, inertia', 'intermediate', '9-12'),
('Science', 'Chemistry', 'Periodic Table', 'The periodic table organizes elements by atomic number. Elements in the same group have similar properties.', 'periodic table, elements, atomic number, groups', 'beginner', '9-12'),
('History', 'World History', 'World War II', 'World War II (1939-1945) was a global conflict involving most nations. It ended with the defeat of the Axis powers.', 'world war 2, global conflict, axis powers', 'intermediate', '9-12'),
('English', 'Literature', 'Shakespeare', 'William Shakespeare was an English playwright and poet, widely regarded as the greatest writer in the English language.', 'shakespeare, playwright, literature, english', 'intermediate', '9-12');

-- Insert sample study tips
INSERT INTO knowledge_base (subject, topic, subtopic, content, keywords, difficulty_level, grade_level) VALUES
('Study Tips', 'Time Management', 'Pomodoro Technique', 'The Pomodoro Technique involves studying for 25 minutes, then taking a 5-minute break. After 4 cycles, take a longer 15-30 minute break.', 'pomodoro, time management, study technique, breaks', 'beginner', 'all'),
('Study Tips', 'Memory', 'Active Recall', 'Active recall involves testing yourself on material rather than just re-reading. This strengthens memory and improves retention.', 'active recall, memory, testing, retention', 'beginner', 'all'),
('Study Tips', 'Note Taking', 'Cornell Method', 'The Cornell note-taking method divides your page into three sections: notes, cues, and summary. This helps organize and review information effectively.', 'cornell method, note taking, organization, review', 'beginner', 'all');

-- Create indexes for better performance
CREATE INDEX idx_chat_history_user_id ON chat_history(user_id);
CREATE INDEX idx_chat_history_timestamp ON chat_history(timestamp);
CREATE INDEX idx_knowledge_base_subject ON knowledge_base(subject);
CREATE INDEX idx_knowledge_base_keywords ON knowledge_base(keywords);
CREATE INDEX idx_study_schedules_user_date ON study_schedules(user_id, scheduled_date);
CREATE INDEX idx_reminders_user_date ON reminders(user_id, reminder_date);
