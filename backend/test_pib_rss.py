import feedparser
import requests

# Test PIB RSS feed
url = "https://pib.gov.in/RssMain.aspx?ModId=6&Lang=1&Regid=3"

print("Fetching PIB RSS feed...")
response = requests.get(url)
print(f"Status: {response.status_code}")
print(f"Content length: {len(response.content)}")
print("\nFirst 500 chars of content:")
print(response.text[:500])

print("\n" + "="*50)
print("Parsing with feedparser...")
feed = feedparser.parse(url)
print(f"Feed version: {feed.version}")
print(f"Feed title: {feed.feed.get('title', 'N/A')}")
print(f"Number of entries: {len(feed.entries)}")

if feed.entries:
    print("\nFirst entry:")
    entry = feed.entries[0]
    print(f"  Title: {entry.get('title', 'N/A')}")
    print(f"  Link: {entry.get('link', 'N/A')}")
    print(f"  Summary: {entry.get('summary', 'N/A')[:100]}")
else:
    print("\nNo entries found!")
    print("\nFeed keys:", feed.feed.keys())
    print("\nFeed bozo:", feed.bozo)
    if feed.bozo:
        print("Bozo exception:", feed.bozo_exception)
