#!/usr/bin/env python3
"""
Database migration script to add messaging tables to AgriConnect.
Run this script to add the messages and conversations tables to your database.
"""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.extensions import db
from app.models.message import Message, Conversation

def create_messaging_tables():
    """Create the messaging tables in the database."""
    app = create_app()
    
    with app.app_context():
        try:
            # Create the tables
            db.create_all()
            print("✅ Successfully created messaging tables (messages and conversations)")
            
            # Verify tables were created
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            
            if 'messages' in tables:
                print("✅ Messages table created successfully")
            else:
                print("❌ Messages table not found")
                
            if 'conversations' in tables:
                print("✅ Conversations table created successfully")
            else:
                print("❌ Conversations table not found")
                
        except Exception as e:
            print(f"❌ Error creating messaging tables: {e}")
            return False
            
    return True

if __name__ == "__main__":
    print("🚀 Adding messaging functionality to AgriConnect...")
    success = create_messaging_tables()
    
    if success:
        print("\n🎉 Messaging system successfully added!")
        print("You can now:")
        print("- Send messages between users")
        print("- View conversation history")
        print("- Real-time messaging with Socket.IO")
    else:
        print("\n❌ Failed to add messaging system. Please check the errors above.")
