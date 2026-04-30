from dataclasses import dataclass, field
from typing import List


@dataclass
class RSSSource:
    name: str
    url: str
    credibility: str  # "high" | "medium" | "low"
    region: str       # "india" | "global"


@dataclass
class FactCheckSource:
    name: str
    rss_url: str
    base_url: str
    requires_js: bool = False


RSS_SOURCES: List[RSSSource] = [
    RSSSource("NDTV India", "https://feeds.feedburner.com/ndtvnews-india-news", "high", "india"),
    RSSSource("The Hindu National", "https://www.thehindu.com/news/national/feeder/default.rss", "high", "india"),
    RSSSource("Times of India", "https://timesofindia.indiatimes.com/rssfeeds/296589292.cms", "high", "india"),
    RSSSource("Indian Express", "https://indianexpress.com/section/india/feed/", "high", "india"),
    RSSSource("Hindustan Times", "https://www.hindustantimes.com/feeds/rss/india-news/rssfeed.xml", "high", "india"),
    RSSSource("ANI News", "https://aninews.in/rss/india.xml", "high", "india"),
    RSSSource("DD News", "https://ddnews.gov.in/en/feed/", "high", "india"),
]

# Skip articles containing these keywords (opinion pieces, statements, etc.)
SKIP_KEYWORDS = [
    "opinion", "editorial", "column", "analysis", "comment", "interview",
    "letter to editor", "review", "explained", "explainer", "open letter",
    "statement by", "says minister", "minister says", "press release",
    "speech by", "address by", "remarks by", "react to", "responds to"
]

@dataclass
class TelegramSource:
    channel_id: int
    username: str
    source: str
    verdict: str
    base_url: str

TELEGRAM_SOURCES: List[TelegramSource] = [
    TelegramSource(
        channel_id=-1001559076845,
        username="PIB_FactCheck",
        source="PIB Fact Check",
        verdict="debunked",
        base_url="https://t.me/PIB_FactCheck",
    ),
]

FACTCHECK_SOURCES: List[FactCheckSource] = [
    FactCheckSource(
        name="PIB Fact Check",
        rss_url="https://pib.gov.in/RssMain.aspx?ModId=6&Lang=1&Regid=3",
        base_url="https://factcheck.pib.gov.in",
        requires_js=False,
    ),
    FactCheckSource(
        name="Alt News",
        rss_url="https://www.altnews.in/feed/",
        base_url="https://www.altnews.in",
        requires_js=False,
    ),
    FactCheckSource(
        name="Boom Live",
        rss_url="https://www.boomlive.in/feed",
        base_url="https://www.boomlive.in",
        requires_js=False,
    ),
]

GEOPOLITICAL_SEED_KEYWORDS: List[str] = [
    "india pakistan",
    "india china border",
    "geopolitical",
    "military conflict",
    "nuclear",
    "sanctions",
    "ceasefire",
    "terrorism",
    "coup",
    "election fraud",
]
