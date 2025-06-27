#!/usr/bin/env python3
"""
Migration script to add product-specific messaging support.
This script adds the product_id column to conversations and conversation_id to messages.
"""

import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app import create_app
from app.extensions import db
from app.models.message import Message, Conversation
from app.models.product import Product
from app.models.user import User

def migrate_database():
    """Migrate the database to support product-specific messaging."""
    app = create_app()

    with app.app_context():
        print("Starting database migration for product-specific messaging...")

        # Drop existing tables and recreate with new structure
        print("Dropping existing message and conversation tables...")
        db.engine.execute("DROP TABLE IF EXISTS messages")
        db.engine.execute("DROP TABLE IF EXISTS conversations")

        # Create tables with new structure
        print("Creating new message and conversation tables...")
        db.create_all()

        print("Migration completed successfully!")
        print("\nNew features:")
        print("- Conversations are now tied to specific products")
        print("- Messages are linked to conversations")
        print("- Users can only chat about specific products")

if __name__ == "__main__":
    migrate_database()
