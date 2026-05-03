# 🚌 Find My Caravan

> A web app for searching, collecting and comparing used camper/motorhome listings in Northern and Central Italy.

![Build](https://img.shields.io/badge/build-passing-brightgreen) ![License](https://img.shields.io/badge/license-MIT-blue) ![Python](https://img.shields.io/badge/python-3.12-blue) ![Vue](https://img.shields.io/badge/vue-3-42b883)

---

<!-- Screenshot placeholder -->
<!-- ![Screenshot](docs/screenshot.png) -->

---

## ✨ Features

- **Listing aggregation** – collect camper and motorhome listings from multiple sources (CSV, JSON, manual entry, saved HTML, dealer websites)
- **Advanced search & filters** – filter by price, year, mileage, brand, body type, region, and more
- **Interactive map** – browse listings on a Leaflet map pinned to their geographic location
- **Side-by-side comparison** – compare up to four vehicles on a single screen
- **Analytics dashboard** – price-by-year charts, brand breakdowns, and market-trend summaries
- **Data quality scoring** – confidence badge per listing based on completeness of fields
- **Import wizard** – bulk-import listings via CSV or JSON file upload through the `/import` page
- **Source management** – manage data sources with rate-limit controls and robots-check audit trail
- **REST API** – fully documented OpenAPI/Swagger interface at `/docs`

---

## 🛠 Tech Stack

| Backend | Frontend |
|---------|----------|
| Python 3.12 | Vue 3 + TypeScript |
| FastAPI | Pinia (state management) |
| SQLAlchemy 2.x async | TanStack Query (server state) |
| Alembic (migrations) | Vue Router 4 |
| PostgreSQL 16 | Leaflet (maps) |
| Redis 7 | Chart.js + vue-chartjs |
| asyncpg | Tailwind CSS 4 |
| structlog | Axios |
| Celery + Redis *(Phase 2)* | Vite 8 |

---

## ☁️ Quick Start (GitHub Codespaces)

The fastest way to try Find My Caravan without installing anything locally.

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/nos86/find-my-caravan)

1. Click the badge above (or **Code → Codespaces → Create codespace on …** from GitHub).
2. Wait ~2 minutes while the container builds and the `post-create.sh` script runs automatically. It will:
   - Install Python 3.12 backend dependencies into a `.venv`
   - Install Node 20 frontend dependencies
   - Create a `.env` file pre-configured for the Codespaces environment
   - Apply the Alembic database migrations
3. Start the backend in the integrated terminal:
   ```bash
   cd backend && source .venv/bin/activate
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```
4. Open a **second terminal** and start the frontend:
   ```bash
   cd frontend && npm run dev -- --host 0.0.0.0
   ```
5. Codespaces will automatically prompt you to open the forwarded **port 5173** in your browser.

> **Tip:** Use the **Run and Debug** panel (`F5`) and select *"Backend: FastAPI (uvicorn)"* for a fully-integrated debugging experience.

---

## 🚀 Quick Start (Docker)

**Prerequisites:** Docker and Docker Compose installed.

```bash
# 1. Clone the repository
git clone https://github.com/nos86/find-my-caravan.git
cd find-my-caravan

# 2. Copy the example env file and set your secrets
cp .env.example .env
# Edit .env and change POSTGRES_PASSWORD and DATABASE_URL password

# 3. Start all services
docker-compose up -d

# 4. Open the app
open http://localhost:5173
```

The backend API is available at **http://localhost:8000** and its interactive docs at **http://localhost:8000/docs**.

---

## 🧑‍💻 Development Setup (manual)

### Backend

Requires **Python 3.12** and a running **PostgreSQL** instance.

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
# Set DATABASE_URL in .env (see .env.example)
alembic upgrade head
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

The dev server starts at **http://localhost:5173** with hot-module replacement.

---

## 🧪 Running Tests

```bash
cd backend
pytest tests/ -v
```

---

## 📖 API Documentation

Interactive Swagger UI: **http://localhost:8000/docs**
ReDoc: **http://localhost:8000/redoc**

---

## 📥 Importing Data

### Via the web UI

Navigate to **http://localhost:5173/import** and upload a CSV or JSON file using the import wizard.

### Via the API

| Format | Endpoint |
|--------|----------|
| CSV | `POST /api/v1/imports/csv` |
| JSON | `POST /api/v1/imports/json` |

**Sample files** are provided in the `backend/` directory:

- `backend/sample_listings.csv`
- `backend/sample_listings.json`

---

## 🔌 Data Sources

The app supports the following source types:

| Type | Description |
|------|-------------|
| `manual` | Listings entered one-by-one through the UI or API |
| `csv` | Bulk import via a comma-separated values file |
| `json` | Bulk import via a JSON file |
| `saved_html` | Parse a locally saved HTML page from a listing site |
| `dealer_website` | Structured scrape of a permitted dealer website |

> **Note on Subito.it:** Due to the platform's terms of service, the Subito.it connector operates only in **manual entry** and **import** mode (no automated crawling). Always respect a site's `robots.txt` and terms before adding it as an automated source.

---

## 🏗 Architecture

```
┌─────────────┐     HTTP/REST     ┌──────────────────────┐
│  Vue 3 SPA  │ ◄───────────────► │  FastAPI (async)     │
│  (port 5173)│                   │  (port 8000)         │
└─────────────┘                   └──────────┬───────────┘
                                             │ asyncpg
                                   ┌─────────▼──────────┐
                                   │   PostgreSQL 16     │
                                   └────────────────────┘
                                             │
                                   ┌─────────▼──────────┐
                                   │    Redis 7          │
                                   │  (cache / Phase 2   │
                                   │   Celery broker)    │
                                   └────────────────────┘
```

- **Backend:** FastAPI + SQLAlchemy 2.x async + Alembic + PostgreSQL
- **Frontend:** Vue 3 + TypeScript + Pinia + TanStack Query + Leaflet + Chart.js
- **Background tasks:** Celery + Redis *(planned for Phase 2 – automated scraping)*

---

## 🗺 Geographic Scope

Listings are scoped to **Northern and Central Italy**, covering these 13 regions:

1. Valle d'Aosta
2. Piemonte
3. Liguria
4. Lombardia
5. Trentino-Alto Adige
6. Veneto
7. Friuli-Venezia Giulia
8. Emilia-Romagna
9. Toscana
10. Marche
11. Umbria
12. Lazio
13. Abruzzo

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Commit your changes: `git commit -m "feat: add my feature"`
4. Push to the branch: `git push origin feature/my-feature`
5. Open a Pull Request

Please keep commits small and focused, and ensure `pytest tests/ -v` passes before opening a PR.

---

## 📄 License

This project is licensed under the **MIT License** – see the [LICENSE](LICENSE) file for details.
