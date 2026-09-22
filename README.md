# roborecruiter

An assisted job application pipeline. It prepares the application materials for a job opening and
hands you the steps that need a person: the review gates, any verification challenge, and the final
submit button. Later it learns to find the openings too.

**Status:** planning. No application code yet.
**Next:** Phase 1, which applies to postings you bring it.
**Pilot for Phase 2:** ZIP 94085, 5-mile radius, front-of-house roles (server, host, busser).

## Documentation

| Document | For | Read it for |
| --- | --- | --- |
| [Product overview](docs/planning/00-product-overview.md) | Anyone | What this is, what it deliberately will not do, and where it is weak |
| [Engineering plan](docs/planning/01-engineering-plan.md) | Building it | Scope, stage design, milestones, and what "done" means at each one |
| [Open investigations](docs/planning/02-deferred-investigations.md) | Building it | The questions that are still unanswered, and who answers them |
| [Review log](docs/planning/03-review-log.md) | Curious why | What changed in the plan and the reasoning behind it |
| [Decisions](docs/adr/) | Building it | One record per significant decision |
| [Agent materials](docs/agent/) | Coding agents only | Context an agent needs before it can read the above correctly |

## How it gets built

Three phases in the [engineering plan](docs/planning/01-engineering-plan.md). Each one is useful on
its own, and each step inside one ends in something runnable.

**Phase 1, Apply.** You paste a posting; it produces materials that trace to confirmed facts and an
application sheet you submit yourself. Source-agnostic, so a restaurant posting and a software
posting travel the same path.

**Phase 2, Discover.** Finds the postings for you, around a ZIP code. This is where the two
validation spikes live: one checks whether the employer data source actually finds local
restaurants, the other whether careers pages can be detected without silently discarding real
openings. Both are assumptions capable of invalidating automated discovery, so they are tested
before the crawl infrastructure is built on them. A third measurement asks whether the postings
exist at all, because the first two can pass while the pipeline returns nothing.

**Phase 3, Generalize.** Other ways of assembling an employer set, description-level matching, more
job types, and eventually verticals that are not geographic. Prefill and writer models are here too.

Why this order rather than building discovery first: [ADR 0001](docs/adr/0001-phased-delivery.md).

## Before Phase 1 starts

- Investigation G (effort instrumentation) is open and blocks step 1.4. It is small.
- A base resume, cover letter, experience file, and timeline need to exist as input.

## Before Phase 2 starts

- Investigation D (source policy) is open and blocks every fetch in the phase.
- The Overture `basic_category_allow` list needs filling from the pinned taxonomy release.
- A current-year extract of the Santa Clara County permit data needs confirming as downloadable.

## Rules the system follows by design

Not preferences, and not negotiable for convenience:

- No evading bot detection, solving CAPTCHAs, or ignoring `robots.txt`. Challenges go to you.
- No automated access to Indeed or any source whose terms forbid it. Manual paste only.
- No code path can submit an application. You press submit.
- Materials use only facts you have confirmed. Anything unverifiable is flagged, never invented.
- One application per posting unless you deliberately press Resubmit.
