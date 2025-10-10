"""
Diagnostic script to check Open Graph configuration
Run: python diagnose_og.py
"""

import os
import sys

print("🔍 Open Graph Configuration Diagnostic")
print("=" * 60)

# Check if .env file exists
env_file = ".env"
if os.path.exists(env_file):
    print(f"✅ .env file found: {env_file}")
    
    # Read .env file
    with open(env_file, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Check for OG_IMAGE_ABS
    if "OG_IMAGE_ABS" in content:
        print("\n⚠️  OG_IMAGE_ABS found in .env file:")
        for line in content.split('\n'):
            if 'OG_IMAGE_ABS' in line and not line.strip().startswith('#'):
                print(f"   {line}")
                
                # Check if it's a placeholder
                if 'your-domain.com' in line:
                    print("\n❌ PROBLEM FOUND!")
                    print("   OG_IMAGE_ABS contains placeholder 'your-domain.com'")
                    print("\n💡 SOLUTION:")
                    print("   1. Delete this line from .env")
                    print("   2. Or change to: OG_IMAGE_ABS=https://marketing-agent-p4ig.onrender.com/static/img/og-default.jpg")
                elif 'marketing-agent-p4ig.onrender.com' in line:
                    print("   ✅ Correct domain found!")
    else:
        print("\n✅ OG_IMAGE_ABS not in .env - will use automatic fallback")
else:
    print(f"ℹ️  .env file not found (this is OK for production)")

print("\n" + "=" * 60)
print("🧪 Testing Flask app configuration...")

try:
    from app import create_app
    
    app = create_app()
    
    with app.app_context():
        og_image_abs = app.config.get('OG_IMAGE_ABS', '')
        og_site_name = app.config.get('OG_SITE_NAME', '')
        og_title = app.config.get('OG_TITLE', '')
        
        print(f"\n📊 Current Configuration:")
        print(f"   OG_SITE_NAME: {og_site_name}")
        print(f"   OG_TITLE: {og_title}")
        print(f"   OG_IMAGE_ABS: '{og_image_abs}'")
        
        if not og_image_abs:
            print("\n✅ GOOD: OG_IMAGE_ABS is empty")
            print("   Templates will automatically generate:")
            print("   https://[your-domain]/static/img/og-default.jpg")
        elif 'your-domain.com' in og_image_abs:
            print("\n❌ ERROR: Placeholder URL detected!")
            print(f"   Current: {og_image_abs}")
            print(f"   Should be: https://marketing-agent-p4ig.onrender.com/static/img/og-default.jpg")
            print("\n💡 Fix on Render.com:")
            print("   1. Go to: https://dashboard.render.com/")
            print("   2. Select your service")
            print("   3. Environment → Delete OG_IMAGE_ABS variable")
            print("   4. Or change to correct URL")
        elif 'marketing-agent-p4ig.onrender.com' in og_image_abs:
            print("\n✅ GOOD: Correct domain configured!")
        else:
            print(f"\n⚠️  WARNING: Custom URL set")
            print(f"   Make sure this URL is accessible: {og_image_abs}")
            
except Exception as e:
    print(f"\n❌ Error loading Flask app: {e}")
    print("   This is OK if dependencies are not installed")

print("\n" + "=" * 60)
print("📁 Checking static files...")

og_image_path = "app/static/img/og-default.jpg"
favicon_path = "app/static/img/favicon.png"

if os.path.exists(og_image_path):
    size = os.path.getsize(og_image_path)
    print(f"✅ og-default.jpg exists ({size:,} bytes)")
    if size < 10000:
        print("   ⚠️  WARNING: File seems too small!")
    elif size > 1000000:
        print("   ⚠️  WARNING: File is very large (>1MB)")
else:
    print(f"❌ og-default.jpg NOT FOUND at {og_image_path}")

if os.path.exists(favicon_path):
    size = os.path.getsize(favicon_path)
    print(f"✅ favicon.png exists ({size:,} bytes)")
else:
    print(f"❌ favicon.png NOT FOUND at {favicon_path}")

print("\n" + "=" * 60)
print("🎯 Recommendations:\n")

recommendations = []

if os.path.exists(env_file):
    with open(env_file, 'r', encoding='utf-8') as f:
        if 'your-domain.com' in f.read():
            recommendations.append("❗ Remove 'your-domain.com' placeholder from .env file")

if not recommendations:
    print("✅ Everything looks good!")
    print("\nNext steps:")
    print("1. Deploy to Render")
    print("2. Check Render Environment variables for OG_IMAGE_ABS")
    print("3. If OG_IMAGE_ABS exists with 'your-domain.com' - DELETE IT")
    print("4. Test with Facebook Sharing Debugger")
else:
    for rec in recommendations:
        print(rec)

print("\n" + "=" * 60)
print("🔗 Testing URLs:")
print("\nAfter deployment, test these URLs:")
print("1. https://marketing-agent-p4ig.onrender.com/static/img/og-default.jpg")
print("2. https://developers.facebook.com/tools/debug/")
print("3. https://www.linkedin.com/post-inspector/")
print("\n" + "=" * 60)
