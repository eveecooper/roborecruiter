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
- Build order is M0 through M6 in the engineering plan. M1 and M2 are validation spikes that gate
  the architecture; if one fails, fix the source or the approach rather than building around it.
- Say plainly when something is unverified. Several plan facts depend on external sources that
  move, so check rather than recall.

## Constraints that are not negotiable

These exist for legal and safety reasons, not preference. Do not relax one for convenience, and do
not implement a capability that would make relaxing it easy:

- No bot-detection evasion, CAPTCHA solving, proxy rotation, or `robots.txt` violations.
- No automated access to Indeed or any source whose terms forbid it.
- **No code path that can submit an application.** The first build ships no browser worker at all,
  and CI asserts no adapter exposes a submit, click-to-submit, or form-post operation.
- No claim in generated materials that does not trace to a confirmed fact.
