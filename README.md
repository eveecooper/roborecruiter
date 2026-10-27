# roborecruiter

An assisted job application pipeline. It prepares the materials for a job opening and hands you the
steps that need a person: looking over the draft, and the submit button. Later it learns to find the
openings too.

**Status:** planning. No application code yet.
**Next:** stage 1, step 1.0.

## Documentation

| Document | For | Read it for |
| --- | --- | --- |
| [Build plan](docs/planning/10-build-plan.md) | Building it | The six stages, the seams, and what "done" means at each step. **The one to follow.** |
| [Feature inventory](docs/planning/12-feature-inventory.md) | Anyone | Every requested feature and the stage it arrives in |
| [Open investigations](docs/planning/11-investigations.md) | Building it | The questions still unanswered, what each gates, and who answers them |
| [Discovery notes](docs/planning/13-discovery-notes.md) | Stages 1, 3, 4 | Careers-page outcomes, block detection, Overture facts and licence obligations |
| [Coding standards](docs/agent/coding-standards.md) | Building it | How to write it: config over code, seams, profiles, tests, types |
| [Development workflow](docs/agent/development-workflow.md) | Building it | How a request becomes a ticket becomes code |
| [Decisions](docs/adr/) | Building it | One record per significant decision. 0002-0011 are the 2026-10-26 reset. |
| [Review log](docs/planning/03-review-log.md) | Curious why | What changed in the plan and the reasoning |
| [Agent materials](docs/agent/) | Coding agents only | Conventions an agent needs before reading the above |

## How it gets built

Six stages. Each is usable on its own, and the order is what is cheapest to get right first.

**1. First real application.** You paste a posting; a Word template fills from your profile; you edit
the document freely; the terminal walks you through sending it; the record stores the hash of the
file that actually went out. **No model and no network code** — both asserted in CI. Done when one
real application has been sent.

**2. Repeatable.** A batch review file, several job families you write by hand, duplicate prevention,
stale-posting handling, and a view of what is new since the last run. Still offline.

**3. Source policy, then the first fetch.** The source-policy decision comes first and gates every
fetch after it. Then one or two permitted posting sources.

**4. Discovery.** The employer list generated from map data and pruned by you, careers-page checks,
distance and pay filters.

**5. Model-assisted curation.** Per-posting tailored documents, fit scoring, job-family clustering,
style profiles, writing in your voice from your own samples, cost caps and caching.

**6. Evidence-gated.** Email response tracking, follow-up reminders, an optional web interface.
Browser prefill only if the data justifies it and Investigation C clears it.

Why applying comes before discovering: [ADR 0001](docs/adr/0001-phased-delivery.md). Why the model
work comes late: [ADR 0005](docs/adr/0005-stage1-no-model-no-network.md).

## Before you start

- **Nothing blocks stages 1 and 2.** No open investigation needs answering first.
- Your facts need to exist as `config/profile.yaml`. It gets drafted in conversation from your old
  resumes and notes rather than by code.
- A Word template for the resume, and one for the cover letter.

## Before stage 3

- **Investigation D (source policy) is open and gates every fetch**, structured job-board APIs
  included. It is the one question routed to outside expertise.
- The candidate job sources are unverified — nobody has called an endpoint yet.

## Rules the system follows by design

Not preferences, and not negotiable for convenience. Reasons are in the build plan's
[non-goals](docs/planning/10-build-plan.md#non-goals).

- **No code path can submit an application. You press submit.** CI asserts it.
- No evading bot detection, solving CAPTCHAs, or ignoring `robots.txt`. Challenges go to you (human user).
- No direct automated access to Indeed, or to any source whose terms forbid it. Running an
  open-source scraper locally counts as direct access. Whether a third party could supply
  Indeed-sourced postings lawfully is [Investigation H](docs/planning/11-investigations.md) — open,
  and a last resort.
- Materials use only facts you have confirmed. Anything unverifiable is flagged, never invented.
- One application per posting unless you deliberately resubmit.
- Nothing is fetched before the source policy exists.
- One applicant at a time. Data is user-scoped so a second person costs a directory, but there is no
  authentication, no hosting, and no concurrent use.
