# ADR 0001: Phased delivery, applying before discovering

- **Status:** accepted
- **Date:** 2026-09-21
- **Deciders:** EVC

## Context

The plan sequenced work as M0 through M6, with two validation spikes ahead of the architecture so
that the assumptions most capable of invalidating the product were tested before anything was built
on them. That ordering is good spike discipline and the reasoning behind it still holds.

Three things about it did not survive contact with the owner's actual goal.

**Nothing was usable until M6.** The owner's near-term need is to apply for front-of-house jobs.
Under M0 through M6 the first application could not be produced until the last milestone, so the
tool delivered nothing while the applying happened by hand anyway.

**Investigation D deadlocked the build.** D settles crawler identity, robots versus terms, and
snapshot retention. It blocks M2, M2 gates M3 through M6, and D's named owner is technology and
privacy counsel. On a single-applicant local project that owner is unlikely to exist, so the
sequence could reach M1 and stop permanently with no defined way forward.

**The milestone order was shaped by the restaurant vertical, which is the starting point rather
than the goal.** The owner intends to extend the system to other verticals, beginning with software
roles, where discovery is not geographic. Restaurant search is employer-first: find places, find
their careers pages, find postings. Software search is posting-first: query an index, get postings,
resolve the employer afterwards. The plan already contained a posting-first path, drawn in the stage
diagram as the manual-intake edge, but treated it as a convenience feature rather than as the seam
the second vertical would need.

Separately, neither spike measured whether postings exist. M1 measures employer recall and M2
measures detection accuracy, and both can pass in full while the pilot produces a Gate 1 table with
almost nothing in it.

## Decision

Delivery is three phases rather than seven milestones.

**Phase 1, Apply.** The complete path from a posting to a recorded application: intake, fact bank,
materials, Gate 2, application sheet, Gate 3, records. Fed by manual intake, which is implemented as
the first posting-source adapter rather than as a special case. Source-agnostic, so it serves
restaurant and software postings equally.

**Phase 2, Discover.** Employer-first discovery feeding the pipeline Phase 1 built: the two
validation spikes, the crawl security boundary, the durable job queue, discovery accounting, and
Gate 1 selection. Gated by Investigation D, which now blocks this phase rather than the project.

**Phase 3, Generalize.** Further employer-set strategies and posting sources, description-level
classification, and additional job profiles, including software roles.

Phase 1 builds only the architecture its own path requires: the content-addressed artifact store and
`stage_runs` with input fingerprints. Both are load-bearing for materials, because a Gate 2 approval
binds to a document content hash and must invalidate when an input changes. The durable job queue
waits for Phase 2, where there is asynchronous work to queue.

Four interfaces are settled in Phase 1 while they are still cheap to change:

1. Posting sources are adapters behind a port; manual intake is the first implementation.
2. The employer entity is `Employer`, not `EmployerLocation`. Location is an attribute, not identity.
3. Employer-set discovery is a registered strategy. A geographic radius is one strategy among several.
4. Classification is a named strategy. Title-pattern rules are the first implementation.

## Consequences

**Easier.** An application can be submitted during Phase 1 rather than after the whole system exists.
The phases are independently valuable, so a disappointing Phase 2 yield costs the discovery work and
nothing else. Investigation D returns to being a normal prerequisite for the phase that needs it.
Phase 3's adapters slot into a port that a working implementation has already exercised.

**Harder.** Four interfaces are defined before a second implementation exists to test them against,
and some of those guesses will be wrong. Revising them in Phase 2 costs a migration against live
application history, which is the situation the old M3 was ordered early to avoid. The cost is
accepted because the alternative pays the same bill later with more code behind it.

**Foreclosed.** The original claim that architecture is hardened in one pass before feature work.
Hardening is now distributed to the phase that needs each piece, and the discipline that kept it
honest has to come from the phase exit criteria instead of from a single milestone.

**Accepted cost.** The spikes no longer run before any architecture exists. Phase 1 commits to a
domain model that Phase 1 alone cannot validate, because only Phase 2 exercises it against a second
source. The four seams above are the hedge, and they are a hedge rather than a guarantee.

## Alternatives considered

**Keep M0 through M6.** Preserves spike-before-architecture ordering exactly. Rejected because it
delivers nothing usable until the final milestone, leaves the Investigation D deadlock in place, and
spends the owner's first months on the vertical they are least certain about.

**Thin slice, thin seams.** Build the applying path the most direct way and refactor when discovery
arrives. Fastest to a first application. Rejected because the refactor would land on a domain model
with real application history and migrations behind it.

**Slice plus full hardening.** Pull the old M3 into Phase 1 whole. Rejected because it builds a
durable job queue for a pipeline whose only asynchronous work is a person pasting a link, and it
pushes the first application out by weeks for infrastructure nothing yet uses.

## Evidence

This decision rests on stated goals rather than measurement, which is appropriate for a sequencing
decision and worth naming plainly.

- The owner's priority ordering and reach goal, given during the 2026-09-21 planning session.
- Investigation D's own brief, which records that the previous reviewer declined to answer it and
  names counsel as the owner. The deadlock is visible in the briefs as written.
- Investigation E's background, which observes that restaurant employers hire through
  hospitality-specific tools and Indeed-hosted applications rather than through Greenhouse and
  Lever. This is a market observation, not a measurement, and E exists to measure it.
- Review 1 verified that the Greenhouse public job board API remains public and unauthenticated.
  That adapter looks marginal for the restaurant pilot and is a primary source for Phase 3.

**What would test it.** Phase 1 completing without the missing discovery work blocking it, and
Phase 2 exercising the four seams against a real second source without a domain migration. If
Phase 2 needs a migration against live data anyway, the thick-seams hedge did not pay and the
thin-seams alternative was the better call.
