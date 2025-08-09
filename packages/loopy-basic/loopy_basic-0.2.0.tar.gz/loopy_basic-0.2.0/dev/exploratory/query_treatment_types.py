"""
Query Treatment Types

This script connects to the MongoDB database and queries the "treatments" collection
to find all unique values for the "eventType" field.

Run with: uv run python dev/exploratory/query_treatment_types.py
"""

from loopy.connection.mongodb import MongoDBConnection

def main():
    """Connect to MongoDB and query distinct eventType values in treatments collection."""
    print("=" * 80)
    print("QUERYING UNIQUE TREATMENT TYPES")
    print("=" * 80)
    
    # Connect to MongoDB
    conn = MongoDBConnection()
    if not conn.connect():
        print("Failed to connect to MongoDB")
        return
    
    try:
        # Check if treatments collection exists
        collections = conn.list_collections()
        if 'treatments' not in collections:
            print("Treatments collection not found in database")
            return
        
        # Query distinct eventType values
        treatments_collection = conn.database['treatments']
        event_types = treatments_collection.distinct("eventType")
        
        # Display results
        print(f"\nFound {len(event_types)} unique eventType values in treatments collection:")
        print("-" * 80)
        
        for i, event_type in enumerate(sorted(event_types), 1):
            print(f"{i:2d}. {event_type}")
        
        print("\n" + "=" * 80)
        print("QUERY COMPLETE")
        print("=" * 80)
        
    finally:
        # Disconnect
        conn.disconnect()

if __name__ == "__main__":
    main()