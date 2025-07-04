from flask import Blueprint, request, jsonify, session
from app.routes.auth import login_required
from app.services.chat_service import chat_service
from app.services.knowledge_service import knowledge_service
from app.models.chat import ChatHistory, ChatSession, StudySchedule, Reminder
from app.models.knowledge_base import KnowledgeBase, UserNote
from datetime import datetime, date, time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create blueprint
chat_bp = Blueprint('chat', __name__)

@chat_bp.route('/message', methods=['POST'])
@login_required
def send_message():
    """Send a message to the chatbot"""
    try:
        data = request.get_json()
        
        if 'message' not in data:
            return jsonify({'error': 'Message is required'}), 400
        
        user_id = session['user_id']
        message = data['message'].strip()
        session_id = data.get('session_id')
        
        if not message:
            return jsonify({'error': 'Message cannot be empty'}), 400
        
        # Process message
        result = chat_service.process_message(user_id, message, session_id)
        
        return jsonify({
            'response': result['response'],
            'session_id': result['session_id'],
            'intent': result['intent'],
            'subject': result['subject'],
            'confidence': result['confidence'],
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Message processing error: {e}")
        return jsonify({'error': 'Failed to process message'}), 500

@chat_bp.route('/history', methods=['GET'])
@login_required
def get_chat_history():
    """Get user's chat history"""
    try:
        user_id = session['user_id']
        session_id = request.args.get('session_id')
        limit = int(request.args.get('limit', 50))
        
        if session_id:
            history = ChatHistory.get_session_history(session_id, limit)
        else:
            history = ChatHistory.get_user_history(user_id, limit)
        
        return jsonify({
            'history': [chat.to_dict() for chat in history]
        }), 200
        
    except Exception as e:
        logger.error(f"Chat history retrieval error: {e}")
        return jsonify({'error': 'Failed to retrieve chat history'}), 500

@chat_bp.route('/sessions', methods=['GET'])
@login_required
def get_chat_sessions():
    """Get user's chat sessions"""
    try:
        user_id = session['user_id']
        limit = int(request.args.get('limit', 10))
        
        sessions = ChatSession.get_user_sessions(user_id, limit)
        
        return jsonify({
            'sessions': [{
                'id': s.id,
                'session_start': s.session_start.isoformat() if s.session_start else None,
                'session_end': s.session_end.isoformat() if s.session_end else None,
                'total_messages': s.total_messages
            } for s in sessions]
        }), 200
        
    except Exception as e:
        logger.error(f"Chat sessions retrieval error: {e}")
        return jsonify({'error': 'Failed to retrieve chat sessions'}), 500

@chat_bp.route('/search', methods=['GET'])
@login_required
def search_chat_history():
    """Search user's chat history"""
    try:
        user_id = session['user_id']
        search_term = request.args.get('q', '').strip()
        limit = int(request.args.get('limit', 20))
        
        if not search_term:
            return jsonify({'error': 'Search term is required'}), 400
        
        history = ChatHistory.search_user_history(user_id, search_term, limit)
        
        return jsonify({
            'results': [chat.to_dict() for chat in history],
            'search_term': search_term
        }), 200
        
    except Exception as e:
        logger.error(f"Chat history search error: {e}")
        return jsonify({'error': 'Failed to search chat history'}), 500

@chat_bp.route('/knowledge/search', methods=['GET'])
@login_required
def search_knowledge():
    """Search knowledge base"""
    try:
        query = request.args.get('q', '').strip()
        subject = request.args.get('subject')
        limit = int(request.args.get('limit', 10))
        
        if not query:
            return jsonify({'error': 'Search query is required'}), 400
        
        entries = knowledge_service.search_knowledge_base(query, subject, limit)
        
        return jsonify({
            'results': [entry.to_dict() for entry in entries],
            'query': query,
            'subject': subject
        }), 200
        
    except Exception as e:
        logger.error(f"Knowledge search error: {e}")
        return jsonify({'error': 'Failed to search knowledge base'}), 500

@chat_bp.route('/subjects', methods=['GET'])
@login_required
def get_subjects():
    """Get all available subjects"""
    try:
        subjects = KnowledgeBase.get_all_subjects()
        return jsonify({'subjects': subjects}), 200
        
    except Exception as e:
        logger.error(f"Subjects retrieval error: {e}")
        return jsonify({'error': 'Failed to retrieve subjects'}), 500

@chat_bp.route('/subjects/<subject>/topics', methods=['GET'])
@login_required
def get_subject_topics(subject):
    """Get topics for a subject"""
    try:
        topics = KnowledgeBase.get_topics_by_subject(subject)
        return jsonify({
            'subject': subject,
            'topics': topics
        }), 200
        
    except Exception as e:
        logger.error(f"Topics retrieval error: {e}")
        return jsonify({'error': 'Failed to retrieve topics'}), 500

@chat_bp.route('/subjects/<subject>/overview', methods=['GET'])
@login_required
def get_subject_overview(subject):
    """Get overview of a subject"""
    try:
        overview = knowledge_service.get_subject_overview(subject)
        if not overview:
            return jsonify({'error': 'Subject not found'}), 404
        
        return jsonify(overview), 200
        
    except Exception as e:
        logger.error(f"Subject overview error: {e}")
        return jsonify({'error': 'Failed to retrieve subject overview'}), 500

@chat_bp.route('/notes', methods=['GET'])
@login_required
def get_notes():
    """Get user's notes"""
    try:
        user_id = session['user_id']
        subject = request.args.get('subject')
        
        notes = knowledge_service.get_user_notes(user_id, subject)
        
        return jsonify({
            'notes': [note.to_dict() for note in notes],
            'subject': subject
        }), 200
        
    except Exception as e:
        logger.error(f"Notes retrieval error: {e}")
        return jsonify({'error': 'Failed to retrieve notes'}), 500

@chat_bp.route('/notes', methods=['POST'])
@login_required
def create_note():
    """Create a new note"""
    try:
        data = request.get_json()
        user_id = session['user_id']
        
        required_fields = ['subject', 'topic', 'content']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        success = knowledge_service.save_user_note(
            user_id=user_id,
            subject=data['subject'],
            topic=data['topic'],
            content=data['content']
        )
        
        if success:
            return jsonify({'message': 'Note created successfully'}), 201
        else:
            return jsonify({'error': 'Failed to create note'}), 500
        
    except Exception as e:
        logger.error(f"Note creation error: {e}")
        return jsonify({'error': 'Failed to create note'}), 500

@chat_bp.route('/notes/search', methods=['GET'])
@login_required
def search_notes():
    """Search user's notes"""
    try:
        user_id = session['user_id']
        search_term = request.args.get('q', '').strip()
        
        if not search_term:
            return jsonify({'error': 'Search term is required'}), 400
        
        notes = knowledge_service.search_user_notes(user_id, search_term)
        
        return jsonify({
            'results': [note.to_dict() for note in notes],
            'search_term': search_term
        }), 200
        
    except Exception as e:
        logger.error(f"Notes search error: {e}")
        return jsonify({'error': 'Failed to search notes'}), 500

@chat_bp.route('/schedule', methods=['GET'])
@login_required
def get_schedule():
    """Get user's study schedule"""
    try:
        user_id = session['user_id']
        upcoming_only = request.args.get('upcoming', 'true').lower() == 'true'
        
        schedules = knowledge_service.get_study_schedules(user_id, upcoming_only)
        
        return jsonify({
            'schedules': [{
                'id': s.id,
                'subject': s.subject,
                'topic': s.topic,
                'scheduled_date': s.scheduled_date.isoformat() if s.scheduled_date else None,
                'scheduled_time': s.scheduled_time.strftime('%H:%M') if s.scheduled_time else None,
                'duration_minutes': s.duration_minutes,
                'status': s.status,
                'notes': s.notes
            } for s in schedules]
        }), 200
        
    except Exception as e:
        logger.error(f"Schedule retrieval error: {e}")
        return jsonify({'error': 'Failed to retrieve schedule'}), 500

@chat_bp.route('/schedule', methods=['POST'])
@login_required
def create_schedule():
    """Create a study schedule"""
    try:
        data = request.get_json()
        user_id = session['user_id']
        
        required_fields = ['subject', 'topic', 'scheduled_date', 'scheduled_time']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Parse date and time
        scheduled_date = datetime.strptime(data['scheduled_date'], '%Y-%m-%d').date()
        scheduled_time = datetime.strptime(data['scheduled_time'], '%H:%M').time()
        
        success = knowledge_service.create_study_schedule(
            user_id=user_id,
            subject=data['subject'],
            topic=data['topic'],
            scheduled_date=scheduled_date,
            scheduled_time=scheduled_time,
            duration_minutes=data.get('duration_minutes', 60),
            notes=data.get('notes')
        )
        
        if success:
            return jsonify({'message': 'Study schedule created successfully'}), 201
        else:
            return jsonify({'error': 'Failed to create study schedule'}), 500
        
    except ValueError as e:
        return jsonify({'error': 'Invalid date or time format'}), 400
    except Exception as e:
        logger.error(f"Schedule creation error: {e}")
        return jsonify({'error': 'Failed to create study schedule'}), 500

@chat_bp.route('/reminders', methods=['GET'])
@login_required
def get_reminders():
    """Get user's reminders"""
    try:
        user_id = session['user_id']
        pending_only = request.args.get('pending', 'true').lower() == 'true'
        
        reminders = knowledge_service.get_reminders(user_id, pending_only)
        
        return jsonify({
            'reminders': [{
                'id': r.id,
                'title': r.title,
                'description': r.description,
                'reminder_date': r.reminder_date.isoformat() if r.reminder_date else None,
                'reminder_time': r.reminder_time.strftime('%H:%M') if r.reminder_time else None,
                'is_completed': r.is_completed
            } for r in reminders]
        }), 200
        
    except Exception as e:
        logger.error(f"Reminders retrieval error: {e}")
        return jsonify({'error': 'Failed to retrieve reminders'}), 500

@chat_bp.route('/reminders', methods=['POST'])
@login_required
def create_reminder():
    """Create a reminder"""
    try:
        data = request.get_json()
        user_id = session['user_id']
        
        required_fields = ['title', 'reminder_date', 'reminder_time']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Parse date and time
        reminder_date = datetime.strptime(data['reminder_date'], '%Y-%m-%d').date()
        reminder_time = datetime.strptime(data['reminder_time'], '%H:%M').time()
        
        success = knowledge_service.create_reminder(
            user_id=user_id,
            title=data['title'],
            description=data.get('description'),
            reminder_date=reminder_date,
            reminder_time=reminder_time
        )
        
        if success:
            return jsonify({'message': 'Reminder created successfully'}), 201
        else:
            return jsonify({'error': 'Failed to create reminder'}), 500
        
    except ValueError as e:
        return jsonify({'error': 'Invalid date or time format'}), 400
    except Exception as e:
        logger.error(f"Reminder creation error: {e}")
        return jsonify({'error': 'Failed to create reminder'}), 500

@chat_bp.route('/suggestions', methods=['GET'])
@login_required
def get_suggestions():
    """Get personalized study suggestions"""
    try:
        user_id = session['user_id']
        suggestions = knowledge_service.get_study_suggestions(user_id)
        
        return jsonify({'suggestions': suggestions}), 200
        
    except Exception as e:
        logger.error(f"Suggestions retrieval error: {e}")
        return jsonify({'error': 'Failed to retrieve suggestions'}), 500

@chat_bp.route('/learning-path/<subject>', methods=['GET'])
@login_required
def get_learning_path(subject):
    """Get learning path for a subject"""
    try:
        current_level = request.args.get('level', 'beginner')
        path = knowledge_service.get_learning_path(subject, current_level)
        
        if not path:
            return jsonify({'error': 'Subject not found'}), 404
        
        return jsonify(path), 200
        
    except Exception as e:
        logger.error(f"Learning path error: {e}")
        return jsonify({'error': 'Failed to retrieve learning path'}), 500
