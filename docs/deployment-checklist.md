# DEPLOYMENT CHECKLIST & PRODUCTION RUNBOOK — e-BIS SAHAYAK

**Target Operating Systems:** Windows / Linux (Ubuntu 22.04 LTS / Debian 12)  
**Dependencies:** Python 3.11+ / Node.js 18.17+ / Next.js 14  
**Date:** October 10, 2026

---

## 1. Quick-Start Local Launch

To start both Backend and Frontend in development mode on Windows:

```cmd
:: From the project root
start.bat
```

`start.bat` executes preflight verification, starts FastAPI on `http://127.0.0.1:8000`, and starts Next.js on `http://localhost:3000`.

---

## 2. Manual Step-by-Step Setup

### Backend:
```bash
# 1. Navigate to backend directory
cd backend

# 2. Create and activate virtual environment
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run preflight check
python app/preflight.py

# 5. Start development server
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Frontend:
```bash
# 1. Navigate to frontend directory
cd frontend

# 2. Install dependencies
npm install

# 3. Create .env.local if not present
echo NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api/v1 > .env.local

# 4. Build and start production bundle
npm run build
npm run start
```

---

## 3. Production Readiness Verification Checklist

- [x] Environment configuration validated via `preflight.py`.
- [x] Backend unit & integration test suite passing (`pytest backend/tests/`).
- [x] Frontend Next.js production build passing with 0 errors (`npm run build`).
- [x] Direct Groq API integration configured with bounded timeouts and exponential backoff.
- [x] Zero vector database / zero embedding dependencies in deployment manifest.
- [x] Administrative endpoints protected with constant-time authentication.
- [x] Full laboratory dataset (576 facilities) verified and indexed.
- [x] 100% key parity across English, Hindi, and Tamil translation dictionaries.
- [x] Response scrubbing active to prevent API key leakage in production logs.
