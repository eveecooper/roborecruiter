# roborecruiter

An assisted job application pipeline. It finds front-of-house restaurant openings near a chosen
location, prepares the application materials, and hands you the steps that need a person: the three
review gates, any verification challenge, and the final submit button.

**Status:** planning. No application code yet.
**Pilot:** ZIP 94085, 5-mile radius, front-of-house roles (server, host, busser).

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

Seven milestones, M0 through M6, in the [engineering plan](docs/planning/01-engineering-plan.md).
Each one ends in something runnable.

The order is not arbitrary. Two validation spikes come before any serious architecture: **M1**
checks whether the employer data source actually finds local restaurants, and **M2** checks whether
careers pages can be detected without silently discarding real openings. Both are assumptions
capable of invalidating the product, so they get tested before anything is built on top of them.
If a spike fails, the response is to fix the source or the approach, not to add architecture around
the problem.

Prefill, writer models, and extra job types all come after M6.

## Before M0 starts

- The engineering plan has no owner assigned.
- The Overture `basic_category_allow` list needs filling from the pinned taxonomy release.
- A current-year extract of the Santa Clara County permit data needs confirming as downloadable.
- Investigations D (source policy) and F (claim-check feasibility) are open and block M2 and M5.

## Rules the system follows by design

Not preferences, and not negotiable for convenience:

- No evading bot detection, solving CAPTCHAs, or ignoring `robots.txt`. Challenges go to you.
- No automated access to Indeed or any source whose terms forbid it. Manual paste only.
- No code path can submit an application. You press submit.
- Materials use only facts you have confirmed. Anything unverifiable is flagged, never invented.
- One application per posting unless you deliberately press Resubmit.
