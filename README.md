# ✈️ 🏞️ 💻 Silicon Valley Trail: Caribbean Edition - A LinkedIn REACH Project

A turn-based Caribbean transit strategy game. Manage resources, navigate real-time weather APIs, and reach the final pitch. Built with pure Django & React.

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

---

## 🔧 Tech Stack

### **Backend**

- 🐍 Python
- 🚀 Django

### **Frontend**

- ⚛️ React
- 🔵 TypeScript
- 🍃 Tailwind CSS & Vite

### **Database & Infrastructure**

- 🐳 Docker & Docker Compose
- 🌐 Nginx Proxy Manager (Reverse Proxy)

---

## 🚀 Deployment & Infrastructure

---

## 💻 Quick Start Guide

To run this project locally, you will need to follow these steps:

### Prerequisites

- 🐳 Docker & Docker Compose
- 📝 A `.env` file

### 1. Configure Environment (`.env`)

Create a `.env` file based on `env.example`. Make sure to include:

- `DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1`
- `VITE_API_URL=http://localhost:8000`

### 2. Start the Application

```bash
docker compose up -d --build
```

- **Backend**: `http://localhost:8000`
- **Frontend**: `http://localhost:5173`

---

## 🧪 Testing

---

## 🎮 How to Play

---

## 🤖 Use of AI

---

## 🧠 Design Notes

<details>
<summary><b>1. Game Loop & Balance Approach</b></summary>

The game loop utilizes a <b>Strict Server-Authoritative Architecture</b> (Smart Server / Dumb Client). The React frontend only transmits intended actions (e.g., "ferry_travel"). The Django backend executes the core loop: evaluating the move, securely fetching API data, deducting resources, executing RNG (Random Number Generator) events, and checking Win/Loss conditions before returning the serialized state.

Balance Approach: I designed the resources to constantly tension against each other.

    Time vs. Health: Resting restores Morale but burns Days and Cash.

    Risk vs. Reward: Ferries are cheap but highly susceptible to weather delays and morale drains. Flights are fast and comfortable but require premium Award Miles.

    The RNG Element: To fulfill the "random event" constraint, an RNG dice roll occurs on every turn, applying highly contextual tech/island-themed events to ensure no two playthroughs are identical.

</details>

<details>
<summary><b>2. Why I Chose My APIs & How They Affect Gameplay</b></summary>

I chose the Open-Meteo API because it requires no authentication (preventing .env setup friction for reviewing engineers) and provides incredibly granular meteorological data.

Instead of a single API proxy, I implemented a Multi-Domain Routing Strategy to accurately map real-world geography to transit physics:

    Ferry Travel: Queries the Open-Meteo Marine API for real-time wave_height. Small craft advisories (>2.5m swells) cancel ferries, draining time and morale.

    Flight Travel: Queries the Open-Meteo Forecast API for atmospheric WMO weather codes. Thunderstorms ground flights entirely, while high winds permit travel but trigger turbulence (Morale penalty).

</details>

<details>
<summary><b>3. Data Modeling (State, Events, Persistence)</b></summary>

    Persistence (The Database): I opted for the native db.sqlite3 over my usual containerized PostgreSQL to guarantee a 100% frictionless local boot for reviewers, avoiding common psycopg2 C-compiler errors (something I experienced with deployment of my portfolio projects).

    State Management: The GameState model persists the player's current resources and acts as the single source of truth. I bypassed Django REST Framework (DRF) to keep dependencies at absolute zero, instead building a custom serialize_for_api() method directly on the model to feed the React frontend.

    Events & Locations: The map is persisted via a Location model containing exact GPS coordinates. However, turn-based events are stateless—calculated dynamically in views.py using Python's random module to keep the database lean.

    Data Integrity: GameState is tied to Location via on_delete=models.PROTECT, preventing accidental database operations from wiping out active save files.

</details>

<details>
<summary><b>4. Error Handling (Network Failures & Rate Limits)</b></summary>

    Network Failures (Offline Mode): To ensure the game can be played offline or in degraded network environments, all urllib API calls are wrapped in a strict 3-second timeout try/except block. If the API fails, the backend "fails open," assuming clear skies and calm seas. This guarantees the game loop never crashes.

    Rate Limits: Open-Meteo allows 10,000 free daily requests. By restricting API calls only to travel actions (and bypassing it for stationary actions like "Rest" or "Code"), the application heavily throttles its own outbound requests, ensuring it will never hit a rate limit during normal gameplay.

    Input Validation: The backend API wraps json.loads in exception handlers, gracefully returning standard HTTP 400 JSON payloads if the frontend transmits corrupted data.

</details>

<details>
<summary><b>5. Tradeoffs & "If I had more time"</b></summary>

The Tradeoffs:

    Internal State RNG vs. External Joke APIs: I traded infinite external variety (e.g., fetching from a "random quote API") for a hardcoded internal RNG event system. This tradeoff allowed me to tightly couple events to specific game resources (Cash, Bugs) and craft domain-specific narratives (DevOps jokes, Caribbean culture) that a generic API couldn't provide.

    Dependency Minimization vs. Developer Experience (DX): I traded the developer ergonomics of the requests library and DRF for Python's built-in urllib and pure Django views. This slightly clunkier DX was worth the tradeoff to guarantee a zero-dependency, instant installation for the reviewing engineers.

If I had more time (Feature Enhancements):

    Weather/Seasonal Multiplier: Because Caribbean weather is typically beautiful, API travel penalties may trigger infrequently. I would build a "Simulation Modifier" that artificially intercepts the API payload and inflates localized storm probabilities to increase strategic tension.

    Score & Leaderboard System: I would add a Player model and calculate a final numerical score based on the days and resources remaining upon reaching Dominica, allowing for a global Top 10 leaderboard.

    Consumables / "The Bodega": I would introduce an Inventory model allowing players to spend cash on passive items (e.g., "Noise Canceling Headphones" to mitigate flight turbulence penalties).

</details>

---

## 🙏🏾 Acknowlegements

---

## 📬 Contact

**Rajiv Wallace** - [LinkedIn](https://www.linkedin.com/in/rajiv-wallace)

- Email: dev@rajivwallace.com
