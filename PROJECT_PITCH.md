# FakeBuster - AI-Powered Fake News Detection System

## 🎯 Project Overview

FakeBuster is an intelligent news verification platform that automatically detects and flags misinformation in real-time. It aggregates news from Indian sources, analyzes credibility using AI and multi-source verification, and surfaces officially debunked content from government fact-checkers.

## 🚀 Key Features

### 1. **Automated News Aggregation**
- Monitors 7+ major Indian news sources via RSS feeds
- Scrapes 200+ official fact-checks from PIB Fact Check (Telegram)
- Filters opinion pieces and focuses on factual reporting

### 2. **Three-Layer Verification System**
- **Layer 1**: Semantic matching against official fact-check databases (PIB, Alpha Defence)
- **Layer 2**: Multi-source consensus verification via cross-referencing
- **Layer 3**: AI-powered headline credibility analysis using Google Gemini

### 3. **Smart Feed Organization**
- **Verified News** (≥7.0/10): High credibility articles from trusted sources
- **Suspicious Content** (<7.0/10): Low credibility articles requiring caution
- **Pending Analysis**: Articles awaiting verification

### 4. **Ask AI Chatbot**
- Instant headline verification for user-submitted content
- Real-time credibility scoring (0-10 scale)
- Detailed AI explanations for ratings

### 5. **Transparency & Explainability**
- Every article shows AI commentary explaining its rating
- Visual credibility meters with color-coded indicators
- Full verification chain visible to users

## 🛠️ Tech Stack

### **Backend**
- **Framework**: FastAPI (Python 3.13)
- **Database**: SQLite with SQLAlchemy ORM
- **AI/ML**: Google Gemini API (generative AI)
- **Web Scraping**: 
  - Newspaper4k (article extraction)
  - BeautifulSoup4 + lxml (HTML parsing)
  - Playwright (JavaScript-rendered sites)
  - Telethon (Telegram scraping)
- **Data Sources**:
  - Feedparser (RSS feeds)
  - NewsAPI (news aggregation)
  - PyTrends (trending topics)
- **Task Scheduling**: APScheduler (automated pipeline runs)
- **HTTP Clients**: HTTPX, Requests, AIOHTTP
- **Server**: Uvicorn (ASGI server)

### **Frontend**
- **Framework**: Next.js 14.2 (React 18)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Data Visualization**: Chart.js + react-chartjs-2
- **HTTP Client**: Axios
- **Utilities**: 
  - clsx (conditional classes)
  - date-fns (date formatting)

### **DevOps & Tools**
- **Version Control**: Git + GitHub
- **CI/CD**: GitHub Actions (automated pipeline runs)
- **Environment Management**: python-dotenv
- **API Documentation**: FastAPI auto-generated OpenAPI docs

## 📊 System Architecture

```
┌─────────────────┐
│  News Sources   │ (RSS, Telegram, NewsAPI)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Fetchers &    │ (Aggregate news, detect trends)
│    Scrapers     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Verification   │ (3-layer evidence chain)
│    Pipeline     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│    Database     │ (Store articles + scores)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   REST API      │ (FastAPI endpoints)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Next.js UI     │ (User interface)
└─────────────────┘
```

## 💡 Innovation Highlights

1. **Government Integration**: Direct scraping of official PIB Fact Check channel (200+ verified debunks)
2. **Headline-First Analysis**: Focuses on what users see first - the headline
3. **Transparent AI**: Every rating comes with detailed explanation
4. **Real-time Verification**: Users can verify any headline instantly via chatbot
5. **Multi-layer Approach**: Combines fact-check databases, consensus verification, and AI analysis

## 📈 Current Database Stats

- **Total Articles**: 227+
- **PIB Fact Checks**: 200+ official government debunks
- **Verified News**: High credibility articles (≥7.0/10)
- **Flagged Content**: 36+ suspicious articles including demo cases
- **Active Topics**: 15+ trending geopolitical topics

## 🎓 Use Cases

1. **Journalists**: Quick fact-checking before publishing
2. **Social Media Users**: Verify viral headlines before sharing
3. **Educators**: Teaching media literacy and critical thinking
4. **Researchers**: Studying misinformation patterns in Indian media

## 🔒 Security & Privacy

- No user data collection
- Read-only access to public news sources
- Official government sources prioritized
- Transparent scoring methodology

## 🌟 Future Enhancements

- Multi-language support (Hindi, regional languages)
- Browser extension for real-time verification
- WhatsApp/Telegram bot integration
- Advanced NLP for claim extraction
- User reporting system for crowdsourced verification

---

**Built with ❤️ for combating misinformation in India**
