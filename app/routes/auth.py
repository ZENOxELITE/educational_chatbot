from flask import Blueprint, request, jsonify, session
from app.models.user import User
from functools import wraps
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create blueprint
auth_bp = Blueprint('auth', __name__)

def login_required(f):
    """Decorator to require login for routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['username', 'email', 'password', 'first_name', 'last_name']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Check if username exists
        if User.find_by_username(data['username']):
            return jsonify({'error': 'Username already exists'}), 400
        
        # Check if email exists
        if User.find_by_email(data['email']):
            return jsonify({'error': 'Email already exists'}), 400
        
        # Create new user
        user = User(
            username=data['username'],
            email=data['email'],
            password_hash=User.hash_password(data['password']),
            first_name=data['first_name'],
            last_name=data['last_name'],
            grade_level=data.get('grade_level')
        )
        
        user_id = user.save()
        if not user_id:
            return jsonify({'error': 'Failed to create user'}), 500
        
        return jsonify({
            'message': 'User registered successfully',
            'user': {
                'id': user_id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name
            }
        }), 201
        
    except Exception as e:
        logger.error(f"Registration error: {e}")
        return jsonify({'error': 'Registration failed'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """Login user"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if 'username' not in data or 'password' not in data:
            return jsonify({'error': 'Username and password required'}), 400
        
        # Authenticate user
        user = User.authenticate(data['username'], data['password'])
        if not user:
            return jsonify({'error': 'Invalid username or password'}), 401
        
        # Update last login
        user.update_last_login()
        
        # Set session
        session['user_id'] = user.id
        session['username'] = user.username
        
        return jsonify({
            'message': 'Login successful',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Login error: {e}")
        return jsonify({'error': 'Login failed'}), 500

@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    """Logout user"""
    try:
        # Clear session
        session.clear()
        return jsonify({'message': 'Logout successful'}), 200
        
    except Exception as e:
        logger.error(f"Logout error: {e}")
        return jsonify({'error': 'Logout failed'}), 500

@auth_bp.route('/profile', methods=['GET'])
@login_required
def get_profile():
    """Get user profile"""
    try:
        user = User.find_by_id(session['user_id'])
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f"Profile retrieval error: {e}")
        return jsonify({'error': 'Failed to retrieve profile'}), 500

@auth_bp.route('/profile', methods=['PUT'])
@login_required
def update_profile():
    """Update user profile"""
    try:
        data = request.get_json()
        user = User.find_by_id(session['user_id'])
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Update allowed fields
        allowed_fields = ['first_name', 'last_name', 'email', 'grade_level']
        for field in allowed_fields:
            if field in data:
                setattr(user, field, data[field])
        
        # Save changes
        if user.save():
            return jsonify({
                'message': 'Profile updated successfully',
                'user': user.to_dict()
            }), 200
        else:
            return jsonify({'error': 'Failed to update profile'}), 500
        
    except Exception as e:
        logger.error(f"Profile update error: {e}")
        return jsonify({'error': 'Failed to update profile'}), 500

@auth_bp.route('/change-password', methods=['POST'])
@login_required
def change_password():
    """Change user password"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if 'current_password' not in data or 'new_password' not in data:
            return jsonify({'error': 'Current and new password required'}), 400
        
        user = User.find_by_id(session['user_id'])
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Verify current password
        if not User.verify_password(data['current_password'], user.password_hash):
            return jsonify({'error': 'Current password is incorrect'}), 401
        
        # Update password
        user.password_hash = User.hash_password(data['new_password'])
        if user.save():
            return jsonify({'message': 'Password changed successfully'}), 200
        else:
            return jsonify({'error': 'Failed to change password'}), 500
        
    except Exception as e:
        logger.error(f"Password change error: {e}")
        return jsonify({'error': 'Failed to change password'}), 500

@auth_bp.route('/check-auth', methods=['GET'])
def check_auth():
    """Check if user is authenticated"""
    if 'user_id' in session:
        user = User.find_by_id(session['user_id'])
        if user:
            return jsonify({
                'authenticated': True,
                'user': user.to_dict()
            }), 200
    
    return jsonify({
        'authenticated': False
    }), 200
