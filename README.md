🚀 Cosmic Corridor
Desktop + Web Edition
A fast-paced arcade space shooter built with Python, Pygame, uv, ruff, pytest — and fully playable on the web via Railway.

🎮 Overview
Cosmic Corridor is a hybrid arcade project:

Desktop Version:
Built with Python + Pygame, fully playable locally.
Smooth movement, power-ups, procedural enemy generation.

Web Version (Browser Edition):
A JavaScript/Canvas re-implementation embedded inside a minimal Flask server.
Deployed on Railway.app, so anyone can play directly in the browser.

This dual-architecture setup makes Cosmic Corridor both a fun arcade game and a perfect example of:

Clean Python project structure

Tooling with uv, ruff, pytest

Deployment with Railway

Cross-platform game design (desktop + web canvas)

🗂 Project Structure
cosmic-corridor/
│
├─ src/
│   └─ cosmic_corridor/
│        ├─ __init__.py
│        ├─ game.py         # Pygame desktop game
│        └─ ...             # Other modules
│
├─ server.py                # Flask server for Railway (web version)
├─ requirements.txt         # Only Flask for deployment
├─ pyproject.toml           # uv + dependencies for local dev
├─ ruff.toml
├─ tests/
│   └─ test_basic.py
└─ README.md

🖥️ Desktop Version (Python + Pygame)
Requirements
Python 3.11+
uv (recommended for dev)
Pygame installed through pyproject.toml

Install & Run
uv sync
uv run python -m cosmic_corridor

Features

60 FPS gameplay

Player movement + shooting

Enemy waves with increasing difficulty

Power-ups (dual-shot, faster fire rate)

Score + survival timer

Flash damage feedback

Fully modular Pygame codebase

🌐 Web Version (Browser Edition)

The web version is a lightweight JavaScript/Canvas arcade shooter embedded in server.py.
This allows the game to run in any modern browser without installing Python or Pygame.

Play Online (Railway):

→ Your Railway production URL goes here

Example:

cosmic-corridor-production.up.railway.app

How it works
Python/Flask serves a single HTML page
That page contains a complete JS game engine (movement, enemies, bullets, power-ups, collisions, UI)
No Pygame required in deployment
Works instantly in browser
The backend exposes a health endpoint:

/health   →   {"status": "ok"}

⚙️ Development Tools
uv

Used for dependency management & running the Python desktop game:

uv sync
uv run python -m cosmic_corridor
uv run pytest
uv run ruff check .

ruff

Formatting & linting:

uv run ruff check .
uv run ruff format .

pytest

Run all tests:

uv run pytest

🚀 Deployment (Railway)

Deployment is done via a very small Flask app:

Start command:
pip install -r requirements.txt && python server.py

Public port (Railway UI):
8080

requirements.txt

Only includes Flask:

flask>=3.0.0
After pushing to GitHub, Railway auto-deploys the web version.

📦 Why Two Versions?
Because Railway cannot open a Pygame display window (headless server),
so the browser version ensures your game:

Works online

Opens instantly

Requires no installation

Runs consistently across all devices

Meanwhile, your original Python/Pygame game stays preserved for:

Coursework / submissions

Local gameplay

Code quality (uv + ruff + pytest)

Portfolio demonstration

This makes Cosmic Corridor both a Python game project and a web-playable arcade experience.
