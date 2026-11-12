# The Quest for AI: Product Roadmap

This roadmap turns the [project ideation](./🎮%20Project%20Submission_%20_The%20Quest%20for%20AI_%20(TQFAI).md) into a sequence of testable product milestones. It prioritizes a small, safe, playable experience before investing in advanced reasoning or persistent-data infrastructure.

## Product direction

Build a family-friendly, cooperative narrative experience in which a player and an AI companion explore an ethical dilemma, explain their perspectives, and choose a resolution together. The Owl companion provides guidance without declaring one moral framework universally correct.

The initial product is an educational narrative prototype, not a way to train or align a general-purpose AI model. Player choices can inform the experience only with clear consent and safeguards; they must not be presented as proof of model alignment or as a universal measure of human values.

## Milestones

### 0. Define the experience and safety boundaries

**Deliverables**
- A concise product brief covering audience, learning goals, platforms, accessibility needs, and what the prototype will not do.
- A documented choice model for the three proposed dimensions: empathy, ethical perspective, and boundary respect. Define these as prompts for reflection, not objective scores of a person.
- A privacy and safety plan covering age-appropriate content, consent, data collection, retention, deletion, and adult oversight where appropriate.
- A small set of scenario concepts and a review checklist for harm, bias, and clarity.

**Exit criteria**
- Intended users and learning outcomes can be described and tested.
- Scenario content and data-handling boundaries have been reviewed before user testing.
- No personal or sensitive player data is required for the core experience.

### 1. Prototype one complete scenario

**Deliverables**
- A playable, single-session scenario based on a familiar, low-stakes misunderstanding.
- A simple interface for reading the scene, considering perspectives, and making a choice.
- A scripted AI companion that asks clarifying questions, acknowledges uncertainty, and supports the player's agency.
- A branching outcome that shows how a choice affects characters and the relationship, with a non-punitive path to revisit or reflect.
- A basic visual direction inspired by the bioluminescent palette and Owl guide in the ideation.

**Exit criteria**
- A player can complete the scenario from introduction through resolution without developer assistance.
- The scenario has meaningful choices and at least two distinct outcomes.
- Usability sessions show that players understand the choices and feel free to disagree with the companion.

### 2. Establish the narrative engine and authoring workflow

**Deliverables**
- A reusable, versioned scenario format for scenes, choices, character reactions, and endings.
- A deterministic narrative engine that loads scenarios and produces repeatable outcomes.
- At least three reviewed scenarios spanning interpersonal boundaries, workplace misunderstanding, and shared-resource allocation.
- Automated checks for malformed scenario content and unreachable branches.

#### Event-hook prototype and architecture mapping

- [x] Prototype an event-driven hook registry for narrative events and archetype changes; the test exercises callback registration and dispatch, then invokes a basic balanced-parentheses check on the MeTTa files.
- [ ] Connect narrative event context to actual MeTTa/AtomSpace evaluation. The current subprocess check is structural only; it does not parse or execute MeTTa logic.
- [ ] Make hook and MeTTa-check failures fail the test command. The current demo prints completion unconditionally, and the structural checker does not return a failing exit status when a file is malformed.

The prototype is a starting point for an event-to-reasoning pipeline, not a sentient-agent implementation. Miller and Blumberg's *Building Sentient Beings* distinguishes reactive mechanisms, proactive agents, and opportunistic rules, and describes observation and coordination as mechanisms that update memory. A future TQFAI pipeline could apply those ideas as follows:

1. Treat a named narrative event as a reactive input and dispatch it to registered handlers. The current `NarrativeHookSystem` implements only this event dispatch.
2. Validate and normalize the event context, then represent the event and relevant context as transient MeTTa facts or relations. Keep scenario state distinct from any persistent player data.
3. Use MeTTa rules as opportunistic mechanisms: match event facts with applicable context and goals, then derive candidate narrative responses. Keep reasoning explainable and avoid turning `valence` into an objective score of a player.
4. Record the selected action and its reason for the current session, so later handlers can use the outcome as context. Any reflection or coping behavior should be an explicit, player-respecting narrative feature, not a claim of clinical emotional regulation.
5. Test the stages independently: event dispatch, fact translation, rule evaluation, and response selection. A parenthesis-balance check alone is not a MeTTa parser or runtime evaluation.

