#!/usr/bin/env python3
"""
Test database connection with SSL
"""
import os
from dotenv import load_dotenv
import psycopg

# Load environment
load_dotenv()

def test_connection():
    """Test PostgreSQL connection with different SSL modes"""
    
    base_uri = os.getenv("SQLALCHEMY_DATABASE_URI", "")
    
    if not base_uri or "postgresql" not in base_uri:
        print("❌ PostgreSQL URI not found in environment")
        return
    
    # Remove sqlalchemy prefix
    uri = base_uri.replace("postgresql+psycopg://", "postgresql://")
    
    print("🔍 Testing database connection...\n")
    
    # Test 1: Without SSL
    print("Test 1: Without SSL parameters")
    try:
        base_uri_no_ssl = uri.split("?")[0]
        conn = psycopg.connect(base_uri_no_ssl)
        print("✅ Connection successful (no SSL)")
        conn.close()
    except Exception as e:
        print(f"❌ Failed: {e}\n")
    
    # Test 2: With sslmode=require
    print("Test 2: With sslmode=require")
    try:
        uri_with_ssl = uri if "?" in uri else f"{uri}?sslmode=require"
        if "sslmode" not in uri_with_ssl:
            uri_with_ssl = f"{uri_with_ssl}&sslmode=require"
        
        conn = psycopg.connect(uri_with_ssl)
        print("✅ Connection successful with SSL!")
        
        # Test query
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(f"✅ PostgreSQL version: {version[0][:50]}...")
        
        # Test table access
        cursor.execute("SELECT COUNT(*) FROM \"user\";")
        user_count = cursor.fetchone()[0]
        print(f"✅ Users in database: {user_count}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Failed: {e}\n")
    
    # Test 3: With sslmode=prefer
    print("\nTest 3: With sslmode=prefer")
    try:
        base_uri_no_params = uri.split("?")[0]
        uri_prefer = f"{base_uri_no_params}?sslmode=prefer"
        
        conn = psycopg.connect(uri_prefer)
        print("✅ Connection successful with sslmode=prefer")
        conn.close()
    except Exception as e:
        print(f"❌ Failed: {e}\n")

if __name__ == "__main__":
    test_connection()
