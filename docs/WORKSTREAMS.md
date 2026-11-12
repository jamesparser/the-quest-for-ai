# Team Jobs: HyperSprint #3

**Deadline:** the sprint ends **30 November 2026**.
**Judges want:** a game that works in the browser, plus a short video that shows the AI helper, MeTTa, and kind (prosocial) choices.

## What is already done

- **The game works.** Open the website, pick a helper, play Scene 1 ("Squad Night in Sporelands", about 9 choices, 5 parts), and reach one of 5 endings.
- **The AI helper talks.** After each choice, the helper says something short and kind. It uses the free ASI Cloud AI (`asi1-mini`). If the AI is down, the game uses written lines, so it never breaks.
- **The website is online** (Vercel). Colleen has the link.
- **Safety checks.** A checker stops stories that ask kids for personal info. AI lines that are too long or unsafe are thrown away.
- **29 tests** check that everything still works after each change.

## Who does what

| Person | Job | Needs code? |
|---|---|---|
| **Jason** | Built the base, the AI voice and the website. Now only reviews pull requests. | Done |
| **David Ring** | Make the helper speak in the "nonviolent communication" way. Edit the helper's rules (see "David" below). Read 20 AI replies and mark any that feel wrong. | No |
| **Kali** | Play the game like a 10–12 year old would. Write down what is boring, confusing or "cringe". Help write Scenes 2 and 3. | No |
| **Guillermo** | Connect MeTTa to the game so the judges can see it working (see "Guillermo" below). If there is time, make the web page look nicer. | Yes (Python) |
| **Colleen** | Final say on the stories. Write Scenes 2 and 3 with Kali. Make the pitch video and send the submission. | No |

## Suggested dates

| By | What |
|---|---|
| 18 Nov | David's helper rules done. Kali's play-test notes done. |
| 22 Nov | Scenes 2 and 3 written and checked. |
| 25 Nov | MeTTa connected (Guillermo). |
| 28 Nov | Video recorded. |
| 30 Nov | Submit. |

---

## David: the helper's voice

The AI follows the rules in one block of text. It is in `src/tqfai/reasoning/llm.py`, near the top, and is called `SYSTEM_PROMPT`.

You can edit it on the GitHub website: open the file, click the pencil icon, change the words, and click "Propose changes". Jason will review and merge it.

Keep these rules:
- 1 or 2 short sentences, very simple English.
- Never grade, judge or lecture.
- Never ask about the player's real life.

## Kali: play-testing

Play the game at the website link 5 times with different helpers and different choices. For each game, write down:
1. What was fun?
2. What was boring or confusing?
3. Did the helper ever sound fake, preachy, or "like a teacher"?
4. Would a friend your age keep playing? Why or why not?

Send the notes to Colleen. Do not share anything personal about yourself or others.

## Colleen and Kali: Scenes 2 and 3

A scene is one file in `content/scenarios/`. Copy `s01_the_lagging_teammate.json` and change the words. The full guide is in [`SCENARIO_FORMAT.md`](SCENARIO_FORMAT.md).

Ideas:
- **Scene 2: "The Shared Loot."** The team finds one rare item. Who gets it? (sharing fairly)
- **Scene 3: "The Pushy Stranger."** An unknown player keeps sending friend requests and asks personal questions. (boundaries, telling a trusted adult)

If you are not comfortable editing the file, write the scene in a Google Doc using the same shape (what happens, 3–4 choices, what each choice leads to, endings). Ask Jason or Guillermo to turn it into the file.

## Guillermo: MeTTa

Today the game *loads* the MeTTa files but does not *use* them yet. The judges want to see MeTTa doing real work.

1. Install: `pip install hyperon`
2. Open `src/tqfai/reasoning/metta_adapter.py`. Inside `interpret()`, ask MeTTa a question about the choice. For example: "Does this choice raise or lower the tension?" Then use the answer.
3. Use Colleen's rules in `src/logic/*.metta` where they fit.
4. Run `python -m tqfai eval` to compare MeTTa with the simple written rules.
5. Show the result in the video: "MeTTa decided X because of rule Y."

Keep it small. One clear rule that works is better than ten that don't.

## Rules for everyone

- **One job = one branch = one pull request.** Keep pull requests small.
- **Never put an API key in the code or in a pull request.** See [`AI_VOICE.md`](AI_VOICE.md).
- **Never collect players' names, ages or personal info.**
- **Before a pull request:** run `python -m unittest discover -s tests`. All tests must pass.

## Not in this sprint

VR, Unity or Unreal, the mushroom lab (VRE-Lab), and long-term memory (Omega Hive). These are for later.
