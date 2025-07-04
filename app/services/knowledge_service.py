from app.models.knowledge_base import KnowledgeBase, UserNote
from app.models.chat import StudySchedule, Reminder
from app.services.nlp_service import nlp_service
from datetime import datetime, timedelta
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class KnowledgeService:
    def __init__(self):
        self.min_confidence_score = 0.7
    
    def search_knowledge_base(self, query, subject=None, limit=10):
        """Search knowledge base for relevant content"""
        try:
            # Analyze query using NLP
            analysis = nlp_service.process_message(query)
            keywords = analysis['keywords']
            
            if not keywords:
                return []
            
            # Search by keywords
            entries = KnowledgeBase.search_by_keywords(' '.join(keywords), limit)
            
            # If subject is specified, filter results
            if subject and entries:
                entries = [entry for entry in entries if entry.subject.lower() == subject.lower()]
            
            return entries
            
        except Exception as e:
            logger.error(f"Error searching knowledge base: {e}")
            return []
    
    def get_study_materials(self, subject, topic=None, difficulty_level=None):
        """Get study materials for a subject"""
        try:
            if topic:
                entries = KnowledgeBase.get_by_topic(subject, topic)
            else:
                entries = KnowledgeBase.get_by_subject(subject)
            
            if difficulty_level and entries:
                entries = [entry for entry in entries if entry.difficulty_level == difficulty_level]
            
            return entries
            
        except Exception as e:
            logger.error(f"Error getting study materials: {e}")
            return []
    
    def save_user_note(self, user_id, subject, topic, content):
        """Save a user's note"""
        try:
            note = UserNote(
                user_id=user_id,
                subject=subject,
                topic=topic,
                note_content=content
            )
            note_id = note.save()
            return note_id is not None
            
        except Exception as e:
            logger.error(f"Error saving user note: {e}")
            return False
    
    def get_user_notes(self, user_id, subject=None):
        """Get user's notes"""
        try:
            if subject:
                return UserNote.get_notes_by_subject(user_id, subject)
            return UserNote.get_user_notes(user_id)
            
        except Exception as e:
            logger.error(f"Error getting user notes: {e}")
            return []
    
    def search_user_notes(self, user_id, search_term):
        """Search user's notes"""
        try:
            return UserNote.search_user_notes(user_id, search_term)
        except Exception as e:
            logger.error(f"Error searching user notes: {e}")
            return []
    
    def create_study_schedule(self, user_id, subject, topic, scheduled_date,
                            scheduled_time, duration_minutes=60, notes=None):
        """Create a study schedule"""
        try:
            schedule = StudySchedule(
                user_id=user_id,
                subject=subject,
                topic=topic,
                scheduled_date=scheduled_date,
                scheduled_time=scheduled_time,
                duration_minutes=duration_minutes,
                notes=notes
            )
            schedule_id = schedule.save()
            return schedule_id is not None
            
        except Exception as e:
            logger.error(f"Error creating study schedule: {e}")
            return False
    
    def get_study_schedules(self, user_id, upcoming_only=True):
        """Get user's study schedules"""
        try:
            if upcoming_only:
                return StudySchedule.get_upcoming_schedules(user_id)
            return StudySchedule.get_user_schedules(user_id)
            
        except Exception as e:
            logger.error(f"Error getting study schedules: {e}")
            return []
    
    def create_reminder(self, user_id, title, description, reminder_date, reminder_time):
        """Create a reminder"""
        try:
            reminder = Reminder(
                user_id=user_id,
                title=title,
                description=description,
                reminder_date=reminder_date,
                reminder_time=reminder_time
            )
            reminder_id = reminder.save()
            return reminder_id is not None
            
        except Exception as e:
            logger.error(f"Error creating reminder: {e}")
            return False
    
    def get_reminders(self, user_id, pending_only=True):
        """Get user's reminders"""
        try:
            if pending_only:
                return Reminder.get_pending_reminders(user_id)
            return Reminder.get_user_reminders(user_id)
            
        except Exception as e:
            logger.error(f"Error getting reminders: {e}")
            return []
    
    def get_subject_overview(self, subject):
        """Get overview of a subject"""
        try:
            entries = KnowledgeBase.get_by_subject(subject)
            if not entries:
                return None
            
            topics = {}
            for entry in entries:
                if entry.topic not in topics:
                    topics[entry.topic] = []
                if entry.subtopic:
                    topics[entry.topic].append(entry.subtopic)
            
            return {
                'subject': subject,
                'topics': topics,
                'total_entries': len(entries)
            }
            
        except Exception as e:
            logger.error(f"Error getting subject overview: {e}")
            return None
    
    def get_study_suggestions(self, user_id):
        """Get personalized study suggestions"""
        try:
            # Get user's recent schedules
            schedules = StudySchedule.get_user_schedules(user_id, 5)
            subjects_studied = {schedule.subject for schedule in schedules}
            
            suggestions = []
            for subject in subjects_studied:
                # Get related topics
                entries = KnowledgeBase.get_by_subject(subject, 3)
                if entries:
                    suggestions.append({
                        'subject': subject,
                        'topics': [entry.topic for entry in entries],
                        'type': 'related_topics'
                    })
            
            # Add study tips
            entries = KnowledgeBase.search_by_keywords('study tips', 2)
            if entries:
                suggestions.append({
                    'subject': 'Study Tips',
                    'content': [entry.content for entry in entries],
                    'type': 'tips'
                })
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Error getting study suggestions: {e}")
            return []
    
    def get_learning_path(self, subject, current_level='beginner'):
        """Get recommended learning path for a subject"""
        try:
            entries = KnowledgeBase.get_by_subject(subject)
            if not entries:
                return None
            
            # Group entries by difficulty level
            levels = {
                'beginner': [],
                'intermediate': [],
                'advanced': []
            }
            
            for entry in entries:
                if entry.difficulty_level in levels:
                    levels[entry.difficulty_level].append({
                        'topic': entry.topic,
                        'subtopic': entry.subtopic,
                        'description': entry.content[:100] + '...'
                    })
            
            # Determine starting point based on current level
            path = []
            if current_level == 'beginner':
                path.extend(levels['beginner'])
                path.extend(levels['intermediate'])
                path.extend(levels['advanced'])
            elif current_level == 'intermediate':
                path.extend(levels['intermediate'])
                path.extend(levels['advanced'])
            else:
                path.extend(levels['advanced'])
            
            return {
                'subject': subject,
                'current_level': current_level,
                'path': path
            }
            
        except Exception as e:
            logger.error(f"Error getting learning path: {e}")
            return None

# Global knowledge service instance
knowledge_service = KnowledgeService()
