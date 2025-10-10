"""
Quick script to verify Open Graph meta tags on live site
"""
import requests
from bs4 import BeautifulSoup

url = "https://marketing-agent-p4ig.onrender.com"

print(f"🔍 Fetching {url}...")
response = requests.get(url)

if response.status_code == 200:
    soup = BeautifulSoup(response.text, 'html.parser')
    
    print("\n✅ Page loaded successfully!\n")
    
    # Check Open Graph tags
    og_tags = soup.find_all('meta', property=lambda x: x and x.startswith('og:'))
    
    print("📊 Open Graph Tags Found:")
    print("-" * 60)
    for tag in og_tags:
        prop = tag.get('property')
        content = tag.get('content')
        print(f"  {prop}: {content}")
    
    print("\n")
    
    # Check Twitter Card tags
    twitter_tags = soup.find_all('meta', attrs={'name': lambda x: x and x.startswith('twitter:')})
    
    print("🐦 Twitter Card Tags Found:")
    print("-" * 60)
    for tag in twitter_tags:
        name = tag.get('name')
        content = tag.get('content')
        print(f"  {name}: {content}")
    
    print("\n")
    
    # Check Meta Pixel
    meta_pixel = soup.find('script', string=lambda x: x and 'fbq' in x)
    if meta_pixel:
        print("📈 Meta Pixel: ✅ Found")
    else:
        print("📈 Meta Pixel: ❌ Not configured (optional)")
    
    print("\n")
    
    # Check favicon
    favicon = soup.find('link', rel='icon')
    if favicon:
        print(f"🎨 Favicon: ✅ {favicon.get('href')}")
    else:
        print("🎨 Favicon: ❌ Not found")
    
    # Verify og:image URL
    og_image = soup.find('meta', property='og:image')
    if og_image:
        image_url = og_image.get('content')
        print(f"\n🖼️  Checking og:image accessibility: {image_url}")
        img_response = requests.head(image_url)
        if img_response.status_code == 200:
            print(f"   ✅ Image accessible (Status: {img_response.status_code})")
            print(f"   📦 Content-Type: {img_response.headers.get('Content-Type')}")
            print(f"   📏 Content-Length: {img_response.headers.get('Content-Length')} bytes")
        else:
            print(f"   ❌ Image not accessible (Status: {img_response.status_code})")
    
    print("\n" + "=" * 60)
    print("🎯 Next Step: Test on Facebook Sharing Debugger")
    print("   URL: https://developers.facebook.com/tools/debug/")
    print("   Enter: https://marketing-agent-p4ig.onrender.com")
    print("=" * 60)
    
else:
    print(f"❌ Failed to fetch page. Status: {response.status_code}")
