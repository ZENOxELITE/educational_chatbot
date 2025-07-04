from datetime import datetime
from app.utils.db import db_manager

class KnowledgeBase:
    def __init__(self, id=None, subject=None, topic=None, subtopic=None,
                 content=None, keywords=None, difficulty_level='beginner',
                 grade_level=None, created_at=None, updated_at=None, is_active=True):
        self.id = id
        self.subject = subject
        self.topic = topic
        self.subtopic = subtopic
        self.content = content
        self.keywords = keywords
        self.difficulty_level = difficulty_level
        self.grade_level = grade_level
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()
        self.is_active = is_active
    
    def save(self):
        """Save knowledge base entry to database"""
        if self.id:
            # Update existing entry
            query = """
                UPDATE knowledge_base 
                SET subject=%s, topic=%s, subtopic=%s, content=%s, keywords=%s,
                    difficulty_level=%s, grade_level=%s, updated_at=%s, is_active=%s
                WHERE id=%s
            """
            params = (self.subject, self.topic, self.subtopic, self.content, self.keywords,
                     self.difficulty_level, self.grade_level, datetime.now(), self.is_active, self.id)
            db_manager.execute_update(query, params)
        else:
            # Create new entry
            query = """
                INSERT INTO knowledge_base (subject, topic, subtopic, content, keywords,
                                          difficulty_level, grade_level, is_active)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            params = (self.subject, self.topic, self.subtopic, self.content, self.keywords,
                     self.difficulty_level, self.grade_level, self.is_active)
            self.id = db_manager.execute_insert(query, params)
        return self.id
    
    @staticmethod
    def find_by_id(kb_id):
        """Find knowledge base entry by ID"""
        query = "SELECT * FROM knowledge_base WHERE id = %s AND is_active = TRUE"
        result = db_manager.execute_single_query(query, (kb_id,))
        if result:
            return KnowledgeBase(**result)
        return None
    
    @staticmethod
    def search_by_keywords(keywords, limit=10):
        """Search knowledge base by keywords"""
        search_terms = keywords.lower().split()
        conditions = []
        params = []
        
        for term in search_terms:
            conditions.append("(LOWER(keywords) LIKE %s OR LOWER(content) LIKE %s OR LOWER(topic) LIKE %s)")
            search_pattern = f"%{term}%"
            params.extend([search_pattern, search_pattern, search_pattern])
        
        if not conditions:
            return []
        
        query = f"""
            SELECT * FROM knowledge_base 
            WHERE is_active = TRUE AND ({' OR '.join(conditions)})
            ORDER BY subject, topic
            LIMIT %s
        """
        params.append(limit)
        
        results = db_manager.execute_query(query, params)
        return [KnowledgeBase(**result) for result in results] if results else []
    
    @staticmethod
    def get_by_subject(subject, limit=20):
        """Get knowledge base entries by subject"""
        query = """
            SELECT * FROM knowledge_base 
            WHERE subject = %s AND is_active = TRUE
            ORDER BY topic, subtopic
            LIMIT %s
        """
        results = db_manager.execute_query(query, (subject, limit))
        return [KnowledgeBase(**result) for result in results] if results else []
    
    @staticmethod
    def get_by_topic(subject, topic, limit=10):
        """Get knowledge base entries by subject and topic"""
        query = """
            SELECT * FROM knowledge_base 
            WHERE subject = %s AND topic = %s AND is_active = TRUE
            ORDER BY subtopic
            LIMIT %s
        """
        results = db_manager.execute_query(query, (subject, topic, limit))
        return [KnowledgeBase(**result) for result in results] if results else []
    
    @staticmethod
    def get_all_subjects():
        """Get all unique subjects"""
        query = """
            SELECT DISTINCT subject FROM knowledge_base 
            WHERE is_active = TRUE 
            ORDER BY subject
        """
        results = db_manager.execute_query(query)
        return [result['subject'] for result in results] if results else []
    
    @staticmethod
    def get_topics_by_subject(subject):
        """Get all topics for a subject"""
        query = """
            SELECT DISTINCT topic FROM knowledge_base 
            WHERE subject = %s AND is_active = TRUE 
            ORDER BY topic
        """
        results = db_manager.execute_query(query, (subject,))
        return [result['topic'] for result in results] if results else []
    
    @staticmethod
    def search_content(search_term, limit=15):
        """Search knowledge base content"""
        query = """
            SELECT * FROM knowledge_base 
            WHERE is_active = TRUE AND (
                LOWER(content) LIKE %s OR 
                LOWER(topic) LIKE %s OR 
                LOWER(subtopic) LIKE %s OR 
                LOWER(keywords) LIKE %s
            )
            ORDER BY subject, topic
            LIMIT %s
        """
        search_pattern = f"%{search_term.lower()}%"
        params = [search_pattern] * 4 + [limit]
        
        results = db_manager.execute_query(query, params)
        return [KnowledgeBase(**result) for result in results] if results else []
    
    def to_dict(self):
        """Convert knowledge base entry to dictionary"""
        return {
            'id': self.id,
            'subject': self.subject,
            'topic': self.topic,
            'subtopic': self.subtopic,
            'content': self.content,
            'keywords': self.keywords,
            'difficulty_level': self.difficulty_level,
            'grade_level': self.grade_level,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'is_active': self.is_active
        }

class UserNote:
    def __init__(self, id=None, user_id=None, subject=None, topic=None,
                 note_content=None, created_at=None, updated_at=None):
        self.id = id
        self.user_id = user_id
        self.subject = subject
        self.topic = topic
        self.note_content = note_content
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()
    
    def save(self):
        """Save user note to database"""
        if self.id:
            # Update existing note
            query = """
                UPDATE user_notes 
                SET subject=%s, topic=%s, note_content=%s, updated_at=%s
                WHERE id=%s
            """
            params = (self.subject, self.topic, self.note_content, datetime.now(), self.id)
            db_manager.execute_update(query, params)
        else:
            # Create new note
            query = """
                INSERT INTO user_notes (user_id, subject, topic, note_content)
                VALUES (%s, %s, %s, %s)
            """
            params = (self.user_id, self.subject, self.topic, self.note_content)
            self.id = db_manager.execute_insert(query, params)
        return self.id
    
    @staticmethod
    def get_user_notes(user_id, limit=50):
        """Get user's notes"""
        query = """
            SELECT * FROM user_notes 
            WHERE user_id = %s 
            ORDER BY updated_at DESC 
            LIMIT %s
        """
        results = db_manager.execute_query(query, (user_id, limit))
        return [UserNote(**result) for result in results] if results else []
    
    @staticmethod
    def get_notes_by_subject(user_id, subject, limit=20):
        """Get user's notes by subject"""
        query = """
            SELECT * FROM user_notes 
            WHERE user_id = %s AND subject = %s 
            ORDER BY updated_at DESC 
            LIMIT %s
        """
        results = db_manager.execute_query(query, (user_id, subject, limit))
        return [UserNote(**result) for result in results] if results else []
    
    @staticmethod
    def search_user_notes(user_id, search_term, limit=20):
        """Search user's notes"""
        query = """
            SELECT * FROM user_notes 
            WHERE user_id = %s AND (
                LOWER(note_content) LIKE %s OR 
                LOWER(topic) LIKE %s OR 
                LOWER(subject) LIKE %s
            )
            ORDER BY updated_at DESC 
            LIMIT %s
        """
        search_pattern = f"%{search_term.lower()}%"
        params = [user_id] + [search_pattern] * 3 + [limit]
        
        results = db_manager.execute_query(query, params)
        return [UserNote(**result) for result in results] if results else []
    
    def to_dict(self):
        """Convert user note to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'subject': self.subject,
            'topic': self.topic,
            'note_content': self.note_content,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
