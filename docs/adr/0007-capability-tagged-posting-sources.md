# ADR 0007: Posting sources are capability-tagged against one query object

- **Status:** accepted
- **Date:** 2026-10-26
- **Deciders:** EVC

## Context

The owner proposed separating **discovery strategies** — what to search for: a location, a job
title, a specific employer — from **source adapters** — where the information comes from: Overture,
Greenhouse, Lever, Ashby, a pasted URL, a website crawler. The distinction is correct: what to
search for is not a property of a data source, and several strategies can use the same source.

The obvious implementation is a two-dimensional matrix of strategies against adapters. The `tbro`
review established that the matrix is mostly empty, which makes it the wrong shape:

- Greenhouse, Lever and Ashby all require a specific employer's board token. They answer exactly one
  kind of question and are **not search engines**.
- An aggregator, if a permitted one exists, answers title and area queries.
- A pasted URL is a degenerate case.
- **Overture populates no cell at all** — it is a source of *places*, not postings.

So six named adapters collapse into two capability sets plus a special case, and one of them does not
belong in the table.

The review also dissolved two of the proposed strategies. **Preferences is not a discovery mode** —
it ranks and filters what comes back, which is the matcher's job, and putting it here duplicates it.
**Employer mode is not a mode** — it is the employer-reference path through the same router.

## Decision

**One query object, and a capability set declared by each posting source.** A discovery "mode" is a
pure function from configuration to a query; a router selects the sources whose capabilities can
answer it. **No registry, no plugin entry points, no mode classes.**

Place sources stay on their own seam and `config/employers.yaml` stays source-neutral, so its shape
does not leak Overture's schema.

The seam is established in stage 3, where both a source and a consumer actually exist.

> **The current interface definitions — `PostingQuery`, `Capability`, `PostingSource` — live in
> [`../planning/10-build-plan.md`](../planning/10-build-plan.md) and are maintained there.** This
> ADR records why the shape is what it is, not what the fields currently are.

## Consequences

**Easier.** Adding a source is one object with a capability set. The router needs no change, and a
query that no source can answer fails visibly at selection rather than silently returning nothing.
Separating places from postings keeps Overture out of an interface it does not fit.

**Harder.** Capability tags are a claim about a source, not a proof. A source tagged
`SEARCH_BY_TITLE` that quietly ignores the titles will return irrelevant results rather than an
error.

**Foreclosed.** A strategy-by-adapter matrix, and the registry infrastructure it would have implied.

**Accepted cost.** `SEARCH_BY_TITLE` may have no implementation at all. The free board APIs cannot
provide it, Indeed is denied, and Google for Jobs has no public search API. The candidate sources —
CareerOneStop and the National Labor Exchange, USAJOBS, Adzuna — are **all unverified**, and all are
subject to ADR 0006. Title search across employers the applicant has not individually named may
therefore be an empty capability for some time, which also means title-based discovery is likely to
serve software roles before local hourly work.

## Alternatives considered

**A strategy-by-adapter matrix.** Rejected: mostly empty cells, and it invites a registry for a
handful of objects.

**One generic `fetch(source)` port, as an earlier draft had.** Rejected: it hides the fact that
different sources answer different questions, so the caller has to know which source can serve which
query — exactly the knowledge the capability set makes explicit.

**Preferences and employer-list as first-class discovery modes.** Rejected per the review:
preferences is ranking, and employer-list is the employer-reference path.

## Evidence

- `tbro` review, 2026-10-25: the matrix is two populated capability sets, Overture populates none,
  and `python-jobspy`-style tools that do offer title search all scrape Indeed or LinkedIn which is a last resort as it could lead to violations of ToS.
- Investigation E, which is what selects the adapters actually worth building.

**What would test it.** Whether a second posting source slots in without changing the router. If it
needs router changes, the capability set is too coarse.
