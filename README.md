# 🤖 AI Chat Platform

> 一個具備即時 AI 對話功能的後端系統，展示後端架構設計、資料庫優化與 AI 串接能力。
---

## ✨ 專案亮點

### 🏗️ 分層架構設計
採用 **Router → Service → Repository** 三層架構：
- Router 只處理 HTTP，不含業務邏輯
- Service 封裝所有業務邏輯，可跨 Router 複用
- Repository 統一管理所有 DB 查詢，方便維護與測試
- 展示對「可擴展、可維護」系統設計的理解

### ⚡ 非同步高效能
- 全程使用 `async/await`，搭配 SQLAlchemy AsyncSession
- MySQL 連線池設定（pool_size=10, max_overflow=20）
- 確保高併發下的穩定回應效能

### 💬 WebSocket 即時串流
- 用戶送出訊息後，AI 回應逐字即時串流回傳
- 體驗與 ChatGPT 相同的打字機效果
- 完整處理 WebSocket 連線中斷事件

### 🗄️ 資料庫優化設計
- 針對高頻查詢欄位建立 Index（conversation_id、user_id）
- 複合索引 `(conversation_id, created_at)` 支援高效分頁查詢
- ON DELETE CASCADE 維護資料一致性
- 訊息列表支援分頁（page + limit）

### 📄 自動 API 文件
- FastAPI 內建 Swagger UI，部署後即可互動測試所有 API
- 所有 endpoint 均定義 Pydantic response_model，型別安全有保障

### 🐳 容器化與 CI/CD
- Docker Compose 一鍵啟動完整環境（app + MySQL）
- GitHub Actions 自動化測試與部署至 AWS EC2

---

## 🛠️ 技術棧

| 層級 | 技術 |
|------|------|
| 語言 | Python 3.11 |
| 框架 | FastAPI |
| 即時通訊 | FastAPI WebSocket |
| 資料庫 | MySQL 8 + SQLAlchemy (async) |
| Migration | Alembic |
| 驗證 | JWT (python-jose) + bcrypt (passlib) |
| AI 串接 | OpenAI API / Anthropic Claude API |
| 資料驗證 | Pydantic v2 |
| 容器化 | Docker + Docker Compose |
| CI/CD | GitHub Actions → AWS EC2 |
| API 文件 | Swagger UI（內建） |

---

## 📐 系統架構

```
┌─────────────┐        ┌─────────────────────────────────────┐
│   Client    │──HTTP──▶  FastAPI Router                     │
│             │        │  /api/auth  /api/chat  /api/messages│
│             │──WS────▶  WebSocket /ws/{conversation_id}    │
│             │               └──▶ AI Stream（逐字回傳）      │
└─────────────┘        └──────────────┬──────────────────────┘
                                       │
                               ┌───────▼────────┐
                               │  MySQL         │
                               │  users         │
                               │  conversations │
                               │  messages      │
                               └────────────────┘
```

---

## 📂 專案結構

```
src/
├── config/         # 資料庫連線、環境變數設定
├── routers/        # HTTP 路由（auth、chat、message）
├── models/         # SQLAlchemy ORM 模型
├── schemas/        # Pydantic 請求／回應驗證
├── services/       # 業務邏輯層
├── repositories/   # 資料庫查詢層
├── middlewares/    # JWT 驗證、CORS 設定
├── websocket/      # WebSocket 串流處理
└── main.py
```

---

## ⚡ 快速啟動

```bash
# 1. 複製環境變數
cp .env.example .env
# 填入 DB_PASSWORD、JWT_SECRET、OPENAI_API_KEY 或 ANTHROPIC_API_KEY

# 2. 啟動 MySQL
docker compose -f docker/docker-compose.yml up -d

# 3. 執行資料庫 migration
alembic upgrade head

# 4. 啟動伺服器
uvicorn src.main:app --reload

# 5. 開啟 API 文件
# http://localhost:8000/docs
```

---

## 📡 API 一覽

### 驗證
```
POST /api/auth/register   註冊帳號
POST /api/auth/login      登入，回傳 JWT token
```

### 對話管理（需帶 JWT）
```
GET    /api/chat          取得所有對話列表
POST   /api/chat          建立新對話
DELETE /api/chat/{id}     刪除對話
```

### 訊息（需帶 JWT）
```
GET  /api/messages/{conversation_id}?page=1&limit=20   取得對話歷史
POST /api/messages/{conversation_id}                   送出訊息，觸發 AI 回應
```

### WebSocket
```
WS /ws/{conversation_id}?token=<JWT>

Server 回傳：
{ "type": "stream_chunk", "content": "..." }   ← 逐字串流
{ "type": "stream_end",   "message_id": 123 }  ← 串流結束
{ "type": "error",        "detail": "..." }
```

---

## 🗄️ 資料庫設計

```sql
users           → id, username, email, hashed_password, created_at
conversations   → id, user_id (FK), title, created_at
messages        → id, conversation_id (FK), role, content, created_at
```

**索引優化：**
- `messages.conversation_id` — 加速對話歷史查詢
- `conversations.user_id` — 加速用戶對話列表查詢
- `(conversation_id, created_at)` 複合索引 — 支援高效分頁

---

## 🔄 CI/CD 流程

```
Push to main
    │
    ▼
GitHub Actions
    ├── 安裝套件
    ├── 執行 pytest
    └── SSH 部署至 AWS EC2
            └── docker compose up -d --build
```

---

## 🌿 Git 分支策略

| 分支 | 用途 |
|------|------|
| `main` | 正式環境，自動部署 |
| `develop` | 開發主線 |
| `feature/*` | 新功能開發 |
| `hotfix/*` | 緊急修復 |

