#!/usr/bin/env python
"""
Script to download clean views.py from GitHub and replace local file
Run: python fix_conflict.py
"""

import urllib.request
import os

def fix_conflict():
    print("🔧 Fixing git conflict in api/views.py...")
    
    # GitHub raw URL
    url = "https://raw.githubusercontent.com/Aryankaushik541/white-beat-backend/main/api/views.py"
    
    # Local file path
    local_file = "api/views.py"
    
    try:
        print(f"📥 Downloading clean file from GitHub...")
        with urllib.request.urlopen(url) as response:
            content = response.read()
        
        print(f"💾 Writing to {local_file}...")
        with open(local_file, 'wb') as f:
            f.write(content)
        
        print("✅ File fixed successfully!")
        print("\n🚀 Now run: python manage.py runserver")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n📝 Manual fix:")
        print("1. Open api/views.py in editor")
        print("2. Search for '<<<<<<< HEAD'")
        print("3. Delete all lines with conflict markers:")
        print("   - <<<<<<< HEAD")
        print("   - =======")
        print("   - >>>>>>> 6ff2d3b2811ea43ff35efe7aa3c62b0373fb7a99")
        print("4. Keep only one version of the code")
        print("5. Save and run: python manage.py runserver")

if __name__ == '__main__':
    fix_conflict()
