# Code Agent — AI-Powered Coding Assistant Platform

A complete, production-ready **Code Agent Platform** featuring a **Django REST Framework (DRF)** backend and a **Next.js 15 (React 19 + Tailwind CSS v4)** frontend. Built to power AI-driven coding workflows: code generation, debugging, code review, project scaffolding, and agentic task execution.

---

## Key Features

### Backend (Django REST Framework)
1. **Core Package (`code_agent_core`)**: Settings, URLs, WSGI, and Celery configuration tailored for the Code Agent platform.
2. **User & Authentication (`users`)**: Custom `User` model, `UserProfile`, and Token & OTP Auth — supports developer accounts with API key management.
3. **Agents (`agents`)**: `Agent`, `AgentSession`, and `AgentLog` models — manage AI agent configurations, session history, and execution logs.
4. **Conversations (`conversations`)**: `Conversation` & `Message` models — full chat-based interface for interacting with agents.
5. **Code Execution (`executor`)**: Sandboxed code execution endpoints — run Python, JavaScript, Bash snippets securely.
6. **Projects (`projects`)**: `Project` & `ProjectFile` models — workspace management for multi-file agentic coding tasks.
7. **Swagger OpenAPI Documentation**: Auto-generated interactive API docs at `/api-docs/`.

### Frontend (Next.js 15 + React 19 + Tailwind CSS v4)
1. **Dark Glassmorphism Design**: Responsive UI with a dark-mode-first aesthetic, gradient accents, and micro-animations.
2. **Global State Context (`AgentContext`)**: Real-time session state, streaming response support, and seamless DRF API synchronization.
3. **Interactive Navigation & Header**: Search bar, agent selector dropdown, user profile menu.
4. **Dashboard (Homepage)**: Active sessions panel, recent conversations, usage statistics, and quick-start actions.
5. **Chat Interface**: Streaming markdown response renderer, code block highlighting, copy-to-clipboard, agent switching.
6. **Code Editor**: Monaco-based editor with syntax highlighting, file-tree navigation, and inline agent suggestions.
7. **Agent Management**: Create, configure, and test agent instances with system prompt editor.
8. **Project Workspace**: Multi-file project view with agentic file generation and diff viewer.
9. **Execution Console**: Live terminal output for sandboxed code runs.

---

## How to Run the Project

### Running Backend (Django)

```bash
# 1. Install Dependencies
pip install -r requirements.txt

# 2. Run Database Migrations
python manage.py makemigrations agents conversations executor projects users
python manage.py migrate

# 3. Seed Initial Data (demo agents & templates)
python manage.py seed_code_agent

# 4. Start Development Server
python manage.py runserver 0.0.0.0:8000
```

### Running Frontend (Next.js)

```bash
cd frontend

# 1. Install NPM Dependencies
npm install

# 2. Start Development Server
npm run dev

# 3. Build Production Bundle
npm run build
```

---

## API Endpoints

- `GET /api/agents/` — List all available agents.
- `POST /api/agents/` — Create a new agent configuration.
- `GET /api/conversations/` — List user conversations.
- `POST /api/conversations/` — Start a new conversation.
- `POST /api/conversations/{id}/send_message/` — Send a message to an agent.
- `GET /api/projects/` — List user projects.
- `POST /api/projects/` — Create a new coding project.
- `POST /api/executor/run/` — Execute a code snippet in the sandbox.
- `GET /api-docs/` — Interactive Swagger API documentation.

---

## Project Structure

```
code-agent/
├── code_agent_core/        # Django core: settings, URLs, Celery, WSGI
├── users/                  # Auth, User model, UserProfile, API key management
├── agents/                 # Agent model, sessions, logs
├── conversations/          # Conversation & Message models
├── executor/               # Sandboxed code execution
├── projects/               # Project & ProjectFile management
├── frontend/               # Next.js 15 frontend
│   └── src/
│       ├── app/            # Next.js App Router pages
│       ├── components/     # Reusable UI components
│       ├── context/        # AgentContext, AuthContext
│       └── Services/       # API service layer
├── requirements.txt
├── manage.py
└── .env.example
```

---

## Environment Variables

Copy `.env.example` to `.env` and fill in your values.

Key variables:
- `SECRET_KEY` — Django secret key
- `OPENAI_API_KEY` — OpenAI API key for agent AI calls
- `ANTHROPIC_API_KEY` — Anthropic Claude API key
- `REDIS_URL` — Redis connection URL (for Celery & caching)
- `POSTGRES_*` — PostgreSQL connection details

---

## Tech Stack

| Layer      | Technology                              |
|------------|------------------------------------------|
| Backend    | Django 4.2, Django REST Framework 3.14  |
| AI         | OpenAI, Anthropic, LangChain            |
| Frontend   | Next.js 15, React 19, Tailwind CSS v4   |
| Task Queue | Celery 5 + Redis                        |
| Database   | PostgreSQL (prod) / SQLite (dev)        |
| Auth       | Token Auth + OTP                        |
| Docs       | drf-yasg (Swagger / OpenAPI)            |
