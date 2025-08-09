import os
from urllib.parse import quote_plus
from dotenv import load_dotenv
from pymongo import MongoClient

# Load environment variables from .env file
load_dotenv()

def test_basic_connection():
    """Test basic MongoDB connection without specifying target database."""
    username = os.getenv('MONGODB_USERNAME')
    password = os.getenv('MONGODB_PW')
    uri_template = os.getenv('MONGODB_URI')
    
    if not all([username, password, uri_template]):
        print("✗ Missing required environment variables")
        return False
    
    # Build connection string
    encoded_username = quote_plus(username)
    encoded_password = quote_plus(password)
    connection_string = uri_template.replace('<username>', encoded_username).replace('<password>', encoded_password)
    
    print(f"Testing connection with username: {username}")
    
    try:
        client = MongoClient(connection_string, serverSelectionTimeoutMS=5000)
        # Test connection
        client.admin.command('ping')
        print("✓ Basic connection successful!")
        
        # List databases
        databases = client.list_database_names()
        print(f"Available databases: {databases}")
        
        client.close()
        return True
        
    except Exception as e:
        print(f"✗ Connection failed: {e}")
        return False

if __name__ == "__main__":
    test_basic_connection()