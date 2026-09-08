# Smart Greenhouse
A simple Smart Greenhouse application built with FastAPI, PostgreSQL, React, and TypeScript.

## Prerequisites
- Python 3.11+
- Node.js
- Docker

## First-time setup

### Backend
```bash
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
alembic upgrade head
```

### Frontend
```bash
cd frontend
npm install
```

## Daily Start
Open three terminals.

### Terminal 1 - Database
```bash
docker compose up -d
```

### Terminal 2 - Backend
```bash
cd backend
.venv\Scripts\Activate.ps1
cd src
uvicorn main:app --reload --port 8000
```

### Terminal 3 - Frontend
```bash
cd frontend
npm run dev
```

## URLs
- API: http://localhost:8000
- Scalar: http://localhost:8000/scalar
- OpenAPI: http://localhost:8000/openapi.json
- UI: http://localhost:5173
