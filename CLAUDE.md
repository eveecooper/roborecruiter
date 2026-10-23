# roborecruiter

An assisted job application pipeline. Planning stage - no application code exists yet.

## Where things are

Two planning documents with non-overlapping jobs. Neither supersedes the other.

- `docs/planning/00-product-overview.md` - what this is, what it will not do, where it is weak.
- `docs/planning/01-engineering-plan.md` - how it is built: scope, stage design, milestones,
  acceptance criteria, standards. **This is the one to follow when building.**
- `docs/planning/02-deferred-investigations.md` - open questions. If a question is listed here,
  it is undecided on purpose.
- `docs/adr/` - outranks both planning documents, on the decision each ADR records.

Conventions and the rest: [`docs/agent/README.md`](docs/agent/README.md).

## Working on this repo

- Planning documents are the current deliverable. Treat them as code: record what changed and why
  in `docs/planning/03-review-log.md`, including what you chose not to change.
- Do not close an open investigation (A through G) by picking a reasonable-sounding answer. Several
  are routed to outside expertise on purpose. Flag it as unresolved instead.
- Build order is Phase 1 (Apply), Phase 2 (Discover), Phase 3 (Generalize) in the engineering plan.
  Steps 2.1 and 2.2 are validation spikes; if one fails, fix the source or the approach rather than
  building around it. [ADR 0001](docs/adr/0001-phased-delivery.md) records why this replaced the
  earlier M0-M6 sequence, and outranks any leftover milestone wording.
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

### Who explains the work

- **Substantial technical work gets explained by the `technical-explainer` subagent**, invoked
  after the work is done: a completed implementation, a debugging result, a performance analysis,
  or a design I have asked you to walk me through. Relay its output as written. It is addressed to
  me, not to you, and it is read-only - it explains the work, it never does the work.
- **Routine changes do not.** Report those yourself in a sentence or two: what changed, whether it
  worked, what happens next. Do not invoke another agent for them.
- The explainer defaults to 100 words and closes by offering depth on one specific point. If I
  take the offer, relay the follow-up; do not pre-empt it by pasting the long version first.

## Constraints that are not negotiable

These exist for legal and safety reasons, not preference. Do not relax one for convenience, and do
not implement a capability that would make relaxing it easy:

- No bot-detection evasion, CAPTCHA solving, proxy rotation, or `robots.txt` violations.
- No automated access to Indeed or any source whose terms forbid it.
- **No code path that can submit an application.** Phases 1 and 2 ship no browser worker at all,
  and CI asserts no adapter exposes a submit, click-to-submit, or form-post operation.
- No claim in generated materials that does not trace to a confirmed fact.
