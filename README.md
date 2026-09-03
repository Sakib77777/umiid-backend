# Umiid Backend

Backend API for **Umiid** — *"Your mental well-being, our priority."*

An AI-assisted mental well-being platform, originally built for Smart India Hackathon (internally referred to as ECHOCORE) as a Real-Time Multimodal Emotional Distress Signal Intelligence System.

> This is a decision-support tool intended to help trained counselors — **not** a medical diagnostic system or a replacement for human counselors.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | Python + FastAPI |
| Auth & Database | Firebase Authentication + Cloud Firestore |
| Email (OTP delivery) | Gmail SMTP |

---

## Project Structure

```
backend/
├── app/
│   ├── main.py                   # FastAPI app entry point, wires up routers
│   ├── firebase.py               # Firebase Admin SDK init, exports `db`
│   ├── config.py                 # Loads .env values
│   │
│   ├── routes/                   # API endpoints
│   │   ├── auth.py
│   │   ├── users.py
│   │   ├── sessions.py
│   │   ├── analysis.py           # placeholder — future AI features
│   │   └── reports.py            # placeholder — future reporting features
│   │
│   ├── services/                 # Business logic
│   │   ├── auth_service.py
│   │   ├── user_service.py
│   │   ├── counseling_service.py
│   │   ├── session_service.py
│   │   ├── email_service.py
│   │   ├── analysis_service.py   # placeholder
│   │   └── report_service.py     # placeholder
│   │
│   ├── models/                   # Pydantic request/response schemas
│   │   ├── auth_models.py
│   │   ├── user_models.py
│   │   ├── session_models.py
│   │   ├── counseling_session_models.py
│   │   └── analysis_models.py    # placeholder
│   │
│   ├── ai/                       # Reserved for future AI pipeline (Phase 2+)
│   │
│   ├── utils/
│   │   ├── validators.py         # password strength rules
│   │   ├── common_passwords.py   # blocklist
│   │   └── security.py           # OTP generation, hashing, verification
│   │
│   └── dependencies/
│       └── auth.py               # get_current_uid — verifies Bearer tokens
│
├── credentials/                  # Firebase service account JSON (NOT in git)
├── .env                          # Secrets (NOT in git)
├── .env.example                  # Template — safe to commit
├── .gitignore
└── requirements.txt
```

---

## Setup

### 1. Clone the repo
```bash
git clone <repo-url>
cd backend
```

### 2. Create a virtual environment
```bash
python -m venv venv
venv\Scripts\Activate.ps1      # Windows PowerShell
# source venv/bin/activate     # macOS/Linux
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Get the secrets
Ask Sakib directly — **never shared via GitHub.**

- Copy `.env.example` → `.env` and fill in:
  - `FIREBASE_WEB_API_KEY`
  - `GMAIL_ADDRESS`
  - `GMAIL_APP_PASSWORD`
- Place the Firebase service account JSON in `credentials/`

### 5. Run the server
```bash
python -m uvicorn app.main:app --reload
```

### 6. Test the API
Open `http://127.0.0.1:8000/docs` for the interactive Swagger UI — every endpoint can be tested there directly.

**Testing from Android:**
```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0
```
| Target | Base URL |
|---|---|
| Android emulator | `http://10.0.2.2:8000` |
| Real device (same Wi-Fi) | `http://<your-machine-local-ip>:8000` |

---

## API Reference

### Authentication — `/auth`

| Endpoint | Method | Notes |
|---|---|---|
| `/auth/register` | POST | Creates Firebase Auth account + Firestore profile |
| `/auth/login` | POST | Accepts `identifier` (email **or** phone) + `password` |
| `/auth/me` | GET | Returns the logged-in user's profile |
| `/auth/forgot-password` | POST | Sends a 4-digit OTP via Gmail (expires in 1 min) |
| `/auth/verify-otp` | POST | Verifies the OTP |
| `/auth/reset-password` | POST | Sets new password after OTP verification |
| `/auth/refresh-token` | POST | Exchanges `refresh_token` for a new `id_token` |
| `/auth/sessions` | GET | Returns the user's active login session |
| `/auth/logout` | POST | Ends the login session |

**Password rules:** 6–16 characters, must include a digit and a special character. Rejected if it's a common password, contains a predictable sequence (e.g. `1234`, `qwerty`), or contains the user's own name, email, or phone number.

**OTP security:** OTPs are never stored in plaintext — hashed with SHA-256 before writing to Firestore, and verified using a constant-time comparison to prevent timing attacks.

> **Login sessions ≠ counseling sessions.** `/auth/sessions` tracks login/device sessions only (one active session per user, no `device_id` needed). This is unrelated to the counseling session lifecycle below.

### User Profiles — `/users`

| Endpoint | Method | Notes |
|---|---|---|
| `/users/me` | PUT | Update name, phone, or profile photo URL |

Profile photo uploads happen client-side to Firebase Storage — the backend only stores the resulting URL.

### Counseling Sessions — `/sessions`

| Endpoint | Method | Notes |
|---|---|---|
| `/sessions/start` | POST | Starts a session between two existing users |
| `/sessions/{id}/end` | POST | Marks a session completed |
| `/sessions/{id}` | GET | Fetch one session (must be a participant) |
| `/sessions` | GET | List all sessions the caller is part of |

No client/counselor role distinction yet — intentionally deferred until the team finalizes role design.

---

## Frontend Integration Notes

- **Auth header:** protected endpoints require `Authorization: Bearer <id_token>`
- **Silent auto-refresh:** on a `401`, call `/auth/refresh-token` in the background and retry — don't force the user to log in again. Only log out if the refresh itself fails (invalid/revoked `refresh_token`).
- **Token rotation:** every `/auth/refresh-token` call returns a **new** `id_token` **and** a **new** `refresh_token` — always save both; never reuse the old `refresh_token`.
- `id_token`s expire after 1 hour (fixed by Firebase, cannot be changed) — invisible to the user as long as silent refresh is implemented.

---

## Not Yet Built

- Client/counselor roles
- Fake/simulated AI analysis endpoint (Phase 1 of AI integration)
- Real speech-to-text, voice analysis, text analysis, multimodal fusion
- Emotional Threat Score (ETS), timeline, contradiction/escalation detection, Counselor Copilot
- Reports, audit trail
- Video calls, counselor/rehab-center map, marketplace, SC/ST sensitive-case module

---

## Security Notes

- `.env` and `credentials/*.json` are gitignored — **never commit these**, even to a private repo
- Share real secrets with teammates directly (chat, password manager) — never through GitHub
- Logout currently only clears the tracked session record; it does not revoke the underlying Firebase token (tokens expire naturally within 1 hour)