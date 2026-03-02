# CLAUDE.md

## Project Overview
AI Chat Platform — Real-time AI chat backend using Node.js, MySQL, Socket.io, and OpenAI API.

---

## Commands

### Install dependencies
```bash
npm install
```

### Start development server
```bash
npm run dev
```

### Start with Docker
```bash
docker compose up -d
```

### Run tests
```bash
npm test
```

### Database migration
```bash
npx sequelize-cli db:migrate
```

### Database seed
```bash
npx sequelize-cli db:seed:all
```

---

## Project Structure
```
src/
├── config/         # DB and OpenAI config
├── controllers/    # Route handlers and business logic
├── models/         # Sequelize models (User, Conversation, Message)
├── routes/         # Express route definitions
├── middlewares/    # JWT auth middleware, error handler
├── socket/         # Socket.io WebSocket logic
└── app.js          # Entry point
```

---

## Code Conventions

- Use **async/await** for all asynchronous operations, never callbacks
- All controllers must use **try/catch** and pass errors to `next(err)`
- Use **camelCase** for variables and functions
- Use **PascalCase** for Sequelize models
- Always validate request body before processing
- Never expose raw SQL errors to the client

---

## Architecture Notes

- **Auth:** JWT stored in Authorization header as `Bearer <token>`
- **WebSocket:** Socket.io handles real-time AI streaming; each conversation is a room identified by `conversationId`
- **AI Streaming:** OpenAI streaming API emits `ai_stream_chunk` events token by token, ends with `ai_stream_end`
- **Database:** MySQL via Sequelize ORM; always use model methods, avoid raw queries unless necessary

---

## Environment Variables

Required in `.env`:
```
PORT=3000
DB_HOST=
DB_PORT=3306
DB_NAME=ai_chat_db
DB_USER=
DB_PASSWORD=
JWT_SECRET=
JWT_EXPIRES_IN=7d
OPENAI_API_KEY=
```

---

## Important Rules

- Never commit `.env` to git
- Always create a `feature/xxx` branch from `develop` for new features
- Keep controllers thin — move business logic to a service layer if it grows
- When adding a new route, register it in `src/app.js` and document it in Postman
- MySQL indexes are set on `messages.conversation_id` and `conversations.user_id` — do not remove them
