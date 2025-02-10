"""
Script to run database migrations for the scheduler.
"""
import os
import logging
from pathlib import Path
from typing import List
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def get_migration_files() -> List[Path]:
    """Get all SQL migration files in order."""
    migrations_dir = Path(__file__).parent
    return sorted(
        [f for f in migrations_dir.glob("*.sql") if f.name.startswith("0")]
    )

def run_migration(cursor, file_path: Path) -> None:
    """Run a single migration file."""
    logger.info(f"Running migration: {file_path.name}")
    
    try:
        with open(file_path, 'r') as f:
            sql = f.read()
            cursor.execute(sql)
            logger.info(f"Successfully executed {file_path.name}")
    except Exception as e:
        logger.error(f"Error executing {file_path.name}: {str(e)}")
        raise

def main():
    """Main function to run all migrations."""
    database_uri = os.getenv("DATABASE_URI")
    if not database_uri:
        raise ValueError("DATABASE_URI environment variable is not set")

    logger.info("Starting database migrations")
    
    try:
        # Connect to database
        conn = psycopg2.connect(database_uri)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Get and run migrations
        migration_files = get_migration_files()
        for file_path in migration_files:
            run_migration(cursor, file_path)
        
        logger.info("All migrations completed successfully")
        
    except Exception as e:
        logger.error(f"Migration failed: {str(e)}")
        raise
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    main() 
