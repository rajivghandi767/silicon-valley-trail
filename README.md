# ✈️ 🏞️ 💻 Silicon Valley Trail: Caribbean Edition - A LinkedIn REACH Project

**An API-driven, containerized backend application built for the LinkedIn REACH Apprenticeship.**

This turn-based strategy game focuses on robust backend design, resource management, and external API integration. It utilizes a pure Django game engine to act as the single source of truth—handling complex state calculations, enforcing strict game-loop validations, and processing real-time marine and aviation weather data to dynamically influence gameplay. The project is fully Dockerized and self-hosted on bare-metal homelab infrastructure.

**Live Demo**: [**silicon-valley-trail.rajivwallace.com**](https://silicon-valley-trail.rajivwallace.com)

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

- **Frontend (Dumb Client):** A React/Vite application that only captures user input and renders the JSON state provided by the backend. It contains zero game logic.
- **Backend (Smart Server):** A Python/Django application acting as the authoritative game engine. It calculates resource deltas, enforces rules, communicates with external weather APIs, and controls the single source of truth.
- **Proxy Routing:** A multi-stage Docker build uses Nginx to serve the static React frontend while reverse-proxying `/api/` and `/admin/` requests to the Django backend served via Gunicorn.

---

## 🔧 Tech Stack

### **Backend & DB**

- 🐍 Python
- 🚀 Django/SQLite

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

To run this project locally, you will need to follow these steps:

### Prerequisites

- 🐳 Docker & Docker Compose

### 2. Start the Application

```bash
docker compose up -d --build
```

or

```bash
docker-compose up -d --build
```

**Whether or not you need the hyphen will depend on your version of Docker Compose.**

- **Backend**: `http://localhost:8000`
- **Frontend**: `http://localhost:5173`

---

## 🧪 Testing

This project utilizes Django's built-in `unittest` framework (`django.test.TestCase`) to ensure the core game mechanics and resource economy function correctly without regressions.

**Core Mechanics Tested:**

1. **Initial State:** Verifies the game boots with correct default limits (18 Days, $2500, etc.).
2. **Resource Deltas:** Verifies that stationary actions (like Resting) correctly deduct cash and time while capping morale boosts.
3. **Loss Conditions:** Verifies the custom "Fatal Exception" logic (e.g., hitting 50 bugs immediately locks the game state).

**API Mocking:**
To guarantee that the test suite can run in offline environments and to prevent hitting Open-Meteo rate limits during CI/CD pipelines, external API calls are strictly mocked using Python's `@patch` decorator (`unittest.mock.patch`). The tests simulate both "Clear Skies" and "Severe Weather" API payloads to test the backend logic independently of external network health.

**How to run the tests:**
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

During the development of this application, I utilized Google's Gemini primarily as a pair-programmer, auditor and architectural sounding board. As a self-taught engineer transitioning into backend development, I've embraced AI to accelerate my workflow, rubber-duck complex bugs, and provide comparisons when debating different development routes.

Specifically, I leveraged AI for:

- **Architectural Validation:** Discussing and solidifying the strict "Smart Server / Dumb Client" design pattern before writing the integration logic.
- **Targeted Debugging:** Troubleshooting complex Python logic, specifically catching scope and indentation edge-cases within the random event loop.
- **Game Economy & Balancing:** Brainstorming resource limits, probability distributions, and RNG balancing to ensure the game felt tense, realistic, and fair.
- **UI/UX Brainstorming:** Streamlining the transition from standard React boilerplate to a custom, pure CSS IDE aesthetic without relying on heavy frontend frameworks like Tailwind.

Ultimately, the AI served as an accelerator and an auditor, but the strict architectural constraints, data modeling, and final implementation logic remained entirely human-driven.

---

## 🧠 Design Notes

<details>
<summary><b>1. Game Loop & Balance Approach</b></summary>

The game loop utilizes a Strict Server-Authoritative Architecture (Smart Server / Dumb Client). The React frontend only transmits intended actions (e.g., "travel_ferry") and renders the resulting JSON state. The Django backend executes the core loop: evaluating the move, securely fetching API data, deducting resources, executing RNG events, and checking Win/Loss conditions.

Balance Approach: I designed the resources to constantly tension against each other, fine-tuned for a fast-paced 10-stop sprint:

    Time vs. Health: Resting restores Morale but burns Days and Cash.

    Risk vs. Reward: Ferries are cheap but highly susceptible to weather delays. Flights are fast but require premium Award Miles.

    Smart Deltas: To maintain a polished UI, the backend calculates precise resource deltas, ensuring stats never overflow their caps (e.g., max 100 Morale) and omitting redundant text.

    Strict Constraints: Reaching 50 Bugs or 0 Morale triggers an immediate "Fatal Exception" game over, forcing players to actively balance coding against traveling.

</details>

<details>
<summary><b>2. Why I Chose My APIs & How They Affect Gameplay</b></summary>

I chose the Open-Meteo API because it requires no authentication (preventing .env setup friction for reviewing engineers) and provides incredibly granular meteorological data.

Instead of a single API proxy, I implemented a Multi-Domain Routing Strategy, enhanced by a Dynamic Volatility Modifier:

    Ferry Travel (Marine API): Queries real-time wave_height. Because real-world oceans are often safe, the backend blends actual wave data with a localized RNG squall chance, ensuring ferries carry inherent risk.

    Flight Travel (Forecast API): Queries atmospheric WMO weather codes and wind speeds. Thunderstorms ground flights entirely, while a dynamic math function calculates turbulence probability based on live wind speed, resulting in Morale penalties.

</details>

<details>
<summary><b>3. Data Modeling (State, Events, Persistence)</b></summary>

    Persistence (The Database): I opted for the native db.sqlite3 over my usual containerized PostgreSQL to guarantee a 100% frictionless local boot for reviewers, avoiding common psycopg2 C-compiler errors.

    Context-Aware State: The GameState model acts as the single source of truth. To strictly enforce the "Dumb Client" UI, the model dynamically generates a status_summary. Instead of React parsing logic to figure out if the game is over, Django pushes the exact terminal readout (including the Final Score breakdown on victory) directly to the frontend via a custom serialize_for_api() method.

    Events & Locations: The map is persisted via a Location model. However, the 12 highly contextual, tech/Caribbean-themed turn events are stateless—calculated dynamically in views.py using Python's random module to keep the database lean.

</details>

<details>
<summary><b>4. Error Handling (Network Failures & Rate Limits)</b></summary>

    Network Failures (Failing Aggressive): To ensure the game can be played offline or in degraded network environments, all urllib API calls are wrapped in a strict 3-second timeout try/except block. If the API fails, the backend doesn't "fail safe" (which would make the game too easy); it "fails aggressive" by defaulting to a localized RNG dice roll (e.g., 40% chance of a storm), preserving gameplay tension while guaranteeing the loop never crashes.

    Rate Limits: Open-Meteo allows 10,000 free daily requests. By restricting API calls only to travel actions, the application heavily throttles its own outbound requests, ensuring it will never hit a rate limit.

    Input Validation: The backend API wraps json.loads in exception handlers, gracefully returning standard HTTP 400 JSON payloads if the frontend transmits corrupted data.

</details>

<details>
<summary><b>5. Tradeoffs & "If I had more time"</b></summary>

The Tradeoffs:

    Internal State RNG vs. External Joke APIs: I traded infinite external variety (e.g., fetching from a "random quote API") for a hardcoded internal RNG event system. This tradeoff allowed me to tightly couple 12 distinct events to specific game resources and craft domain-specific narratives (LinkedIn REACH jokes, Caribbean culture) that a generic API couldn't provide.

    Dependency Minimization vs. Developer Experience (DX): I traded the developer ergonomics of the requests library and DRF for Python's built-in urllib and pure Django views. This slightly clunkier DX was worth the tradeoff to guarantee a zero-dependency, instant installation for the reviewing engineers.

If I had more time (Feature Enhancements):

    Score & Leaderboard System: I would add a Player model and calculate a final numerical score based on the days and resources remaining upon reaching Dominica, allowing for a global Top 10 leaderboard.

    Consumables / "The Bodega": I would introduce an Inventory model allowing players to spend cash on passive items (e.g., "Noise Canceling Headphones" to mitigate flight turbulence penalties).

</details>

---

## 🙏🏾 Acknowlegements

I would like to extend my sincere gratitude to the LinkedIn team for providing this incredibly fun and challenging technical assessment.

A special thank you to my assigned recruiter, Nia Stewart, for her guidance and communication throughout this process, as well as to my interview panel for their time, insight, and consideration.

Building the Silicon Valley Trail: Caribbean Edition has been a fantastic learning experience, and I am excited about the opportunity to bring this passion for Backend Engineering to LinkedIn!

---

## 📬 Contact

**Rajiv Wallace** - [LinkedIn](https://www.linkedin.com/in/rajiv-wallace)

- Email: dev@rajivwallace.com
