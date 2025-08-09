import os
from urllib.parse import quote_plus
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

# Load environment variables from .env file
load_dotenv()


class MongoDBConnection:
    """Handle MongoDB connection and basic operations for diabetes data analysis."""
    
    def __init__(self):
        self.client = None
        self.database = None
        self.username = os.getenv('MONGODB_USERNAME')
        self.password = os.getenv('MONGODB_PW')
        self.uri_template = os.getenv('MONGODB_URI')
        self.database_name = os.getenv('MONGODB_DATABASE', 'diabetes_data')
        
        if not all([self.username, self.password, self.uri_template]):
            raise ValueError("MONGODB_USERNAME, MONGODB_PW, and MONGODB_URI environment variables are required")
        
        # Build connection string with URL-encoded credentials
        encoded_username = quote_plus(self.username)
        encoded_password = quote_plus(self.password)
        self.connection_string = self.uri_template.replace('<username>', encoded_username).replace('<password>', encoded_password)
    
    def connect(self):
        """Establish connection to MongoDB."""
        try:
            print(f"Attempting connection to database: {self.database_name}")
            print(f"Username: {self.username}")
            self.client = MongoClient(
                self.connection_string,
                serverSelectionTimeoutMS=5000  # 5 second timeout
            )
            # Test the connection
            self.client.admin.command('ping')
            self.database = self.client[self.database_name]
            print(f"✓ Connected to MongoDB database: {self.database_name}")
            return True
        except Exception as e:
            print(f"✗ Failed to connect to MongoDB: {e}")
            return False
    
    def disconnect(self):
        """Close the MongoDB connection."""
        if self.client:
            self.client.close()
            print("✓ Disconnected from MongoDB")
    
    def list_databases(self):
        """List all available databases."""
        if self.client is None:
            print("✗ Not connected to MongoDB")
            return []
        
        try:
            databases = self.client.list_database_names()
            print(f"Available databases: {databases}")
            return databases
        except Exception as e:
            print(f"✗ Error listing databases: {e}")
            return []
    
    def list_collections(self):
        """List all collections in the current database."""
        if self.database is None:
            print("✗ Not connected to database")
            return []
        
        try:
            collections = self.database.list_collection_names()
            print(f"Collections in {self.database_name}: {collections}")
            return collections
        except Exception as e:
            print(f"✗ Error listing collections: {e}")
            return []


def test_connection():
    """Test the MongoDB connection setup."""
    print("Testing MongoDB connection...")
    
    try:
        db_conn = MongoDBConnection()
        
        if db_conn.connect():
            db_conn.list_databases()
            db_conn.list_collections()
            db_conn.disconnect()
            return True
        else:
            print("Connection test failed. Check your MONGODB_URI environment variable.")
            return False
    except ValueError as e:
        print(f"Configuration error: {e}")
        return False


if __name__ == "__main__":
    test_connection()