import spacy
import re
from datetime import datetime, timedelta
from config import Config
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NLPService:
    def __init__(self):
        self.nlp = None
        self.load_model()
        
        # Define intent patterns
        self.intent_patterns = {
            'question': [
                r'\b(what|how|why|when|where|who|which|explain|tell me about)\b',
                r'\?',
                r'\b(can you|could you|would you)\b'
            ],
            'study_tip': [
                r'\b(study|learn|memorize|remember|tips|advice|help)\b',
                r'\b(how to study|study better|improve|focus)\b'
            ],
            'reminder': [
                r'\b(remind|reminder|schedule|appointment|deadline)\b',
                r'\b(set reminder|add reminder|create reminder)\b'
            ],
            'schedule': [
                r'\b(schedule|plan|timetable|calendar|organize)\b',
                r'\b(study plan|study schedule|time management)\b'
            ],
            'note': [
                r'\b(note|notes|write down|save|record)\b',
                r'\b(take notes|make notes|add note)\b'
            ],
            'greeting': [
                r'\b(hello|hi|hey|good morning|good afternoon|good evening)\b',
                r'\b(how are you|what\'s up)\b'
            ],
            'goodbye': [
                r'\b(bye|goodbye|see you|farewell|exit|quit)\b',
                r'\b(thank you|thanks|that\'s all)\b'
            ]
        }
        
        # Subject keywords
        self.subject_keywords = {
            'mathematics': ['math', 'mathematics', 'algebra', 'geometry', 'calculus', 'trigonometry', 'statistics'],
            'science': ['science', 'physics', 'chemistry', 'biology', 'astronomy', 'geology'],
            'history': ['history', 'historical', 'ancient', 'medieval', 'modern', 'war', 'civilization'],
            'english': ['english', 'literature', 'grammar', 'writing', 'reading', 'poetry', 'shakespeare'],
            'computer science': ['programming', 'coding', 'computer', 'software', 'algorithm', 'data structure'],
            'study tips': ['study', 'learning', 'memory', 'focus', 'concentration', 'time management']
        }
    
    def load_model(self):
        """Load spaCy model"""
        try:
            self.nlp = spacy.load(Config.SPACY_MODEL)
            logger.info("spaCy model loaded successfully")
        except OSError:
            logger.warning("spaCy model not found. Using basic NLP processing.")
            self.nlp = None
    
    def process_message(self, message):
        """Process user message and extract information"""
        if not message:
            return {
                'intent': 'unknown',
                'subject': None,
                'keywords': [],
                'entities': [],
                'confidence': 0.0
            }
        
        message_lower = message.lower().strip()
        
        # Extract intent
        intent = self.extract_intent(message_lower)
        
        # Extract subject
        subject = self.extract_subject(message_lower)
        
        # Extract keywords
        keywords = self.extract_keywords(message_lower)
        
        # Extract entities using spaCy if available
        entities = self.extract_entities(message) if self.nlp else []
        
        # Calculate confidence score
        confidence = self.calculate_confidence(intent, subject, keywords)
        
        return {
            'intent': intent,
            'subject': subject,
            'keywords': keywords,
            'entities': entities,
            'confidence': confidence,
            'original_message': message
        }
    
    def extract_intent(self, message):
        """Extract intent from message"""
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, message, re.IGNORECASE):
                    return intent
        return 'general'
    
    def extract_subject(self, message):
        """Extract subject from message"""
        for subject, keywords in self.subject_keywords.items():
            for keyword in keywords:
                if keyword in message:
                    return subject
        return None
    
    def extract_keywords(self, message):
        """Extract important keywords from message"""
        if not self.nlp:
            # Basic keyword extraction without spaCy
            words = re.findall(r'\b\w+\b', message.lower())
            # Filter out common stop words
            stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those'}
            keywords = [word for word in words if word not in stop_words and len(word) > 2]
            return keywords[:10]  # Return top 10 keywords
        
        # Advanced keyword extraction with spaCy
        doc = self.nlp(message)
        keywords = []
        
        for token in doc:
            if (token.pos_ in ['NOUN', 'ADJ', 'VERB'] and 
                not token.is_stop and 
                not token.is_punct and 
                len(token.text) > 2):
                keywords.append(token.lemma_.lower())
        
        return list(set(keywords))[:10]  # Return unique keywords, max 10
    
    def extract_entities(self, message):
        """Extract named entities from message"""
        if not self.nlp:
            return []
        
        doc = self.nlp(message)
        entities = []
        
        for ent in doc.ents:
            entities.append({
                'text': ent.text,
                'label': ent.label_,
                'description': spacy.explain(ent.label_)
            })
        
        return entities
    
    def calculate_confidence(self, intent, subject, keywords):
        """Calculate confidence score for the analysis"""
        confidence = 0.0
        
        # Base confidence for intent detection
        if intent != 'unknown':
            confidence += 0.3
        
        # Additional confidence for subject detection
        if subject:
            confidence += 0.3
        
        # Additional confidence for keywords
        if keywords:
            confidence += min(len(keywords) * 0.05, 0.4)
        
        return min(confidence, 1.0)
    
    def extract_date_time(self, message):
        """Extract date and time information from message"""
        date_patterns = [
            r'\b(today|tomorrow|yesterday)\b',
            r'\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\b',
            r'\b(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b',
            r'\b(next week|this week|next month)\b'
        ]
        
        time_patterns = [
            r'\b(\d{1,2}:\d{2})\s*(am|pm)?\b',
            r'\b(\d{1,2})\s*(am|pm)\b',
            r'\b(morning|afternoon|evening|night)\b'
        ]
        
        dates = []
        times = []
        
        for pattern in date_patterns:
            matches = re.findall(pattern, message, re.IGNORECASE)
            dates.extend(matches)
        
        for pattern in time_patterns:
            matches = re.findall(pattern, message, re.IGNORECASE)
            times.extend(matches)
        
        return {
            'dates': dates,
            'times': times
        }
    
    def generate_response_keywords(self, user_keywords, subject=None):
        """Generate keywords for response matching"""
        response_keywords = user_keywords.copy()
        
        if subject:
            response_keywords.extend(self.subject_keywords.get(subject, []))
        
        return list(set(response_keywords))
    
    def similarity_score(self, text1, text2):
        """Calculate similarity between two texts"""
        if not self.nlp:
            # Basic similarity using common words
            words1 = set(text1.lower().split())
            words2 = set(text2.lower().split())
            intersection = words1.intersection(words2)
            union = words1.union(words2)
            return len(intersection) / len(union) if union else 0.0
        
        # Advanced similarity using spaCy
        doc1 = self.nlp(text1)
        doc2 = self.nlp(text2)
        return doc1.similarity(doc2)
    
    def is_question(self, message):
        """Check if message is a question"""
        question_indicators = [
            r'\?',
            r'\b(what|how|why|when|where|who|which)\b',
            r'\b(can you|could you|would you|do you|did you|will you)\b',
            r'\b(is|are|was|were|does|did|will|would|could|should)\b.*\?'
        ]
        
        for pattern in question_indicators:
            if re.search(pattern, message, re.IGNORECASE):
                return True
        return False
    
    def extract_study_duration(self, message):
        """Extract study duration from message"""
        duration_patterns = [
            r'(\d+)\s*(hour|hours|hr|hrs)',
            r'(\d+)\s*(minute|minutes|min|mins)',
            r'(\d+)\s*(day|days)',
            r'(\d+)\s*(week|weeks)'
        ]
        
        for pattern in duration_patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                number = int(match.group(1))
                unit = match.group(2).lower()
                
                if 'hour' in unit or 'hr' in unit:
                    return number * 60  # Convert to minutes
                elif 'minute' in unit or 'min' in unit:
                    return number
                elif 'day' in unit:
                    return number * 24 * 60  # Convert to minutes
                elif 'week' in unit:
                    return number * 7 * 24 * 60  # Convert to minutes
        
        return 60  # Default 1 hour

# Global NLP service instance
nlp_service = NLPService()
