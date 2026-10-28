---
doc: feature-inventory
status: current
pairs_with: 10-build-plan.md
revision: 2026-10-26
---

# Feature Inventory

> **Every request lands here.** This is the register of what was asked for, what stage it arrives
> in, and what is actually built — the quickest answer to "when do I get X".
>
> **No feature gets built before it appears in this file.** A request is placed in a stage, or
> listed under Wish list with the reason it cannot be placed yet, or recorded under Not in plan.
> A request that changes an existing decision needs an ADR rather than a row. Procedure:
> [`../agent/development-workflow.md`](../agent/development-workflow.md).
>
> **[`10-build-plan.md`](10-build-plan.md) wins on any conflict.** Stage contents are defined there;
> this table is derived from it. When a stage changes, the build plan is edited first and this file
> second. Why a feature is excluded is stated once, in that document's Non-goals section.
>
> What gates what: [`11-investigations.md`](11-investigations.md).

**Status column.** `built` means the code exists and its tests pass. `schema` means the database
columns are in place but no command uses them yet. Blank means planned, not started.

## Planned - committed, in stage order

| Feature | Stage | Status | Note |
| --- | --- | --- | --- |
| Apply to a posting, with a record of the exact file sent | 1 |  | |
| Paste a posting in by hand (`rr add`) | 1 | built 1.1 | Manual intake is a posting source, not a special case ([ADR 0001](../adr/0001-phased-delivery.md)) |
| Employer's own posting ID, per-employer duplicate check | 1 | built 1.1 | `--job-id`, or read from the pasted text, or from the link. The tenth unretrofittable item |
| One command, one paste — no intermediate file | 1 | built 1.1 | Interactive paste is the default. Job ID and title read from the posting's own labels by rules, not a model ([ADR 0005](../adr/0005-stage1-no-model-no-network.md)) |
| Hand-edit documents, never overwritten (`.v2`) | 1 | schema 1.0 | |
| Hand-editable facts file (`config/profile.yaml`) | 1 |  | Written in conversation, not by code |
| Area configurable | 1 | config 1.0 | `config/run.yaml`, the only place a ZIP appears |
| Document style via Word templates | 1 |  | |
| Channel + elapsed time per application | 1 | schema 1.0 | Reporting waits on Investigation G |
| Schema migrations (Alembic) | 1 | built 1.0 | |
| Config profiles (`dev` / `demo` / `prod`) | 1 | built 1.0 | |
| Credentials and private documents out of version control | 1 | built 1.0 | |
| Posting-text-is-data assertion | 1 | built 1.0 | |
| Employer records separate from posting records | 1 schema, 4 use | schema 1.0 | |
| SQLite authoritative, YAML editable | 1 | schema 1.0 | |
| Modular seams, independently improvable | 1 onward | ongoing | |
| User-scoped data root, one database per user | 1 | built 1.0 | A second person costs a directory |
| Personas - contact details and headline vary by role | 1 | built 1.0 | One person, several presentations; resolved name stored on the application |
| Batch review and send in one sitting | 2 |  | |
| Quick-apply vs deep tailoring control | 2 |  | Real effect at stage 5 |
| Hand-written job families + template mapping | 2 |  | |
| Duplicate prevention, repeat-run protection | 2 |  | |
| Posting status, lifecycle, stale/closed detection | 2 |  | |
| New-since-last-run view | 2 |  | |
| Skip reasons (enum) | 2 |  | |
| YAML round-trip with conflict detection | 2 |  | |
| Optional UI | 2 |  | Only if it captures a skip reason in one keystroke |
| Effort reporting | 2 |  | Blocked: Investigation G |
| Scan named employers' job boards | 3 |  | Blocked: Investigation D |
| Scan on a schedule | 3 + OS task |  | Not a feature; an operating-system scheduled task |
| Title search across employers not individually named | 3 |  | No permitted source confirmed |
| Discovery strategies separate from source adapters | 3 |  | Capability tags |
| Cross-source duplicate detection | 3 |  | |
| Overture employer-list generation, editable | 4 |  | Investigation A reopens |
| Careers-page fetching | 4 |  | Cuttable if it drags |
| Distance + compensation filters | 4 |  | |
| Eligibility + preference matching (rules) | 4 |  | |
| Manual override for low-scoring jobs | 4 |  | |
| Posting fields extracted by a model, not by label rules | 5 |  | Asked for at stage 1; a model cannot ship there ([ADR 0005](../adr/0005-stage1-no-model-no-network.md)). Rule-based label reading stays as the fallback |
| Fit matching (model), match grading | 5 |  | |
| AI curation of per-posting tailored documents | 5 |  | |
| Dump unfocused material → YAML (`rr distill`) | 5 |  | Per-file, capped, proposed diff |
| Import from resume | 5 |  | |
| AI job-family clustering | 5 |  | Measured against the hand-written set |
| Tailoring depth control | 5 |  | |
| Versioned style profiles | 5 |  | |
| Writing in the applicant's voice from sample materials | 5 |  | Few-shot examples from `config/voice.yaml`, separate sets per document type |
| Model swapping (per-task aliases) | 5 |  | |
| Cost limits + response caching | 5 |  | |
| Prompt-injection test suite | 5 |  | |
| Disclosure of what is sent to the model | 5 |  | `rr draft --explain` |
| Parallel document generation | 5 |  | |
| Match-quality calibration | 5 |  | Against own judgement, not accuracy |
| Skill-gap report — what postings want that the profile lacks | 5 |  | Deterministic: a group-by over unresolved fit reasons |

