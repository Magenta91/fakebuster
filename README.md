# FakeBuster v2

Automated fake news detection pipeline — aggregates news by trending geopolitical topics,
verifies claims through a 3-layer evidence chain, and surfaces confirmed debunked content
from trusted Indian fact-checkers (PIB Fact Check, Alpha Defence).

---

## Project structure

```
fakebuster/
├── backend/
│   ├── app/
│   │   ├── core/               # Base classes + shared clients
│   │   │   ├── base_fetcher.py
│   │   │   ├── base_scraper.py
│   │   │   ├── base_verifier.py
│   │   │   ├── base_processor.py
│   │   │   ├── gemini_client.py
│   │   │   └── scheduler.py
│   │   ├── models/             # SQLAlchemy ORM models
│   │   ├── services/
│   │   │   ├── fetchers/       # RSS, NewsAPI, Trend detector
│   │   │   ├── scrapers/       # Newspaper3k, Playwright, FactCheck scraper
│   │   │   ├── processors/     # Text cleaner, Embeddings
│   │   │   ├── verifiers/      # Layer 1/2/3 + pipeline
│   │   │   └── pipeline_orchestrator.py
│   │   ├── api/
│   │   │   ├── routes/         # articles, topics, pipeline
│   │   │   └── schemas.py
│   │   ├── config/
│   │   │   ├── settings.py     # All env vars via pydantic-settings
│   │   │   └── sources.py      # RSS + fact-check source list (edit here to add sources)
│   │   └── main.py
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   └── src/
│       ├── app/
│       │   ├── feed/           # Main topic-grouped news feed
│       │   ├── debunked/       # Confirmed false news page
│       │   └── article/[id]/   # Full article detail + verification chain
│       ├── components/
│       │   ├── cards/          # ArticleCard, DebunkedCard
│       │   ├── charts/         # VerdictChart (donut)
│       │   ├── layout/         # Navbar
│       │   └── ui/             # VerdictPill, CredibilityMeter, TopicChip
│       ├── lib/api.ts          # All API calls (single file — change base URL here)
│       └── types/index.ts      # All TypeScript types
└── .github/workflows/pipeline.yml
```

---

## Backend setup

```bash
cd backend
python -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium    # For JS-heavy scraping

cp .env.example .env
# Fill in your keys in .env

uvicorn app.main:app --reload
```

---

## Frontend setup

```bash
cd frontend
npm install

cp .env.example .env.local
# Set NEXT_PUBLIC_API_URL=http://localhost:8000

npm run dev
```

---

## API keys needed

| Key | Where to get |
|---|---|
| `NEWSAPI_KEY` | newsapi.org → free account |
| `GEMINI_API_KEY` | aistudio.google.com → Get API Key |
| `SERPAPI_KEY` | serpapi.com → optional, improves Layer 2 |

---

## Verification layers

| Layer | Module | What it does |
|---|---|---|
| 1 | `factcheck_verifier.py` | Semantic match vs PIB / Alpha Defence DB |
| 2 | `consensus_verifier.py` | Cross-source corroboration via search |
| 3 | `llm_verifier.py` | Gemini writes explanation, defaults to suspicious |

---

## Adding a new source

**News source:** Add an `RSSSource` entry to `backend/app/config/sources.py` — no other files change.

**Fact-check source:** Add a `FactCheckSource` entry to `FACTCHECK_SOURCES` in `sources.py`.
Set `requires_js=True` if the site is JavaScript-rendered.

**New verification layer:** Subclass `BaseVerifier` in `services/verifiers/`,
implement `verify()`, then add it to the `self.layers` list in `verifiers/pipeline.py`.

---

## GitHub Actions cron

Set the `BACKEND_URL` secret in your GitHub repo settings to your Railway deployment URL.
The pipeline runs automatically at 08:30 and 20:30 IST daily.
