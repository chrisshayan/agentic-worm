#!/usr/bin/env python3
"""
Simple ArangoDB connection test to diagnose memory system issues.
"""

import sys
import time
import os

def test_arango_connection():
    """Test ArangoDB connection with detailed error reporting."""
    
    print("🧪 ArangoDB Connection Diagnostic Test")
    print("=====================================")
    
    # Step 1: Test imports
    print("1️⃣ Testing imports...")
    try:
        from arango import ArangoClient
        print("✅ ArangoDB client import successful")
    except ImportError as e:
        print(f"❌ Failed to import ArangoDB client: {e}")
        print("💡 Install with: pip install python-arango")
        return False
    except Exception as e:
        print(f"❌ Unexpected import error: {e}")
        return False
    
    # Step 2: Test environment variables
    print("\n2️⃣ Checking environment variables...")
    arango_host = os.environ.get('ARANGO_HOST', 'localhost')
    arango_port = int(os.environ.get('ARANGO_PORT', '8529'))
    arango_database = os.environ.get('ARANGO_DATABASE', 'agentic_worm_memory')
    arango_username = os.environ.get('ARANGO_USERNAME', '')
    arango_password = os.environ.get('ARANGO_PASSWORD', '')
    
    print(f"🔗 Host: {arango_host}")
    print(f"🔗 Port: {arango_port}")
    print(f"🗄️ Database: {arango_database}")
    print(f"👤 Username: {arango_username if arango_username else '(no auth)'}")
    print(f"🔐 Password: {'***' if arango_password else '(no auth)'}")
    
    # Step 3: Test connection
    print("\n3️⃣ Testing ArangoDB connection...")
    try:
        # Create client
        client = ArangoClient(hosts=f"http://{arango_host}:{arango_port}")
        print("✅ ArangoDB client created")
        
        # Test system database connection
        if arango_username:
            sys_db = client.db("_system", username=arango_username, password=arango_password)
        else:
            sys_db = client.db("_system")
        
        # Test connection with version check
        version_info = sys_db.version()
        print(f"✅ Connected to ArangoDB {version_info}")
        
        # Step 4: Test database operations
        print("\n4️⃣ Testing database operations...")
        
        # List databases
        databases = sys_db.databases()
        print(f"📋 Available databases: {databases}")
        
        # Create test database if not exists
        if arango_database not in databases:
            try:
                sys_db.create_database(arango_database)
                print(f"✅ Created database: {arango_database}")
            except Exception as e:
                print(f"⚠️ Database creation failed: {e}")
        else:
            print(f"✅ Database {arango_database} already exists")
        
        # Connect to our database
        if arango_username:
            our_db = client.db(arango_database, username=arango_username, password=arango_password)
        else:
            our_db = client.db(arango_database)
            
        # Test database access
        db_info = our_db.properties()
        print(f"✅ Connected to database: {db_info['name']}")
        
        # List collections
        collections = our_db.collections()
        collection_names = [c['name'] for c in collections if not c['name'].startswith('_')]
        print(f"📁 Collections: {collection_names if collection_names else 'None yet'}")
        
        print("\n🎉 ArangoDB connection test PASSED!")
        return True
        
    except Exception as e:
        print(f"❌ Connection test FAILED: {e}")
        print(f"🔍 Error type: {type(e).__name__}")
        
        # Additional debugging
        if "Connection refused" in str(e):
            print("💡 ArangoDB server may not be running or accessible")
        elif "authentication" in str(e).lower():
            print("💡 Authentication issue - check username/password")
        elif "timeout" in str(e).lower():
            print("💡 Connection timeout - server may be starting up")
        
        return False

if __name__ == "__main__":
    success = test_arango_connection()
    sys.exit(0 if success else 1) 