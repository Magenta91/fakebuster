import requests
from bs4 import BeautifulSoup

# PIB Fact Check page
url = "https://factcheck.pib.gov.in/"

print("Fetching PIB Fact Check page...")
response = requests.get(url, timeout=10)
print(f"Status: {response.status_code}")

soup = BeautifulSoup(response.content, 'html.parser')

# Look for fact-check articles
articles = soup.find_all(['article', 'div'], class_=lambda x: x and ('fact' in x.lower() or 'post' in x.lower()))
print(f"\nFound {len(articles)} potential fact-check containers")

# Try to find headlines
headlines = soup.find_all(['h2', 'h3', 'h4', 'a'], limit=10)
print("\nFirst 10 headlines/links:")
for i, h in enumerate(headlines[:10], 1):
    text = h.get_text(strip=True)
    if len(text) > 20:
        print(f"{i}. {text[:100]}")
        if h.name == 'a' and h.get('href'):
            print(f"   Link: {h.get('href')}")
