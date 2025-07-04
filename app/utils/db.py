import pymysql
from config import Config
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self):
        self.host = Config.MYSQL_HOST
        self.user = Config.MYSQL_USER
        self.password = Config.MYSQL_PASSWORD
        self.database = Config.MYSQL_DB
        
    def get_connection(self):
        """Get database connection"""
        try:
            connection = pymysql.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor,
                autocommit=True
            )
            return connection
        except Exception as e:
            logger.error(f"Database connection error: {e}")
            return None
    
    def execute_query(self, query, params=None):
        """Execute a SELECT query and return results"""
        connection = self.get_connection()
        if not connection:
            return None
            
        try:
            with connection.cursor() as cursor:
                cursor.execute(query, params or ())
                result = cursor.fetchall()
                return result
        except Exception as e:
            logger.error(f"Query execution error: {e}")
            return None
        finally:
            connection.close()
    
    def execute_single_query(self, query, params=None):
        """Execute a SELECT query and return single result"""
        connection = self.get_connection()
        if not connection:
            return None
            
        try:
            with connection.cursor() as cursor:
                cursor.execute(query, params or ())
                result = cursor.fetchone()
                return result
        except Exception as e:
            logger.error(f"Single query execution error: {e}")
            return None
        finally:
            connection.close()
    
    def execute_insert(self, query, params=None):
        """Execute an INSERT query and return the inserted ID"""
        connection = self.get_connection()
        if not connection:
            return None
            
        try:
            with connection.cursor() as cursor:
                cursor.execute(query, params or ())
                return cursor.lastrowid
        except Exception as e:
            logger.error(f"Insert execution error: {e}")
            return None
        finally:
            connection.close()
    
    def execute_update(self, query, params=None):
        """Execute an UPDATE/DELETE query and return affected rows"""
        connection = self.get_connection()
        if not connection:
            return 0
            
        try:
            with connection.cursor() as cursor:
                affected_rows = cursor.execute(query, params or ())
                return affected_rows
        except Exception as e:
            logger.error(f"Update execution error: {e}")
            return 0
        finally:
            connection.close()
    
    def test_connection(self):
        """Test database connection"""
        connection = self.get_connection()
        if connection:
            connection.close()
            return True
        return False

# Global database manager instance
db_manager = DatabaseManager()
