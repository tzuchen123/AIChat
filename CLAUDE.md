# CLAUDE.md

## Project Overview
AI Chat Platform — A production-grade real-time AI chat backend demonstrating scalable architecture,
database optimization, and AI streaming integration.
Built with Python FastAPI, MySQL, WebSocket, and OpenAI API.

---

## Goal
Build a complete backend system where users can:
1. Register and login (JWT auth)
2. Create and manage conversations
3. Send messages and receive real-time AI responses via WebSocket streaming
4. View conversation history

---

## Tech Stack
- **Framework:** FastAPI
- **Runtime:** Python 3.11+
- **Database:** MySQL 8 + SQLAlchemy (async) + Alembic (migrations)
- **Auth:** JWT (python-jose) + bcrypt (passlib)
- **AI:** OpenAI API (GPT-4) with streaming
- **Real-time:** FastAPI native WebSocket
- **Validation:** Pydantic v2
- **Container:** Docker + Docker Compose
- **CI/CD:** GitHub Actions → AWS EC2
- **Testing:** pytest + httpx

---

## Architecture Design (Scalability & Maintainability)

This project follows a **Layered Architecture** to ensure flexibility, scalability, and maintainability:

```
Router Layer      → HTTP/WebSocket handling only, no business logic
Service Layer     → All business logic, reusable across routers
Repository Layer  → All DB queries, abstracted from services
Model Layer       → SQLAlchemy ORM definitions
Schema Layer      → Pydantic request/response validation
```

### Why this matters:
- **Scalability:** Services are stateless and can be horizontally scaled
- **Maintainability:** Each layer has a single responsibility, easy to modify independently
- **Testability:** Services can be unit tested without HTTP layer
- **Flexibility:** DB or AI provider can be swapped with minimal changes

---

## Project Structure to Generate
```
ai-chat-platform/
├── src/
│   ├── config/
│   │   ├── database.py         # Async SQLAlchemy engine, session factory, connection pool config
│   │   └── settings.py         # Pydantic BaseSettings (.env loader)
│   ├── routers/
│   │   ├── auth.py             # POST /api/auth/register, /api/auth/login
│   │   ├── chat.py             # GET/POST/DELETE /api/chat
│   │   └── message.py          # GET/POST /api/messages/{conversation_id}
│   ├── models/
│   │   ├── user.py             # SQLAlchemy User model with indexes
│   │   ├── conversation.py     # SQLAlchemy Conversation model with indexes
│   │   └── message.py          # SQLAlchemy Message model with indexes
│   ├── schemas/
│   │   ├── auth.py             # RegisterRequest, LoginRequest, TokenResponse
│   │   ├── chat.py             # ConversationCreate, ConversationResponse
│   │   ├── message.py          # MessageCreate, MessageResponse
│   │   └── common.py           # StandardResponse wrapper { success, data, error }
│   ├── services/
│   │   ├── auth_service.py     # register, login, hash/verify password
│   │   ├── chat_service.py     # CRUD for conversations
│   │   ├── message_service.py  # save and retrieve messages
│   │   └── openai_service.py   # stream OpenAI response, manage context window
│   ├── repositories/
│   │   ├── user_repo.py        # DB queries for users
│   │   ├── chat_repo.py        # DB queries for conversations
│   │   └── message_repo.py     # DB queries for messages (pagination support)
│   ├── middlewares/
│   │   ├── auth.py             # get_current_user FastAPI Depends()
│   │   └── cors.py             # CORS config for frontend integration
│   ├── websocket/
│   │   └── chat.py             # WebSocket endpoint, stream AI response, handle disconnect
│   └── main.py                 # FastAPI app, include routers, middleware setup
├── alembic/
│   └── versions/               # Migration files
├── tests/
│   ├── test_auth.py
│   ├── test_chat.py
│   └── test_message.py
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml
├── .github/
│   └── workflows/
│       └── ci.yml
├── alembic.ini
├── requirements.txt
├── .env.example
└── CLAUDE.md
```

---

## Database Schema & Optimization

### users
```sql
id                INT PRIMARY KEY AUTO_INCREMENT
username          VARCHAR(50) UNIQUE NOT NULL
email             VARCHAR(100) UNIQUE NOT NULL
hashed_password   VARCHAR(255) NOT NULL
created_at        DATETIME DEFAULT CURRENT_TIMESTAMP

INDEX idx_email (email)         ← fast login lookup
INDEX idx_username (username)   ← fast uniqueness check
```

### conversations
```sql
id          INT PRIMARY KEY AUTO_INCREMENT
user_id     INT NOT NULL (FK → users.id ON DELETE CASCADE)
title       VARCHAR(100)
created_at  DATETIME DEFAULT CURRENT_TIMESTAMP

INDEX idx_user_id (user_id)     ← fast user conversation listing
```

