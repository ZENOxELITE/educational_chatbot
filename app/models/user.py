import bcrypt
from datetime import datetime
from app.utils.db import db_manager

class User:
    def __init__(self, id=None, username=None, email=None, password_hash=None, 
                 first_name=None, last_name=None, grade_level=None, 
                 created_at=None, last_login=None, is_active=True):
        self.id = id
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.first_name = first_name
        self.last_name = last_name
        self.grade_level = grade_level
        self.created_at = created_at
        self.last_login = last_login
        self.is_active = is_active
    
    @staticmethod
    def hash_password(password):
        """Hash a password using bcrypt"""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    @staticmethod
    def verify_password(password, password_hash):
        """Verify a password against its hash"""
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
    
    def save(self):
        """Save user to database"""
        if self.id:
            # Update existing user
            query = """
                UPDATE users 
                SET username=%s, email=%s, first_name=%s, last_name=%s, 
                    grade_level=%s, is_active=%s 
                WHERE id=%s
            """
            params = (self.username, self.email, self.first_name, self.last_name,
                     self.grade_level, self.is_active, self.id)
            db_manager.execute_update(query, params)
        else:
            # Create new user
            query = """
                INSERT INTO users (username, email, password_hash, first_name, 
                                 last_name, grade_level, is_active)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            params = (self.username, self.email, self.password_hash, self.first_name,
                     self.last_name, self.grade_level, self.is_active)
            self.id = db_manager.execute_insert(query, params)
        return self.id
    
    @staticmethod
    def find_by_id(user_id):
        """Find user by ID"""
        query = "SELECT * FROM users WHERE id = %s AND is_active = TRUE"
        result = db_manager.execute_single_query(query, (user_id,))
        if result:
            return User(**result)
        return None
    
    @staticmethod
    def find_by_username(username):
        """Find user by username"""
        query = "SELECT * FROM users WHERE username = %s AND is_active = TRUE"
        result = db_manager.execute_single_query(query, (username,))
        if result:
            return User(**result)
        return None
    
    @staticmethod
    def find_by_email(email):
        """Find user by email"""
        query = "SELECT * FROM users WHERE email = %s AND is_active = TRUE"
        result = db_manager.execute_single_query(query, (email,))
        if result:
            return User(**result)
        return None
    
    @staticmethod
    def authenticate(username, password):
        """Authenticate user with username and password"""
        user = User.find_by_username(username)
        if user and User.verify_password(password, user.password_hash):
            # Update last login
            query = "UPDATE users SET last_login = %s WHERE id = %s"
            db_manager.execute_update(query, (datetime.now(), user.id))
            return user
        return None
    
    def update_last_login(self):
        """Update user's last login timestamp"""
        query = "UPDATE users SET last_login = %s WHERE id = %s"
        db_manager.execute_update(query, (datetime.now(), self.id))
    
    def get_full_name(self):
        """Get user's full name"""
        return f"{self.first_name} {self.last_name}"
    
    def to_dict(self):
        """Convert user object to dictionary"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'grade_level': self.grade_level,
            'created_at': self.created_at,
            'last_login': self.last_login,
            'is_active': self.is_active
        }
    
    # Flask-Login required methods
    def is_authenticated(self):
        return True
    
    def is_active_user(self):
        return self.is_active
    
    def is_anonymous(self):
        return False
    
    def get_id(self):
        return str(self.id)
