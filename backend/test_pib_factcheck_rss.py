import requests
from bs4 import BeautifulSoup

# Try different PIB RSS feeds
urls = [
    "https://pib.gov.in/RssMain.aspx?ModId=6&Lang=1&Regid=3",  # Current (general news)
    "https://factcheck.pib.gov.in/rss.xml",
    "https://factcheck.pib.gov.in/feed",
    "https://pib.gov.in/RssMain.aspx?ModId=6&Lang=1",
]

for url in urls:
    print(f"\nTrying: {url}")
    try:
        response = requests.get(url, timeout=5)
        print(f"  Status: {response.status_code}")
        if response.status_code == 200:
            content = response.content.decode('utf-8-sig')
            if '<item>' in content or '<entry>' in content:
                soup = BeautifulSoup(content, 'xml')
                items = soup.find_all('item')
                print(f"  Items found: {len(items)}")
                if items:
                    title = items[0].find('title')
                    print(f"  First title: {title.text[:80] if title else 'N/A'}")
    except Exception as e:
        print(f"  Error: {e}")
