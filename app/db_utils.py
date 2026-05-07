from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_database_if_not_exists(db_url: str, db_name: str):
    """
    Create database if it doesn't exist
    
    Args:
        db_url: Base database URL (without database name)
        db_name: Name of database to create
    """
    # Connect to default 'postgres' database
    default_engine = create_engine(f"{db_url}/postgres", isolation_level="AUTOCOMMIT")
    
    try:
        with default_engine.connect() as conn:
            # Check if database exists
            result = conn.execute(
                text("SELECT 1 FROM pg_database WHERE datname = :db_name"),
                {"db_name": db_name}
            )
            exists = result.fetchone() is not None
            
            if not exists:
                # Fixed: removed the comma and extra braces
                logger.info(f"Creating database: {db_name}")
                conn.execute(text(f"CREATE DATABASE {db_name}"))
                logger.info(f"Database '{db_name}' created successfully")
            else:
                logger.info(f"Database '{db_name}' already exists")
                
    except SQLAlchemyError as e:
        logger.error(f"Error while creating the database {db_name}: {e}")
        raise
    finally:
        default_engine.dispose()

def get_database_url(base_url: str, db_name: str) -> str:
    """Construct full database URL with database name"""
    return f"{base_url}/{db_name}"