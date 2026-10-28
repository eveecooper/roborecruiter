---
doc: progress
covers: [step status, evidence, what is next]
status: current
pairs_with: 10-build-plan.md
revision: 2026-10-26
---

# Progress

> **Where the work actually is.** One row per unit of work, its status, and the evidence that
> says so.
>
> **This file carries status only.** What a step *contains* and what "done" means for it live in
> [`10-build-plan.md`](10-build-plan.md), which wins on any conflict. Why a feature exists and
> which stage it lands in is [`12-feature-inventory.md`](12-feature-inventory.md). What blocks a
> step is [`11-investigations.md`](11-investigations.md). Nothing here is restated from those -
> the Deliverable column is a pointer, not a specification.
>
> **Updating it is part of a ticket.** A step's status changes in the same session the code lands,
> alongside the review-log entry. A tracker nobody updates is worse than no tracker.

**Status values.** `done` - exit criteria demonstrated, not asserted. `in progress` - started,
criteria not yet met. `next` - the unit of work to pick up. `not started`. `blocked` - named
dependency, with what it is.

---

## Where it stands

**Stage 1, step 1.1 of four steps is done. Next is step 1.2, `rr draft`.**

| Stage | Done | Total | Note |
| --- | --- | --- | --- |
| 1 — First real application | 2 | 4 | Offline. No model, no network, both asserted in CI |
| 2 — Repeatable, still offline | 0 | 7 | Deliverables, not numbered steps — see below |
| 3 — Source policy, then first fetch | 0 | 2 | 3.0 blocked by Investigation D |
| 4 — Discovery | 0 | 4 | Investigation A reopens here |
| 5 — Model-assisted curation | 0 | 10 | First stage with a model |
| 6 — Evidence-gated | 0 | 6 | Built only if recorded data justifies it |

Totals count the deliverables the build plan actually names. **Stages 2 and 4 through 6 are
written as sets of deliverables rather than numbered steps**, so their rows below are those
deliverables, not steps invented here. When a stage gains a step breakdown, the build plan gets it
first and this file follows.

---

## Stage 1 — First real application

