<div align="center">

# 🌊 ORCA

**Marine EcOsystem Reasoning with Collaborative Agents**

*Conversational Marine Intelligence — Weather · Fishing Zones · Safety · Routing*

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.136-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-PostGIS-336791?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org)
[![MongoDB](https://img.shields.io/badge/MongoDB-Motor-47A248?style=for-the-badge&logo=mongodb&logoColor=white)](https://www.mongodb.com)
[![LangChain](https://img.shields.io/badge/LangChain-AI-1C3C3C?style=for-the-badge&logo=chainlink&logoColor=white)](https://langchain.com)
[![LangGraph](https://img.shields.io/badge/LangGraph-Agents-1C3C3C?style=for-the-badge)](https://langchain-ai.github.io/langgraph/)
[![JWT](https://img.shields.io/badge/Auth-JWT-000000?style=for-the-badge&logo=jsonwebtokens&logoColor=white)](https://jwt.io)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](CONTRIBUTING.md)

[API Docs](#) · [Report Bug](issues) · [Request Feature](issues)

</div>

---

## 📌 Overview

**ORCA** is a conversational Marine Intelligence Assistant that helps users understand complex marine information — weather, ocean conditions, Potential Fishing Zones (PFZ), satellite observations, and marine warnings — through natural language, instead of searching across multiple platforms.

Ask ORCA a question like:

> "Can I safely go to the nearest fishing zone tomorrow morning?"

...and a network of collaborative agents identifies what's needed, gathers the relevant marine data, analyzes risk, and returns a clear recommendation — complete with a map and a safer route when required.

> Built as a multi-agent, LLM-powered platform demonstrating end-to-end product engineering — REST APIs, async databases, geospatial reasoning, LangGraph agent orchestration, and human-in-the-loop decision flows.

---

## ✨ Features

<details>
<summary><b>🧭 Marine Intelligence Chat</b></summary>

- Natural language questions about weather, sea state, and safety
- Session-based conversations with history, pinning, and archiving
- Context-aware follow-ups within a session
- Human-in-the-loop confirmation before committing to a plan

</details>

<details>
<summary><b>🎣 Fishing Zone & Safety Analysis</b></summary>

- Identifies candidate Potential Fishing Zones (PFZ) near a location
- Combines weather, wind, and wave data per zone
- Runs each candidate through a risk engine
- Returns a ranked Top 5 list of safe, favourable zones

</details>

<details>
<summary><b>🗺️ Routing & Maps</b></summary>

- Generates a safer route to a selected fishing zone
- Marine zone lookups via geospatial queries
- Save, list, retrieve, and delete personal maps
- Route and zone data ready for map rendering on the frontend

</details>

<details>
<summary><b>🔐 Authentication</b></summary>

- JWT-based register, login, and logout
- Secure password hashing (bcrypt / passlib)
- `GET /auth/me` for current-user context
- Bearer-token protected routes throughout the API

</details>

<details>
<summary><b>👤 Profile & Sessions</b></summary>

- User profile retrieval and updates
- Full session lifecycle: create, list, update, delete
- Pin and archive sessions for quick access later

</details>

---

## 🧠 How ORCA Works

```
User Question
      ↓
Understand the Request
      ↓
Find Relevant Marine Information
      ↓
Combine & Analyze Information
      ↓
Risk / Route Analysis
      ↓
Generate Recommendation
      ↓
Text + Map + Route
```

### Agent Architecture

```
                         USER
                           │
                           ▼
                    ┌─────────────┐
                    │  Chat API   │
                    │  FastAPI    │
                    └──────┬──────┘
                           │
                     session_id
                           │
                           ▼
                    ┌─────────────┐
                    │ Agent State │
                    └──────┬──────┘
                           │
                           ▼
                    ┌─────────────┐
                    │Orchestrator │
                    └──────┬──────┘
                           │
             ┌─────────────┼─────────────┐
             ▼             ▼             ▼
         GENERAL        SAFETY        PLANNING
             │             │             │
             │             └──────┬──────┘
             │                    │
             │             Time + Location
             │                    │
             │                    ▼
             │             PFZ Candidates
             │                    │
             │                    ▼
             │         DATA COLLECTION AGENT
             │                    │
             │          Marine / Weather /
             │          Geospatial functions
             │                    │
             │                    ▼
             │               agent_data
             │                    │
             │                    ▼
             │              RISK ENGINE
             │                    │
             │              risk_result
             │                    │
             │                    ▼
             │                 TOP 5
             │                    │
             │                    ▼
             │             HUMAN-IN-THE-LOOP
             │                    │
             │             selected_pfz
             │                    │
             │                    ▼
             │              ROUTE ENGINE
             │                    │
             │              route_result
             │                    │
             └────────────────────┤
                                  ▼
                           FINAL RESPONSE
                                  │
                                  ▼
                               FRONTEND
                                  │
                                  ▼
                              MAP / PLAN
                                  │
                         User Accepts / Saves
                                  │
                                  ▼
                              DATABASE
```

---

## 🗂 Project Structure

```
ORCA/
│
├── backend/                     # FastAPI application (REST API layer)
│   ├── routes/                  # auth, session, chat, profile, maps
│   ├── schemas/                 # Pydantic request/response models
│   ├── services/                # business logic per domain
│   ├── models/                  # SQLAlchemy ORM models
│   ├── database/
│   │   └── database.py          # async Postgres engine/session
│   ├── core/
│   │   └── exceptions.py
│   ├── config/
│   │   └── logging.py
│   ├── utils/
│   │   └── auth_util.py         # JWT creation/verification
│   ├── requirements.txt
│   └── main.py                  # FastAPI app entrypoint
│
├── ai/                           # LangGraph multi-agent reasoning core
│   ├── orchestrator.py          # routes requests to GENERAL/SAFETY/PLANNING
│   ├── agent_state.py
│   ├── graph/                   # graph.py, nodes.py, routing.py
│   ├── agents/
│   │   └── general_agent/
│   ├── engines/
│   │   ├── data_collection_engine/
│   │   ├── risk_engine/         # engine.py, scoring.py, validator.py
│   │   └── route_engine/        # pathfinding.py, geometry.py, graph.py
│   ├── prompts/                 # orchestrator, time, summary prompts
│   ├── schemas/                 # agent_response, location, time
│   ├── services/
│   │   └── conversation_summary.py
│   ├── tools/                   # geo_tools, marine_tools, weather_tools, risk_helper
│   └── configs/
│       └── config.py
│
├── api/                          # thin wrappers over external data providers
│   ├── marine/marine.py
│   └── weather/weather.py
│
├── services/                     # shared/support services used by ai + backend
│   ├── location/                 # marine_zones, pfz_to_coordinate, place_to_coordinate
│   ├── time/time_parser.py
│   ├── risk_engine_service/      # location_service, marine_batch, weather_batch
│   ├── marine_data.py
│   ├── marine_data_sources.py    # MongoDB-backed PFZ storage
│   └── weather_data.py
│
├── data/
│   └── restricted_zones/restricted_zones.json
│
├── frontend/                     # React 19 + Vite + Tailwind SPA
│   ├── src/
│   │   ├── features/             # auth, chat, landing, maps
│   │   ├── pages/                # login, register, ProfilePage, MapsPage
│   │   ├── components/           # chat, common, layout
│   │   ├── services/              # api.js, authApi.js, mapsApi.js
│   │   └── utils/risk.js
│   ├── package.json
│   └── vite.config.js
│
├── test/                         # pytest suites mirroring ai/ and services/
│   ├── agent_test/ graph_test/ integration_test/ orchestrator_test/
│   ├── risk_engine_test/ risk_helper_test/ route_engine_test/
│   └── test_pfz*.py, test_marine_agent.py, test_data_collection.py
│
├── Dockerfile                    # backend image (uvicorn + Postgres client)
├── docker-compose.yml            # backend + Postgres services
├── .env.example
└── package.json
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- PostgreSQL with PostGIS (geospatial queries)
- MongoDB instance (accessed via `motor`)
- A Groq API key (for `langchain-groq`)

---

### Installation

```bash
# 1. Clone the repository
git clone <repository-url>
cd orca

# 2. Create virtual environment
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment variables
cp .env.example .env
# Edit .env with your values

# 5. Run database migrations
alembic upgrade head

# 6. Run the application
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`, with interactive docs at `http://localhost:8000/docs`.

---

## 🔑 Environment Variables

Create a `.env` file in the project root:

```env
# PostgreSQL (PostGIS-enabled)
DATABASE_URL=postgresql+asyncpg://username:password@localhost:5432/orca_db

# MongoDB
MONGO_URL=mongodb://localhost:27017
MONGO_DB_NAME=orca

# Auth
SECRET_KEY=your_super_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# AI / LLM
GROQ_API_KEY=your_groq_api_key

# External marine/weather data sources
MARINE_DATA_API_KEY=your_provider_api_key
WEATHER_API_KEY=your_provider_api_key
```

| Variable | Required | Description |
|---|---|---|
| `DATABASE_URL` | ✅ | Async PostgreSQL/PostGIS connection string |
| `MONGO_URL` | ✅ | MongoDB connection URI |
| `SECRET_KEY` | ✅ | JWT signing secret |
| `ALGORITHM` | ✅ | JWT algorithm — typically `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | ✅ | Token TTL in minutes |
| `GROQ_API_KEY` | 🤖 | Groq LLM API key for agent reasoning |
| `MARINE_DATA_API_KEY` | 🌊 | Marine conditions / PFZ data provider |
| `WEATHER_API_KEY` | ⛅ | Weather forecast data provider |

---

## 📡 API Reference

Full interactive docs available at `/docs` after running the backend.

### Auth
| Method | Endpoint | Description |
|---|---|---|
| POST | `/auth/register` | Register a new user |
| POST | `/auth/login` | Log in and receive an access token |
| GET | `/auth/me` | Get the current authenticated user |
| POST | `/auth/logout` | Log out the current user |

### Sessions
| Method | Endpoint | Description |
|---|---|---|
| POST | `/sessions` | Create a new session |
| GET | `/sessions` | List sessions |
| GET | `/sessions/pinned` | List pinned sessions |
| POST | `/sessions/{session_id}/pin` | Pin a session |
| DELETE | `/sessions/{session_id}/pin` | Unpin a session |
| GET | `/sessions/archived` | List archived sessions |
| POST | `/sessions/{session_id}/archive` | Archive a session |
| DELETE | `/sessions/{session_id}/archive` | Unarchive a session |
| GET | `/sessions/{session_id}` | Get a session by ID |
| PATCH | `/sessions/{session_id}` | Update a session |
| DELETE | `/sessions/{session_id}` | Delete a session |

### Chat
| Method | Endpoint | Description |
|---|---|---|
| POST | `/chat` | Send a message to the assistant |
| POST | `/chat/{session_id}/resume` | Resume a chat session |
| GET | `/chat/{session_id}/history` | Get chat history for a session |

### Profile
| Method | Endpoint | Description |
|---|---|---|
| GET | `/profile` | Get the current user's profile |
| PATCH | `/profile` | Update the current user's profile |

### Maps
| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/routes/generate` | Generate a route to a selected location |
| GET | `/api/marine-zones` | Get marine zone data |
| POST | `/api/maps` | Create a saved map |
| GET | `/api/maps` | List saved maps |
| GET | `/api/maps/{map_id}` | Get a saved map by ID |
| DELETE | `/api/maps/{map_id}` | Delete a saved map |

---

## 🤖 AI / Agent Pipeline

ORCA's reasoning is handled by a set of collaborative **LangGraph** agents coordinated by an orchestrator:

- **Orchestrator** — routes each request to `GENERAL`, `SAFETY`, or `PLANNING` handling
- **Safety Agent** — assesses whether current/forecast conditions are safe for a given time and location
- **Planning Agent** — resolves time + location into a set of PFZ candidates
- **Data Collection Agent** — gathers marine, weather, and geospatial data per candidate
- **Risk Engine** — scores each candidate and returns a ranked Top 5
- **Human-in-the-Loop** — user selects a PFZ from the ranked list
- **Route Engine** — generates a safer route to the selected zone

---

## 🔒 Security

| Feature | Implementation |
|---|---|
| Password hashing | `bcrypt` via `passlib` |
| Token auth | JWT (HS256) with expiry |
| SQL injection | Prevented via SQLAlchemy ORM |
| Input validation | Pydantic schemas on every request |

---

## 🔮 Future Improvements

- [ ] 📱 Mobile-friendly client
- [ ] 🔔 Real-time marine warning alerts
- [ ] 🛰️ Direct satellite observation ingestion
- [ ] 🌍 Multi-language support for coastal communities
- [ ] 📊 Historical trend dashboard for a given zone
- [ ] 🧭 Offline-capable route caching

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!

```bash
# Fork the repo, then:
git checkout -b feature/your-feature-name
git commit -m "feat: add your feature"
git push origin feature/your-feature-name
# Open a Pull Request
```

Please follow the existing code style and add relevant tests where applicable.

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

<div align="center">

Built by the ORCA Team

**[⬆ Back to top](#-orca)**

</div>
