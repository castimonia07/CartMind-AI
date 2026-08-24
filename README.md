# CartMind AI
**Context-Aware Voice Shopping & Decision Agent**

CartMind AI is an advanced shopping assistant that understands natural language context, manages a smart shopping basket, provides AI-driven product recommendations with trade-offs, and optimizes your cart based on hard constraints (like budget) and soft preferences.

## Architecture

- **Backend:** FastAPI, Python, PostgreSQL, SQLAlchemy
- **Frontend:** React, Vite, Tailwind CSS, Framer Motion, Zustand
- **AI Engines:**
  - Intent & Entity Extraction (Parses natural language into structured JSON)
  - Command Router (Routes to Fast Shopping Mode or Decision Mode)
  - Recommendation Engine (Calculates Pareto trade-offs based on user preferences)
  - Constraint Engine (Filters candidates by hard constraints)
  - Optimization Engine (Knapsack-style budget optimization)
  - Substitution Engine (Finds similar products)
- **Real-time:** WebSockets for state streaming

## Setup

### Prerequisites
- Python 3.10+
- Node.js 18+
- PostgreSQL (or use the fallback SQLite by modifying `DATABASE_URL` in `.env`)
- Docker (optional)

### Environment Variables
Copy `backend/.env.example` to `backend/.env` and update the keys.

### Running Locally (Without Docker)

**Backend:**
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # (Windows)
pip install -r requirements.txt
python seed\seed_data.py  # Seed the database
uvicorn app.main:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```
Access the UI at `http://localhost:5173`.

### Running with Docker
```bash
docker compose up --build
```

## Demo Scenarios
1. **Basic Addition:** Click the mic and say "Add 2kg rice" (Fast Path)
2. **Complex Decision:** "I need a laptop for machine learning under 80000" (Decision Path)
3. **Budget Optimization:** Open the smart basket and click "Optimize Basket" when over budget.

## Future Improvements
- LLM API integration (currently using deterministic regex/mock intents for speed & safety in dev)
- Full text search using `pgvector`
- Advanced speech-to-text integration (Whisper)
