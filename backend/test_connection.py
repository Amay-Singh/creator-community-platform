#!/usr/bin/env python3
"""
Test the new Supabase connection string
"""

import psycopg2
import sys

# New connection string with updated password format
CONNECTION_STRING = "postgresql://postgres:colab_123Colab@db.qgdmsaxsizzlvkgochqd.supabase.co:5432/postgres"

def test_connection():
    """Test the Supabase connection"""
    print("Testing Supabase connection...")
    print(f"Connection string: {CONNECTION_STRING}")
    
    try:
        conn = psycopg2.connect(CONNECTION_STRING)
        
        # Test basic query
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        
        print(f"✅ SUCCESS: Connected to Supabase")
        print(f"PostgreSQL version: {version[0]}")
        
        # Test schema access
        cursor.execute("SELECT schema_name FROM information_schema.schemata;")
        schemas = cursor.fetchall()
        print(f"Available schemas: {[s[0] for s in schemas]}")
        
        cursor.close()
        conn.close()
        return True
        
    except psycopg2.OperationalError as e:
        print(f"❌ FAILED: Connection failed")
        print(f"Error: {e}")
        return False
    except Exception as e:
        print(f"❌ UNEXPECTED ERROR: {e}")
        return False

if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)
