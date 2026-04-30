import requests
from bs4 import BeautifulSoup
import re

url = "https://pib.gov.in/RssMain.aspx?ModId=6&Lang=1&Regid=3"

print("Fetching PIB RSS feed...")
response = requests.get(url)

# Remove BOM
content = response.content.decode('utf-8-sig')

print("Cleaned content (first 1000 chars):")
print(content[:1000])

print("\n" + "="*50)
print("Parsing with BeautifulSoup...")
soup = BeautifulSoup(content, 'xml')

items = soup.find_all('item')
print(f"Found {len(items)} items")

if items:
    print("\nFirst 3 items:")
    for i, item in enumerate(items[:3], 1):
        title = item.find('title')
        link = item.find('link')
        print(f"\n{i}. Title: {title.text if title else 'N/A'}")
        print(f"   Link: {link.text if link else 'N/A'}")
