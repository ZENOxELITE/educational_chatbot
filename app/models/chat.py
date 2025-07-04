from datetime import datetime
from app.utils.db import db_manager

class ChatSession:
    def __init__(self, id=None, user_id=None, session_start=None, 
                 session_end=None, total_messages=0):
        self.id = id
        self.user_id = user_id
        self.session_start = session_start or datetime.now()
        self.session_end = session_end
        self.total_messages = total_messages
    
    def save(self):
        """Save chat session to database"""
        if self.id:
            # Update existing session
            query = """
                UPDATE chat_sessions 
                SET session_end=%s, total_messages=%s 
                WHERE id=%s
            """
            params = (self.session_end, self.total_messages, self.id)
            db_manager.execute_update(query, params)
        else:
            # Create new session
            query = """
                INSERT INTO chat_sessions (user_id, session_start, total_messages)
                VALUES (%s, %s, %s)
            """
            params = (self.user_id, self.session_start, self.total_messages)
            self.id = db_manager.execute_insert(query, params)
        return self.id
    
    @staticmethod
    def find_by_id(session_id):
        """Find session by ID"""
        query = "SELECT * FROM chat_sessions WHERE id = %s"
        result = db_manager.execute_single_query(query, (session_id,))
        if result:
            return ChatSession(**result)
        return None
    
    @staticmethod
    def get_user_sessions(user_id, limit=10):
        """Get user's recent chat sessions"""
        query = """
            SELECT * FROM chat_sessions 
            WHERE user_id = %s 
            ORDER BY session_start DESC 
            LIMIT %s
        """
        results = db_manager.execute_query(query, (user_id, limit))
        return [ChatSession(**result) for result in results] if results else []
    
    def end_session(self):
        """End the chat session"""
        self.session_end = datetime.now()
        self.save()
    
    def increment_message_count(self):
        """Increment total message count"""
        self.total_messages += 1
        self.save()

class ChatHistory:
    def __init__(self, id=None, session_id=None, user_id=None, message=None, 
                 response=None, message_type='general', confidence_score=0.0, 
                 timestamp=None):
        self.id = id
        self.session_id = session_id
        self.user_id = user_id
        self.message = message
        self.response = response
        self.message_type = message_type
        self.confidence_score = confidence_score
        self.timestamp = timestamp or datetime.now()
    
    def save(self):
        """Save chat history to database"""
        query = """
            INSERT INTO chat_history (session_id, user_id, message, response, 
                                    message_type, confidence_score, timestamp)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        params = (self.session_id, self.user_id, self.message, self.response,
                 self.message_type, self.confidence_score, self.timestamp)
        self.id = db_manager.execute_insert(query, params)
        return self.id
    
    @staticmethod
    def get_session_history(session_id, limit=50):
        """Get chat history for a session"""
        query = """
            SELECT * FROM chat_history 
            WHERE session_id = %s 
            ORDER BY timestamp ASC 
            LIMIT %s
        """
        results = db_manager.execute_query(query, (session_id, limit))
        return [ChatHistory(**result) for result in results] if results else []
    
    @staticmethod
    def get_user_history(user_id, limit=100):
        """Get user's chat history"""
        query = """
            SELECT * FROM chat_history 
            WHERE user_id = %s 
            ORDER BY timestamp DESC 
            LIMIT %s
        """
        results = db_manager.execute_query(query, (user_id, limit))
        return [ChatHistory(**result) for result in results] if results else []
    
    @staticmethod
    def search_user_history(user_id, search_term, limit=20):
        """Search user's chat history"""
        query = """
            SELECT * FROM chat_history 
            WHERE user_id = %s AND (message LIKE %s OR response LIKE %s)
            ORDER BY timestamp DESC 
            LIMIT %s
        """
        search_pattern = f"%{search_term}%"
        results = db_manager.execute_query(query, (user_id, search_pattern, search_pattern, limit))
        return [ChatHistory(**result) for result in results] if results else []
    
    def to_dict(self):
        """Convert chat history to dictionary"""
        return {
            'id': self.id,
            'session_id': self.session_id,
            'user_id': self.user_id,
            'message': self.message,
            'response': self.response,
            'message_type': self.message_type,
            'confidence_score': float(self.confidence_score),
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }

