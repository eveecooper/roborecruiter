# ADR 0006: Every fetch waits for the source-policy ADR, structured APIs included

- **Status:** accepted
- **Date:** 2026-10-26
- **Deciders:** EVC

## Context

Investigation D settles crawler identity, the precedence of `robots.txt` against a site's terms of
service, and whether local snapshots of third-party pages may be retained. Its named owner is
technology and privacy counsel, and a previous reviewer declined to answer it on purpose.

In the previous plan, D blocked all of Phase 2, which gated Phases 3 through 6. On a
single-applicant project that owner is unlikely to materialise, so the sequence could reach one
milestone and stop permanently. [ADR 0001](0001-phased-delivery.md) restructured delivery partly to
break that deadlock.

A draft of the reset reintroduced the problem in a subtler form. It ordered structured applicant
tracking system APIs — Greenhouse, Lever, Ashby — ahead of generic careers-page crawling, which is
good sequencing, and described them as available "where permitted". The `bob` review identified that
two words were doing this ADR's job: a board API call is a fetch, and crawler identity, terms
precedence and retention of fetched posting text all apply to it.

## Decision

**No code in this project fetches anything over the network until the source-policy ADR exists**,
written from Investigation D actually answered. This includes structured, documented, free, public
board APIs.

Stage 3 step 3.0 *is* that ADR. Step 3.1 is the first fetch. Nothing in stages 1 or 2 fetches
anything, asserted in CI by forbidding the import of `httpx`, `requests` and `playwright`.

The cost of leaving D open is therefore zero until stage 3, which is the point of this ordering.

## Consequences

**Easier.** An unanswerable question blocks exactly one stage instead of the project. Stages 1 and 2
deliver a working tool with no exposure to it. When the ADR lands, every fetch in the codebase can
point at a specific clause.

**Harder.** Automated discovery of any kind — including the board APIs that are the software
vertical's primary channel — sits behind a question the owner cannot answer alone. Stage 3 may be
blocked while stages 1 and 2 are in daily use.

**Foreclosed.** The convenience of treating a documented public API as self-evidently permitted.

**Accepted cost.** The owner may end up answering D themselves at a scope appropriate to local
single-user operation: honest user agent with a contact address, strict `robots.txt` and crawl-delay
obedience, a per-domain rate cap, a deny list covering Indeed and any terms-forbidding source (a third-party
route for Indeed data is Investigation H, which this ADR does not prejudge), and a
retention rule — recorded with the condition that it reopens if the project is ever hosted, shared,
or multi-user. That is a legitimate resolution. What is not legitimate is proceeding without
recording one.

## Alternatives considered

**Treat board APIs as exempt.** Rejected: the distinction is between structured and unstructured
responses, not between fetching and not fetching, and the retention question is identical either
way.

**Answer D now with conservative defaults.** Chosen in an earlier draft, then withdrawn. Once
crawling moved to stage 3, answering it bought nothing immediately, and `bob` observed that
pre-answering an investigation routed to counsel is exactly what the deferral exists to prevent.

**Keep D blocking the whole project.** Rejected by ADR 0001 for the reasons recorded there.

## Evidence

- Investigation D's brief, which records its named owner and that a previous reviewer declined it.
- `bob` review, 2026-10-25: identified "where permitted" as standing in for the policy, and that
  Investigation E rather than intuition selects which adapters are worth building.
- ADR 0001's Context section, which documents the original deadlock.
