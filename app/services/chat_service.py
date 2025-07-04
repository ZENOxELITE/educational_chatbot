import random
from datetime import datetime, timedelta
from app.models.knowledge_base import KnowledgeBase
from app.models.chat import ChatHistory, ChatSession, StudySchedule, Reminder
from app.services.nlp_service import nlp_service
from config import Config
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ChatService:
    def __init__(self):
        self.greeting_responses = [
            "Hello! I'm your educational assistant. How can I help you with your studies today?",
            "Hi there! Ready to learn something new? What subject interests you?",
            "Welcome! I'm here to help with your academic questions and study planning.",
            "Hello! Whether you need help with homework, study tips, or scheduling, I'm here for you!"
        ]
        
        self.goodbye_responses = [
            "Goodbye! Keep up the great work with your studies!",
            "See you later! Remember to stay curious and keep learning!",
            "Farewell! Don't forget to review your notes and stay organized!",
            "Bye! Wishing you success in all your academic endeavors!"
        ]
        
        self.fallback_responses = [
            "I'm not sure I understand that completely. Could you rephrase your question?",
            "That's an interesting question! Could you provide more details so I can help better?",
            "I'd love to help! Can you be more specific about what you're looking for?",
            "Let me try to help you with that. Could you clarify what subject or topic you're interested in?"
        ]
        
        self.study_tips = [
            "Try the Pomodoro Technique: Study for 25 minutes, then take a 5-minute break!",
            "Create a dedicated study space free from distractions.",
            "Use active recall - test yourself instead of just re-reading notes.",
            "Break large topics into smaller, manageable chunks.",
            "Teach someone else what you've learned - it reinforces your understanding!",
            "Use the Cornell note-taking method to organize your thoughts better.",
            "Review material within 24 hours to improve retention.",
            "Get enough sleep - your brain consolidates memories during rest!"
        ]
    
    def process_message(self, user_id, message, session_id=None):
        """Process user message and generate response"""
        try:
            # Analyze the message using NLP
            analysis = nlp_service.process_message(message)
            
            # Create or get chat session
            if not session_id:
                session = ChatSession(user_id=user_id)
                session_id = session.save()
            else:
                session = ChatSession.find_by_id(session_id)
                if not session:
                    session = ChatSession(user_id=user_id)
                    session_id = session.save()
            
            # Generate response based on intent
            response = self.generate_response(analysis, user_id)
            
            # Save chat history
            chat_history = ChatHistory(
                session_id=session_id,
                user_id=user_id,
                message=message,
                response=response,
                message_type=analysis['intent'],
                confidence_score=analysis['confidence']
            )
            chat_history.save()
            
            # Update session message count
            session.increment_message_count()
            
            return {
                'response': response,
                'session_id': session_id,
                'intent': analysis['intent'],
                'subject': analysis['subject'],
                'confidence': analysis['confidence']
            }
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return {
                'response': "I'm sorry, I encountered an error. Please try again.",
                'session_id': session_id,
                'intent': 'error',
                'subject': None,
                'confidence': 0.0
            }
    
    def generate_response(self, analysis, user_id):
        """Generate response based on message analysis"""
        intent = analysis['intent']
        subject = analysis['subject']
        keywords = analysis['keywords']
        
        if intent == 'greeting':
            return random.choice(self.greeting_responses)
        
        elif intent == 'goodbye':
            return random.choice(self.goodbye_responses)
        
        elif intent == 'question':
            return self.handle_question(keywords, subject, user_id)
        
        elif intent == 'study_tip':
            return self.handle_study_tip_request(subject, keywords)
        
        elif intent == 'reminder':
            return self.handle_reminder_request(analysis, user_id)
        
        elif intent == 'schedule':
            return self.handle_schedule_request(analysis, user_id)
        
        elif intent == 'note':
            return self.handle_note_request(analysis, user_id)
        
        else:
            return self.handle_general_query(keywords, subject, user_id)
    
    def handle_question(self, keywords, subject, user_id):
        """Handle educational questions"""
        if not keywords:
            return "What would you like to know? Please ask me a specific question about any subject!"
        
        # Search knowledge base
        knowledge_entries = KnowledgeBase.search_by_keywords(' '.join(keywords))
        
        if knowledge_entries:
            # Find the best match
            best_match = knowledge_entries[0]
            response = f"**{best_match.topic}**\n\n{best_match.content}"
            
            if len(knowledge_entries) > 1:
                response += f"\n\nI found {len(knowledge_entries)} related topics. Would you like to know more about any specific aspect?"
            
            return response
        
        # If no direct match, try subject-based search
        if subject:
            subject_entries = KnowledgeBase.get_by_subject(subject)
            if subject_entries:
                response = f"I found some information about {subject}:\n\n"
                for entry in subject_entries[:3]:  # Show top 3
                    response += f"• **{entry.topic}**: {entry.content[:100]}...\n\n"
                response += "Would you like me to explain any of these topics in detail?"
                return response
        
        return f"I don't have specific information about that topic yet. However, I can help you with study strategies or connect you with resources. What specific aspect would you like to explore?"
    
    def handle_study_tip_request(self, subject, keywords):
        """Handle study tip requests"""
        if subject:
            subject_tips = {
                'mathematics': [
                    "Practice problems daily - math requires consistent practice!",
                    "Work through problems step by step and show all your work.",
                    "Use visual aids like graphs and diagrams to understand concepts.",
                    "Form study groups to discuss different problem-solving approaches."
                ],
                'science': [
                    "Create concept maps to connect different scientific principles.",
                    "Conduct experiments or simulations to see theories in action.",
                    "Use mnemonics to remember scientific facts and formulas.",
                    "Relate scientific concepts to real-world examples."
                ],
                'history': [
                    "Create timelines to understand chronological relationships.",
                    "Use storytelling techniques to remember historical events.",
                    "Connect historical events to current events for better understanding.",
                    "Study primary sources to get firsthand perspectives."
                ],
                'english': [
                    "Read actively - take notes and ask questions while reading.",
                    "Practice writing regularly to improve your skills.",
                    "Analyze literary devices and their effects on meaning.",
                    "Discuss literature with others to gain different perspectives."
                ]
            }
            
            if subject in subject_tips:
                tip = random.choice(subject_tips[subject])
                return f"Here's a study tip for {subject}:\n\n{tip}\n\nWould you like more specific advice for any particular topic?"
        
        # General study tip
        tip = random.choice(self.study_tips)
        return f"Here's a helpful study tip:\n\n{tip}\n\nWould you like tips for a specific subject?"
    
    def handle_reminder_request(self, analysis, user_id):
        """Handle reminder creation requests"""
        message = analysis['original_message']
        
        # Extract date/time information
        datetime_info = nlp_service.extract_date_time(message)
        
        if datetime_info['dates'] or datetime_info['times']:
            return ("I can help you set up reminders! To create a reminder, please provide:\n"
                   "1. What you want to be reminded about\n"
                   "2. The date (e.g., 'tomorrow', '12/25/2024')\n"
                   "3. The time (e.g., '3:00 PM', 'morning')\n\n"
                   "For example: 'Remind me to study chemistry tomorrow at 2 PM'")
        
        return ("I'd be happy to help you set reminders for your studies! "
               "Please tell me what you want to be reminded about and when. "
               "For example: 'Remind me to review math notes tomorrow at 3 PM'")
    
    def handle_schedule_request(self, analysis, user_id):
        """Handle study schedule requests"""
        message = analysis['original_message']
        subject = analysis['subject']
        
        if 'create' in message.lower() or 'make' in message.lower():
            return ("I can help you create a study schedule! Please provide:\n"
                   "1. Subject you want to study\n"
                   "2. Topics you need to cover\n"
                   "3. Available time slots\n"
                   "4. Your goals or deadlines\n\n"
                   "For example: 'Schedule math study sessions for algebra and geometry, "
                   "I have 2 hours daily after 4 PM'")
        
        # Get user's upcoming schedules
        schedules = StudySchedule.get_upcoming_schedules(user_id, 5)
        
        if schedules:
            response = "Here are your upcoming study sessions:\n\n"
            for schedule in schedules:
                response += f"• **{schedule.subject}** - {schedule.topic}\n"
                response += f"  📅 {schedule.scheduled_date} at {schedule.scheduled_time}\n"
                response += f"  ⏱️ {schedule.duration_minutes} minutes\n\n"
            response += "Would you like to add more sessions or modify existing ones?"
        else:
            response = ("You don't have any scheduled study sessions yet. "
                       "Would you like me to help you create a study schedule?")
        
        return response
    
    def handle_note_request(self, analysis, user_id):
        """Handle note-related requests"""
        return ("I can help you with note-taking strategies! Here are some effective methods:\n\n"
               "📝 **Cornell Method**: Divide your page into notes, cues, and summary sections\n"
               "📝 **Mind Mapping**: Create visual connections between concepts\n"
               "📝 **Outline Method**: Use hierarchical structure with main points and sub-points\n"
               "📝 **Charting Method**: Use tables for comparing information\n\n"
               "Would you like me to explain any of these methods in detail?")
    
    def handle_general_query(self, keywords, subject, user_id):
        """Handle general queries"""
        if keywords:
            # Try to find relevant content
            knowledge_entries = KnowledgeBase.search_content(' '.join(keywords))
            
            if knowledge_entries:
                entry = knowledge_entries[0]
                return f"I found this information that might help:\n\n**{entry.topic}**\n{entry.content}\n\nWould you like to know more about this topic?"
        
        # Fallback response
        response = random.choice(self.fallback_responses)
        
        # Add helpful suggestions
        subjects = KnowledgeBase.get_all_subjects()
        if subjects:
            response += f"\n\nI can help you with: {', '.join(subjects[:5])}"
            if len(subjects) > 5:
                response += " and more!"
        
        return response
    
    def get_personalized_suggestions(self, user_id):
        """Get personalized study suggestions for user"""
        # Get user's recent chat history
        recent_chats = ChatHistory.get_user_history(user_id, 10)
        
        if not recent_chats:
            return "Start by asking me questions about any subject you're studying!"
        
        # Analyze user's interests
        subjects_mentioned = []
        for chat in recent_chats:
            analysis = nlp_service.process_message(chat.message)
            if analysis['subject']:
                subjects_mentioned.append(analysis['subject'])
        
        if subjects_mentioned:
            most_common_subject = max(set(subjects_mentioned), key=subjects_mentioned.count)
            return f"Based on our conversations, you seem interested in {most_common_subject}. Would you like some advanced topics or practice problems in this area?"
        
        return "Feel free to ask me about any subject - I'm here to help with your studies!"

# Global chat service instance
chat_service = ChatService()
