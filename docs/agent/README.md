# Agent materials

**For coding agents. A person does not need this folder** - start at the
[root README](../../README.md).

[`CLAUDE.md`](../../CLAUDE.md) at the repo root holds the rules that always apply and loads
automatically. This file holds the rest: where to look, and the conventions that are not obvious
from reading the documents.

## Where to look

| Question | Document |
| --- | --- |
| How is it built, in what order, what does "done" mean? | [`10-build-plan.md`](../planning/10-build-plan.md) |
| When do I get feature X? | [`12-feature-inventory.md`](../planning/12-feature-inventory.md) |
| Is this decided? | [`11-investigations.md`](../planning/11-investigations.md) - if it is listed there, no |
| How do I write the code? | [`coding-standards.md`](coding-standards.md) |
| How does a request become code? | [`development-workflow.md`](development-workflow.md) |
| Why is it like this? | [`03-review-log.md`](../planning/03-review-log.md), then [`../adr/`](../adr/) |
| Careers-page outcomes, block detection, Overture facts? | [`13-discovery-notes.md`](../planning/13-discovery-notes.md) |
| What was this before the reset? | Git history. The pre-reset `00`, `01` and `02` were deleted in Review 5 after their load-bearing content was extracted. |

An ADR outranks the planning documents on the single decision it records. **ADRs 0002 through 0010
record the 2026-10-26 reset** and are the ones most likely to matter. Delivery is six stages; any
leftover Phase 1/2/3 or M0-M6 wording anywhere is stale. [ADR 0001](../adr/0001-phased-delivery.md)
survives on one point: apply before discover, and manual intake is a posting source rather than a
special case.

**Three things a stale prior gets wrong.** Hand-editing generated documents is *allowed* (ADR 0002).
Stage 1 ships *no model and no network code*, both asserted in CI (ADR 0005). There is *no mandatory
UI* (ADR 0004).

## Conventions

- **Open investigations A through H are not yours to close.** Several are routed to outside
  expertise on purpose: legal review of crawl policy, entity-resolution thresholds, browser
  submit-boundary safety. Picking a reasonable-sounding answer defeats the point of deferring it.
  Flag the question and say plainly that it is unresolved.
- **Record planning changes in the review log** with the reasoning, including what you chose not
  to change. No silent rewrites of a decision.
- **A feature is recorded before it is built.** Place it in a stage or defer it with a reason;
  a decision change needs an ADR. Building ahead of the plan is how the plan stops being true,
  and it has already happened once here - see Review 5's second addendum.
- **Check external facts rather than recalling them.** Several plan facts depend on sources that
  move: the Overture schema and taxonomy, hiring-platform APIs, county open data. The review log
  lists which were verified and when.
- **[`tbro-stack-log.md`](tbro-stack-log.md) belongs to the `tbro` subagent.** It is the running
  list of technologies the project uses or has considered. Only that agent edits it; read it freely.
- Planning documents carry YAML front matter describing what each one covers.
- Filenames describe the document, not the editing event. "Revised", "final", and "v2" belong in
  git history.

## Keeping this small

This folder is loaded into a limited context window. Detail belongs in the planning documents; only
what an agent needs *before* reading those belongs here. If something here duplicates a planning
document, the planning document wins and the copy here should become a link.
