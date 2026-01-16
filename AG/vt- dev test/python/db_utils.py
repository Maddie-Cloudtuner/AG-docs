"""
Database utility functions
"""

import psycopg2
from psycopg2.extras import RealDictCursor
from config import Config
import logging

logger = logging.getLogger(__name__)


def get_db_connection():
    """
    Get database connection
    
    Returns:
        psycopg2.connection
    """
    try:
        conn = psycopg2.connect(
            host=Config.DB_HOST,
            port=Config.DB_PORT,
            dbname=Config.DB_NAME,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD
        )
        logger.info(f"Connected to database: {Config.DB_NAME}")
        return conn
    except psycopg2.Error as e:
        logger.error(f"Database connection failed: {e}")
        raise


def test_connection():
    """Test database connection"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT version();")
        version = cur.fetchone()[0]
        cur.close()
        conn.close()
        logger.info(f"Database connection successful: {version}")
        return True
    except Exception as e:
        logger.error(f"Database connection test failed: {e}")
        return False


def initialize_database():
    """Initialize database with cloud_resource_tags table"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Check if table exists
    cur.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_name = 'cloud_resource_tags'
        );
    """)
    
    table_exists = cur.fetchone()[0]
    
    if not table_exists:
        logger.info("cloud_resource_tags table not found. Run setup script first.")
        cur.close()
        conn.close()
        return False
    
    # Check row count
    cur.execute("SELECT COUNT(*) FROM cloud_resource_tags;")
    count = cur.fetchone()[0]
    logger.info(f"cloud_resource_tags table has {count} rows")
    
    cur.close()
    conn.close()
    return True


def execute_sql_file(filepath):
    """Execute SQL file"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    with open(filepath, 'r', encoding='utf-8') as f:
        sql = f.read()
    
    try:
        cur.execute(sql)
        conn.commit()
        logger.info(f"Successfully executed SQL file: {filepath}")
        return True
    except Exception as e:
        conn.rollback()
        logger.error(f"Failed to execute SQL file: {e}")
        return False
    finally:
        cur.close()
        conn.close()
