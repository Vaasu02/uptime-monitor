# AI Collaboration Log

## AI Tools Used

- **Claude Code** (VS Code extension) — Claude Opus 4.6 model
- Used as a pair-programming assistant for scaffolding, boilerplate generation, and rapid prototyping

---

## My Approach

I started by sketching out the system architecture on paper — three containers (frontend, backend, db), REST API design, and the polling-based monitoring pattern. Once I had the design clear, I used AI to accelerate the implementation of boilerplate code while I focused on architecture decisions, debugging, and integration.

---

## Key Prompts & Interactions

### 1. System Architecture Design (Iterative)

**My first prompt:** "I want you to understand the assignment deeply and technically and then design a simple system architecture for an uptime monitor — show me the components, data flow, and how they connect."

**AI output:** Generated an initial architecture with three services, REST API design, and a polling-based approach.

**What I did:** Reviewed the architecture, asked about pros and cons of different approaches (WebSockets vs polling, separate worker vs in-process scheduler, Nginx reverse proxy vs direct API calls). After understanding the tradeoffs, I told the AI to go with polling + APScheduler in-process + Nginx proxy. Then I chose the specific tech stack (FastAPI, PostgreSQL, React) and asked AI to update the plan accordingly.

### 2. Tech Stack & Database Schema (My Decision, AI-assisted)

**My prompt:** "Let's go with FastAPI for backend, PostgreSQL for DB, React + Vite for frontend, and Docker Compose. Generate the database models — I need a monitored_urls table and a health_checks table with proper relationships."

**AI output:** Generated SQLAlchemy models with the schema I described.

**What I did next:** Reviewed the models, adjusted field types, and added the cascade delete relationship so removing a URL cleans up its check history.

### 2. Pinger Logic (Collaborative)

**My prompt:** "Write an async pinger function using httpx that takes a URL, makes a GET request with a 10s timeout, and returns status_code, response_time_ms, and is_up. Handle DNS failures and timeouts gracefully."

**AI output:** Generated the `ping_url()` and `check_all_urls()` functions.

**What I did:** Added User-Agent header after testing showed some sites block bare requests. Changed the is_up threshold from `< 400` to `< 500` because a 403 still means the server is reachable — that was my call based on how real uptime monitors work.

### 3. Frontend Components (AI-assisted scaffolding)

**My prompt:** "Create a React component that polls GET /api/urls every 15 seconds and displays each URL with a colored status dot — green for up, red for down, gray for pending. Include an add form and delete button."

**AI output:** Generated App.jsx, URLList.jsx, AddURLForm.jsx, StatusBadge.jsx.

**What I did:** Styled the layout with Tailwind (dark theme), fixed the polling interval, and tested the UI flow end-to-end in the browser.

### 4. Docker & Nginx (My Configuration)

**My prompt:** "Generate a multi-stage Dockerfile for the React frontend — Node build stage, then serve with nginx. I also need an nginx.conf that proxies /api to the backend container."

**AI output:** Generated Dockerfile and nginx.conf.

**What I did:** Configured the port mappings in docker-compose.yml, set up the postgres healthcheck, and tuned the `depends_on` conditions so services boot in the right order.

---

## Course Corrections (Debugging I Did)

### 1. Node Version Mismatch
The AI-generated Dockerfile used Node 18, but Vite's latest release requires Node 20+. Build failed with a clear error. I caught this immediately and bumped the base image to `node:20-alpine`.

### 2. APScheduler Misfiring
After deploying, I noticed the scheduler was logging "job missed" errors and URLs were stuck on "Pending." I diagnosed this by reading the APScheduler docs — the default `misfire_grace_time` was too short. I added:
- `misfire_grace_time: 60`
- `coalesce: True`
- `next_run_time=datetime.now()` for immediate first run

### 3. Bot Protection on Some URLs
During testing, I noticed chatgpt.com and gemini.google.com showed as "down" even though they're online. Identified the issue: these sites require a User-Agent header. Added a proper UA string to the httpx client. Also realized the 403 threshold was too aggressive — changed to `< 500` since a 403 means the server IS responding.

### 4. WSL2 Networking
`localhost:3000` didn't work from my Windows browser even though containers were running. Debugged by curling from inside WSL2 (worked), then realized it's a known WSL2 port-forwarding quirk. Accessed via the WSL2 IP directly.

---

## What AI Was Good For vs. What I Did Myself

| Task | Who Did It |
|------|-----------|
| System design & architecture | Collaborative — AI proposed initial design, I reviewed, asked questions, and directed changes |
| Tech stack selection | Me (validated with AI) |
| Database schema design | AI generated from my spec, I reviewed relationships |
| API endpoint design | AI wrote the FastAPI code from my endpoint list |
| Pinger logic & thresholds | Collaborative — AI wrote the skeleton, I tuned the logic |
| Frontend components | AI scaffolded and styled, I tested and adjusted |
| Docker/Nginx config | AI generated, I configured ports and service dependencies |
| Debugging & fixing issues | Collaborative — I identified symptoms, AI diagnosed root causes, I verified fixes |
| Testing & verification | Me |
