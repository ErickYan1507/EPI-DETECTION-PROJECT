#!/usr/bin/env python
import sys
import traceback

try:
    print("=== Test import app.routes_notifications_api ===")
    from app.routes_notifications_api import notifications_api
    print("✅ notifications_api imported successfully")
except Exception as e:
    print(f"❌ ERROR: {e}")
    traceback.print_exc()

try:
    print("\n=== Test import app.routes_notifications ===")
    from app.routes_notifications import notifications_bp
    print("✅ notifications_bp imported successfully")
except Exception as e:
    print(f"❌ ERROR: {e}")
    traceback.print_exc()

print("\n=== Test app.main_new ===")
try:
    from app.main_new import app
    print("✅ app created successfully")
except Exception as e:
    print(f"❌ ERROR: {e}")
    traceback.print_exc()
