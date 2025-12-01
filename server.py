from __future__ import annotations

import os

from flask import Flask, render_template_string

app = Flask(__name__)

GAME_HTML = r"""
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Cosmic Corridor – Browser Edition</title>
  <style>
    * { box-sizing: border-box; }
    body {
      margin: 0;
      padding: 0;
      background: radial-gradient(circle at top, #151632 0, #050516 55%, #02020a 100%);
      color: #f5f5ff;
      font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      display: flex;
      justify-content: center;
      align-items: center;
      min-height: 100vh;
    }
    .frame {
      background: rgba(3, 3, 15, 0.95);
      border-radius: 18px;
      padding: 18px 18px 12px;
      border: 1px solid rgba(120, 160, 255, 0.4);
      box-shadow: 0 18px 45px rgba(0, 0, 0, 0.75);
    }
    #gameCanvas {
      display: block;
      background: #050515;
      border-radius: 12px;
      border: 1px solid rgba(90, 110, 200, 0.7);
    }
    .info {
      margin-top: 8px;
      font-size: 12px;
      color: #c6c6f0;
      display: flex;
      justify-content: space-between;
      gap: 12px;
    }
    code {
      background: rgba(15, 18, 50, 0.9);
      padding: 2px 6px;
      border-radius: 6px;
      font-size: 11px;
    }
  </style>
</head>
<body>
  <div class="frame">
    <canvas id="gameCanvas" width="800" height="500"></canvas>
    <div class="info">
      <div>
        Controls:
        <code>← →</code> move |
        <code>SPACE</code> shoot
      </div>
      <div>
        This is the <b>browser version</b> of the Python/Pygame project.
      </div>
    </div>
  </div>

<script>
(() => {
  const canvas = document.getElementById("gameCanvas");
  const ctx = canvas.getContext("2d");

  const WIDTH = canvas.width;
  const HEIGHT = canvas.height;

  const keys = {};
  window.addEventListener("keydown", e => {
    keys[e.code] = true;
    if (["ArrowLeft","ArrowRight","Space"].includes(e.code)) {
      e.preventDefault();
    }
  });
  window.addEventListener("keyup", e => { keys[e.code] = false; });

  class Player {
    constructor() {
      this.x = WIDTH / 2;
      this.y = HEIGHT - 60;
      this.w = 40;
      this.h = 20;
      this.speed = 360;
      this.cooldown = 0.25;
      this.fireTimer = 0;
      this.powerTimer = 0;
      this.lives = 3;
    }
    update(dt) {
      let dx = 0;
      if (keys["ArrowLeft"]) dx -= 1;
      if (keys["ArrowRight"]) dx += 1;
      this.x += dx * this.speed * dt;
      this.x = Math.max(40, Math.min(WIDTH - 40, this.x));
      if (this.fireTimer > 0) this.fireTimer -= dt;
      if (this.powerTimer > 0) this.powerTimer -= dt;
    }
    canFire() { return this.fireTimer <= 0; }
    resetFire() {
      this.fireTimer = this.powerTimer > 0 ? this.cooldown * 0.45 : this.cooldown;
    }
    hasPower() { return this.powerTimer > 0; }
  }

  class Bullet {
    constructor(x, y) {
      this.x = x;
      this.y = y;
      this.vy = -520;
      this.w = 4;
      this.h = 12;
    }
    update(dt) { this.y += this.vy * dt; }
    outOfBounds() { return this.y + this.h < 0; }
  }

  class Enemy {
    constructor(x, speed, hp) {
      this.x = x;
      this.y = -30;
      this.w = 36;
      this.h = 26;
      this.vy = speed;
      this.hp = hp;
    }
    update(dt) { this.y += this.vy * dt; }
    outOfBounds() { return this.y - this.h > HEIGHT + 40; }
    isDead() { return this.hp <= 0; }
  }

  class PowerUp {
    constructor(x) {
      this.x = x;
      this.y = -20;
      this.size = 18;
      this.vy = 160;
    }
    update(dt) { this.y += this.vy * dt; }
    outOfBounds() { return this.y - this.size > HEIGHT + 20; }
  }

  const player = new Player();
  let bullets = [];
  let enemies = [];
  let powerups = [];

  let enemyTimer = 0;
  let enemyInterval = 0.9;

  let powerTimer = 0;
  let powerInterval = 8.0;

  let timeSurvived = 0;
  let score = 0;
  let flashTimer = 0;
  let gameOver = false;

  function spawnEnemy() {
    const x = 60 + Math.random() * (WIDTH - 120);
    const base = 140 + timeSurvived * 4;
    const speed = base + Math.random() * 60;
    const hp = Math.random() < 0.8 ? 1 : 2;
    enemies.push(new Enemy(x, speed, hp));
  }

  function spawnPowerUp() {
    const x = 60 + Math.random() * (WIDTH - 120);
    powerups.push(new PowerUp(x));
  }

  function rectsOverlap(a, b) {
    return !(
      a.x + a.w < b.x ||
      a.x > b.x + b.w ||
      a.y + a.h < b.y ||
      a.y > b.y + b.h
    );
  }

  function draw() {
    // background
    const grd = ctx.createLinearGradient(0, 0, 0, HEIGHT);
    grd.addColorStop(0, "#151632");
    grd.addColorStop(1, "#050516");
    ctx.fillStyle = grd;
    ctx.fillRect(0, 0, WIDTH, HEIGHT);

    // stars
    ctx.fillStyle = "rgba(250,250,255,0.8)";
    for (let i = 0; i < 80; i++) {
      const x = (i * 97 + timeSurvived * 40) % WIDTH;
      const y = (i * 53 + timeSurvived * 80) % HEIGHT;
      ctx.fillRect(x, y, 2, 2);
    }

    // player glow
    ctx.save();
    ctx.translate(player.x, player.y);
    const glowGrad = ctx.createRadialGradient(0, 0, 0, 0, 0, 80);
    glowGrad.addColorStop(0, "rgba(140,140,255,0.7)");
    glowGrad.addColorStop(1, "rgba(0,0,0,0)");
    ctx.fillStyle = glowGrad;
    ctx.beginPath();
    ctx.ellipse(0, 10, 60, 30, 0, 0, Math.PI * 2);
    ctx.fill();
    ctx.restore();

    // player
    ctx.fillStyle = "#5050c0";
    ctx.fillRect(player.x - player.w/2 - 2, player.y - player.h/2 - 2, player.w + 4, player.h + 4);
    ctx.fillStyle = "#e6e6fa";
    ctx.fillRect(player.x - player.w/2, player.y - player.h/2, player.w, player.h);
    ctx.fillStyle = "#ffffff";
    ctx.fillRect(player.x - 4, player.y - player.h/2 - 8, 8, 10);

    if (player.hasPower()) {
      ctx.strokeStyle = "rgba(80,255,170,0.9)";
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.ellipse(player.x, player.y, 36, 26, 0, 0, Math.PI * 2);
      ctx.stroke();
    }

    // bullets
    ctx.fillStyle = "#b4f0ff";
    bullets.forEach(b => {
      ctx.fillRect(b.x - b.w/2, b.y - b.h/2, b.w, b.h);
    });

    // enemies
    enemies.forEach(e => {
      ctx.fillStyle = "#3a0c20";
      ctx.fillRect(e.x - e.w/2 - 2, e.y - e.h/2 - 2, e.w + 4, e.h + 4);
      ctx.fillStyle = "#f05a78";
      ctx.fillRect(e.x - e.w/2, e.y - e.h/2, e.w, e.h);
      ctx.fillStyle = "#f5e6e6";
      ctx.fillRect(e.x - 6, e.y - e.h/2 + 4, 12, 8);
    });

    // powerups
    powerups.forEach(p => {
      ctx.fillStyle = "#144326";
      ctx.fillRect(p.x - p.size/2 - 2, p.y - p.size/2 - 2, p.size + 4, p.size + 4);
      ctx.fillStyle = "#50dd88";
      ctx.fillRect(p.x - p.size/2, p.y - p.size/2, p.size, p.size);
    });

    // UI
    ctx.fillStyle = "#0b0b1c";
    ctx.fillRect(0, 0, WIDTH, 34);
    ctx.fillStyle = "#f5f5ff";
    ctx.font = "14px system-ui";
    ctx.fillText("SCORE: " + score, 12, 22);
    ctx.fillText("TIME: " + Math.floor(timeSurvived) + "s", 140, 22);

    ctx.fillStyle = "#ff708c";
    let hearts = "";
    for (let i = 0; i < player.lives; i++) hearts += "❤";
    ctx.fillText(hearts, WIDTH - 60, 22);

    if (player.hasPower()) {
      const barW = 120;
      const ratio = Math.max(0, Math.min(1, player.powerTimer / 6.0));
      ctx.strokeStyle = "#245035";
      ctx.strokeRect(WIDTH/2 - barW/2, 10, barW, 8);
      ctx.fillStyle = "#7af0b4";
      ctx.fillRect(WIDTH/2 - barW/2, 10, barW * ratio, 8);
      ctx.fillStyle = "#dafeea";
      ctx.font = "10px system-ui";
      ctx.fillText("POWER-UP", WIDTH/2 - 26, 30);
    }

    if (flashTimer > 0) {
      const alpha = flashTimer / 0.25;
      ctx.fillStyle = "rgba(255,120,120," + alpha.toFixed(2) + ")";
      ctx.fillRect(0, 0, WIDTH, HEIGHT);
    }

    if (gameOver) {
      ctx.fillStyle = "rgba(0,0,0,0.75)";
      ctx.fillRect(0, 0, WIDTH, HEIGHT);
      ctx.fillStyle = "#f8f2ff";
      ctx.font = "32px system-ui";
      ctx.textAlign = "center";
      ctx.fillText("GAME OVER", WIDTH/2, HEIGHT/2 - 20);
      ctx.font = "18px system-ui";
      ctx.fillText("Final Score: " + score, WIDTH/2, HEIGHT/2 + 10);
      ctx.font = "14px system-ui";
      ctx.fillText("Press ENTER to restart", WIDTH/2, HEIGHT/2 + 36);
      ctx.textAlign = "start";
    }
  }

  let lastTime = performance.now();

  function loop(now) {
    const dt = Math.min(0.05, (now - lastTime) / 1000);
    lastTime = now;

    if (!gameOver) update(dt);
    draw();

    requestAnimationFrame(loop);
  }

  function resetGame() {
    bullets = [];
    enemies = [];
    powerups = [];
    enemyTimer = 0;
    powerTimer = 0;
    timeSurvived = 0;
    score = 0;
    flashTimer = 0;
    gameOver = false;
    player.x = WIDTH / 2;
    player.y = HEIGHT - 60;
    player.lives = 3;
    player.powerTimer = 0;
  }

  function update(dt) {
    timeSurvived += dt;
    player.update(dt);

    enemyTimer += dt;
    powerTimer += dt;

    const interval = Math.max(0.35, enemyInterval - timeSurvived * 0.01);
    if (enemyTimer >= interval) {
      enemyTimer -= interval;
      spawnEnemy();
    }
    if (powerTimer >= powerInterval) {
      powerTimer = 0;
      spawnPowerUp();
    }

    if (keys["Space"] && player.canFire()) {
      player.resetFire();
      if (player.hasPower()) {
        bullets.push(new Bullet(player.x - 10, player.y - 12));
        bullets.push(new Bullet(player.x + 10, player.y - 12));
      } else {
        bullets.push(new Bullet(player.x, player.y - 12));
      }
    }

    bullets.forEach(b => b.update(dt));
    enemies.forEach(e => e.update(dt));
    powerups.forEach(p => p.update(dt));

    bullets = bullets.filter(b => !b.outOfBounds());
    enemies = enemies.filter(e => !e.outOfBounds());
    powerups = powerups.filter(p => !p.outOfBounds());

    // bullets vs enemies
    const remainingBullets = [];
    bulletsLoop:
    for (const b of bullets) {
      const bRect = {x: b.x - b.w/2, y: b.y - b.h/2, w: b.w, h: b.h};
      let hit = false;
      for (const e of enemies) {
        const eRect = {x: e.x - e.w/2, y: e.y - e.h/2, w: e.w, h: e.h};
        if (rectsOverlap(bRect, eRect)) {
          e.hp -= 1;
          score += 10;
          hit = true;
          break;
        }
      }
      if (!hit) remainingBullets.push(b);
    }
    bullets = remainingBullets;
    enemies = enemies.filter(e => !e.isDead());

    // player vs enemies
    const pRect = {x: player.x - player.w/2, y: player.y - player.h/2, w: player.w, h: player.h};
    const remainingEnemies = [];
    for (const e of enemies) {
      const eRect = {x: e.x - e.w/2, y: e.y - e.h/2, w: e.w, h: e.h};
      if (rectsOverlap(pRect, eRect)) {
        if (!gameOver) {
          player.lives -= 1;
          flashTimer = 0.25;
          if (player.lives <= 0) gameOver = true;
        }
      } else remainingEnemies.push(e);
    }
    enemies = remainingEnemies;

    // player vs powerups
    const remainingP = [];
    for (const p of powerups) {
      const r = {x: p.x - p.size/2, y: p.y - p.size/2, w: p.size, h: p.size};
      if (rectsOverlap(pRect, r)) {
        player.powerTimer = 6.0;
      } else remainingP.push(p);
    }
    powerups = remainingP;

    score += Math.floor(dt * 4);

    if (flashTimer > 0) flashTimer -= dt;

    if (gameOver && keys["Enter"]) {
      resetGame();
    }
  }

  requestAnimationFrame(loop);
})();
</script>
</body>
</html>
"""


@app.get("/")
def index() -> str:
    return render_template_string(GAME_HTML)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


def main() -> None:
    port = int(os.getenv("PORT", "8080"))
    app.run(host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()
