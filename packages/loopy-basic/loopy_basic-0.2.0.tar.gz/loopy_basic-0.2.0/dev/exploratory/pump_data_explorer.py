"""
Pump Data Explorer

This script explores the MongoDB database to identify and examine pump data.
It connects to the database, lists collections, and examines sample documents
from collections that might contain pump data (treatments, settings, profile).

Run with: uv run python dev/exploratory/pump_data_explorer.py
"""

from loopy.connection.mongodb import MongoDBConnection
import json
from datetime import datetime, timedelta
import pandas as pd
from pprint import pprint

def explore_database_structure():
    """Explore the overall database structure."""
    print("\n" + "="*80)
    print("EXPLORING DATABASE STRUCTURE")
    print("="*80)
    
    # Connect to MongoDB
    conn = MongoDBConnection()
    if not conn.connect():
        print("Failed to connect to MongoDB")
        return None
    
    try:
        # List all collections
        collections = conn.list_collections()
        
        # Get document counts for each collection
        print("\nDocument counts for each collection:")
        for collection_name in collections:
            count = conn.database[collection_name].count_documents({})
            print(f"  {collection_name}: {count:,} documents")
        
        return conn
    except Exception as e:
        print(f"Error exploring database: {e}")
        conn.disconnect()
        return None

def explore_collection(conn, collection_name, limit=5):
    """Explore a specific collection's structure."""
    print("\n" + "="*80)
    print(f"EXPLORING COLLECTION: {collection_name}")
    print("="*80)
    
    try:
        # Get the collection
        collection = conn.database[collection_name]
        
        # Get sample documents
        sample_docs = list(collection.find().limit(limit))
        
        if not sample_docs:
            print(f"No documents found in {collection_name}")
            return
        
        # Print the first document to see its structure
        print(f"\nSample document from {collection_name}:")
        pprint(sample_docs[0])
        
        # Analyze field names across all sample documents
        all_fields = set()
        for doc in sample_docs:
            all_fields.update(doc.keys())
        
        print(f"\nFields found in {collection_name}:")
        for field in sorted(all_fields):
            print(f"  - {field}")
        
        # If there are many documents, show some statistics
        if collection.count_documents({}) > limit:
            print(f"\nShowing {limit} of {collection.count_documents({}):,} documents")
            
            # For date-based collections, show the date range
            if any('date' in field.lower() for field in all_fields):
                date_field = next((f for f in all_fields if 'date' in f.lower()), None)
                if date_field:
                    oldest = collection.find().sort(date_field, 1).limit(1)
                    newest = collection.find().sort(date_field, -1).limit(1)
                    
                    oldest_doc = list(oldest)
                    newest_doc = list(newest)
                    
                    if oldest_doc and newest_doc:
                        print(f"\nDate range ({date_field}):")
                        print(f"  Oldest: {oldest_doc[0].get(date_field)}")
                        print(f"  Newest: {newest_doc[0].get(date_field)}")
        
    except Exception as e:
        print(f"Error exploring collection {collection_name}: {e}")

def explore_pump_data(conn):
    """Focus specifically on pump-related data."""
    print("\n" + "="*80)
    print("EXPLORING PUMP DATA")
    print("="*80)
    
    # Collections likely to contain pump data
    pump_collections = ['treatments', 'profile', 'settings', 'devicestatus']
    
    for collection_name in pump_collections:
        if collection_name in conn.list_collections():
            print(f"\nExamining {collection_name} for pump data...")
            collection = conn.database[collection_name]
            
            # Look for insulin-related fields
            insulin_fields = ['insulin', 'bolus', 'basal', 'rate', 'ratio', 'carb', 'carbs']
            
            for field in insulin_fields:
                # Try to find documents with this field
                query = {field: {"$exists": True}}
                count = collection.count_documents(query)
                
                if count > 0:
                    print(f"  Found {count} documents with '{field}' field")
                    
                    # Show a sample document
                    sample = collection.find(query).limit(1)
                    sample_doc = list(sample)
                    if sample_doc:
                        print(f"  Sample {field} data:")
                        if isinstance(sample_doc[0].get(field), dict):
                            pprint(sample_doc[0].get(field))
                        else:
                            print(f"    {sample_doc[0].get(field)}")

def main():
    """Main function to explore pump data in MongoDB."""
    print("="*80)
    print("PUMP DATA EXPLORER")
    print("="*80)
    print("This script explores MongoDB to identify and examine pump data.")
    
    # Connect and explore database structure
    conn = explore_database_structure()
    if not conn:
        return
    
    try:
        # Explore collections that might contain pump data
        pump_collections = ['treatments', 'profile', 'settings', 'devicestatus']
        for collection_name in pump_collections:
            if collection_name in conn.list_collections():
                explore_collection(conn, collection_name)
        
        # Specifically look for pump data
        explore_pump_data(conn)
        
        print("\n" + "="*80)
        print("EXPLORATION COMPLETE")
        print("="*80)
        
    finally:
        # Disconnect
        conn.disconnect()

if __name__ == "__main__":
    main()