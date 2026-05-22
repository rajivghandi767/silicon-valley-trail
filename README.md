# 🌴 💻 Silicon Valley Trail

![Live Demo](https://img.shields.io/badge/Live-Demo-brightgreen.svg)
![Django](https://img.shields.io/badge/Django-092E20?style=flat&logo=django&logoColor=white)
![React](https://img.shields.io/badge/React-20232A?style=flat&logo=react&logoColor=61DAFB)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=flat&logo=postgresql&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-DC382D?style=flat&logo=redis&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2CA5E0?style=flat&logo=docker&logoColor=white)
![Jenkins](https://img.shields.io/badge/Jenkins-D24939?style=flat&logo=jenkins&logoColor=white)

**Live Demo:** [**svt.rajivwallace.com**](https://svt.rajivwallace.com)

**Silicon Valley Trail** is a turn-based, API-driven strategy web application. Players must manage technical debt, financial resources, and real-time Caribbean weather patterns to successfully navigate from New York City to Dominica and pitch a vacationing Engineering Director.

Originally developed as a time-boxed submission for the **LinkedIn REACH Apprenticeship**, this repository has been extensively refactored to demonstrate modern production standards, focusing on robust backend decoupling, CI/CD pipeline automation, and strict data security.

> **⚠️ Note for LinkedIn REACH Recruitment:**
> This `main` branch reflects the post-interview refactor and production deployment. If you are looking to review the original, unedited take-home submission, please visit the [**archive/linkedin-reach-submission**](https://github.com/rajivghandi767/silicon-valley-trail/tree/archive/linkedin-reach-submission) branch.

---

## 🚀 Post-Interview Refactor & Improvements

Following a technical pair-programming session, this codebase underwent a comprehensive architectural overhaul to transition from a local prototype to a scalable, production-ready application:

- **Redis Game Session Caching:** Transitioned temporary game state management to Redis caching. This decouples dynamic session data from the relational database, significantly reducing disk I/O and optimizing read/write speeds during the core game loop.
- **Separation of Concerns ("Fat Models, Skinny Views"):** Decoupled the monolithic `views.py`. Complex external API logic (weather routing) is now abstracted into a dedicated `services` layer, and state mutations are handled by an isolated `engine`.
- **Security Hardening:** Removed the development-phase `@csrf_exempt` decorators. The application now executes a full CSRF handshake between the React SPA and Django via `@ensure_csrf_cookie` and strict `X-CSRFToken` header validation.
- **Database Modernization:** Migrated the data layer from SQLite to a dedicated, containerized PostgreSQL instance to support highly concurrent transactions.
- **Clean Code & Maintainability:** Eradicated "magic numbers" across the backend by centralizing configurations and narrative strings into dedicated constant files.
- **Gameplay & UX Rebalancing:** Introduced positive random events for successful turns to improve player progression, and overhauled the frontend CSS to ensure the game is fully responsive and playable on mobile screens.

---

## 🏗️ Architecture & Infrastructure

This application utilizes a strict **"Smart Server / Dumb Client"** architecture. Production is deployed on a custom self-hosted bare-metal environment (headless Debian) utilizing strict environment segregation.

### Backend Pipeline & Integrations

- **Engine:** Python / Django APIs.
- **Data Layer:** PostgreSQL (persistent data) & Redis (session caching).
- **External Integrations:** Open-Meteo APIs (Dynamic real-time marine and aviation forecasting dictating travel risk algorithms).
- **Network Security:** Nginx handles CORS interception via `$http_origin` maps, dropping unauthorized `OPTIONS` requests natively to conserve Gunicorn worker cycles. Dedicated rate-limiting zones protect API routes.
- **Dependency Management:** Python dependencies are deterministically managed via `pip-tools`. Strict separation is enforced between lightweight production packages (`requirements.txt`) and testing/local middleware (`dev-requirements.txt`).

### CI/CD & DevOps Automation

Deployments are fully automated via Jenkins Multibranch Pipelines (`Jenkinsfile` and `Jenkinsfile.deploy`).

1. **Build & Tag:** Jenkins tests the codebase, builds the `backend`, `frontend`, and `nginx` Docker images, and pushes them to the GitHub Container Registry (ghcr.io) tagged with the exact Git commit hash.
2. **Secret Injection:** The pipeline authenticates dynamically with **HashiCorp Vault** to securely pull and inject environment variables into the host agent.
3. **Orchestration:** A remote SSH command pulls the latest images and executes zero-downtime updates via Docker Compose.

---

## 💻 Local Development Quick Start (Zero-Friction Setup)

The local development environment is strictly isolated from production infrastructure. The default `docker-compose.yml` utilizes lightweight, hot-reloading images tailored for a seamless developer (and reviewer) experience.

### Prerequisites

- Docker & Docker Compose
- Git

### Installation

1. **Clone the repository:**

   ```bash
   git clone [https://github.com/rajivghandi767/silicon-valley-trail.git](https://github.com/rajivghandi767/silicon-valley-trail.git)
   cd silicon-valley-trail
   ```

2. **Configure Environment Variables:**
   Copy the example `.env` file. The defaults are pre-configured to automatically route the frontend, backend, PostgreSQL, and Redis containers over a custom local Docker network out-of-the-box.

   ```bash
   cp .env.example .env
   ```

3. **Spin up the stack:**
   This command will build the containers, run database migrations, load narrative seed data, and start the local servers.

   ```bash
   docker compose up --build -d
   ```

4. **Access the application:**
   - Frontend SPA: `http://localhost:5173`
   - Backend API: `http://localhost:8000/api/`
   - PostgreSQL (Direct Inspection): `localhost:5432`
   - Redis (Direct Inspection): `localhost:6379`

---

## 🧪 Testing Coverage

The Django test suite (`django.test.TestCase`) ensures strict mathematical validation of the resource economy and fault tolerance. Tests are isolated and cover:

- **Resource Economics:** Verifying stationary actions calculate precise mathematical deltas (e.g., resting caps morale boosts while deducting time and cash).
- **Dependency Mocking:** Utilizing `@patch` to mock external API weather data and control RNG matrices, ensuring deterministic state progression during testing.
- **Network Fallbacks:** Intentionally injecting `urllib` exceptions to validate the "Fail Aggressive" logic, ensuring backend continuity during network timeouts.
- **Terminal Boundaries:** Verifying game-over states and database safety locks trigger appropriately upon hitting specific loss conditions.

Run the suite locally via:

```bash
docker compose exec backend python manage.py test
```
