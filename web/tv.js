// The 8-bit TV: a little pixel world above the story text.
//
// Controls:  Arrow keys / WASD = walk,  SPACE or ENTER = choose the sign you're standing at,
//            1-4 = choose directly,  mouse/finger = click a spot to walk there, click a sign to pick it.
//
// index.html talks to it with:
//   TV.show({ sceneId, state, last, history, ending, options: [{ label, button, pick }] })
//   TV.setBusy(true|false)
// All art is drawn here from tiny pixel maps. No image files needed.

(function () {
  const W = 256, H = 144, GROUND = 110;
  const canvas = document.getElementById("tv");
  const ctx = canvas.getContext("2d");
  // Draw at 3x so pixel art stays sharp and text is easy to read.
  const S = 3;
  canvas.width = W * S; canvas.height = H * S;
  ctx.setTransform(S, 0, 0, S, 0, 0);
  ctx.imageSmoothingEnabled = false;
  const FONT = 'bold 7px "Trebuchet MS", Verdana, sans-serif';

  // ---------- pixel art ----------
  const MUSH = [
    "...XXXXXX...",
    "..XCCCCCCX..",
    ".XCCWWCCCCX.",
    "XCCCWWCCWCCX",
    "XCCCCCCCCCCX",
    "XXXXXXXXXXXX",
    "..XSSSSSSX..",
    "..XSESSESX..",
    "..XSSSSSSX..",
    "..XSSMMSSX..",
    "..XSSSSSSX..",
    "...XXXXXX...",
  ];
  const GOLD_CAP = ["..Y.YY.Y..", "..YYYYYY..", "...YYYY..."];
  const BUG = [".X..X.", "XBBBBX", "BBRBBB", ".X..X."];
  const OWL = [
    ".XX....XX.",
    "XOOX..XOOX",
    "XOOOOOOOOX",
    "XOWWOOWWOX",
    "XOWEOOEWOX",
    "XOOOYYOOOX",
    "XOOOOOOOOX",
    ".XOOOOOOX.",
    "..XYXXYX..",
  ];
  const BASE = { X: "#2a1b33", W: "#ffffff", S: "#fff4e3", E: "#2a1b33", M: "#2a1b33",
                 Y: "#ffd23f", B: "#3f7a3a", R: "#d94a4a", O: "#8a6a4a" };

  function sprite(map, x, y, colors, scale = 1, alpha = 1) {
    ctx.globalAlpha = alpha;
    for (let r = 0; r < map.length; r++)
      for (let c = 0; c < map[r].length; c++) {
        const k = map[r][c];
        if (k === ".") continue;
        ctx.fillStyle = colors[k] || BASE[k] || "#f0f";
        ctx.fillRect(Math.round(x + c * scale), Math.round(y + r * scale), scale, scale);
      }
    ctx.globalAlpha = 1;
  }

  // ---------- characters ----------
  const CAST = {
    you: { name: "YOU", cap: "#ffb347", home: 60 },
    Sam: { name: "SAM", cap: "#6ab8ff", home: 96 },
    Max: { name: "MAX", cap: "#ff5d6c", home: 132 },
    Mia: { name: "MIA", cap: "#ff8fd0", home: 168 },
  };
  const player = { x: 60, y: 86, tx: null, ty: null, pendingPick: -1 };
  let view = { sceneId: "menu", state: { entropy: 0, connection: 2 }, options: [], history: [] };
  let prompt = null, busy = false, nearIndex = -1, bubble = null, pulse = 0, lastConnection = 0, t0 = performance.now();
  const keys = new Set();
  const confetti = [];

  // Which scenes have which props.
  const PART1 = ["intro", "s_sam_reply", "s_heat", "s_vote_fails", "s_max_pushback"];
  const STRANGER = ["s_stranger", "s_stranger_push"];
  const BOSS = ["s_boss", "s_boss_mid", "s_lose"];

  function capOwner(history) {
    let owner = null;
    for (const h of history || []) {
      if (h.choice_id === "c_roll" || h.choice_id === "c_ask_team") owner = "Max";
      if (h.choice_id === "c_give_mia" || h.choice_id === "c_give_back") owner = "Mia";
      if (h.choice_id === "c_grab") owner = "you";
    }
    return owner;
  }

  function signSpots(n) {
    if (n <= 0) return [];
    const left = 22, right = 190, y = 50;
    return Array.from({ length: n }, (_, i) => ({ x: n === 1 ? 106 : left + i * (right - left) / (n - 1), y }));
  }

  // ---------- public API ----------
  window.TV = {
    show(v) {
      const prevScene = view.sceneId;
      v._lastEnding = view._lastEnding;
      view = v;
      if ((v.state?.connection ?? 0) > lastConnection) pulse = 1;
      lastConnection = v.state?.connection ?? 0;
      bubble = null; // story text and speech now live in the dialog box under the screen
      const newEnding = v.ending?.id && v.ending.id !== view._lastEnding;
      if ((v.sceneId === "s_win" && prevScene !== "s_win") || (newEnding && v.ending.id === "e_mycelial")) burstConfetti();
      view._lastEnding = v.ending?.id;
      if (prevScene !== v.sceneId) { player.tx = player.ty = null; player.pendingPick = -1; }
    },
    setBusy(b) { busy = b; },
    setPrompt(s) { prompt = s; },
    onAction: null,
  };

  function speaker(text) {
    for (const n of ["Sam", "Max", "Mia", "GlowKing_99"]) if (text.startsWith(n)) return n;
    return null;
  }

  // ---------- input ----------
  addEventListener("keydown", e => {
    if (e.target.closest && e.target.closest("button, input, textarea")) return;
    const k = e.key.toLowerCase();
    if (["arrowleft", "arrowright", "arrowup", "arrowdown", "a", "d", "w", "s"].includes(k)) {
      keys.add(k); player.tx = player.ty = null; e.preventDefault();
    } else if (k === " " || k === "enter") {
      if (window.TV.onAction && window.TV.onAction()) { e.preventDefault(); return; }
      if (nearIndex >= 0) { pick(nearIndex); e.preventDefault(); }
    } else if (/^[1-4]$/.test(k)) {
      pick(Number(k) - 1);
    }
  });
  addEventListener("keyup", e => keys.delete(e.key.toLowerCase()));

  canvas.addEventListener("pointerdown", e => {
    const r = canvas.getBoundingClientRect();
    const x = (e.clientX - r.left) * W / r.width, y = (e.clientY - r.top) * H / r.height;
    const spots = signSpots(view.options?.length || 0);
    const hit = spots.findIndex(s => Math.abs(s.x - x) < 14 && y > s.y - 14 && y < s.y + 22);
    player.tx = Math.max(4, Math.min(W - 28, (hit >= 0 ? spots[hit].x - 12 : x - 12)));
    player.ty = Math.max(46, Math.min(86, hit >= 0 ? spots[hit].y + 4 : y - 12));
    player.pendingPick = hit;
  });

  function pick(i) {
    const opt = view.options?.[i];
    if (!opt || busy) return;
    opt.pick();
  }

  // ---------- update ----------
  function update() {
    const sp = 1.4;
    let dx = 0, dy = 0;
    if (keys.has("arrowleft") || keys.has("a")) dx -= sp;
    if (keys.has("arrowright") || keys.has("d")) dx += sp;
    if (keys.has("arrowup") || keys.has("w")) dy -= sp;
    if (keys.has("arrowdown") || keys.has("s")) dy += sp;
    if (player.tx !== null) {
      const ddx = player.tx - player.x, ddy = player.ty - player.y, dist = Math.hypot(ddx, ddy);
      if (dist < 1.5) {
        player.tx = player.ty = null;
        if (player.pendingPick >= 0) { const p = player.pendingPick; player.pendingPick = -1; pick(p); }
      } else { dx = ddx / dist * sp; dy = ddy / dist * sp; }
    }
    player.x = Math.max(4, Math.min(W - 28, player.x + dx));
    player.y = Math.max(46, Math.min(86, player.y + dy));

    // Which sign is the player standing at?
    const spots = signSpots(view.options?.length || 0);
    nearIndex = spots.findIndex(s => Math.abs(s.x - (player.x + 12)) < 16 && Math.abs(s.y + 16 - (player.y + 12)) < 20);
    (view.options || []).forEach((o, i) => o.button?.classList.toggle("near", i === nearIndex));

    pulse = Math.max(0, pulse - 0.008);
    for (const c of confetti) { c.x += c.vx; c.y += c.vy; c.vy += 0.03; }
    while (confetti.length && confetti[0].y > H) confetti.shift();
  }

  function burstConfetti() {
    for (let i = 0; i < 80; i++)
      confetti.push({ x: Math.random() * W, y: -Math.random() * 40, vx: (Math.random() - .5) * .6, vy: Math.random(),
                      c: ["#ffd23f", "#7ef9d4", "#ff8fd0", "#6ab8ff"][i % 4] });
  }

  // ---------- draw ----------
  function draw(now) {
    const t = (now - t0) / 1000;
    const id = view.sceneId, st = view.state || {}, ending = view.ending?.id;
    const tense = (st.entropy ?? 0) >= 4;
    const shade = id === "s_shade";
    const tvOff = ending === "e_rest";
    const lost = id === "s_lose" || ending === "e_cold_network";

    // sky
    const sky = ctx.createLinearGradient(0, 0, 0, GROUND);
    if (shade) { sky.addColorStop(0, "#0b1440"); sky.addColorStop(1, "#1b2a6b"); }
    else if (lost) { sky.addColorStop(0, "#2a2a3a"); sky.addColorStop(1, "#4a4a5a"); }
    else if (tense) { sky.addColorStop(0, "#3a1030"); sky.addColorStop(1, "#7a2a4a"); }
    else { sky.addColorStop(0, "#2a1f5c"); sky.addColorStop(1, "#6a4bb0"); }
    ctx.fillStyle = sky; ctx.fillRect(0, 0, W, GROUND);
    for (let i = 0; i < 18; i++) { ctx.fillStyle = "rgba(255,255,255,.5)"; ctx.fillRect((i * 53) % W, (i * 29) % 50, 1, 1); }

    // ground + underground
    ctx.fillStyle = shade ? "#1f3a5a" : "#3d8b4a"; ctx.fillRect(0, GROUND, W, 4);
    ctx.fillStyle = "#3b2416"; ctx.fillRect(0, GROUND + 4, W, H - GROUND - 4);

    // who is on screen
    const onScreen = shade ? ["you"] : ["you", "Sam", "Max", "Mia"];

    // roots between everyone: colour = team connection
    const conn = Math.min(10, st.connection ?? 0) / 10;
    const rootY = 128;
    const rootColor = lost ? "#555" : `rgb(${Math.round(90 + (126 - 90) * conn)},${Math.round(80 + (249 - 80) * conn)},${Math.round(70 + (212 - 70) * conn)})`;
    ctx.fillStyle = rootColor;
    const xs = onScreen.map(n => (n === "you" ? player.x : CAST[n].home) + 12).sort((a, b) => a - b);
    for (const x of xs) ctx.fillRect(Math.round(x), GROUND + 4, 1, rootY - GROUND - 4);
    if (xs.length > 1) ctx.fillRect(Math.round(xs[0]), rootY, Math.round(xs[xs.length - 1] - xs[0]) + 1, 1);
    if (!shade && !lost) ctx.fillRect(Math.round(xs[xs.length - 1]), rootY, 236 - Math.round(xs[xs.length - 1]), 1);
    if (pulse > 0 && xs.length > 1) {
      const px = xs[0] + (xs[xs.length - 1] - xs[0]) * ((1 - pulse) * 2 % 1);
      ctx.fillStyle = "#ffffff"; ctx.fillRect(Math.round(px) - 1, rootY - 1, 3, 3);
    }

    // background props
    if (shade) {
      sprite(OWL, 180, 80 + Math.round(Math.sin(t * 2)), {}, 2);
      text("HOOT", 184, 76, "#ffd23f");
    } else if (BOSS.includes(id) && id !== "s_win") {
      drawRotKing(206, 52, t);
    } else if (id === "s_win" || ending === "e_mycelial" || ending === "e_quiet_win") {
      ctx.fillStyle = "#6b4a2a"; for (let i = 0; i < 4; i++) ctx.fillRect(200 + i * 9, 100 - (i % 2) * 4, 8, 6); // log pile
      sprite(MUSH, 210, 30, { C: "#b48cff" }, 3);
    } else if (!tvOff && !STRANGER.includes(id)) {
      sprite(MUSH, 206, 62, { C: "#b48cff" }, 4); // Mother Mushroom
      text("MOTHER", 214, 58, "#fff");
    }
    if (STRANGER.includes(id)) {
      const gx = 214, gy = 86 + Math.round(Math.sin(t * 6));
      sprite(MUSH, gx, gy, { C: "#5a2a8a", S: "#cdbbe0", E: "#ff3355" }, 2);
      text("GLOWKING_99", gx - 14, gy - 4, "#ff9fd0");
    }
    if (id === "s_regroup") { // Golden Cap sparkle on the ground
      sprite(GOLD_CAP, 112, 102, {}, 2);
      if (Math.floor(t * 4) % 2) { ctx.fillStyle = "#fff"; ctx.fillRect(116, 97, 2, 2); ctx.fillRect(128, 99, 2, 2); }
    }

    // bugs: more bugs when the team is tense
    if (!shade && !tvOff && !(id === "s_win" || ending)) {
      const n = 1 + Math.min(8, st.entropy ?? 0);
      for (let i = 0; i < n; i++) {
        const bx = (i * 37 + t * (12 + i * 3)) % 50 - 10, by = 102 - (i % 3) * 3;
        sprite(BUG, bx, by, {}, 2);
      }
    }

    // characters
    const owner = capOwner(view.history);
    for (const n of onScreen) {
      const c = CAST[n];
      let x = n === "you" ? player.x : c.home + Math.sin(t * .8 + c.home) * 3;
      let y = n === "you" ? player.y : 86;
      const happy = !tense && !lost && (st.connection ?? 0) >= 4;
      if (n !== "you" && happy) y -= Math.abs(Math.sin(t * 4 + c.home)) * 3;
      if (tense) x += Math.sin(t * 40 + c.home) * .8;
      let alpha = 1, color = c.cap;
      const lagging = n === "Sam" && PART1.includes(id) && id !== "s_vote_fails";
      if (lagging && Math.floor(t * 3) % 3 === 0) alpha = .25;
      if (n === "Sam" && id === "s_vote_fails") color = "#6b7a8a";
      if (n === "Max" && id === "s_boss") { y = 96; color = "#8a5a60"; text("KO!", x + 6, y - 12, "#fff"); }
      sprite(MUSH, x, y, { C: color }, 2, alpha);
      if (owner === n) sprite(GOLD_CAP, x + 2, y - 6, {}, 2);
      if (!(n === "Max" && id === "s_boss")) text(c.name, x + 6, y - (owner === n ? 9 : 3), n === "you" ? "#ffd23f" : "#ffffff");
      if (lagging) text("LAG", x + 6, y + 31, "#ff8fa3");
    }

    // choice signs
    const spots = signSpots(view.options?.length || 0);
    spots.forEach((s, i) => {
      const near = i === nearIndex;
      ctx.fillStyle = "#6b4a2a"; ctx.fillRect(s.x - 1, s.y + 6, 2, 10);
      ctx.fillStyle = near ? "#7ef9d4" : "#f3d9a4"; ctx.fillRect(s.x - 7, s.y - 4, 14, 11);
      ctx.fillStyle = "#2a1b33"; ctx.fillRect(s.x - 7, s.y - 4, 14, 1); ctx.fillRect(s.x - 7, s.y + 6, 14, 1);
      text(String(i + 1), s.x - 2, s.y + 4, "#2a1b33");
    });

    // speech bubble
    if (bubble && performance.now() < bubble.until) {
      const who = bubble.who && CAST[bubble.who];
      const bx = who ? Math.min(W - 112, Math.max(2, who.home - 40)) : 4;
      drawBubble(bubble.text, bx, 4);
    }

    // hint bar
    ctx.fillStyle = "rgba(0,0,0,.7)"; ctx.fillRect(0, H - 11, W, 11);
    const hint = busy ? "Your helper is thinking..." : prompt ? prompt : nearIndex >= 0
      ? `Press SPACE: ${short(view.options[nearIndex].label)}`
      : view.options?.length ? "Walk to a sign: arrow keys or W A S D. Or click a sign." : "";
    text(hint, 4, H - 3, nearIndex >= 0 ? "#7ef9d4" : "#ffffff");

    for (const c of confetti) { ctx.fillStyle = c.c; ctx.fillRect(Math.round(c.x), Math.round(c.y), 2, 2); }
    if (tense) { ctx.strokeStyle = "rgba(255,80,110,.6)"; ctx.lineWidth = 2; ctx.strokeRect(1, 1, W - 2, H - 2); }
    if (tvOff) { ctx.fillStyle = "rgba(0,0,0,.75)"; ctx.fillRect(0, 0, W, H); text("ZZZ...  SEE YOU TOMORROW", 70, 72, "#7ef9d4"); }

    // old-TV scanlines
    ctx.fillStyle = "rgba(0,0,0,.06)";
    for (let y = 0; y < H; y += 2) ctx.fillRect(0, y, W, .5);
  }

  function drawRotKing(x, y, t) {
    const wob = Math.round(Math.sin(t * 2) * 1);
    ctx.fillStyle = "#5a3a22"; ctx.fillRect(x, y + wob, 44, 58);
    ctx.fillStyle = "#7a5232"; for (let i = 0; i < 5; i++) ctx.fillRect(x + 2, y + 6 + i * 11 + wob, 40, 3);
    ctx.fillStyle = "#3a5a2a"; ctx.fillRect(x - 2, y - 4 + wob, 48, 6);
    ctx.fillStyle = "#ffdd33"; ctx.fillRect(x + 10, y + 16 + wob, 6, 4); ctx.fillRect(x + 28, y + 16 + wob, 6, 4);
    ctx.fillStyle = "#2a1b10"; ctx.fillRect(x + 12, y + 32 + wob, 20, 4);
    text("ROT KING", x + 4, y - 7 + wob, "#ffdd33");
  }

  function short(s) { return s.length > 44 ? s.slice(0, 43) + "…" : s; }

  function text(s, x, y, color) {
    ctx.font = FONT; ctx.fillStyle = "rgba(0,0,0,.85)"; ctx.fillText(s, x + .6, y + .6);
    ctx.fillStyle = color; ctx.fillText(s, x, y);
  }

  function drawBubble(s, x, y) {
    ctx.font = FONT;
    const words = s.split(" "), lines = []; let line = "";
    for (const w of words) { if ((line + " " + w).trim().length > 26) { lines.push(line.trim()); line = w; } else line += " " + w; }
    if (line.trim()) lines.push(line.trim());
    const h = lines.slice(0, 4).length * 8 + 4;
    ctx.fillStyle = "#fff"; ctx.fillRect(x, y, 110, h);
    ctx.fillStyle = "#2a1b33"; ctx.fillRect(x, y, 110, 1); ctx.fillRect(x, y + h - 1, 110, 1); ctx.fillRect(x, y, 1, h); ctx.fillRect(x + 109, y, 1, h);
    lines.slice(0, 4).forEach((l, i) => { ctx.fillStyle = "#2a1b33"; ctx.fillText(l, x + 3, y + 9 + i * 8); });
  }

  function loop(now) { update(); draw(now); requestAnimationFrame(loop); }
  requestAnimationFrame(loop);
})();
