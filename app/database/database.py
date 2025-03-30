import os
import logging
from functools import lru_cache
from typing import Optional
from contextlib import asynccontextmanager


from supabase import create_client, Client, ClientOptions
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("supabase_client")


# Database connection parameters
DB_HOST = os.getenv("SUPABASE_DB_HOST")
DB_KEY = os.getenv("SUPABASE_DB_KEY")

class SupabaseConfig:
    """Configuration for Supabase client."""
    
    def __init__(self):
        # Get configuration from environment variables with fallbacks
        self.url = os.environ.get("SUPABASE_DB_HOST")
        if not self.url:
            raise ValueError("SUPABASE_DB_KEY environment variable is required")
            
        self.key = os.environ.get("SUPABASE_DB_KEY")
        if not self.key:
            raise ValueError("SUPABASE_KEY environment variable is required")
            
        # Optional timeout configuration
        self.timeout = int(os.environ.get("SUPABASE_TIMEOUT", "10"))
        
        # Optional retry configuration
        self.max_retries = int(os.environ.get("SUPABASE_MAX_RETRIES", "3"))


@lru_cache()
def get_supabase_config() -> SupabaseConfig:
    """Returns cached Supabase configuration."""
    return SupabaseConfig()


class SupabaseClientManager:
    """Manager for Supabase client instances."""
    
    _instance: Optional[Client] = None
    
    @classmethod
    def get_client(cls) -> Client:
        """Get or create a Supabase client instance."""
        if cls._instance is None:
            config = get_supabase_config()
            logger.info(f"Initializing Supabase client with URL: {config.url}")
            try:
                
                cls._instance = create_client(config.url,config.key)
                logger.info("Supabase client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Supabase client: {str(e)}")
                raise
        return cls._instance


@asynccontextmanager
async def get_supabase_client():
    """Context manager for getting a Supabase client."""
    client = None
    try:
        client = SupabaseClientManager.get_client()
        logger.debug("Supabase client acquired")
        yield client
    except Exception as e:
        logger.error(f"Error while using Supabase client: {str(e)}")
        raise
    finally:
        # No explicit close needed, but we can log the release
        if client:
            logger.debug("Supabase client operation completed")


# Dependency for FastAPI or other async frameworks
async def get_db():
    """Dependency to get Supabase client for request handlers."""
    print (f"getting a databse client for supabase connection")
    async with get_supabase_client() as supabase:
        yield supabase


# Example usage
async def example_usage():
    """Example of how to use the client in application code."""
    try:
        async with get_supabase_client() as supabase:
            # Fetch data
            response = supabase.table("users").select("*").limit(10).execute()
            users = response.data
            logger.info(f"Retrieved {len(users)} users")
            
            # Insert data
            new_user = {"name": "John Doe", "email": "john@example.com"}
            insert_response = supabase.table("users").insert(new_user).execute()
            logger.info(f"Inserted user with id: {insert_response.data[0]['id']}")
            
            # Error handling example
            try:
                # Intentional error - table doesn't exist
                supabase.table("non_existent_table").select("*").execute()
            except Exception as e:
                logger.error(f"Expected error occurred: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")