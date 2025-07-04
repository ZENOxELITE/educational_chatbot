#!/usr/bin/env python3
"""
Command-line version of the Educational Chatbot
This can be used to test the chatbot functionality without the web interface
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.chat_service import chat_service
from app.services.nlp_service import nlp_service
from app.models.user import User
from app.utils.db import db_manager
import getpass

class CLIChatbot:
    def __init__(self):
        self.current_user = None
        self.session_id = None
        
    def test_database(self):
        """Test database connection"""
        print("Testing database connection...")
        if db_manager.test_connection():
            print("✅ Database connection successful!")
            return True
        else:
            print("❌ Database connection failed!")
            print("Make sure XAMPP MySQL is running and database exists.")
            return False
    
    def register_user(self):
        """Register a new user"""
        print("\n=== User Registration ===")
        username = input("Username: ").strip()
        email = input("Email: ").strip()
        password = getpass.getpass("Password: ")
        first_name = input("First Name: ").strip()
        last_name = input("Last Name: ").strip()
        grade_level = input("Grade Level (optional): ").strip() or None
        
        # Check if user exists
        if User.find_by_username(username):
            print("❌ Username already exists!")
            return False
        
        if User.find_by_email(email):
            print("❌ Email already exists!")
            return False
        
        # Create user
        user = User(
            username=username,
            email=email,
            password_hash=User.hash_password(password),
            first_name=first_name,
            last_name=last_name,
            grade_level=grade_level
        )
        
        if user.save():
            print("✅ Registration successful!")
            return True
        else:
            print("❌ Registration failed!")
            return False
    
    def login_user(self):
        """Login user"""
        print("\n=== User Login ===")
        username = input("Username: ").strip()
        password = getpass.getpass("Password: ")
        
        user = User.authenticate(username, password)
        if user:
            self.current_user = user
            print(f"✅ Welcome, {user.get_full_name()}!")
            return True
        else:
            print("❌ Invalid username or password!")
            return False
    
    def chat_loop(self):
        """Main chat loop"""
        print(f"\n=== Chat with Educational Assistant ===")
        print("Type 'quit' to exit, 'help' for commands")
        print("-" * 50)
        
        while True:
            try:
                message = input(f"\n{self.current_user.first_name}: ").strip()
                
                if message.lower() in ['quit', 'exit', 'bye']:
                    print("Goodbye! Keep learning! 📚")
                    break
                
                if message.lower() == 'help':
                    self.show_help()
                    continue
                
                if not message:
                    continue
                
                # Process message
                result = chat_service.process_message(
                    user_id=self.current_user.id,
                    message=message,
                    session_id=self.session_id
                )
                
                self.session_id = result['session_id']
                
                print(f"\nBot: {result['response']}")
                
                # Show additional info
                if result['intent'] != 'general':
                    print(f"[Intent: {result['intent']}, Confidence: {result['confidence']:.2f}]")
                
            except KeyboardInterrupt:
                print("\n\nGoodbye! Keep learning! 📚")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
    
    def show_help(self):
        """Show help commands"""
        print("\n=== Available Commands ===")
        print("• Ask questions: 'What is photosynthesis?'")
        print("• Get study tips: 'How to study better?'")
        print("• Subject help: 'Help me with math'")
        print("• General chat: 'Hello', 'How are you?'")
        print("• Quit: 'quit', 'exit', 'bye'")
        print("• Help: 'help'")
    
    def run(self):
        """Main application loop"""
        print("🎓 Educational Assistant Chatbot (CLI Version)")
        print("=" * 50)
        
        # Test database
        if not self.test_database():
            return
        
        while True:
            if not self.current_user:
                print("\n=== Authentication Required ===")
                print("1. Login")
                print("2. Register")
                print("3. Quit")
                
                choice = input("\nChoose option (1-3): ").strip()
                
                if choice == '1':
                    if self.login_user():
                        self.chat_loop()
                elif choice == '2':
                    self.register_user()
                elif choice == '3':
                    print("Goodbye!")
                    break
                else:
                    print("Invalid choice!")
            else:
                self.chat_loop()
                self.current_user = None
                self.session_id = None

def main():
    """Main function"""
    try:
        chatbot = CLIChatbot()
        chatbot.run()
    except Exception as e:
        print(f"Application error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