Exit criteria per step: [`10-build-plan.md`](10-build-plan.md#stage-1--first-real-application).

| Step | Deliverable | Status | Evidence |
| --- | --- | --- | --- |
| 1.0 | Repo, tooling, migrations, the unretrofittable items, personas, enums, config profiles | **done** | CI green. Three safety assertions pass. `alembic upgrade head` applies to an empty database. `rr doctor` runs |
| 1.1 | `rr add` — paste a posting, get a row with full text, a hash and the employer's job ID | **done** | 62 tests pass. Demonstrated on a real IBM posting: one command, one paste, no flags; job ID read from the posting's own labels; the same requisition through a different link with a rewritten body recognised rather than duplicated |
| 1.2 | `rr draft` — template fill from `profile.yaml` via docxtpl, pinned LibreOffice to PDF, field allowlist, autoescape | **next** | — |
| 1.3 | `rr submit` + `rr log` — terminal walkthrough, records channel, elapsed time, and the hash of each file sent | not started | — |

**What 1.2 needs that is not code.** Every persona in `config/profile.yaml` still has `email`,
`phone`, `location` and `headline` as `TODO`, so a rendered document has no contact details to
put in its header. A Word template has to exist, and LibreOffice has to be installed and pinned.
None of that is a code task and all of it blocks the step.

**Stage 1 exit criterion, the one that matters:** one real application sent end to end, with
`rr log` naming the hash of the file that went out. That lands in 1.3.

---

## Stage 2 — Repeatable, still offline

| Deliverable | Status | Blocked by |
| --- | --- | --- |
| `inbox.yaml` with statuses and in-place corrections | not started | |
| Skip reasons as an enum | not started | |
| Hand-written job families with tailoring depth | not started | |
| Duplicate prevention across runs | not started | |
| Closed and stale posting handling | not started | |
| New-since-last-run view | not started | |
| File-ownership rules and the conflict check | not started | |
| *(Effort reporting — distributions, not raw numbers)* | **blocked** | Investigation G |

Effort reporting is listed separately because stage 1 already records the raw channel and elapsed
time; only the statistics wait.

---

## Stage 3 — Source policy, then the first fetch

| Step | Deliverable | Status | Blocked by |
| --- | --- | --- | --- |
| 3.0 | Source-policy ADR, written from Investigation D answered | **blocked** | **Investigation D** — named owner is technology and privacy counsel. Not ours to close |
| 3.1 | `PostingSource`, `PostingQuery`, capability router, one or two sources, cross-source dedupe | **blocked** | 3.0. Nothing in 3.1 may run before the ADR exists |

Leaving D open costs nothing until here, which is the point of this ordering. Investigation E
picks which sources get built, and every candidate source named in the build plan is unverified.

---

## Stage 4 — Discovery

| Deliverable | Status | Note |
| --- | --- | --- |
| Overture place source behind `iter_places` → source-neutral `employers.yaml` | not started | **Investigation A reopens here** |
| Careers checks as append-only rows against the six-outcome enum | not started | Table exists since 1.0; nothing writes it |
| Distance and compensation filters | not started | |
| The match gate — eligibility and preference, both rules | not started | Partial by design: fit needs a model and arrives in stage 5 |

**Two decisions are owed by this stage**, both recorded as undecided: what happens to walk-in and
instructions-only employers, which produce no posting; and whether schedule, seniority and
remote/hybrid become filters.

---

## Stage 5 — Model-assisted curation

First stage with a model, so it carries the safeguard work.

| Deliverable | Status |
| --- | --- |
| One typed `call(task, output_model, inputs)` site, per-task aliases in `models.yaml` | not started |
| `rr distill` — per-file extraction, caps, `count_tokens` dry-run, proposed diff | not started |
| Fit scoring — band plus reasons carrying spans | not started |
| Model-assisted extraction of a posting's structured fields | not started |
| Family clustering as a proposed diff with stable IDs | not started |
| Response caching, call cap, dollar ceiling | not started |
| The hostile-fixture injection suite | not started |
| Style profiles, voice matching from `voice.yaml` few-shot examples | not started |
| Parallel drafting, profile prune | not started |
| Skill-gap report — a group-by over unresolved fit reasons | not started |

---

## Stage 6 — Evidence-gated

Wanted, none committed. Built when recorded data shows the manual version costs enough to replace.
Conditions are in [`12-feature-inventory.md`](12-feature-inventory.md#wish-list---wanted-not-committed).

| Deliverable | Status | Gate |
| --- | --- | --- |
| Email response tracking | not started | Evidence |
| Follow-up reminders | not started | Evidence |
| Optional web interface | not started | Evidence |
| Local API | not started | Evidence |
| Browser fills the form, applicant presses submit | **blocked** | **Investigation C**, plus `channel` data showing one portal carries real volume |
| Career coaching plan | not started | Only if the deterministic skill-gap report proves insufficient |

---

## The ten unretrofittable items

Cheap now, expensive later. The list and the reasoning are in
[`10-build-plan.md`](10-build-plan.md#ten-things-that-are-cheap-now-and-unretrofittable-later);
this is only whether each is in place.

| # | Item | In place |
| --- | --- | --- |
| 1 | Version stamps on generated rows | yes, on `generated_documents`. Nothing else generates rows yet |
| 2 | Full posting text persisted | yes |
| 3 | Per-posting family assignment history | table exists; nothing writes it until stage 2 |
| 4 | `careers_check` as append-only rows | table exists; nothing writes it until stage 4 |
| 5 | Source-neutral `employers.yaml` | not yet — the file arrives in stage 4 |
| 6 | `schema:` integers checked at load | yes, refused rather than mis-parsed |
| 7 | Resolved application mode on the application row | column exists; nothing writes it until 1.3 |
| 8 | `content_hash` and `updated_at` on anything that round-trips | yes on postings and generated documents. `inbox.yaml` does not exist yet |
| 9 | User-scoped data root | yes |
| 10 | The employer's own posting ID | yes, since 1.1 |

---

## What is unverified or unmeasured

Carried here so it stays visible rather than being tidied away. Detail is in
[`10-build-plan.md`](10-build-plan.md#open-and-unverified) and the review log.

- **Nothing replaced the deleted matching spike.** Stage 4's gate arrives unmeasured with three
  times the surface of the single score it replaced.
- **Every cross-employer posting source is unverified.** No endpoint has been called.
- **Overture's schema and taxonomy move** on separate cycles and have not been re-checked.
- **Pyright is named in the coding standards but CI does not run it**, and the tool is not
  installed in the project environment.
- **Nothing is committed.** Step 1.0, step 1.1 and the whole 2026-10-26 planning reset are
  uncommitted working-tree changes on `main`.
