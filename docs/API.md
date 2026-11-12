# Web API

The website and the API share one address:
- **Online:** the Vercel link
- **Local:** `python -m tqfai serve`, then open http://127.0.0.1:8787

The server stores nothing. The browser keeps the game **save** and sends it back with every move.

| Method | Address | Send | Get back |
|---|---|---|---|
| GET | `/api/health` | – | `{ok, version, voice}` |
| GET | `/api/companions` | – | the 4 helpers and the Owl guide |
| GET | `/api/scenarios` | – | the list of stories |
| POST | `/api/start` | `{scenario_id, companion_id}` | **View** + `save` |
| POST | `/api/choose` | `{save, choice_id}` | **View** + `save` + `last` |

If something goes wrong, you get HTTP 400 with `{"error": "a friendly message"}`. It is safe to show this to the player.

## View (what the page shows)
```json
{
  "scenario":  {"id": "s01_the_lagging_teammate", "title": "The Lagging Teammate", "version": "0.1.0"},
  "companion": {"id": "Bookworm", "name": "Lumi", "title": "The Nerdy Bookworm"},
  "state":     {"entropy": 1, "connection": 0, "shade": 0},
  "finished":  false,
  "scene": {
    "id": "intro", "speaker": "narrator", "background": "orchard_dusk",
    "text": "What is happening...",
    "companion_line": "What the helper says about the scene",
    "choices": [{"id": "c_ask_sam", "text": "Send Sam a private message"}]
  },
  "last": {
    "choice_id": "c_ask_sam",
    "reaction": "What the other characters did",
    "companion_note": "What the helper said about your choice",
    "source": "asi1-mini"
  },
  "save": {"...": "send this back unchanged with the next move"}
}
```

When `finished` is `true`, there is an `ending` with `title`, `text` and `reflection_questions` in place of `scene`.

**What the numbers mean:**
- `entropy` (0–10): how tense the team is. It could make the screen glitch.
- `connection` (0–10): how close the team is. It could make the roots glow.
- `shade`: how often the player took a break.
