// The 8-bit TV. EVERYTHING the player sees is drawn here as pixel art:
// power bars, the pixel world, the story dialog box and the choices.
//
// Screen layout (256 x 256 "console pixels", drawn 3x sharper):
//    y   0-15   power bars + story part
//    y   0-143  the pixel world (mushrooms, signs, roots)
//    y 133-143  hint line
//    y 144-255  dialog box: story pages, then choices
//
// Controls: arrows / WASD walk · SPACE or ENTER = next page / choose the sign you stand at
//           1-4 = choose · click/tap: dialog = next or pick a choice, world = walk (click a sign to pick it)
//
// index.html calls:
//   TV.play({ world: {sceneId, state, history, ending}, part, pages: [{who, kind, text}],
//             choicesTitle, choices: [{label, sub, pick}], notes: [string] })
//   TV.setBusy(name | null)      // "Bram is thinking..."
//   TV.error(message)

(function () {
  const W = 256, H = 256, WORLD_H = 144, GROUND = 110, DLG = 144;
  const S = 3;
  const canvas = document.getElementById("tv");
  const ctx = canvas.getContext("2d");
  canvas.width = W * S; canvas.height = H * S;
  ctx.setTransform(S, 0, 0, S, 0, 0);
  ctx.imageSmoothingEnabled = false;

  const BODY = '12px "VT323", monospace';         // easy-to-read terminal pixel font
  const LABEL = '8px "Press Start 2P", monospace'; // chunky 8-bit font for labels
  const SMALL = '11px "VT323", monospace';
  let fontsReady = false;
  if (document.fonts) Promise.all([document.fonts.load(BODY), document.fonts.load(LABEL)]).then(() => { fontsReady = true; wrapCache.clear(); });

  const C = { ink: "#fff7ee", dim: "#bfb6e6", gold: "#ffd23f", glow: "#7ef9d4", heat: "#ff6f8a",
              box: "#1b1650", boxDark: "#0d0a24", line: "#ffffff", black: "#000000", hi: "#3a2f8a" };

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
  const ARROW = ["X...", "XX..", "XXX.", "XX..", "X..."];
  const DOWN = ["XXXXX", ".XXX.", "..X.."];
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
  let world = { sceneId: "menu", state: { entropy: 0, connection: 3 }, history: [] };
  let part = "THE QUEST FOR AI";
  let pages = [], page = null, shown = 0, stage = "pages";
  let choices = [], choicesTitle = "", notes = [], busy = null, errorMsg = null;
  let nearIndex = -1, hoverIndex = -1, pulse = 0, lastConnection = 0, lastEnding = null, t0 = performance.now();
  const keys = new Set();
  const confetti = [];
  const wrapCache = new Map();
  let choiceRects = [];

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

  // How healthy each mushroom's root is: 1 = glowing, 0.5 = dim, 0 = cold patch.
  // Follows the story: hurting someone dims their root, repairing it lights it back up.
  const ROOT_EVENTS = {
    c_pile_on: { Sam: .5 }, c_keep_quiet: { Sam: .5 }, c_vote_kick: { Sam: 0 }, c_blame: { Sam: 0 },
    c_suggest_role: { Sam: 1 }, c_tell_team_gently: { Sam: 1 }, c_own_it: { Sam: 1 }, c_sorry_after_vote: { Sam: 1 },
    c_stop_sam: { Sam: 1 }, c_friend_sam: { Sam: 1 },
    c_roll: { Mia: .5 }, c_ask_team: { Mia: .5 }, c_grab: { Mia: .5 }, c_keep_it: { Mia: 0 },
    c_comfort_mia: { Mia: 1 }, c_give_mia: { Mia: 1 }, c_give_back: { Mia: 1 },
    c_keep_arguing: { Max: .5 }, c_complain: { Max: .5 }, c_ignore_max: { Max: .5 }, c_let_quit: { Max: .5 }, c_mock_max: { Max: 0 },
    c_hear_max: { Max: 1 }, c_cheer_max: { Max: 1 }, c_explain_max: { Max: 1 }, c_calm_max: { Max: 1 }, c_revive_max: { Max: 1 },
  };
  const SCENE_ROOTS = { s_heat: { Sam: .5 } };   // the story says Sam's roots turn grey here
  function rootHealth(history, sceneId) {
    const h = { you: 1, Sam: 1, Max: 1, Mia: 1 };
    for (const step of history || []) Object.assign(h, ROOT_EVENTS[step.choice_id] || {});
    for (const [n, v] of Object.entries(SCENE_ROOTS[sceneId] || {})) h[n] = Math.min(h[n], v);
    return h;
  }

  function signSpots(n) {
    if (n <= 0) return [];
    const left = 22, right = 190, y = 50;
    return Array.from({ length: n }, (_, i) => ({ x: n === 1 ? 106 : left + i * (right - left) / (n - 1), y }));
  }

  // ---------- public API ----------
  window.TV = {
    play(o) {
      const prevScene = world.sceneId;
      world = o.world || world;
      const conn = world.state?.connection ?? 0;
      if (conn > lastConnection) pulse = 1;
      lastConnection = conn;
      const endId = world.ending?.id || null;
      if ((world.sceneId === "s_win" && prevScene !== "s_win") || (endId === "e_mycelial" && lastEnding !== endId)) burstConfetti();
      lastEnding = endId;
      if (prevScene !== world.sceneId) { player.tx = player.ty = null; player.pendingPick = -1; }
      part = (o.part || part).toUpperCase();
      pages = (o.pages || []).filter(p => p && p.text);
      choices = o.choices || []; choicesTitle = o.choicesTitle || "WHAT DO YOU DO?"; notes = o.notes || [];
      busy = null; errorMsg = null;
      stage = "pages";
      nextPage();
    },
    setBusy(name) { busy = name; },
    error(msg) { errorMsg = msg; busy = null; stage = "choices"; },
  };

  function nextPage() {
    if (!pages.length) { page = null; stage = "choices"; announce(); return; }
    page = pages.shift(); shown = 0; announce();
  }

  function advance() {
    if (busy || stage !== "pages" || !page) return false;
    if (shown < page.text.length) { shown = page.text.length; return true; }
    nextPage(); return true;
  }

  function pick(i) {
    if (busy || stage !== "choices") return;
    const c = choices[i];
    if (c) c.pick();
  }

  // Screen readers: mirror what's on screen as text.
  function announce() {
    const live = document.getElementById("tv-live");
    if (!live) return;
    live.textContent = page ? `${page.who || "Story"}: ${page.text}`
      : `${choicesTitle} ${notes.join(" ")} ` + choices.map((c, i) => `${i + 1}: ${c.label}.`).join(" ");
  }

  // ---------- input ----------
  addEventListener("keydown", e => {
    const k = e.key.toLowerCase();
    if (["arrowleft", "arrowright", "arrowup", "arrowdown", "a", "d", "w", "s"].includes(k)) {
      keys.add(k); player.tx = player.ty = null; e.preventDefault();
    } else if (k === " " || k === "enter") {
      e.preventDefault();
      if (advance()) return;
      if (stage === "choices" && nearIndex >= 0) pick(nearIndex);
    } else if (/^[1-4]$/.test(k)) {
      pick(Number(k) - 1);
    }
  });
  addEventListener("keyup", e => keys.delete(e.key.toLowerCase()));

  function toScreen(e) {
    const r = canvas.getBoundingClientRect();
    return { x: (e.clientX - r.left) * W / r.width, y: (e.clientY - r.top) * H / r.height };
  }
  function choiceAt(x, y) { return choiceRects.findIndex(r => x >= r.x && x <= r.x + r.w && y >= r.y && y <= r.y + r.h); }

  canvas.addEventListener("pointermove", e => {
    const { x, y } = toScreen(e);
    hoverIndex = stage === "choices" ? choiceAt(x, y) : -1;
    canvas.style.cursor = hoverIndex >= 0 || (y >= DLG && stage === "pages") ? "pointer" : "default";
  });
  canvas.addEventListener("pointerdown", e => {
    const { x, y } = toScreen(e);
    if (y >= DLG) {                       // dialog box
      if (advance()) return;
      const i = stage === "choices" ? choiceAt(x, y) : -1;
      if (i >= 0) pick(i);
      return;
    }
    if (advance()) return;                // tapping the world also moves the story on
    const spots = stage === "choices" ? signSpots(choices.length) : [];
    const hit = spots.findIndex(s => Math.abs(s.x - x) < 14 && y > s.y - 14 && y < s.y + 22);
    player.tx = Math.max(4, Math.min(W - 28, (hit >= 0 ? spots[hit].x - 12 : x - 12)));
    player.ty = Math.max(46, Math.min(86, hit >= 0 ? spots[hit].y + 4 : y - 12));
    player.pendingPick = hit;
  });

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

    const spots = stage === "choices" ? signSpots(choices.length) : [];
    nearIndex = spots.findIndex(s => Math.abs(s.x - (player.x + 12)) < 16 && Math.abs(s.y + 16 - (player.y + 12)) < 20);

    if (page && shown < page.text.length) shown = Math.min(page.text.length, shown + 1.6);
    pulse = Math.max(0, pulse - 0.008);
    for (const c of confetti) { c.x += c.vx; c.y += c.vy; c.vy += 0.03; }
    while (confetti.length && confetti[0].y > WORLD_H) confetti.shift();
  }

  function burstConfetti() {
    for (let i = 0; i < 80; i++)
      confetti.push({ x: Math.random() * W, y: -Math.random() * 40, vx: (Math.random() - .5) * .6, vy: Math.random(),
                      c: ["#ffd23f", "#7ef9d4", "#ff8fd0", "#6ab8ff"][i % 4] });
  }

  // ---------- text helpers ----------
  function text(s, x, y, color, font = BODY, shadow = true) {
    ctx.font = font;
    if (shadow) { ctx.fillStyle = C.black; ctx.fillText(s, x + 1, y + 1); }
    ctx.fillStyle = color; ctx.fillText(s, x, y);
  }
  function wrap(s, width, font = BODY) {
    const key = font + "|" + width + "|" + s + "|" + fontsReady;
    if (wrapCache.has(key)) return wrapCache.get(key);
    ctx.font = font;
    const lines = [];
    for (const para of s.split("\n")) {
      let line = "";
      for (const w of para.split(/\s+/).filter(Boolean)) {
        const test = line ? line + " " + w : w;
        if (ctx.measureText(test).width > width && line) { lines.push(line); line = w; } else line = test;
      }
      lines.push(line);
    }
    wrapCache.set(key, lines);
    return lines;
  }
  function fit(s, width, font) {
    ctx.font = font;
    if (ctx.measureText(s).width <= width) return s;
    while (s.length > 1 && ctx.measureText(s + "…").width > width) s = s.slice(0, -1);
    return s + "…";
  }
  function pixelBox(x, y, w, h, fill = C.box) {
    ctx.fillStyle = C.black; ctx.fillRect(x - 1, y + 1, w + 2, h - 2); ctx.fillRect(x + 1, y - 1, w - 2, h + 2);
    ctx.fillStyle = C.line; ctx.fillRect(x, y + 1, w, h - 2); ctx.fillRect(x + 1, y, w - 2, h);
    ctx.fillStyle = fill; ctx.fillRect(x + 2, y + 2, w - 4, h - 4);
  }

  // ---------- draw: world ----------
  function drawWorld(t) {
    const id = world.sceneId, st = world.state || {}, ending = world.ending?.id;
    const tense = (st.entropy ?? 0) >= 4;
    const shade = id === "s_shade";
    const tvOff = ending === "e_rest";
    const lost = id === "s_lose" || ending === "e_cold_network";

    const sky = ctx.createLinearGradient(0, 0, 0, GROUND);
    if (shade) { sky.addColorStop(0, "#0b1440"); sky.addColorStop(1, "#1b2a6b"); }
    else if (lost) { sky.addColorStop(0, "#2a2a3a"); sky.addColorStop(1, "#4a4a5a"); }
    else if (tense) { sky.addColorStop(0, "#3a1030"); sky.addColorStop(1, "#7a2a4a"); }
    else { sky.addColorStop(0, "#2a1f5c"); sky.addColorStop(1, "#6a4bb0"); }
    ctx.fillStyle = sky; ctx.fillRect(0, 0, W, GROUND);
    for (let i = 0; i < 18; i++) { ctx.fillStyle = "rgba(255,255,255,.5)"; ctx.fillRect((i * 53) % W, 18 + (i * 29) % 40, 1, 1); }

    ctx.fillStyle = shade ? "#1f3a5a" : "#3d8b4a"; ctx.fillRect(0, GROUND, W, 4);
    ctx.fillStyle = "#3b2416"; ctx.fillRect(0, GROUND + 4, W, WORLD_H - GROUND - 4);

    const onScreen = shade ? ["you"] : ["you", "Sam", "Max", "Mia"];

    // Roots under the ground. Each mushroom has its own root: it glows with the team,
    // and goes dim or cold when that person gets hurt (see rootHealth).
    const conn = Math.min(10, st.connection ?? 0) / 10;
    const rootY = 126, top = GROUND + 4;
    const glowRGB = lost ? [85, 85, 85] : [Math.round(90 + 36 * conn), Math.round(80 + 169 * conn), Math.round(70 + 142 * conn)];
    const coldRGB = [30, 26, 34];
    const mix = h => `rgb(${glowRGB.map((g, i) => Math.round(coldRGB[i] + (g - coldRGB[i]) * h)).join(",")})`;
    const health = rootHealth(world.history, id);
    const flicker = id === "intro" && Math.floor(t * 6) % 4 === 0;
    const roots = onScreen.map(n => ({ n, x: Math.round((n === "you" ? player.x : CAST[n].home) + 12), h: health[n] ?? 1 }))
                          .sort((a, b) => a.x - b.x);
    // cold patches in the soil under hurt mushrooms
    for (const r of roots) if (r.h < 1) {
      ctx.fillStyle = `rgba(6,4,14,${0.8 * (1 - r.h)})`;
      ctx.fillRect(r.x - 12, top, 25, WORLD_H - top - 11);
      if (r.h === 0 && Math.floor(t * 2) % 2) { ctx.fillStyle = "#8fa3c8"; ctx.fillRect(r.x - 6, top + 6, 1, 1); ctx.fillRect(r.x + 5, top + 12, 1, 1); ctx.fillRect(r.x - 3, top + 15, 1, 1); }
    }
    // horizontal links: each piece takes the colour of the weaker end
    for (let i = 0; i < roots.length - 1; i++) {
      const a = roots[i], b = roots[i + 1];
      ctx.fillStyle = mix(Math.min(a.h, b.h)); ctx.globalAlpha = flicker ? .35 : 1;
      ctx.fillRect(a.x, rootY, b.x - a.x + 2, 2);
    }
    if (!shade && !lost && roots.length) { // link to the Mother Mushroom
      const last = roots[roots.length - 1];
      ctx.fillStyle = mix(last.h); ctx.fillRect(last.x, rootY, 236 - last.x, 2);
    }
    // each mushroom's own root
    for (const r of roots) { ctx.fillStyle = mix(r.h); ctx.fillRect(r.x, top, 2, rootY - top); }
    ctx.globalAlpha = 1;
    if (pulse > 0 && roots.length > 1) {
      const px = roots[0].x + (roots[roots.length - 1].x - roots[0].x) * ((1 - pulse) * 2 % 1);
      ctx.fillStyle = "#ffffff"; ctx.fillRect(Math.round(px) - 1, rootY - 1, 3, 3);
    }

    // background props
    if (shade) {
      sprite(OWL, 180, 80 + Math.round(Math.sin(t * 2)), {}, 2);
      text("HOOT", 186, 76, C.gold, SMALL);
    } else if (BOSS.includes(id)) {
      drawRotKing(206, 52, t);
    } else if (id === "s_win" || ending === "e_mycelial" || ending === "e_quiet_win") {
      ctx.fillStyle = "#6b4a2a"; for (let i = 0; i < 4; i++) ctx.fillRect(200 + i * 9, 100 - (i % 2) * 4, 8, 6);
      sprite(MUSH, 210, 34, { C: "#b48cff" }, 3);
    } else if (!tvOff && !STRANGER.includes(id)) {
      sprite(MUSH, 206, 62, { C: "#b48cff" }, 4);
      text("MOTHER", 214, 58, C.ink, SMALL);
    }
    if (STRANGER.includes(id)) {
      const gx = 214, gy = 86 + Math.round(Math.sin(t * 6));
      sprite(MUSH, gx, gy, { C: "#5a2a8a", S: "#cdbbe0", E: "#ff3355" }, 2);
      text("GLOWKING_99", gx - 16, gy - 3, "#ff9fd0", SMALL);
    }
    if (id === "s_regroup") {
      sprite(GOLD_CAP, 112, 102, {}, 2);
      if (Math.floor(t * 4) % 2) { ctx.fillStyle = "#fff"; ctx.fillRect(116, 97, 2, 2); ctx.fillRect(128, 99, 2, 2); }
    }

    // bugs: more bugs when the team is tense
    if (!shade && !tvOff && !(id === "s_win" || ending)) {
      const n = 1 + Math.min(8, st.entropy ?? 0);
      for (let i = 0; i < n; i++) sprite(BUG, (i * 37 + t * (12 + i * 3)) % 50 - 10, 102 - (i % 3) * 3, {}, 2);
    }

    // characters
    const owner = capOwner(world.history);
    for (const n of onScreen) {
      const c = CAST[n];
      let x = n === "you" ? player.x : c.home + Math.sin(t * .8 + c.home) * 3;
      let y = n === "you" ? player.y : 86;
      if (n !== "you" && !tense && !lost && (st.connection ?? 0) >= 4) y -= Math.abs(Math.sin(t * 4 + c.home)) * 3;
      if (tense) x += Math.sin(t * 40 + c.home) * .8;
      let alpha = 1, color = c.cap;
      const lagging = n === "Sam" && PART1.includes(id) && id !== "s_vote_fails";
      if (lagging && Math.floor(t * 3) % 3 === 0) alpha = .25;
      if (n === "Sam" && id === "s_vote_fails") color = "#6b7a8a";
      const ko = n === "Max" && id === "s_boss";
      if (ko) { y = 96; color = "#8a5a60"; text("KO!", x + 7, y - 4, C.ink, SMALL); }
      sprite(MUSH, x, y, { C: color }, 2, alpha);
      if (owner === n) sprite(GOLD_CAP, x + 2, y - 6, {}, 2);
      if (!ko) text(c.name, x + 7, y - (owner === n ? 8 : 2), n === "you" ? C.gold : C.ink, SMALL);
      if (lagging) text("LAG", x + 7, y + 34, "#ff8fa3", SMALL);
    }

    // choice signs (only when it's time to choose)
    if (stage === "choices" && !busy) {
      signSpots(choices.length).forEach((s, i) => {
        const near = i === nearIndex || i === hoverIndex;
        ctx.fillStyle = "#6b4a2a"; ctx.fillRect(s.x - 1, s.y + 6, 2, 10);
        ctx.fillStyle = C.black; ctx.fillRect(s.x - 8, s.y - 5, 16, 13);
        ctx.fillStyle = near ? C.glow : "#f3d9a4"; ctx.fillRect(s.x - 7, s.y - 4, 14, 11);
        text(String(i + 1), s.x - 3, s.y + 5, "#2a1b33", LABEL, false);
      });
    }

    for (const c of confetti) { ctx.fillStyle = c.c; ctx.fillRect(Math.round(c.x), Math.round(c.y), 2, 2); }
    if (tense) { ctx.fillStyle = "rgba(255,80,110,.55)"; ctx.fillRect(0, 16, W, 2); ctx.fillRect(0, WORLD_H - 2, W, 2); ctx.fillRect(0, 16, 2, WORLD_H - 16); ctx.fillRect(W - 2, 16, 2, WORLD_H - 16); }
    if (tvOff) { ctx.fillStyle = "rgba(0,0,0,.8)"; ctx.fillRect(0, 0, W, WORLD_H); text("ZZZ... SEE YOU TOMORROW", 70, 76, C.glow, BODY); }
  }

  function drawRotKing(x, y, t) {
    const wob = Math.round(Math.sin(t * 2));
    ctx.fillStyle = "#5a3a22"; ctx.fillRect(x, y + wob, 44, 58);
    ctx.fillStyle = "#7a5232"; for (let i = 0; i < 5; i++) ctx.fillRect(x + 2, y + 6 + i * 11 + wob, 40, 3);
    ctx.fillStyle = "#3a5a2a"; ctx.fillRect(x - 2, y - 4 + wob, 48, 6);
    ctx.fillStyle = "#ffdd33"; ctx.fillRect(x + 10, y + 16 + wob, 6, 4); ctx.fillRect(x + 28, y + 16 + wob, 6, 4);
    ctx.fillStyle = "#2a1b10"; ctx.fillRect(x + 12, y + 32 + wob, 20, 4);
    text("ROT KING", x + 4, y - 6 + wob, "#ffdd33", SMALL);
  }

  // ---------- draw: power bars ----------
  function drawHud() {
    const st = world.state || {};
    ctx.fillStyle = "rgba(8,6,24,.88)"; ctx.fillRect(0, 0, W, 16);
    ctx.fillStyle = C.black; ctx.fillRect(0, 16, W, 1);
    text(fit(part, 104, BODY), 4, 11, C.gold, BODY);
    bar("TENSION", st.entropy ?? 0, 112, C.heat);
    bar("GLOW", st.connection ?? 0, 190, C.glow);
  }
  function bar(label, value, x, color) {
    text(label, x, 11, C.ink, SMALL);
    ctx.font = SMALL;
    const bx = x + Math.ceil(ctx.measureText(label).width) + 3;
    for (let i = 0; i < 10; i++) {
      ctx.fillStyle = C.black; ctx.fillRect(bx + i * 3 - 1, 4, 4, 9);
      ctx.fillStyle = i < value ? color : "#2a2450"; ctx.fillRect(bx + i * 3, 5, 2, 7);
    }
  }

  // ---------- draw: hint line + dialog box ----------
  function drawHint() {
    ctx.fillStyle = "rgba(0,0,0,.7)"; ctx.fillRect(0, WORLD_H - 11, W, 11);
    let hint, color = C.dim;
    if (busy) hint = `${busy.toUpperCase()} IS THINKING${".".repeat(1 + Math.floor(performance.now() / 300) % 3)}`;
    else if (stage === "pages") hint = "SPACE OR TAP = NEXT    ARROWS / WASD = WALK";
    else if (nearIndex >= 0) { hint = `SPACE = PICK ${nearIndex + 1}`; color = C.glow; }
    else hint = "WALK TO A SIGN + SPACE  -  OR PRESS 1-4  -  OR TAP";
    text(fit(hint, W - 8, SMALL), 4, WORLD_H - 3, color, SMALL);
  }

  function drawDialog(t) {
    ctx.fillStyle = C.boxDark; ctx.fillRect(0, DLG, W, H - DLG);
    const bx = 5, by = DLG + 9, bw = W - 10, bh = H - DLG - 13;
    pixelBox(bx, by, bw, bh);
    const tx = bx + 7, maxW = bw - 14;
    choiceRects = [];

    const tag = (label, color) => {
      ctx.font = LABEL;
      const w = Math.ceil(ctx.measureText(label).width) + 8;
      pixelBox(bx + 6, by - 8, w, 15, color);
      text(label, bx + 10, by + 3.5, "#000", LABEL, false);
    };

    if (busy) {
      tag(busy.toUpperCase(), C.glow);
      text("Thinking" + ".".repeat(1 + Math.floor(t * 3) % 3), tx, by + 22, C.dim, BODY);
      return;
    }
    if (stage === "pages" && page) {
      const kindColor = page.kind === "helper" ? C.glow : page.kind === "narrator" ? "#cdbbff" : C.gold;
      tag(fit((page.who || "STORY").toUpperCase(), 200, LABEL), kindColor);
      const lines = wrap(page.text.slice(0, Math.floor(shown)), maxW);
      lines.slice(0, 8).forEach((l, i) => text(l, tx, by + 19 + i * 10, page.kind === "helper" ? "#dffcf3" : C.ink, BODY));
      if (shown >= page.text.length && Math.floor(t * 2) % 2) sprite(DOWN, bx + bw - 14, by + bh - 9, { X: C.glow });
      return;
    }
    // choices
    tag(fit(choicesTitle.toUpperCase(), 200, LABEL), C.gold);
    let y = by + 19;
    for (const n of notes) {
      const lines = wrap("• " + n, maxW);
      for (const l of lines) { text(l, tx, y, C.dim, BODY); y += 10; }
    }
    if (notes.length) y += 3;
    choices.forEach((c, i) => {
      const lines = wrap(c.label, maxW - 14);
      const sub = c.sub ? wrap(c.sub, maxW - 14, SMALL) : [];
      const h = lines.length * 10 + sub.length * 9 + 2;
      const active = i === nearIndex || i === hoverIndex;
      if (active) { ctx.fillStyle = C.hi; ctx.fillRect(tx - 3, y - 9, maxW + 4, h); sprite(ARROW, tx - 2, y - 6, { X: C.glow }); }
      text(String(i + 1), tx + 4, y, C.gold, BODY);
      lines.forEach((l, j) => text(l, tx + 14, y + j * 10, active ? "#ffffff" : C.ink, BODY));
      sub.forEach((l, j) => text(l, tx + 14, y + lines.length * 10 + j * 9, C.dim, SMALL));
      choiceRects.push({ x: tx - 3, y: y - 9, w: maxW + 4, h });
      y += h + 1;
    });
    if (errorMsg) text(fit(errorMsg, maxW, SMALL), tx, by + bh - 5, C.heat, SMALL);
  }

  function draw(now) {
    const t = (now - t0) / 1000;
    ctx.clearRect(0, 0, W, H);
    drawWorld(t);
    drawHud();
    drawHint();
    drawDialog(t);
    ctx.fillStyle = "rgba(0,0,0,.07)";                  // old-TV scanlines
    for (let y = 0; y < H; y += 2) ctx.fillRect(0, y, W, .5);
  }

  function loop(now) { update(); draw(now); requestAnimationFrame(loop); }
  requestAnimationFrame(loop);
})();
