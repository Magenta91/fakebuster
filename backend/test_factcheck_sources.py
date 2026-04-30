import requests
from bs4 import BeautifulSoup

sources = [
    ("Alt News", "https://www.altnews.in/feed/"),
    ("Boom Live", "https://www.boomlive.in/feed"),
]

for name, url in sources:
    print(f"\n{'='*60}")
    print(f"Testing: {name}")
    print(f"URL: {url}")
    try:
        response = requests.get(url, timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            content = response.content.decode('utf-8-sig', errors='ignore')
            soup = BeautifulSoup(content, 'xml')
            items = soup.find_all('item')
            print(f"Items found: {len(items)}")
            
            if items:
                print("\nFirst 3 items:")
                for i, item in enumerate(items[:3], 1):
                    title = item.find('title')
                    link = item.find('link')
                    desc = item.find('description')
                    print(f"\n{i}. {title.text[:80] if title else 'N/A'}")
                    if desc:
                        desc_text = desc.text[:100].replace('\n', ' ')
                        print(f"   Desc: {desc_text}...")
    except Exception as e:
        print(f"Error: {e}")
