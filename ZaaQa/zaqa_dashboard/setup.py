"""
ZaaQa — Setup & Verification Script
Run this ONCE before starting the app.

Usage:
    python setup.py

This will:
  1. Check your MongoDB connection
  2. Print the default admin credentials
  3. Confirm the app is ready to run
"""

from werkzeug.security import generate_password_hash

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

hashed = generate_password_hash(ADMIN_PASSWORD)

print("=" * 60)
print("  ZaaQa — Amritsar Food Delivery System — Setup")
print("=" * 60)

# Check MongoDB
try:
    from pymongo import MongoClient
    client = MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=3000)
    client.server_info()
    print("✅ MongoDB connected     → localhost:27017")
    client.close()
except Exception as e:
    print(f"❌ MongoDB NOT connected  → {e}")
    print("   Install & start MongoDB: https://www.mongodb.com/try/download/community")

print()
print("Admin login credentials:")
print(f"  URL      : http://localhost:5000/admin/login")
print(f"  Username : {ADMIN_USERNAME}")
print(f"  Password : {ADMIN_PASSWORD}")
print()
print("User registration:")
print(f"  URL      : http://localhost:5000/register")
print()
print("Email notifications (optional):")
print("  Edit EMAIL_USER and EMAIL_PASSWORD in app.py")
print("  Use a Gmail App Password (not your main password)")
print()
print("To start the app:")
print("  pip install -r requirements.txt")
print("  python app.py")
print("=" * 60)