### messages
```sql
id              INT PRIMARY KEY AUTO_INCREMENT
conversation_id INT NOT NULL (FK → conversations.id ON DELETE CASCADE)
role            ENUM('user', 'assistant') NOT NULL
content         TEXT NOT NULL
created_at      DATETIME DEFAULT CURRENT_TIMESTAMP

INDEX idx_conversation_id (conversation_id)              ← fast history fetch
INDEX idx_conv_created (conversation_id, created_at)     ← optimized for sorted pagination
```

### DB Performance Notes (explain in interview):
- All foreign keys have indexes to avoid full table scans on JOINs
- `ON DELETE CASCADE` keeps data consistent without manual cleanup
- Composite index on `(conversation_id, created_at)` supports efficient paginated message queries
- Connection pool configured in `database.py`: `pool_size=10, max_overflow=20`

---

## API Endpoints

### Auth
```
POST /api/auth/register   body: { username, email, password }
POST /api/auth/login      body: { email, password } → returns { access_token, token_type }
```

### Chat (JWT required)
```
GET    /api/chat              → list all conversations for current user
POST   /api/chat              body: { title } → create conversation
DELETE /api/chat/{id}         → delete conversation
```

### Messages (JWT required)
```
GET  /api/messages/{conversation_id}?page=1&limit=20  → paginated message history
POST /api/messages/{conversation_id}  body: { content } → send message, save both user msg and AI response
```

### WebSocket
```
WS /ws/{conversation_id}?token=<JWT>

Server emits:
{ "type": "stream_chunk", "content": "..." }   ← one per token
{ "type": "stream_end", "message_id": 123 }    ← when done
{ "type": "error", "detail": "..." }
```

---

## Standardized Response Format
All REST API responses must follow this format for consistent frontend integration:

```json
// Success
{ "success": true, "data": { ... } }

// Error
{ "success": false, "error": { "code": "UNAUTHORIZED", "message": "..." } }
```

Define this in `schemas/common.py` as a generic Pydantic model and use as `response_model` on all endpoints.

---

## Performance Considerations

### Async DB
- Use `AsyncSession` from SQLAlchemy for all DB operations
- Never use blocking calls inside async routes
- Configure connection pool: `pool_size=10, max_overflow=20, pool_pre_ping=True`

### OpenAI Streaming
- Use `async for chunk in response` pattern to stream tokens
- Send each chunk immediately via WebSocket without buffering
- Save full AI response to DB only after stream ends

### Pagination
- All list endpoints support `page` and `limit` query params
- Default: `limit=20`, Max: `limit=100`
- Use `offset` with SQLAlchemy for implementation

---

## CORS Configuration (Frontend Integration)
Configure in `middlewares/cors.py`:
```python
allow_origins=["http://localhost:3000", "https://your-frontend-domain.com"]
allow_methods=["GET", "POST", "PUT", "DELETE"]
allow_headers=["Authorization", "Content-Type"]
```

---

## Code Conventions
- Use `async/await` everywhere (routers, services, DB calls)
- Routers only handle HTTP — all logic goes in `services/`
- DB queries only in `repositories/` — services never query DB directly
- Use `Depends()` for auth and DB session injection
- All endpoints must define `response_model` with Pydantic schema
- Raise `HTTPException` for all errors with proper status codes
- Use `bcrypt` for password hashing, never store plain text

---

## Environment Variables (.env)
```
PORT=8000
DB_HOST=localhost
DB_PORT=3306
DB_NAME=ai_chat_db
DB_USER=root
DB_PASSWORD=
JWT_SECRET=your_secret_key
JWT_EXPIRES_DAYS=7
OPENAI_API_KEY=
```

---

## Docker Setup
- `Dockerfile`: Python 3.11 slim, install requirements, run uvicorn
- `docker-compose.yml`: app + mysql services, env_file .env, healthcheck on mysql

## CI/CD (GitHub Actions)
- On push to `main`: install deps → run pytest → SSH into EC2 → docker compose up -d --build

## Git Branching
- `main` → production, auto-deployed
- `develop` → integration branch
- `feature/xxx` → new features (branch from develop)
- `hotfix/xxx` → urgent production fixes

---

## Important Rules
- Never commit `.env`
- Always branch from `develop` for new features
- WebSocket must handle client disconnect gracefully with try/finally
- Never remove DB indexes
- Repository layer must never leak SQLAlchemy models to routers — always convert to Pydantic schemas in service layer
- OpenAI context: pass last 10 messages as context to avoid token limit issues
