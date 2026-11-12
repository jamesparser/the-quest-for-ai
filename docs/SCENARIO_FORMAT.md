# How to Write a Story (Scenario)

Each story is one file in `content/scenarios/`. The easiest way to start is to copy `s01_the_lagging_teammate.json` and change the words.

## The shape of a story file

```jsonc
{
  "id": "s02_shared_loot",            // short name, same as the file name
  "version": "0.1.0",                 // change this when you change the story
  "title": "The Shared Loot",
  "summary": "One or two sentences for the menu.",
  "audience": {"min_age": 9, "max_age": 12, "content_notes": []},
  "learning_goals": ["What should the kid learn?"],
  "initial_state": {"entropy": 1, "connection": 0, "shade": 0},
  "start": "intro",                   // the first scene
  "scenes": {
    "intro": {
      "speaker": "narrator",          // narrator, WiseOwl, or a character name
      "background": "orchard_dusk",   // which picture or place to show
      "text": "What is happening (700 letters or less).",
      "companion_lines": {            // what each helper says. "default" is required
        "default": "...", "Protector": "...", "Bookworm": "...",
        "ScientificallyAttuned": "...", "ClassClown": "..."
      },
      "choices": [
        {
          "id": "c_short_name",                 // different for each choice in this scene
          "text": "What the player does (120 letters or less)",
          "next": "next_scene_or_ending",
          "perspectives": ["empathy"],          // see the list below
          "effects": {"entropy": -1, "connection": 1},
          "condition": {"min": {"entropy": 3}}, // optional: only show the choice if...
          "reaction": "What the others say or do right after."
        }
      ]
    }
  },
  "endings": {
    "e_example": {
      "title": "...", "tone": "warm",          // warm, neutral or bittersweet
      "text": "...",
      "reflection_questions": ["Open questions. Not a quiz."]
    }
  }
}
```

**Note:** `ScientificallyAttuned` is the code name for the helper called "The Listener."

## The numbers
- `entropy`: how tense the team is
- `connection`: how close the team is
- `shade`: taking a break to calm down

All of them stay between 0 and 10.

## Perspectives (what the choice shows)
`empathy` · `boundaries` · `fairness` · `curiosity` · `repair` · `self_care` · `escalation`

These tell the helper what to talk about. They are **not** points.

## Writing rules
- At least 2 endings. No "bad" endings. A sad ending must help the kid think, not feel ashamed.
- Every scene needs at least one choice that is always shown (no `condition`).
- A mean choice is allowed. Show what happens next. Don't punish the kid.
- Never ask for the player's real name, age, school, location or photos.
- Use simple words. Kids aged 9–12 will read this.

## Check your story
Run `python -m tqfai validate`. It tells you if a choice leads nowhere, a scene can't be reached, or the text asks for personal info.
