import os
import psycopg2
import getpass
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
from langchain_community.vectorstores.pgvector import PGVector
from langchain_community.embeddings import HuggingFaceEmbeddings
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs/db.log")),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Default database connection string - can be overridden from .env
DEFAULT_CONNECTION_STRING = f"postgresql://{getpass.getuser()}@localhost:5433/hr_assistant"

# Default collection name for documents
COLLECTION_NAME = "hr_documents"

# Get database connection string from environment or use default
def get_connection_string():
    return os.getenv("POSTGRES_CONNECTION_STRING", DEFAULT_CONNECTION_STRING)

# Initialize database and create pgvector extension if needed
def init_database():
    """Initialize PostgreSQL database with pgvector extension"""
    connection_string = get_connection_string()
    
    try:
        # Connect to PostgreSQL
        conn = psycopg2.connect(connection_string)
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Create pgvector extension if it doesn't exist
        cursor.execute("CREATE EXTENSION IF NOT EXISTS vector;")
        
        # Close connection
        cursor.close()
        conn.close()
        
        logger.info("Successfully initialized database with pgvector extension")
        return True
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        return False

# Create a PGVector collection for storing document vectors
def get_pgvector_store(collection_name="hr_documents", embedding_function=None):
    """Get a PGVector store with the specified collection name and embedding function"""
    if embedding_function is None:
        embedding_function = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    connection_string = get_connection_string()
    
    try:
        # Create PGVector store
        store = PGVector(
            collection_name=collection_name,
            connection_string=connection_string,
            embedding_function=embedding_function,
        )
        return store
    except Exception as e:
        logger.error(f"Error creating PGVector store: {str(e)}")
        raise

# Function to check if a collection exists
def collection_exists(collection_name="hr_documents"):
    """Check if a collection exists in the database"""
    connection_string = get_connection_string()
    engine = create_engine(connection_string)
    
    try:
        with engine.connect() as conn:
            result = conn.execute(text(
                f"SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'langchain_pg_embedding_{collection_name}')"
            ))
            return result.scalar()
    except Exception as e:
        logger.error(f"Error checking if collection exists: {str(e)}")
        return False

# Delete a collection if it exists
def delete_collection(collection_name="hr_documents"):
    """Delete a collection if it exists"""
    connection_string = get_connection_string()
    engine = create_engine(connection_string)
    
    try:
        with engine.connect() as conn:
            conn.execute(text(f"DROP TABLE IF EXISTS langchain_pg_embedding_{collection_name}"))
            conn.commit()
            logger.info(f"Collection {collection_name} deleted successfully")
            return True
    except Exception as e:
        logger.error(f"Error deleting collection: {str(e)}")
        return False
