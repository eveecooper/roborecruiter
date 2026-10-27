# roborecruiter

An assisted job application pipeline. Planning stage - no application code exists yet.

## Where things are

- `docs/planning/10-build-plan.md` - stages, architecture, seams, what "done" means.
  **This is the one to follow when building.**
- `docs/planning/11-investigations.md` - open questions A through H and what each one gates. If a
  question is listed there, it is undecided on purpose.
- `docs/planning/12-feature-inventory.md` - every requested feature and the stage it arrives in.
  The quickest answer to "when do I get X".
- `docs/agent/coding-standards.md` - how to write the code. Read before any build ticket.
- `docs/agent/development-workflow.md` - how a request becomes a ticket becomes code.
- `docs/adr/` - outranks the planning documents, on the decision each ADR records. 0002 through
  0011 record the 2026-10-26 reset.
- `docs/planning/13-discovery-notes.md` - the six-outcome careers enum, block detection, discovery
  accounting labels, and the Overture facts and licence obligation. Needed at step 1.0 and stages 3-4.

Conventions and the rest: [`docs/agent/README.md`](docs/agent/README.md).

## Working on this repo

- Planning documents are the current deliverable. Treat them as code: record what changed and why
  in `docs/planning/03-review-log.md`, including what you chose not to change.
- **A new feature request goes into the plan before any code is written for it.** Give it a stage,
  or say plainly that it is deferred and why. If it changes a decision, it needs an ADR rather than
  an edit. If I ask for several things at once, place each one before building any of them.
  Procedure: `docs/agent/development-workflow.md`.
- Do not close an open investigation (A through H) by picking a reasonable-sounding answer. Several
  are routed to outside expertise on purpose. Flag it as unresolved instead.
- Build order is the six stages in the build plan: first application (offline), repeatable
  (offline), source policy then first fetch, discovery, model-assisted curation, evidence-gated
  extras. ADRs 0002-0011 record the 2026-10-26 reset and outrank any leftover Phase 1/2/3 or M0-M6
  wording. [ADR 0001](docs/adr/0001-phased-delivery.md) survives on one point only: apply before
  discover, and manual intake is a posting source rather than a special case.
- **Stage 1 ships no model and no network code**, both asserted in CI. Hand-editing generated
  documents is allowed. Neither is negotiable by a scope argument; see ADRs 0005 and 0002.
- Say plainly when something is unverified. Several plan facts depend on external sources that
  move, so check rather than recall.

## How to report to me

I am learning the craft as this gets built. Use the correct industry term, define it once in a
clause, and assume I have not met it before. The target is that I can hold a technical conversation
about this system unaided.

Formatting carries the signal of what a message is, so the sentences carry only content:

| Form | Means |
| --- | --- |
| **Bold lead line**, one sentence | A conclusion, decision, or result - the part I act on |
| Plain prose and bullets | Intermediate work: what you are doing, what you have found so far |
| **Needs your call:** then options | You are blocked on a judgement that is mine to make |
| `## Heading` | The message covers more than one subject |

- **One recommendation per decision.** State the choice first, the reasoning after it. Survey the
  alternatives only when I ask for them.
- **A settled decision stays settled.** If evidence genuinely overturns one, state the reversal in
  one line and carry on; keep it out of later messages.
- Write short. Delete any sentence that restates the one before it.
- Professional register: exact names for things, full terms over abbreviations I have not seen
  yet, no slang, no filler enthusiasm.

  Answer my exact question first, directly and literally.
  Use the minimum information necessary for me to understand the answer. Do not summarize the entire project, investigation, or implementation unless I explicitly request it.
  Default to 1–3 sentences, maximum 80 words.
  For "What is X?", begin "X is..." or "X's goal is..."
  For recommendations, begin "I recommend X because Y."
  Explain unfamiliar technical details only when essential to the answer. Do not volunteer background information, implementation steps, caveats, or follow-up suggestions unless they materially change the answer.
  Use natural, connected prose. No decorative formatting or fragmented one-sentence paragraphs.
  If the question has been answered, stop.

### Who explains the work

- **Substantial technical work gets summarized by the `technical-explainer` subagent**, invoked
  after the work is done if there is a lot to explain: a completed implementation, a debugging result, a performance analysis, or a design I have asked you to walk me through. Relay its output as written. It is addressed to
  me, not to you, and it is read-only - it explains the work, it never does the work.
- **Routine changes do not.** Report those yourself in a sentence or two: what changed, whether it
  worked, what happens next. Do not invoke another agent for them.
- The explainer sets its own length and does not ask whether I want more depth. If I want more, I
  will ask for it. Its definition lives only in `~/.claude/agents/`, because this repository
  ignores `.claude/` and a copy here could never travel with it.

### Agents I summon by name

Two review agents, invoked only when I ask for them. **If a message of mine contains `/bob` or
`/tbro` anywhere in it, invoke that agent before replying**, with the relevant part of our
conversation in the prompt, and relay the reply as written. They cannot listen in on their own -
a subagent only runs when it is invoked - so the mention is the trigger.

- **`/bob`** - scope and MVP guardian. Judges whether what we are discussing belongs in Phase 1,
  and defers what makes Phase 1 harder to Phase 2, 3, or later with the reason. He answers with one
  line when there is nothing to flag; relay that line as it is and do not expand on it.
- **`/tbro`** - feasibility engineer. Rates the proposed task easy, hard, or difficult; lists the
  technologies it would need; and says whether it is a very common, uncommon, or rare task. He
  maintains the running stack log at [`docs/agent/tbro-stack-log.md`](docs/agent/tbro-stack-log.md),
  the one file he writes.

Neither closes an open investigation and neither does the work. Their definitions live in
`.claude/agents/`, which this repository ignores.

## Project Priorities

- Functional and gets the job done
- Easiest solution first, sacrificing features to get something working, and not having to work so hard mentally to solve a huge task just to get something done. shift gears if there is a huge roadblock in production.
- Code is easy to maintain, read, and iteratively improve upon. Easily fixable after QA testing.

## Preferences

- Use existing work if it is open-source, credible, has no vulnerabilities, is widely adopted by coders, and would have been hard to recreate on your own. 
- No bot-detection evasion, CAPTCHA solving, proxy rotation, or `robots.txt` violations. Possibly should consider this though if it makes the job easier to do.
- **No code path that can submit an application.** Phases 1 and 2 ship no browser worker at all,
  and CI asserts no adapter exposes a submit, click-to-submit, or form-post operation.
- No claim in generated materials that does not trace to a confirmed fact.
