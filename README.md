# 🌴 Silicon Valley Trail

**Silicon Valley Trail** is an interactive, full-stack web application originally developed as a submission for the LinkedIn REACH Backend Apprenticeship program. Inspired by the classic Oregon Trail, players must manage resources, technical debt, and real-time Caribbean weather conditions to successfully pitch a Senior Engineering Director vacationing in Dominica.

This repository demonstrates modern web development practices, focusing heavily on **systems architecture, CI/CD automation, and resource optimization** for self-hosted infrastructure.

![Live Demo](https://img.shields.io/badge/Live-Demo-brightgreen.svg)
![Django](https://img.shields.io/badge/Django-092E20?style=flat&logo=django&logoColor=white)
![React](https://img.shields.io/badge/React-20232A?style=flat&logo=react&logoColor=61DAFB)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=flat&logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2CA5E0?style=flat&logo=docker&logoColor=white)
![Jenkins](https://img.shields.io/badge/Jenkins-D24939?style=flat&logo=jenkins&logoColor=white)

---

## 🏗️ Architecture & Tech Stack

This project is deployed on a custom Homelab infrastructure (Raspberry Pi 4B running headless DietPi), requiring strict memory management and highly optimized I/O operations.

- **Frontend:** TypeScript, React, Vite, standard CSS.
- **Backend:** Python, Django (utilizing standard views and `JsonResponse`), Prometheus metrics.
- **Database & Caching:** PostgreSQL.
- **External APIs:** Open-Meteo (Real-time Marine & Aviation forecasting).
- **Infrastructure:** Docker, Nginx Proxy Manager, Cloudflare.
- **CI/CD:** Jenkins, GitHub Container Registry (ghcr.io), HashiCorp Vault.

---

## 🚀 Engineering Highlights & Optimizations

### 1. Database Caching for Game State Management

To conserve memory and minimize disk I/O on the host machine, temporary game state was completely decoupled from the Django ORM. Instead of spinning up a dedicated Redis container, the application utilizes `django.core.cache.backends.db.DatabaseCache` to write serialized Python objects directly to a lightweight, auto-culling PostgreSQL cache table. Persistent data (like island coordinates) remains in standard relational tables.

### 2. "Skinny Views, Fat Services"

The backend architecture strictly adheres to modular design principles.

- Complex external API logic (weather forecasting) is abstracted into a dedicated `services` layer.
- Dynamic game states, win/loss boundaries, and statistical mutations are handled by an isolated `engine`.
- All narrative strings and status messages are decentralized into `constants.py`, leaving the HTTP routing (`views.py`) clean, readable, and highly testable.

### 3. Production-Grade Security & Routing

- **Nginx Preflight Interception:** CORS is handled entirely at the Nginx reverse-proxy level using `$http_origin` maps, instantly returning `204 No Content` for `OPTIONS` requests without waking up Django Gunicorn workers.
- **CSRF Protection:** Full CSRF handshake implementation between the React SPA and Django via `@ensure_csrf_cookie` and `X-CSRFToken` headers.
- **Rate Limiting:** Dedicated Nginx zones established to protect the API, admin panels, and static file delivery from abuse.

### 4. Automated CI/CD Pipeline

Deployment is fully automated via Jenkins Multibranch Pipelines (`Jenkinsfile` and `Jenkinsfile.deploy`).

1. **Build:** Jenkins checks out the code, builds the `backend`, `frontend`, and `nginx` Docker images, tags them with the Git commit hash, and pushes them to GitHub Container Registry.
2. **Secrets Injection:** The deployment script dynamically authenticates with **HashiCorp Vault** (via AppRole) to securely pull and generate the `.env.prod` file directly on the host agent.
3. **Deploy:** A remote SSH command pulls the latest images and spins up the Docker Compose stack seamlessly.

---

## 💻 Local Development

### Prerequisites

- Docker & Docker Compose
- Git

### Quick Start

1. **Clone the repository:**

   ```bash
   git clone [https://github.com/rajivghandi767/silicon-valley-trail.git](https://github.com/rajivghandi767/silicon-valley-trail.git)
   cd silicon-valley-trail
   ```

2. **Environment Variables:**
   Copy the example environment files and update them if necessary (the defaults work out-of-the-box for local testing).

   ```bash
   cp .env.example
   ```

3. **Spin up the stack:**

   ```bash
   docker compose up --build -d
   ```

4. **Access the application:**
   - Frontend: `http://localhost:5173`
   - Backend API: `http://localhost:8000/api/`

_Note: The local development environment automatically defaults to Django's `LocMemCache` (Local Memory Cache) to completely bypass the need for generating Postgres cache tables while developing._
