# 🌴 💻 Silicon Valley Trail - Caribbean Edition

![Live Demo](https://img.shields.io/badge/Live-Demo-brightgreen.svg)
![Django](https://img.shields.io/badge/Django-092E20?style=flat&logo=django&logoColor=white)
![React](https://img.shields.io/badge/React-20232A?style=flat&logo=react&logoColor=61DAFB)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=flat&logo=postgresql&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-DC382D?style=flat&logo=redis&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2CA5E0?style=flat&logo=docker&logoColor=white)
![GitHub Actions](https://img.shields.io/badge/github%20actions-%232671E5.svg?style=flat&logo=githubactions&logoColor=white)

**Live Demo:** [**svt.rajivwallace.com**](https://svt.rajivwallace.com)

**Silicon Valley Trail** is a turn-based, API-driven strategy web application. Players must manage technical debt, financial resources, and real-time Caribbean weather patterns to successfully navigate from New York City to Dominica and pitch a vacationing Engineering Director.

Originally developed as a time-boxed submission for the **LinkedIn REACH Apprenticeship**, this repository has been extensively refactored to demonstrate modern production standards, focusing on robust backend decoupling, CI/CD pipeline automation, and strict data security.

> **⚠️ Note for LinkedIn REACH Recruitment:**
> This `main` branch reflects the post-interview refactor and production deployment. If you are looking to review the original, unedited take-home submission, please visit the [**archive/linkedin-reach-submission**](https://github.com/rajivghandi767/silicon-valley-trail/tree/archive/linkedin-reach-submission) branch.

---

## 🚀 Post-Interview Refactor & Improvements

Following a technical pair-programming session, this codebase underwent a comprehensive architectural overhaul to transition from a local prototype to a scalable, production-ready application:

- **Redis Game Session Caching:** Transitioned temporary game state management to Redis caching, completely bypassing SQL row contention (see Technical Architecture below).
- **Separation of Concerns ("Fat Models, Skinny Views"):** Decoupled the monolithic `views.py`. Complex external API logic (weather routing) is now abstracted into a dedicated `services` layer, and state mutations are handled by an isolated `engine`.
- **Security Hardening:** Removed the development-phase `@csrf_exempt` decorators. The application now executes a full CSRF handshake between the React SPA and Django via `@ensure_csrf_cookie` and strict `X-CSRFToken` header validation.
- **Database Modernization:** Migrated the data layer from SQLite to a dedicated, containerized PostgreSQL instance to support highly concurrent transactions.
- **Clean Code & Maintainability:** Eradicated "magic numbers" across the backend by centralizing configurations and narrative strings into dedicated constant files.
- **Gameplay & UX Rebalancing:** Introduced positive random events for successful turns to improve player progression, and overhauled the frontend CSS to ensure the game is fully responsive and playable on mobile screens.

---

## 🏗️ Architecture & Infrastructure

This application utilizes a strict **"Smart Server / Dumb Client"** architecture. Production is self-hosted on a bare-metal **Raspberry Pi 4B 8GB RAM** running a headless Debian distro (DietPi). To ensure strict environmental segregation and security, the network infrastructure is managed via **Ubiquiti UniFi** hardware, utilizing custom VLANs, VPNs, and firewall rules to safely sandbox traffic before routing through Cloudflare.

### Technical Architecture & Game Engine

Traditional text-based games heavily rely on SQL database row-locking to maintain session state. To adhere to modern stateless web architecture best practices and maximize throughput, SVT utilizes a **Decoupled Memory-First Architecture**:

- **Sub-Millisecond State Retrieval:** Active gameplay sessions (`CacheGameState`) are exclusively serialized and stored in Redis. This completely eliminates SQL row contention and allows the engine to process concurrent player actions instantly.
- **Static Payload Caching:** Map locations and mathematical boundaries (e.g., total stops) are cached indefinitely upon initialization. The Django engine accesses this data in `O(1)` time, completely bypassing repetitive `SELECT COUNT(*)` queries.
- **Session Expiry:** Inactive gameplay sessions are automatically swept from memory after 24 hours, ensuring the server's RAM footprint remains minimal regardless of user volume.

### Backend Pipeline & Integrations

- **Engine:** Python / Django APIs. The backend utilizes an RPC-style (Action-Oriented) architecture rather than strict REST. Endpoints like /api/action/ and /api/state/ directly mutate the game's internal state machine, providing a much cleaner structure for turn-based gameplay loops.
- **Data Layer:** PostgreSQL (persistent data) & Redis (session caching).
- **External Integrations:** Open-Meteo APIs (Dynamic real-time marine and aviation forecasting dictating travel risk algorithms).
- **Network Security:** Nginx handles CORS interception via `$http_origin` maps, dropping unauthorized `OPTIONS` requests natively to conserve Gunicorn worker cycles. Dedicated rate-limiting zones protect API routes.
- **Dependency Management:** Python dependencies are deterministically managed via `pip-tools`. Strict separation is enforced between lightweight production packages (`requirements.txt`) and testing/local middleware (`dev-requirements.txt`).

### CI/CD & DevOps Automation

Deployments are fully automated via GitHub Actions (`.github/workflows`).

1. **Build & Tag:** The GitHub Actions runner tests the codebase, builds the `backend`, `frontend`, and `nginx` Docker images, and pushes them to the GitHub Container Registry (ghcr.io) tagged with the exact Git commit hash.
2. **Secret Injection:** The pipeline authenticates dynamically with **HashiCorp Vault** to securely pull and inject environment variables into the host agent.
3. **Orchestration:** A remote SSH command pulls the latest images and executes zero-downtime updates via Docker Compose. Scheduled deployments also run daily at `02:30 AM` EST.

---

## 💻 Local Development Quick Start (Zero-Friction Setup)

The local development environment is strictly isolated from production infrastructure. The default `docker-compose.yml` utilizes lightweight, hot-reloading images tailored for a seamless developer (and reviewer) experience.

### Prerequisites

> ⚠️ **Architecture Note:** To ensure strict parity with the production environment and eliminate local dependency issues, this project is exclusively containerized. Please ensure you have Docker installed before proceeding.

- 🐳 Docker & Docker Compose

### Getting Started

1. **Clone the repository:**

   ```bash
   git clone https://github.com/rajivghandi767/silicon-valley-trail.git
   cd silicon-valley-trail
   ```

2. **Spin up the stack:**
   This command will build the containers, run database migrations, load narrative seed data, and start the local servers. No `.env` configuration is required as the `docker-compose.yml` natively utilizes `.env.example`.

   ```bash
   docker compose up --build -d
   ```

4. **Access the application:**
   - Frontend SPA: `http://localhost:5173`
   - Backend API: `http://localhost:8000/api/`
   - PostgreSQL (Direct Inspection): `localhost:5432`
   - Redis (Direct Inspection): `localhost:6379`

---

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