This design mapping is informed by Michael S. P. Miller and Micah Blumberg, *Building Sentient Beings* (2025), [the repository PDF](./Building_Sentient_Beings_090.pdf) and [doi:10.5281/zenodo.15522356](https://doi.org/10.5281/zenodo.15522356). It adapts high-level architectural ideas; it does not imply that the current hooks implement the paper's memory architecture, autonomy, sentience, or emotion model.

**Exit criteria**
- A new scenario can be authored and tested without changing engine code.
- Automated checks cover valid references, branch reachability, and required content fields.
- The initial scenario set passes the content and safety review.

### 3. Add structured reflection and evaluate symbolic reasoning

**Deliverables**
- A transparent record of the choice and the perspectives considered, stored for the current session only.
- An optional MeTTa/AtomSpace proof of concept that maps a small, documented set of scenario concepts to symbolic relations.
- A comparison against a simple rules-based baseline, using a fixed set of example scenarios.
- An explanation in the interface when the companion's interpretation is uncertain or incomplete.

**Exit criteria**
- The proof of concept can be evaluated against the baseline for correctness, latency, explainability, and maintenance cost.
- The team can identify concrete player or authoring value from symbolic reasoning before adopting it in the product.
- No model or logic component assigns a definitive moral score to a player.

**Decision gate:** Adopt MeTTa/AtomSpace only if the evaluation demonstrates a meaningful benefit over the simpler baseline. Keep the scenario engine usable without it.

### 4. Test cooperative play and improve the experience

**Deliverables**
- A small pilot with representative users and informed consent.
- Session-level feedback on clarity, agency, emotional tone, accessibility, and replay value.
- A reviewed set of edge cases, including disagreement with the AI, ambiguous choices, and requests outside the scenario.
- Revisions to scenarios, companion behavior, and onboarding based on observed results.

**Exit criteria**
- Pilot participants can explain that choices prompt reflection rather than measure their character or train a general model.
- The companion handles disagreement respectfully and does not pressure players to disclose personal experiences.
- Major usability and safety issues found in the pilot have a documented resolution before expansion.

### 5. Decide whether persistent memory is warranted

**Deliverables**
- A written purpose and threat/privacy assessment for any cross-session data.
- A data-minimized design that separates player identity from scenario analytics.
- A deletion and retention policy, access controls, and a user-visible consent and opt-out flow.
- Only if approved, a limited Omega Hive integration storing anonymized, high-level scenario events; keep raw conversation and identifying data out of the integration by default.

**Exit criteria**
- The feature has a clear player benefit that cannot be met with session-only state.
- Consent, retention, deletion, security, and governance have been reviewed before data collection begins.
- The system works when memory is disabled, and users can inspect or remove eligible stored data.

**Decision gate:** Persistent memory is optional and should not block the core game. Do not collect data for a future alignment dataset without a separately reviewed purpose, consent, governance, and evaluation plan.

### 6. Prepare a public beta and measure outcomes

**Deliverables**
- A stable prototype with onboarding, accessibility review, clear privacy information, and feedback reporting.
- A public-facing explanation of the experience, its limitations, and how any optional data is used.
- A release checklist for content review, reliability, incident response, and support.
- A post-beta prioritization based on evidence from players and maintainers.

**Exit criteria**
- Core scenarios work reliably across supported devices and can be completed without account creation.
- Feedback and safety reports have an owner and a response process.
- The next release is scoped from beta evidence rather than presumed ecosystem impact.

## Measures of progress

Use a small set of observable measures and review them alongside qualitative feedback:

- **Playability:** scenario completion rate, abandonment points, and reproducible branch coverage.
- **Comprehension:** whether players understand the dilemma, available choices, and consequences.
- **Agency and respect:** whether players report that they can disagree with the companion and decline to share personal information.
- **Quality:** scenario defects, accessibility issues, and safety concerns found per test cycle.
- **Technical fit:** authoring effort, reliability, latency, and evaluation results against a simpler baseline.
- **Privacy:** amount of data collected, consent and deletion requests completed, and whether the experience remains functional with optional collection disabled.

These are product-quality signals, not measures of a player's morality, a model's empathy, or general AI alignment.

## Initial scope and non-goals

**In scope:** one playable scenario, a cooperative reflection loop, a small narrative framework, and user testing.

**Not in the initial scope:** autonomous self-improvement, claims of preventing goal drift, broad deployment of MeTTa/PLN, cross-session behavioral profiling, or publishing player-derived data as an alignment dataset.

## Dependencies and open decisions

- Choose the target platform and implementation stack before building the interface and scenario engine.
- Confirm the intended age range and appropriate consent/review process before recruiting players.
- Define accessibility requirements and supported languages before expanding scenario content.
- Treat MeTTa/AtomSpace, PLN, and Omega Hive as proposed integrations until prototypes demonstrate value and privacy requirements are met.
