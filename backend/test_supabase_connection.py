#!/usr/bin/env python3
"""
Supabase Connection Diagnostics Script
Tests both pooled and direct connections to Supabase PostgreSQL
"""

import psycopg2
import sys

# Connection strings
POOLED_CONNECTION = "postgresql://postgres.xjytkeabsvxwpuquupls:6XrjGZJuxE2NRRZl@aws-0-us-west-1.pooler.supabase.com:6543/postgres"
DIRECT_CONNECTION = "postgresql://postgres.xjytkeabsvxwpuquupls:6XrjGZJuxE2NRRZl@db.xjytkeabsvxwpuquupls.supabase.co:5432/postgres"

def test_connection(connection_string, connection_type):
    """Test a PostgreSQL connection string"""
    print(f"\n{'='*50}")
    print(f"Testing {connection_type} Connection")
    print(f"{'='*50}")
    
    try:
        print(f"Connection string: {connection_string}")
        conn = psycopg2.connect(connection_string)
        
        # Test basic query
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        
        print(f"✅ SUCCESS: Connected to {connection_type}")
        print(f"PostgreSQL version: {version[0]}")
        
        # Test schema access
        cursor.execute("SELECT schema_name FROM information_schema.schemata;")
        schemas = cursor.fetchall()
        print(f"Available schemas: {[s[0] for s in schemas]}")
        
        cursor.close()
        conn.close()
        return True
        
    except psycopg2.OperationalError as e:
        print(f"❌ FAILED: {connection_type} connection failed")
        print(f"Error: {e}")
        return False
    except Exception as e:
        print(f"❌ UNEXPECTED ERROR: {e}")
        return False

def main():
    """Run connection diagnostics"""
    print("Supabase Connection Diagnostics")
    print("Project ID: xjytkeabsvxwpuquupls")
    
    # Test pooled connection
    pooled_success = test_connection(POOLED_CONNECTION, "Pooled (Port 6543)")
    
    # Test direct connection
    direct_success = test_connection(DIRECT_CONNECTION, "Direct (Port 5432)")
    
    # Summary
    print(f"\n{'='*50}")
    print("SUMMARY")
    print(f"{'='*50}")
    print(f"Pooled Connection: {'✅ SUCCESS' if pooled_success else '❌ FAILED'}")
    print(f"Direct Connection: {'✅ SUCCESS' if direct_success else '❌ FAILED'}")
    
    if not pooled_success and not direct_success:
        print("\n🚨 BOTH CONNECTIONS FAILED")
        print("Possible issues:")
        print("1. Supabase project is paused - check dashboard")
        print("2. Incorrect project reference ID")
        print("3. Wrong password or credentials")
        print("4. Network/firewall restrictions")
        print("5. IP not whitelisted in Supabase settings")
        
    return 0 if (pooled_success or direct_success) else 1

if __name__ == "__main__":
    sys.exit(main())
