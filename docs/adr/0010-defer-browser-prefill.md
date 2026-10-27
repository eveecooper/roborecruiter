# ADR 0010: Browser form fill is deferred and gated by Investigation C

- **Status:** accepted
- **Date:** 2026-10-26
- **Deciders:** EVC

## Context

The owner wants browser form fill and reframed it in a way that appears to resolve the project's
hardest rule: if the machine fills in the application form, then *filling the form is the applying*
and the submit button stays human. The existing plan already describes this interface and even names
it `prefill_until_handoff()`, so the reframing is a legitimate reading rather than a loophole.

Both reviews rejected building it, for different reasons, and the first of those reasons shows the
reframing does not hold.

**The boundary is not a property of the code.** On most portals, attaching a resume or completing
step one of a multi-step form **persists state the employer can see, with no submit event anywhere
for a test to catch**. So "fill but do not submit" has to be established per portal, with a state
machine, a pinned form fingerprint, and a suite of hostile forms that records submit-equivalent
network calls. That is Investigation C's entire deliverable, and its start condition is that the
applying path is complete and the platform census exists.

**The mechanical cost is immediate.** The submission-safety CI check asserts that no module exposes
a submit, click-to-submit or form-post operation. Building a form filler means deleting or rewriting
that check on day one, and it is the only mechanical guarantee behind the rule. Everything else is
discipline.

**The sequencing is wrong too.** The applicant does not yet know which form to fill. Restaurant
employers hire through hospitality-specific tools; Indeed carries much of the hourly market and is
denied by its terms; several hospitality platforms gate the form behind account creation, so the tool
would reach the form and hand over an empty browser. A filler built before the census is necessarily
generic — heuristics against arbitrary employer sites — which is "general autonomous browser
operation across unknown portals", a non-goal in every version of this plan.

## Decision

Browser form fill is **stage 6 and gated by Investigation C**, not scheduled. Its hostile-form suite
and its ruling on employer-visible partial applications are prerequisites, not formalities. It is
additionally conditional on recorded data showing that one portal carries a meaningful share of real
applications.

The submission-safety CI assertion stays as written through every stage.

**What ships instead**, from stage 1: the submit walkthrough hands over the posting link, the files
ready to attach, and every screening answer as copy-ready text. The browser's own autofill already
covers contact fields, which is most of the typing.

**What decides it later:** a `channel` column on every application —
`email` / `form` / `portal:<name>` / `indeed` — plus `submit_seconds`. After a month of real use the
question "is any single portal worth an adapter" has an answer from data rather than impression.
This also converts Investigation E from a scheduled study into a byproduct of use.

## Consequences

**Easier.** The hardest rule keeps its mechanical guarantee. No per-portal state machines, no
fingerprint pinning, no hostile-form test site, and no maintenance treadmill against third-party DOM
changes.

**Harder.** Filling forms stays manual indefinitely, and that is where the applicant's minutes
actually go — drafting was never the bottleneck.

**Foreclosed.** Nothing permanently. The interface shape (`prefill_until_handoff()`, an ephemeral
browser context in a separate process, handoff on any challenge, login, attestation, novel question,
unexpected layout, or submit) is already specified and survives.

**Accepted cost.** If the applicant's volume is dominated by a single portal, the saving is being
deliberately left on the table until Investigation C clears.

## Alternatives considered

**Build one adapter now for a hand-picked platform.** Rated 7 out of 10 feasible, two to four weeks
including the hostile-form test site, plus a few hours a quarter and an unscheduled day whenever that
portal redesigns. Rejected because the platform has not been identified by data and the CI assertion
would be rewritten on day one.

**Generic field matching across arbitrary sites.** Rated 3 out of 10. Identity fields land 60 to 80
percent via `autocomplete` attributes and label associations — which the browser already does free —
and matching collapses on work history, availability grids and screening questions, which is where
the time is. A specific warning from the review: do not put a model in the fill decision, because it
will confidently fill a field it misread, and a wrong screening answer is an outward-facing error the
applicant may not catch while reviewing a batch.

**Bulk mark-submitted with no walkthrough.** Available and simpler, but it loses the batch's place in
the sequence.

## Evidence

- `bob` review, 2026-10-25: Investigation C work item 8 already anticipated and rejected the
  fill-then-submit boundary; building it requires deleting the submission-safety CI assertion; and a
  pre-census filler is a non-goal in every phase.
- `tbro` review, 2026-10-25: 3/10 for arbitrary sites and 7/10 for one hand-picked platform;
  commercial tools in this category either restrict to a few large corporate systems or submit in
  bulk at quality low enough that employers complain; open-source equivalents target one platform
  and are mostly stale. **No prior art exists for prefill with a proven no-submit boundary** — that
  argument would have to be written here first.
- Project `CLAUDE.md`: no code path that can submit an application, asserted in CI.
