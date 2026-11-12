# How the Code Fits Together

```text
 Story files (content/)             Game code (src/tqfai/)
 ├─ scenarios/*.json  ── read by ─▶ scenario/    reads and checks stories
 └─ companions.json   ── read by ─▶ companions/  the 4 helpers
                                        │
                                    engine/      moves the story forward
                                        │
                                    reasoning/   what the helper says:
                                        │          - written lines (always works)
                                        │          - AI voice, asi1-mini (llm.py)
                                        │          - MeTTa (metta_adapter.py, to do)
                                        │
                                    api/         web server + JSON API
                                        │
              web/index.html  ◀─────────┘        the page players see
              api/index.py                       the same server, on Vercel
```

## Rules we follow
1. **Stories are files, not code.** A writer can add a scene without touching the code.
2. **Same choices give the same story.** Only the helper's AI words change.
3. **The game never breaks if the AI breaks.** It falls back to written lines.
4. **We measure the game world, not the child.** `entropy` and `connection` describe the team in the story. They are not scores for the player.
5. **No personal data.** No accounts, names or ages. The server saves nothing.
6. **Plain Python 3.10+.** Nothing extra to install for the core game.

## Older files
`src/engine/metta_connector.py`, `run_archetype_simulation.py`, `test_archetype_simulation.py`, `test_metta.py`, `test_hooks.py` and `src/logic/narrative_hooks.py` are Colleen's earlier experiments. They are kept as they are.
