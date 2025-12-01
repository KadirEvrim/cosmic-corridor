from __future__ import annotations

import os

from flask import Flask, render_template_string

app = Flask(__name__)

HTML = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Cosmic Corridor – Arcade Shooter</title>
  <style>
    body {
      margin: 0;
      padding: 0;
      font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background: radial-gradient(circle at top, #1b1c3a 0, #050516 60%, #02020a 100%);
      color: #f5f5ff;
      display: flex;
      align-items: center;
      justify-content: center;
      min-height: 100vh;
    }
    .card {
      background: rgba(3, 3, 15, 0.9);
      border-radius: 16px;
      padding: 24px 28px;
      max-width: 720px;
      width: 100%;
      box-shadow: 0 18px 45px rgba(0, 0, 0, 0.65);
      border: 1px solid rgba(120, 160, 255, 0.35);
    }
    h1 { margin-top: 0; font-size: 1.8rem; letter-spacing: 0.04em; }
    code {
      background: rgba(10, 12, 40, 0.85);
      padding: 2px 6px;
      border-radius: 6px;
      font-size: 0.9rem;
    }
    pre {
      background: rgba(10, 12, 40, 0.85);
      padding: 10px 12px;
      border-radius: 10px;
      overflow-x: auto;
      font-size: 0.9rem;
    }
    .pill {
      display: inline-block;
      padding: 4px 10px;
      border-radius: 999px;
      font-size: 0.75rem;
      background: rgba(80, 200, 255, 0.08);
      border: 1px solid rgba(80, 200, 255, 0.4);
      margin-right: 6px;
    }
    .footer {
      margin-top: 10px;
      font-size: 0.8rem;
      color: #b6b6d8;
      opacity: 0.9;
    }
  </style>
</head>
<body>
  <main class="card">
    <h1>🚀 Cosmic Corridor</h1>
    <p>
      This is a small arcade space shooter written in <b>Python + Pygame</b>.
      It runs as a desktop game locally. This Railway deployment only shows the project info.
    </p>

    <p>
      <span class="pill">Python 3.11+</span>
      <span class="pill">Pygame</span>
      <span class="pill">uv</span>
      <span class="pill">ruff</span>
      <span class="pill">pytest</span>
    </p>

    <h2>Run locally</h2>
<pre><code>uv sync
uv run python -m cosmic_corridor</code></pre>

    <h2>Run tests</h2>
<pre><code>uv run pytest</code></pre>

    <p class="footer">
      Health check: <code>/health</code>
    </p>
  </main>
</body>
</html>
"""


@app.get("/")
def index() -> str:
    return render_template_string(HTML)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


def main() -> None:
    port = int(os.getenv("PORT", "8080"))
    app.run(host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()
