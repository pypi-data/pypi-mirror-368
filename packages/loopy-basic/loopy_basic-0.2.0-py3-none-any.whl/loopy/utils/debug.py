import os
from urllib.parse import quote_plus
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def debug_connection_info():
    """Debug connection information without revealing password."""
    username = os.getenv('MONGODB_USERNAME')
    password = os.getenv('MONGODB_PW')
    uri_template = os.getenv('MONGODB_URI')
    database = os.getenv('MONGODB_DATABASE')
    
    print("=== Connection Debug Info ===")
    print(f"Username: '{username}'")
    print(f"Password length: {len(password) if password else 'None'}")
    print(f"Password starts with: '{password[:3]}...' (first 3 chars)")
    print(f"URI template: '{uri_template}'")
    print(f"Database: '{database}'")
    print()
    
    if username and password:
        encoded_username = quote_plus(username)
        encoded_password = quote_plus(password)
        
        print(f"URL-encoded username: '{encoded_username}'")
        print(f"URL-encoded password length: {len(encoded_password)}")
        print(f"URL-encoded password starts with: '{encoded_password[:3]}...'")
        
        # Show final URI (with password masked)
        final_uri = uri_template.replace('<username>', encoded_username).replace('<password>', encoded_password)
        masked_uri = final_uri.replace(encoded_password, '***PASSWORD***')
        print(f"Final connection string: '{masked_uri}'")
    
    print("\n=== Troubleshooting Tips ===")
    print("1. Verify credentials in MongoDB Atlas")
    print("2. Check if user has database access permissions")
    print("3. Try connecting with MongoDB Compass first")
    print("4. Ensure no extra spaces in .env file")

if __name__ == "__main__":
    debug_connection_info()