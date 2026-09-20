# roborecruiter

An assisted job application pipeline. Planning stage - no application code exists yet.

## Read the planning docs in precedence order

`docs/planning/` contains two drafts that contradict each other in places, deliberately. Before
acting on anything you read there:

1. `docs/adr/` - outranks everything, on the decision each ADR records.
2. `docs/planning/01-engineering-plan.md` - **draft 3, authoritative** on anything operational.
3. `docs/planning/00-product-overview.md` - **draft 1, superseded.** Product intent only.
4. `docs/planning/02-deferred-investigations.md` - **open questions.** Settles nothing.

Full rule, lineage, and the specific traps: **[`docs/agent/doc-precedence.md`](docs/agent/doc-precedence.md)**.
Read it before your first substantive change to a planning document.

## Working on this repo

- Planning documents are the current deliverable. Treat them as code: no silent rewrites of a
  decision, and record what changed and why in `docs/planning/03-review-log.md`.
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
