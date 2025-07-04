from app import create_app
from app.utils.db import db_manager
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Main function to run the application"""
    # Test database connection
    logger.info("Testing database connection...")
    if not db_manager.test_connection():
        logger.error("Failed to connect to database. Please check your MySQL configuration.")
        logger.error("Make sure XAMPP is running and the database 'educational_chatbot' exists.")
        return
    
    logger.info("Database connection successful!")
    
    # Create Flask app
    app = create_app()
    
    # Run the application
    logger.info("Starting Educational Chatbot...")
    logger.info("Access the application at: http://localhost:5000")
    
    try:
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=app.config['DEBUG']
        )
    except KeyboardInterrupt:
        logger.info("Application stopped by user")
    except Exception as e:
        logger.error(f"Application error: {e}")

if __name__ == '__main__':
    main()
