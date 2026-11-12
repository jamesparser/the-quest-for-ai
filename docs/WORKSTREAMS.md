# Team Handover: HyperSprint #3

**Play it:** https://tqfai-quest-for-ai.vercel.app
**Code:** https://github.com/jamesparser/the-quest-for-ai
**Deadline:** the sprint ends **30 November 2026**.
**Judges want:** a game that works in the browser, plus a short video that shows the AI helper, MeTTa, and kind (prosocial) choices.

## What is already done

- **A full 8-bit game inside a TV.** Pick an AI helper, then play "Squad Night in Sporelands": 5 parts, about 9 choices, 5 endings. Everything is pixel art on the TV screen: power bars, the mushroom world, the story box and the choices.
- **The story:** you and your online squad (Sam, Max, Mia) are mushroom heroes. You deal with a lagging teammate, a rare treasure, a scam stranger, a boss fight and a teammate about to rage-quit.
- **The hidden network:** glowing roots under the ground link every mushroom. Kind choices make them glow. Hurting someone turns their root dark and cold, and saying sorry lights it back up.
- **Controls:** arrows or WASD to walk to a numbered sign, then SPACE. Or press 1–4. Or click or tap. It works on laptops and phones.
- **The AI helper talks.** After each choice, the helper says something short and kind using the free ASI Cloud AI (`asi1-mini`). If the AI is down, the game uses written lines, so the demo never breaks.
- **Safety.** No accounts and no personal data. A checker stops stories that ask kids for personal info, and unsafe AI lines are thrown away.
- **30 tests** check that everything still works after each change.

## Who does what

| Person | Job | Needs code? |
|---|---|---|
| **Jason** | Built the base, the game, the AI voice and the website. Now reviews pull requests and updates the website. | Done |
| **David Ring** | Make the helper speak the "nonviolent communication" way. Read 20 AI replies and mark any that feel wrong. | No |
| **Kali** | Play-test like a 10–12 year old. Help write Scenes 2 and 3. | No |
| **Guillermo** | Connect MeTTa so the judges can see it working. Add the pixel art for Scenes 2 and 3. | Yes |
| **Colleen** | Final say on the stories. Write Scenes 2 and 3 with Kali. Pitch video and submission. | No |

## Dates

| By | What |
|---|---|
| 18 Nov | David's helper rules done. Kali's play-test notes done. |
| 22 Nov | Scenes 2 and 3 written and checked. |
| 25 Nov | MeTTa connected. Pixel art for the new scenes done. |
| 28 Nov | Video recorded. |
| 30 Nov | Submit. |

## How to send changes

1. Open https://github.com/jamesparser/the-quest-for-ai and click **Fork**.
2. Make your change on a new branch. Small text changes can be made on the GitHub website: open the file, click the pencil icon, then "Propose changes".
3. Open a **pull request** to `jamesparser/the-quest-for-ai`. Jason reviews it, merges it, and updates the website.

---

## David: the helper's voice

The AI follows the rules in one block of text called `SYSTEM_PROMPT`, near the top of `src/tqfai/reasoning/llm.py`. Edit the words there.

Keep these rules:
- 1 or 2 short sentences, very simple English.
- Never grade, judge or lecture.
- Never ask about the player's real life.

## Kali: play-testing

Play the game 5 times with different helpers and different choices. For each game, write down:
1. What was fun?
2. What was boring or confusing?
3. Did the helper ever sound fake, preachy, or "like a teacher"?
4. Would a friend your age keep playing? Why or why not?

Send the notes to Colleen. Do not share anything personal about yourself or others.

## Colleen and Kali: Scenes 2 and 3

A scene is one file in `content/scenarios/`. Copy `s01_the_lagging_teammate.json` and change the words. The full guide is in [`SCENARIO_FORMAT.md`](SCENARIO_FORMAT.md).

Scene 1 already covers lag, sharing loot, a scam stranger and rage-quitting, so pick new problems:
- **Scene 2: "Left Out."** The squad starts a group chat and one friend isn't added. (including people)
- **Scene 3: "The Screenshot."** Someone shares a screenshot of a friend's embarrassing message. (rumours, standing up for someone)

Explain every game word the first time it appears, as Scene 1 does. Start each part with "Part 1: Title." so it shows on the TV.

If you are not comfortable editing the file, write the scene in a Google Doc with the same shape: what happens, 3–4 choices, where each choice leads, and the endings. Guillermo or Jason will turn it into the file.

## Guillermo: MeTTa

Today the game *loads* the MeTTa files but does not *use* them yet. The judges want to see MeTTa doing real work.

1. Install it: `pip install hyperon`
2. Open `src/tqfai/reasoning/metta_adapter.py`. Inside `interpret()`, ask MeTTa a question about the choice, for example "Does this choice raise or lower the tension?", and use the answer.
3. Use Colleen's rules in `src/logic/*.metta` where they fit.
4. Run `python -m tqfai eval` to compare MeTTa with the simple written rules.
5. Show it in the video: "MeTTa decided X because of rule Y."

Keep it small. One clear rule that works is better than ten that don't.

## Guillermo: pixel art for new scenes

All the TV art is drawn in code in `web/tv.js`. There are no image files.
- **Who is on screen and the props** (Mother Mushroom, Rot King, stranger, Golden Cap) are chosen by scene id in `drawWorld()`. Add the new scene ids there.
- **Roots** go dim or cold through `ROOT_EVENTS`. Add each new choice id that hurts or helps someone, for example `c_leave_out: { Mia: .5 }`.
- **Sprites** are small text grids at the top of the file (`MUSH`, `OWL`, `BUG`). Copy one to make a new character.

## Running it on your own computer

You need Python 3.10 or newer, and nothing else.
```bash
python -m tqfai serve                     # then open http://127.0.0.1:8787
python -m tqfai validate                  # check the story files
python -m unittest discover -s tests      # run all tests
```
The AI voice needs your own free ASI Cloud key. See [`AI_VOICE.md`](AI_VOICE.md). Without a key, the game uses written lines.

## Rules for everyone

- **One job = one branch = one pull request.** Keep pull requests small.
- **Never put an API key in the code or in a pull request.**
- **Never collect players' names, ages or personal info.**
- **Before a pull request,** run the tests. They must all pass.

## Not in this sprint

VR, Unity or Unreal, the mushroom lab (VRE-Lab), and long-term memory (Omega Hive). These are for later.
