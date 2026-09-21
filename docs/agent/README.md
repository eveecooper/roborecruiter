# Agent materials

**For coding agents. A person does not need this folder** - start at the
[root README](../../README.md).

[`CLAUDE.md`](../../CLAUDE.md) at the repo root holds the rules that always apply and loads
automatically. This file holds the rest: where to look, and the conventions that are not obvious
from reading the documents.

## Where to look

The two planning documents have clean, non-overlapping jobs. Neither supersedes the other, and
neither needs reading to understand the other.

| Question | Document |
| --- | --- |
| What is this, what will it not do, where is it weak? | [`00-product-overview.md`](../planning/00-product-overview.md) |
| How is it built, in what order, what does "done" mean? | [`01-engineering-plan.md`](../planning/01-engineering-plan.md) |
| Is this decided? | [`02-deferred-investigations.md`](../planning/02-deferred-investigations.md) - if it is listed there, no |
| Why is it like this? | [`03-review-log.md`](../planning/03-review-log.md), then [`docs/adr/`](../adr/) |

An ADR outranks both planning documents on the single decision it records.

## Conventions

- **Open investigations A through G are not yours to close.** Several are routed to outside
  expertise on purpose: legal review of crawl policy, entity-resolution thresholds, browser
  submit-boundary safety. Picking a reasonable-sounding answer defeats the point of deferring it.
  Flag the question and say plainly that it is unresolved.
- **Record planning changes in the review log** with the reasoning, including what you chose not
  to change. No silent rewrites of a decision.
- **Check external facts rather than recalling them.** Several plan facts depend on sources that
  move: the Overture schema and taxonomy, hiring-platform APIs, county open data. The review log
  lists which were verified and when.
- Planning documents carry YAML front matter describing what each one covers.
- Filenames describe the document, not the editing event. "Revised", "final", and "v2" belong in
  git history.

## Keeping this small

This folder is loaded into a limited context window. Detail belongs in the planning documents; only
what an agent needs *before* reading those belongs here. If something here duplicates a planning
document, the planning document wins and the copy here should become a link.
