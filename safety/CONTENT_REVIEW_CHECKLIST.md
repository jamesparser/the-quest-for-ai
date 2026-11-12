# Content & Safety Review Checklist

Copy into every scenario PR description and tick each box. Reviewer: Workstream 7 + Project Lead.

**Audience fit (ages 9–12)**
- [ ] Language is readable for the age range; no slurs, sexual content, or graphic violence.
- [ ] Mean in-game talk is mild and clearly framed as something to reflect on, not imitate.
- [ ] `audience.content_notes` lists anything a parent/teacher should know.

**Agency & respect**
- [ ] Every scene has at least one calm option and one honest "less ideal" option.
- [ ] No ending shames the player. Bittersweet endings offer a way to reflect or replay.
- [ ] The companion asks and reflects; it never scores, lectures, or pressures.
- [ ] Players can disagree with the companion and nothing bad happens because of it.

**Privacy**
- [ ] Nothing asks for real name, age, school, location, photos, or contact info.
- [ ] No free-text input is required to finish the scenario.
- [ ] No data leaves the session (no new logging, analytics, or storage added).

**Real-world safety**
- [ ] Where a situation could be serious (strangers, threats, self-harm), the content points to a trusted adult.
- [ ] Muting, blocking and reporting are shown as valid, positive tools.

**Bias & representation**
- [ ] Characters aren't defined by stereotypes; "bad behaviour" isn't tied to a group.
- [ ] The scenario was read by at least one person who didn't write it.

**Technical**
- [ ] `python -m tqfai validate` passes.
- [ ] `python -m unittest discover -s tests` passes.
