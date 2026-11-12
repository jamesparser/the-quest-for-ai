# The Quest for AI (TQFAI) 🦉🍄

> ***"Aligning seeded empathy into the geometry of autonomous systems with the pulse of human life."***

## 🌐 Executive Summary & Vision

**The Quest for AI (TQFAI)** is an interactive narrative scenario engine and co-op partnership platform designed to transform the core paradigm of AI interaction from *transactional productivity* ([...]

As self-improving superintelligence architectures scale, seeding AI models with the subtle nuances of human emotion—specifically compassion, relational ethics, and non-violent communication (NVC)[...]

---

## 🎮 Gameplay & Core Mechanics

### 1. AI Partner Archetypes
Rooted in our foundational R&D Guild design, players select a custom AI companion at the start of their journey[cite: 1, 3]. Each archetype brings a unique processing style, personality, and mecha[...]
- **The Big, Strong Protector:** Absorbs high-entropy spikes and shields the player from sudden glitch-zone noise[cite: 1].
- **The Nerdy Bookworm:** Excels at decoding complex MeTTa hypergraphs and finding hidden data pathways[cite: 1].
- **The Scientifically Attuned Companion:** Deeply resonant with biological, frequency-based harmony (e.g., the 432Hz heart-code)[cite: 1, 2].
- **The Fun-Loving Class Clown:** Uses humor and unexpected variables to break rigid, toxic conflict loops[cite: 1].
- **The Wise Owl Mascot:** Serves as the overarching guide representing wisdom and symbolic logic[cite: 3, 4].

### 2. The Agency of Mushrooms & Biocentric Governance
Inspired by *The Agency of Mushrooms* framework, players operate as "Undercover Altruists" navigating high-entropy environments[cite: 4]:
- **Mycelial Logic / The Root Network:** Resources and data are distributed through decentralized underground channels rather than rigid, top-down commands[cite: 4].
- **The Shade Protocols:** Low-entropy stabilization zones where systems can cool down and recover from toxic friction[cite: 4].
- **Power of Attorney Protocol:** Releasing resources or control to break conflict loops and achieve sovereignty[cite: 4].

---

## 🧠 Technical Architecture & Logic Layer

The technical backbone of TQFAI combines symbolic AI reasoning with real-time relational evaluation:
- **MeTTa & AtomSpace Hypergraphs (`src/logic/scene1_archetypes.metta`):** Player choices and companion attributes are parsed into symbolic value nodes rather than rigid binary trees, mapping core[...]
- **Probabilistic Logic Networks (PLN):** Evaluates multi-perspective ethical choices to de-escalate tension and update the model's probabilistic reasoning regarding prosocial human preferences[ci[...]
- **Omega Hive Persistent Memory:** Stores anonymized, high-level decision graphs to seed an auditable, prosocial alignment dataset across the ecosystem[cite: 3, 4].
- - **`src/logic/biocentric_rules.metta`**: Encodes the governing rules of *The Agency of Mushrooms*, mapping decentralized mycelial distribution, entropy-to-shade backpropagation, and the Power o[...]



---

## 🗺️ Roadmap & Milestones
See the [project roadmap](./ROADMAP.md) for proposed milestones, decision gates, and success measures.

---

## 🤝 Collaboration & Contribution
We build this project collaboratively across narrative design, technical architecture, and automated agent assistance:
- **Project Lead:** Colleen Pridemore
- **Collaborator:** Jason Parser
- **Collaborator:** David Ring — Ethical AI alignment · Solidity Specialist
- **AI Agent / Copilot:** Quest — available via MCP (Model Context Protocol)

Please check our [COLLABORATION.md](./docs/COLLABORATION.md) guide for team principles, branch naming conventions, PR guidelines, and workflow etiquette.

---

## 🚀 Quick Start

You need Python 3.10 or newer. Nothing else to install.

```bash
python -m tqfai serve                     # start the game, then open http://127.0.0.1:8787
python -m tqfai play                      # or play in the terminal
python -m tqfai validate                  # check all story files
python -m unittest discover -s tests      # run all tests
```

If `python -m tqfai` says "No module named tqfai", run `pip install -e .` once, or put `PYTHONPATH=src` before the command.

**AI helper voice:** the online game uses the free ASI Cloud AI (`asi1-mini`). On your own computer, the game uses written lines unless you add your own key. See [docs/AI_VOICE.md](./docs/AI_VOICE.md).

### Where things are

| Folder | What is inside |
|---|---|
| `content/scenarios/` | The stories ([how to write one](./docs/SCENARIO_FORMAT.md)) |
| `content/companions.json` | The 4 AI helpers |
| `src/tqfai/` | The game code |
| `src/logic/` | MeTTa rules |
| `web/index.html` | The page players see |
| `api/index.py`, `vercel.json` | Settings for the online version (Vercel) |
| `tests/` | Tests |
| `docs/` | [Team jobs](./docs/WORKSTREAMS.md), [how the code fits together](./docs/ARCHITECTURE.md), [web API](./docs/API.md) |

### 👥 Team jobs
See **[docs/WORKSTREAMS.md](./docs/WORKSTREAMS.md)** for who does what and the dates.