## Wish list - wanted, not committed

Real requests, kept deliberately out of the planned table so a want does not read as a schedule.
Two kinds.

### Stage 6 - built only if the evidence justifies it

Each of these is wanted. None is committed. They are built when recorded data shows the manual
version is costing enough to be worth replacing - which is a decision made later, with numbers,
not now.

| Feature | Condition |
| --- | --- |
| Career coaching plan — what to go do about the gaps | Evidence-gated; needs a model, and the advice is unverifiable |
| Email response tracking | Evidence-gated |
| Follow-up reminders | Evidence-gated |
| Browser fills the form, applicant presses submit | Blocked: Investigation C |
| Web interface | Evidence-gated |
| API for other personal tools | Evidence-gated |

### Not placeable yet

Requests that cannot be given a stage because they depend on something that does not exist.
"Deferred, because X does not exist" is a complete answer and beats building it early.

| Feature | Why it cannot be placed | What would place it |
| --- | --- | --- |
| *(none currently)* | | |

## Not in plan

Reasons are in [`10-build-plan.md`](10-build-plan.md#non-goals), not restated here.

| Feature | Status |
| --- | --- |
| Machine presses submit | Never — asserted in CI |
| Model fine-tuning on the applicant's writing | Not planned |
| Services architecture (separate processes, IPC) | Rejected |
| Hosted or multi-user *operation* | Standing non-goal — but data is user-scoped ([ADR 0011](../adr/0011-user-scoped-data-roots.md)) |
| Direct automated Indeed access | Denied by terms |
| Indeed postings via a third party | **Open question** - [Investigation H](11-investigations.md), last resort |
| CAPTCHA solving, proxy rotation, bot-detection evasion | Denied |
| Approval gates that halt the pipeline | Removed ([ADR 0003](../adr/0003-batch-over-gates.md)) |
| Background service or built-in scheduler | Rejected |
| Four environments (adding UAT) | Rejected |

## Undecided

Neither blocks stage 1.

- **Walk-in and instructions-only employers.** They produce no Posting, so two of the six
  careers-page outcomes currently have no destination. This was an open question in the previous
  plan and was deliberately not carried into this one. Needs a decision by stage 4.
- **Filters beyond distance and compensation.** Schedule, seniority and remote/hybrid were named
  during planning but are unspecified. Needs a decision by stage 4.