class StudySchedule:
    def __init__(self, id=None, user_id=None, subject=None, topic=None,
                 scheduled_date=None, scheduled_time=None, duration_minutes=60,
                 status='pending', notes=None, created_at=None):
        self.id = id
        self.user_id = user_id
        self.subject = subject
        self.topic = topic
        self.scheduled_date = scheduled_date
        self.scheduled_time = scheduled_time
        self.duration_minutes = duration_minutes
        self.status = status
        self.notes = notes
        self.created_at = created_at or datetime.now()
    
    def save(self):
        """Save study schedule to database"""
        if self.id:
            # Update existing schedule
            query = """
                UPDATE study_schedules 
                SET subject=%s, topic=%s, scheduled_date=%s, scheduled_time=%s,
                    duration_minutes=%s, status=%s, notes=%s
                WHERE id=%s
            """
            params = (self.subject, self.topic, self.scheduled_date, self.scheduled_time,
                     self.duration_minutes, self.status, self.notes, self.id)
            db_manager.execute_update(query, params)
        else:
            # Create new schedule
            query = """
                INSERT INTO study_schedules (user_id, subject, topic, scheduled_date,
                                           scheduled_time, duration_minutes, status, notes)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            params = (self.user_id, self.subject, self.topic, self.scheduled_date,
                     self.scheduled_time, self.duration_minutes, self.status, self.notes)
            self.id = db_manager.execute_insert(query, params)
        return self.id
    
    @staticmethod
    def get_user_schedules(user_id, limit=20):
        """Get user's study schedules"""
        query = """
            SELECT * FROM study_schedules 
            WHERE user_id = %s 
            ORDER BY scheduled_date DESC, scheduled_time DESC 
            LIMIT %s
        """
        results = db_manager.execute_query(query, (user_id, limit))
        return [StudySchedule(**result) for result in results] if results else []
    
    @staticmethod
    def get_upcoming_schedules(user_id, limit=10):
        """Get user's upcoming study schedules"""
        query = """
            SELECT * FROM study_schedules 
            WHERE user_id = %s AND scheduled_date >= CURDATE() AND status = 'pending'
            ORDER BY scheduled_date ASC, scheduled_time ASC 
            LIMIT %s
        """
        results = db_manager.execute_query(query, (user_id, limit))
        return [StudySchedule(**result) for result in results] if results else []

class Reminder:
    def __init__(self, id=None, user_id=None, title=None, description=None,
                 reminder_date=None, reminder_time=None, is_completed=False,
                 created_at=None):
        self.id = id
        self.user_id = user_id
        self.title = title
        self.description = description
        self.reminder_date = reminder_date
        self.reminder_time = reminder_time
        self.is_completed = is_completed
        self.created_at = created_at or datetime.now()
    
    def save(self):
        """Save reminder to database"""
        if self.id:
            # Update existing reminder
            query = """
                UPDATE reminders 
                SET title=%s, description=%s, reminder_date=%s, reminder_time=%s,
                    is_completed=%s
                WHERE id=%s
            """
            params = (self.title, self.description, self.reminder_date, 
                     self.reminder_time, self.is_completed, self.id)
            db_manager.execute_update(query, params)
        else:
            # Create new reminder
            query = """
                INSERT INTO reminders (user_id, title, description, reminder_date,
                                     reminder_time, is_completed)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            params = (self.user_id, self.title, self.description, self.reminder_date,
                     self.reminder_time, self.is_completed)
            self.id = db_manager.execute_insert(query, params)
        return self.id
    
    @staticmethod
    def get_user_reminders(user_id, limit=20):
        """Get user's reminders"""
        query = """
            SELECT * FROM reminders 
            WHERE user_id = %s 
            ORDER BY reminder_date DESC, reminder_time DESC 
            LIMIT %s
        """
        results = db_manager.execute_query(query, (user_id, limit))
        return [Reminder(**result) for result in results] if results else []
    
    @staticmethod
    def get_pending_reminders(user_id, limit=10):
        """Get user's pending reminders"""
        query = """
            SELECT * FROM reminders 
            WHERE user_id = %s AND is_completed = FALSE AND reminder_date >= CURDATE()
            ORDER BY reminder_date ASC, reminder_time ASC 
            LIMIT %s
        """
        results = db_manager.execute_query(query, (user_id, limit))
        return [Reminder(**result) for result in results] if results else []
