# ✈️ 🏞️ 💻 Silicon Valley Trail: Caribbean Edition - A LinkedIn REACH Project

**An API-driven, containerized backend application built for the LinkedIn REACH Apprenticeship.**

_Traditional application portals are a black hole. As a self-taught developer from New York, you need a different strategy to land your dream Backend Apprenticeship. Word on the wire is that the head of the REACH program is taking a rare, unplugged vacation at the Nature Island Hiking Festival in Dominica. Your mission: Island-hop your way from NYC down the Caribbean chain to deliver a flawless solo pitch. Manage your limited resources, navigate real-time tropical weather, keep your morale high, and ensure your codebase remains bug-free!_

This turn-based strategy game focuses on robust backend design, resource management, and external API integration. It utilizes a pure Django game engine to act as the single source of truth—handling complex state calculations, enforcing strict game-loop validations, and processing real-time marine and aviation weather data to dynamically influence gameplay. The project is fully Dockerized and self-hosted on bare-metal homelab infrastructure.

**Live Demo**: [**silicon-valley-trail.rajivwallace.com**](https://silicon-valley-trail.rajivwallace.com)

> ⚠️ **Note to Reviewers:** As the focus of this assessment is strictly on server-side logic, data modeling, and backend architecture, frontend and UI/UX polish is beyond the scope of this project. The live demo is designed for **Desktop viewing only** and is not optimized for mobile screens.

---

## 📜 Table of Contents

- [📖 Architecture Overview](#-architecture-overview)
- [🔧 Tech Stack](#-tech-stack)
- [🚀 Deployment & Infrastructure](#-deployment--infrastructure)
- [💻 Quick Start Guide](#-quick-start-guide)
- [🧪 Testing](#-testing)
- [🎮 How to Play](#-how-to-play)
- [🤖 Use of AI](#-use-of-ai)
- [🧠 Design Notes](#-design-notes)
- [🙏🏾 Acknowlegements](#-acknowledgements)
- [📬 Contact](#-contact)

---

## 📖 Architecture Overview

This project strictly follows a **"Smart Server / Dumb Client"** architecture to ensure absolute state security and prevent browser manipulation but also since UI/UX are beyond the scope of the assignment:

- **Frontend (Dumb Client):** A React/Vite application that only captures user input and renders the JSON state provided by the backend. It contains zero game logic. Standard CLI inputs are bypassed; instead, "commands" are transmitted as JSON payloads via the UI buttons (e.g., `POST /api/action/` -> `{"action": "travel_flight"}`).
- **Backend (Smart Server):** A Python/Django application acting as the authoritative game engine. It calculates resource deltas, enforces rules, communicates with external weather APIs, and controls the single source of truth.
- **Proxy Routing:** A multi-stage Docker build uses Nginx to serve the static React frontend while reverse-proxying `/api/` and `/admin/` requests to the Django backend served via Gunicorn.

---

## 🔧 Tech Stack

### **Backend & DB**

- 🐍 Python
- 🚀 Django/SQLite

### **API Used**

- ☁️ Open-Meteo Weather Forecast API
- 🌊 Open-Meteo Marine Weather API

### **Frontend**

- ⚛️ React
- 🔵 TypeScript
- 🍃 CSS & Vite

### **Infrastructure**

- 🐳 Docker & Docker Compose
- 🌐 Nginx Proxy Manager (Reverse Proxy)

---

## 🚀 Deployment & Infrastructure

The live demo is fully self-hosted and deployed on a bare-metal homelab environment:

- **Hardware:** Raspberry Pi 4B running DietPi (headless Debian).
- **Containerization:** The entire stack is completely containerized and orchestrated using `docker compose` or `docker compose`, (depending on Docker Compose version).
- **Traffic Management:** Cloudflare manages DNS and SSL edge encryption, routing incoming traffic to an Nginx Proxy Manager instance on the host machine, which then securely proxies requests to the application's internal container port. This was possible since I have invested in my own domain, rajivwallace.com.

---

## 💻 Quick Start Guide

### Option 1: Docker (Recommended)

Ensure Docker is installed and running on your machine.

First, clone the repository and navigate into the project directory:

```bash
git clone [https://github.com/rajivghandi767/silicon-valley-trail.git](https://github.com/rajivghandi767/silicon-valley-trail.git)
cd silicon-valley-trail
```

Then, boot the containers using the command that matches your version of Docker:

```bash
# For newer versions of Docker (Docker Compose V2)
docker compose up -d --build

# For older versions of Docker (Docker Compose V1)
docker-compose up -d --build
```

- **Frontend UI:** `http://localhost:5173`
- **Backend API:** `http://localhost:8000/api/state/`

### Option 2: Local Setup (Without Docker)

If you prefer to run the environments manually:

**1. Start the Django Backend:**

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py load_islands
python manage.py runserver
```

**2. Start the React Frontend:**
Open a new terminal window:

```bash
cd frontend
npm install
npm run dev
```

### 🔑 API Keys & Environment Variables

To eliminate reviewer friction, the chosen external API (Open-Meteo) requires NO authentication keys and the `settings.py` file is properly factored for fallbacks.

However, to demonstrate standard security practices, a `.env.example` file is included in the root directory. In a production environment, this would house the `DJANGO_SECRET_KEY` and third-party tokens.

---

## 🧪 Testing

This project utilizes Django's built-in `unittest` framework (`django.test.TestCase`) to ensure the core game mechanics and resource economy function correctly without regressions. The test suite is designed to cover 5 distinct operational paradigms:

1. **Initial State & Serialization:** Validates the model boots with correct default limits and maps Python objects to the JSON API correctly.
2. **Resource Economy:** Verifies that stationary actions correctly calculate mathematical deltas (e.g., resting caps morale boosts while deducting time and cash).
3. **Dependency Mocking:** Utilizes `@patch` to mock external API weather data and control RNG behavior, ensuring deterministic state progression.
4. **Network Fallbacks:** Intentionally forces an exception in `urllib` to prove the backend's "Fail Aggressive" logic intercepts fatal network timeouts without crashing the game loop.
5. **Boundary Constraints:** Verifies terminal states by manually injecting 50 bugs into the database to prove the Game Over safety lock functions securely.

**How to run Tests:**
Ensure your virtual environment is activated, navigate to the `backend/` directory, and run:

```bash
python manage.py test
```

---

## 🎮 How to Play

**The Goal:**

Travel through 10 locations starting in New York City, to reach your final pitch in Dominica before time or resources run out!

**Core Actions:**

- **Code:** Squashes bugs but consumes time.
- **Mentor:** Boosts team morale at the cost of time.
- **Rest:** Greatly recovers morale but burns days and cash.
- **Travel by Ferry:** A cheaper option, but highly susceptible to delays based on real-time marine weather.
- **Take a Flight:** Fast, but costs Award Miles and risks morale drops from real-time flight turbulence.

_Loss Conditions: Hitting 50 bugs, dropping below $0 cash, or reaching 0 morale will result in an immediate Game Over._

---

## 🤖 Use of AI

As a self-taught developer transitioning into a backend engineering career, I treat AI as a simulated Senior Developer. Throughout this project, I utilized Google's Gemini as a pair programmer, auditor, editor, and architectural sounding board.

My goal was to use AI to accelerate my learning and execution, while ensuring I fundamentally understood every line of code committed to the repository.

Specifically, I leveraged AI for:

- **Architectural Sounding Board:** Before writing any code, I used AI to debate system design tradeoffs, ultimately deciding on the strict "Smart Server / Dumb Client" architecture and discussing the security implications of decoupling the frontend. This was particularly helpful is weighing the pros and cons of spinning up a Postgres container vs using the SQLite contained in Django.
- **Pair Programming:** When building the core game loop, I used AI to help isolate complex Python logic errors, catch edge-cases within my random event matrix, and discuss the nuances of Django's test client session management.
- **Auditing & Editing:** I utilized AI as an editor to audit my test suite for coverage gaps, review my docstrings for clarity and typos, and refine this README to ensure it met my own formatting standards.

While AI was an invaluable accelerator that helped me weigh technical tradeoffs, all core architectural constraints, database modeling, external API logic, and final implementations are entirely my own.

---

## 🧠 Design Notes

<details>
<summary><b>1. Game Loop & Balance Approach</b></summary>
The game loop utilizes a Strict Server-Authoritative Architecture (Smart Server / Dumb Client). The React frontend only transmits intended actions (e.g., "travel_ferry") and renders the resulting JSON state. The Django backend executes the core loop: evaluating the move, securely fetching API data, deducting resources, executing RNG events, and checking Win/Loss conditions.

Balance Approach: I designed the resources to constantly tension against each other, fine-tuned for a fast-paced 10-stop sprint:

- **Time vs. Health:** Resting restores Morale but burns Days and Cash.
- **Risk vs. Reward:** Ferries are cheap but highly susceptible to weather delays. Flights are fast but require premium Award Miles.
- **Smart Deltas:** To maintain a polished UI, the backend calculates precise resource deltas, ensuring stats never overflow their caps (e.g., max 100 Morale) and omitting redundant text.
- **Strict Constraints:** Reaching 50 Bugs or 0 Morale triggers an immediate "Fatal Exception" game over, forcing players to actively balance coding against traveling.
</details>

<details>
<summary><b>2. Why I Chose My APIs & How They Affect Gameplay</b></summary>
I chose the Open-Meteo API because it requires no authentication (preventing .env setup friction for reviewing engineers) and provides incredibly granular meteorological data.

Instead of a single API proxy, I implemented a Multi-Domain Routing Strategy, enhanced by a Dynamic Volatility Modifier:

- **Ferry Travel (Marine Weather API):** Queries real-time wave_height. Because the Caribbean has relatively good weather, the backend blends the fetched data with an RNG to simulate rough sea probability, ensuring ferries carry inherent risk.
- **Flight Travel (Weather Forecast API):** Queries atmospheric WMO weather codes and wind speeds. Thunderstorms ground flights entirely, while a dynamic math function calculates turbulence probability based on live wind speed, resulting in Morale penalties.
</details>

<details>
<summary><b>3. Data Modeling (State, Events, Persistence)</b></summary>

- **Session-Based "Accountless" Auth:** I utilized Django's built in `request.session.session_key` to map the `GameState` to the player's browser. This allows concurrent gameplay, while maintaining a secure, persistent state on the server without collecting personal information.
- **Context-Aware State:** The GameState model acts as the single source of truth. To strictly enforce the "Dumb Client" UI, the model dynamically generates a status_summary. Instead of React parsing logic to figure out if the game is over, Django pushes the exact terminal readout directly to the frontend via a custom `serialize_for_api()` method.
- **Database Seeding via Management Commands:** Instead of using raw SQL or hardcoded JSON fixtures, I built a custom Django management command (`load_islands.py`). This allows for a robust, repeatable database seed process that integrates seamlessly into the Docker build sequence.
</details>

<details>
<summary><b>4. Error Handling (Network Failures & Rate Limits)</b></summary>

- **Network Failures (Failing Aggressive):** To ensure the game can be played offline or in degraded network environments, all urllib API calls are wrapped in a strict 3-second timeout try/except block. If the API fails, the backend doesn't "fail safe" (which would make the game too easy); it "fails aggressive" by defaulting to a localized RNG dice roll, preserving gameplay tension while guaranteeing the loop never crashes.
- **Rate Limits:** Open-Meteo allows 10,000 free daily requests. By restricting API calls only to travel actions, the application heavily throttles its own outbound requests, ensuring it will never hit a rate limit.
</details>

<details open>
<summary><b>5. Tradeoffs & "If I had more time"</b></summary>

**The Tradeoffs:**

- **Security vs. Evaluator Friction (CSRF Bypass):** In a production environment, a decoupled React frontend communicating with a Django API requires strict CSRF token management or JWT authentication. To ensure zero-friction local testing for the reviewing engineers, I opted to use the `@csrf_exempt` decorator on the API routes.
- **Internal State RNG vs. External APIs:** I traded infinite external variety for a hardcoded internal RNG event system. This tradeoff allowed me to tightly couple distinct events to specific game resources and craft a specific narrative that a generic API couldn't provide.
- **Dependency Minimization vs. Developer Experience (DX):** I traded the developer ergonomics of the `requests` library for Python's built-in `urllib`. This slightly clunkier DX was worth the tradeoff to guarantee a zero-dependency setup.

**If I had more time (Future Iterations):**
Because this application is designed around a tight, stateless game loop, I intentionally avoided feature bloat that would require messy database migrations. However, if I had a bit more time to iterate, I'd love to tackle the following:

1. **API Caching to Fix UI Delays:** During testing, I noticed a slight delay when choosing "Ferry" or "Flight" because the backend has to pause and wait for the Open-Meteo API to respond. I would love to implement Django's basic caching framework. Saving the weather data for a specific island would make the game feel much snappier.
2. **Smarter Random Events:** Right now, the random events just use `random.randint`, meaning every event has an equal chance of happening. While testing, I realized it feels a bit weird to get a negative "burnout" event when my morale is at 100%. I'd love to implement `random.choices` to make the events react to the player's state—like making bad events more likely if you are running low on cash or morale.
3. **Cleaning up views.py:** Currently, my `views.py` handles both the web request routing and all the core game math. As the game grew during testing, that file got a bit crowded. I'd love to spend some time pulling the core game logic out into its own separate file (like a `services.py`) just to make things cleaner and easier to read.
4. **Database Decoupling:** Right now, the SQLite database lives directly alongside the backend to ensure a zero-friction local boot for the reviewing engineers. However, I recognize that coupling compute and storage is a massive system design no no. If I had more time, I would decouple the data layer by migrating to a dedicated PostgreSQL container. This would allow the backend API nodes to scale and increase reliability.
</details>

---

## 🙏🏾 Acknowledgements

I would like to extend my sincere gratitude to the LinkedIn team for providing this incredibly fun and challenging technical assessment.

A special thank you to my assigned recruiter, Nia Stewart, for her guidance and communication throughout this process, as well as to you my interview panel for your time, insight, and consideration.

Building the Silicon Valley Trail: Caribbean Edition has been a fantastic learning experience, and I am excited about the opportunity to bring this passion for Backend Engineering to LinkedIn!

I hope this interaction is as fun for you as it was for me and outside of the professional scope of this assessment, I hope you also learned something new about Dominica and the Caribbean!

---

## 📬 Contact

**Rajiv Wallace** - [LinkedIn](https://www.linkedin.com/in/rajiv-wallace)

- Email: dev@rajivwallace.com
