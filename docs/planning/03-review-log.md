---
doc: review-log
status: record
reviews: 01-engineering-plan.md
---

# Review log

> **History, not instruction.** What changed in the planning documents, the reasoning, and what
> was deliberately left alone. Newest review last. Earlier entries are kept as written even where a
> later review reversed them; the reversal is noted rather than the record edited.

## Review 1 - 2026-09-20

**Scope:** the engineering plan at draft 2, and
the open investigations.

**Method:** documentary review plus verification of the external facts the plan depends on. Claims
were checked against source documentation rather than accepted, because several load-bearing facts
about Overture and the hiring platforms had moved since the plan was written.

### What was verified

| Claim in draft 2 | Result |
| --- | --- |
| Overture per-source table, licenses, and the ~74 million figure | Exact match to Overture's documentation as of August 2026 |
| `categories` is deprecated in favour of taxonomy fields | Confirmed, and stronger than the plan assumed: removed in the September 2026 release |
| Taxonomy release cadence | Quarterly, in March, June, September, and December, separate from the monthly data release |
| `confidence` semantics | Likelihood the place exists, 0 to 1, explicitly independent of `operating_status` |
| Overture known issues: duplicates, junk rate, property completeness | Documented by Overture, as the plan states |
| Greenhouse public job board API | Still public and unauthenticated. The August 2026 deprecation is the separate employer-side Harvest API and does not affect it |
| An independent sampling frame for the answer key | Santa Clara County DEH food facility data exists on data.sccgov.org. A current-year extract was not confirmed |
| Google Maps "more than 150 million places as of 2019" | Not re-verified. No replacement figure was proposed, and the row is now marked as dated |

### Findings applied

| # | Finding | Change |
| --- | --- | --- |
| P1 | The submission-safety criterion required a prefill handoff test, but prefill is post-M6, so the first build could not pass its own criterion | Criterion restated as a structural check: no submit-capable code path ships, asserted in CI. The handoff test became the entry gate for post-M6 prefill work |
| P2 | The claim check required tracing every objective assertion in applicant-edited prose, which rules alone cannot do and the first build has no model for | Split into structural provenance for generated text and attestation for applicant edits. Investigation F measures the remaining boundary |
| P3 | The 20-employer answer key was recalled from memory and too small. 16 of 20 is a 95% interval of roughly 58% to 92%, and recall bias runs in the same direction as the risk being measured | M1's key is now sampled from the county permit frame and reported with its interval. The recalled list is kept separately as a relevance check. M2's key stays at 30 and gains a dev/holdout split |
| P4 | The config example used the `categories` field Overture removes this month, and pinned only the data release | Config filters on taxonomy hierarchy, pins the taxonomy version separately, and validates labels at startup. The confidence versus operating status distinction is now written down |
| P5 | Greenhouse and Lever serve corporate hiring and may return nothing for restaurants | Reframed as the reference implementation of the native-ID pattern. The adapter build list is now an output of M2's platform census, Investigation E |
| P6 | The `stage_runs` uniqueness constraint made a deliberate re-run after a bug fix impossible without deleting rows by hand | The fingerprint now includes a stage implementation version. Failed attempts update their row; `invalidated_at` marks superseded runs |
| P7 | One real opening can exist as two unmerged canonical postings, so posting-level uniqueness alone does not prevent a second application | Added an employer-plus-role duplicate guard with a 30-day window, independent of posting identity, with logged overrides |
| P8 | Effort was a success criterion with no measurement mechanism, and p90 over 20 applications is the second-largest value | Clock boundaries, a 15-minute idle timeout, and abandoned-session handling are specified. Reports use n, median, min, and max; p90 is dropped at pilot sizes |
| P11 | M1 forbade a review UI while M2 listed a review list as a deliverable | Clarified: the M1 and M2 review list is a generated report file. The console arrives with Gate 1 in M4 |
| P12 | Nothing said whether spike data survived M3 | M1 states spike persistence is throwaway by default. M3 records a re-import or discard decision |
| P13 | A 2019 Google figure sat unlabelled in a 2026 document, and the Overture attribution obligation was missing | Figure marked as dated rather than replaced. Attribution obligation added, scoped to redistribution |
| P14 | The draft lineage was nowhere stated, so a reader opening the product brief first would act on superseded commitments | Front matter on each document, a superseded-points table in draft 1, and the precedence rule in `CLAUDE.md` with the detail in `docs/agent/doc-precedence.md`. **Superseded by Review 2**, which removed the conflicts instead of explaining them |

Five decisions were added to the decision log (23 to 27) and three rows to open discussions.

### Investigations

Briefs A, B, and C gained two fields each: what the investigation unblocks, and what it costs to
keep deferring it. A deferred brief without those has no natural trigger to be picked back up.

Additions to the existing briefs:

- **A.** The precision-versus-recall asymmetry, stated up front so the expert does not try to set a
  recall SLO the sample cannot support. Cost-weighted noise rather than a pooled rate.
- **B.** A blocking step before labeling, since all-pairs labeling is quadratic and will not get
  done. The dependency on P7's duplicate guard, which is what permits a conservative auto-merge
  band. An explicit instruction to confirm rather than assume GERS ID stability across releases.
- **C.** A pinned portal fingerprint so a redesign is detected before the adapter interacts, and
  server-side partial-application creation modeled as a distinct outcome. The existing acceptance
  criterion counted only final-submit events, which would pass while a partial application was
  created employer-side.

Four briefs were added: **D** source policy, **E** platform census, **F** claim-check feasibility,
**G** effort instrumentation. D and F are open now rather than deferred, because they block M2 and
M5 respectively.

### Deliberately not changed

- **Draft 1's duplicated tech stack and open-questions tables.** They will keep diverging from
  draft 2's equivalents. They are retained because draft 1 is a historical record, and deleting
  content from a historical record defeats its purpose. Worth revisiting at the next revision.
  **Revisited in Review 2 and removed:** once the product overview stopped being a historical
  record and became a current document with its own scope, the duplicates had no reason to stay.
- **The crawler identity question.** A custom user-agent raises block rates on WAF-protected sites,
  which feeds directly into M2's pass criteria. The tradeoff is real and was left to Investigation D
  rather than decided in passing.
- **The Overture restaurant label set.** `casual_eatery` and a `[food_and_drink, restaurant, ...]`
  hierarchy path were observed, but not the full label set. Guessing would produce a config that
  silently returns zero rows instead of failing, so `basic_category_allow` was left empty with a
  note to fill it from the pinned release.
- **Any legal question.** Snapshot retention, robots versus terms, and applicant-initiated capture
  on restricted sources are jurisdiction-specific and went to Investigation D unanswered.

### Open as of this review

A snapshot, not a live list - the root README carries the current status.

- The owner field in the engineering plan is unassigned.
- `basic_category_allow` is empty and must be filled from the pinned taxonomy release before M1.
- A current-year extract of the county permit data has not been confirmed downloadable.
- Investigations D and F are open now and block M2 and M5 wording respectively.

---

## Review 2 - 2026-09-20

**Scope:** document structure. No engineering decision changed.

**Problem.** Review 1 kept two planning documents that disagreed, and explained the disagreement
with a precedence rule. The rule ended up restated in seven places, and every future revision would
have widened the gap it described. A reader also had to know the draft history before they could
trust either document.

**What was actually wrong.** The two documents only conflicted on four points, all engineering
specifics. Everything else in the product brief was material the engineering plan never covered.
They were not competing drafts; they were two documents that had never been given clean boundaries.

**Resolution.** Boundaries instead of precedence.

- The product overview keeps product intent, limitations, and the restrictions accepted by design.
- The engineering plan keeps everything operational.
- Neither supersedes the other, so no precedence rule is needed and none is stated.

**Eight requirements were stranded in the product brief** and had no home in the engineering plan.
They were moved rather than lost:

| Requirement | Now in |
| --- | --- |
| Source policy holds allow and deny lists | Operating principles, "Rules first" |
| Credentials from the environment; narrowest OAuth scope | Storage, security, and privacy |
| At most one series of three in prose | Style profile schema |
| Single column; no tables, text boxes, columns, or icons | Style profile schema and Documents |
| Style rules reduce but do not remove machine-writing tells | Operating principles, "Accuracy over polish" |
| Roughly four in five Overture records come from Meta | Kept in the product overview, as a data limitation |
| Multi-applicant use needs isolation, hosting, authentication | Kept in the product overview, as a scale limitation |
| Journals excluded, autobiography allowed | Already in both; left in both, it is a product boundary and an implementation rule |

**Removed from the product overview** as duplicates that would drift: its success criteria table,
its non-goals list, the tech stack table, the "still being considered" table, and the future tasks
checklist. The engineering plan carries all five in better form. The four conflicting claims went
with them - prefill in the first build, the five-minute target, unattended scanning, and the daily
cap - so the conflicts no longer exist to be explained.

**Removed from the repository:** `docs/planning/README.md` and `docs/agent/doc-precedence.md`,
both of which existed only to explain the conflict.

**Audience split.** The root README and the product overview are for a person. `CLAUDE.md` and
`docs/agent/` are for an agent and say so in their first line. The planning documents serve both.

**Not changed.** No milestone, acceptance criterion, decision-log entry, or investigation was
altered. Review 1's findings all stand as recorded above.

---

## Review 3 - 2026-09-20

**Scope:** a direction check on Review 2. When the two documents were given clean boundaries, did
every surviving statement come from the *later* decision, or did any older wording survive?

**Why it was asked.** Review 1's superseded-points table listed the four conflicts found during
that review. Review 2 then removed those four and declared the conflict resolved. But that table
was never a complete inventory - it recorded what one pass happened to catch - so resolving exactly
those four proved nothing about the rest of the document.

**Three older statements had survived.** All three were brought forward to the engineering plan's
position. Nothing moved in the other direction.

| Stale statement | Superseded by | Now says |
| --- | --- | --- |
| "It prepares, prefills where allowed, and stops", plus a bullet describing prefill coverage | Decision 22: prefill is post-M6, and the first build ships no browser worker | The first build does not fill forms at all; assisted prefill comes later on approved portals |
| Overture licenses listed as CDLA Permissive 2.0 and Apache 2.0 | The verified three-license list, including CC0 1.0 for AllThePlaces | All three, noted as depending on contributing source |
| "One application per posting, enforced by the database", stated flatly | P7: posting-level uniqueness alone does not catch one opening listed as two unmerged records | Adds the employer-and-role warning and the override |

The prefill one mattered. A reader would have come away believing the first build fills forms,
which is the single capability the plan most deliberately removed.

**One duplicate of my own making, removed.** Review 2 said it was moving the machine-writing-tells
limitation into the engineering plan, then left a copy in the product overview. It now lives only
in the product overview, where it sets expectations, rather than in both.

**Method note for next time.** Checking the conflicts already on a list only confirms that list.
The check that actually works is to sweep the older document against each decision in the newer
one, which is what this review did.

---

## Review 4 - 2026-09-21

**Scope:** the engineering plan's sequencing, and a general review of the whole plan at the owner's
request. This review changed the delivery order. Earlier reviews changed wording and structure;
this one changed what gets built first.

**Why it was asked.** The owner asked what the plan looked like and what needed clarifying. The
review surfaced findings, and answering the first question - what is this project for? - turned out
to change the answer to most of the others.

### What the plan was not asking

Six findings, in the order they mattered.

| # | Finding | Response |
| --- | --- | --- |
| R1 | **Nothing measured yield.** M1 measured employer recall and M2 measured detection accuracy. Neither asked whether postings exist. Both could pass in full - 85% recall, 30/30 correct outcomes - while the Gate 1 table held four rows, three of them routing to Indeed | Posting yield is now a Phase 2 exit criterion in its own right, reported by channel, with an explicit continue-or-stop decision. Investigation E gains the yield breakdown, since step 2.2 visits those sites anyway. Decision 35 |
| R2 | **Investigation D deadlocked the build.** D blocked M2, M2 gated M3 through M6, and D's named owner is counsel. On a single-applicant local project that owner is unlikely to exist, so the sequence could reach M1 and stop permanently | Dissolved by the phase restructure rather than answered. D now blocks Phase 2 alone; Phase 1 fetches nothing. The question itself remains open and unanswered, which is correct |
| R3 | **Two of six detection outcomes fell out of the pipeline.** Walk-in and Instructions only produce no Posting, but Gate 1 is a posting table, materials fill slots from a posting, the duplicate guard keys on employer plus role, and the application record stores a posting snapshot hash | Named as an open question at step 2.4 and as an open-discussion row, with the specific sub-questions written down. Not answered here: it needs real walk-in counts to answer well |
| R4 | **A single-sweep design for a recurring activity.** No delta between runs, no posting-closed detection, no re-scan cadence. Run one harvests a standing pool; run two re-presents decisions the applicant already made | Posting lifecycle and a new-since-last-run view are required at step 2.4, and the risk is in the risks table. The design itself is an open discussion |
| R5 | **Nothing was usable until M6.** Manual intake, materials, and the application sheet have no dependency on discovery, and they are where the owner's near-term value sits | The restructure. See below |
| R6 | **M2's zero-defect bar was weaker than M1's stated rigor.** The plan applies Wilson intervals carefully to recall, then states a zero-defect criterion on a holdout of roughly 15 without the same caveat. Zero silent false negatives on 15 is consistent with a true miss rate up to about 20%, and a detector missing one in ten passes it about one time in five | The criterion stays, because one known silent miss is worth stopping for. The plan now states what the holdout size actually licenses, so the report cannot imply the detector is clean |

Smaller: M0's exit criterion required running the discovery query that M1 listed as its own
deliverable, the owner field was unassigned ceremony on a single-applicant project, and
`requirements.txt` is committed empty. The first dissolved with the restructure, the second is now
set, the third is left alone.

### The restructure

**What the owner said.** Both the system and the job matter, in that order of care but not of
urgency: real engineering rather than a script, and a job soon. Front-of-house restaurant work is a
starting point chosen because restaurants are easy to enumerate by location. The reach goal is
other verticals, beginning with software roles, selected by what a posting says rather than where
it is - and the owner named the hard part correctly, which is finding and filtering postings
without paying for a data source.

**What that changed.** Restaurant search is employer-first: find places, find careers pages, find
postings. Software search is posting-first: query an index, get postings, resolve the employer
afterwards. The plan already contained a posting-first path - the manual-intake edge in the stage
diagram - but treated it as a convenience feature rather than as the seam the second vertical needs.

Delivery is now three phases, recorded in [ADR 0001](../adr/0001-phased-delivery.md):

- **Phase 1, Apply.** Intake, fact bank, materials, Gate 2, application sheet, Gate 3, records.
  Fed by manual intake. Source-agnostic.
- **Phase 2, Discover.** The two spikes, the crawl boundary, the durable queue, Gate 1. Gated by
  Investigation D.
- **Phase 3, Generalize.** Company lists, board APIs, description matching, the software profile,
  prefill, writer models.

Phase 1 builds the artifact store and `stage_runs`, because approval hashing is load-bearing for
materials, and defers the durable job queue to the phase that has asynchronous work. Architecture
hardening stopped being a milestone and became a property of each phase, which means the discipline
that kept it honest now has to come from phase exit criteria instead.

**Four seams settled early**, as the hedge against freezing the wrong domain model: posting sources
behind a port with manual intake as the first adapter; `Employer` rather than `EmployerLocation`;
employer-set discovery as a registered strategy; classification as a named strategy. Decisions 29
through 32. The cost is defining four interfaces before a second implementation exists to test them
against, and ADR 0001 names what would show the hedge did not pay.

Eight decisions added, 28 through 35. Four open-discussion rows added. Three risks added.

### Deliberately not changed

- **Every investigation A through G stays open.** D in particular was made non-blocking for Phase 1
  without being answered, and the brief now says so explicitly so the distinction is not lost. The
  crawler-identity tradeoff, the retention question, and robots-versus-terms precedence are all
  still unanswered and still routed to counsel.
- **Investigation F was not closed either**, though it is no longer blocking. Decision 34 removes
  hand-editing from Phase 1, which removes the free prose a detector would have scanned. The
  question of what a rule-based detector can actually catch is unanswered; it is now unasked. If
  editing returns, F returns with it, and F's brief says so.
- **The 80% recall gate, the 30-employer key, the Wilson interval discipline, the dev/holdout split,
  the cost-weighted noise framing.** Review 1 got these right and nothing here disturbs them. They
  moved to Phase 2 unchanged.
- **The restaurant pilot.** Keeping ZIP 94085 and front-of-house as Phase 2's target was tempting to
  revisit given the reach goal, but the owner's reasoning holds: restaurants are the easiest
  employer set to enumerate by location, which makes them the right vertical to debug discovery
  against even if they are not the vertical with the best yield.
- **`requirements.txt`, committed and empty.** Not worth a line in a planning review; it will be
  filled by the first code.
- **The Google Maps figure marked as dated in Review 1.** Still dated, still marked, still not
  re-verified.

### Unverified in this review

This review checked no external facts. It is a sequencing and structure review, and every external
claim in the plan traces to Review 1's verification table with the dates recorded there. Anything
load-bearing that has moved since 2026-09-20 has moved unnoticed.

### Open as of this review

A snapshot, not a live list - the root README carries the current status.

- Investigation G blocks step 1.4 and is small and unowned.
- Investigation D blocks all of Phase 2 and has no path to resolution on a solo project. The
  restructure bought time; it did not solve this.
- `basic_category_allow` is empty and must be filled from the pinned taxonomy release before Phase 2.
- A current-year extract of the county permit data has not been confirmed downloadable.
- Non-posting outcomes and repeat-run behaviour are open discussions with no leaning recorded.

## Review 5 - 2026-10-26

A reset rather than a review. The planning documents were restructured, nine decisions were
reversed or added as ADRs 0002-0010, and delivery was restaged from three phases into six stages.
Triggered by the owner asking why hand-editing was forbidden, and by an information-overload
complaint about the size of the engineering plan.

### What was wrong

**Hand-editing was banned to protect an untestable criterion.** Decision 34 forbade editing a
generated document, citing claim provenance. The real cause is recorded in Investigation F's own
brief: draft 2 required every objective claim in every document, including edited ones, to trace to
a confirmed fact, which needs claim extraction from prose, which needs a model Phase 1 refused to
use. The criterion could not be met or tested, so the previous draft removed its subject rather than
answering the question. ADR 0002 withdraws the criterion instead.

**The pipeline halted at three gates.** The owner's objection is the resulting rhythm - wait, act
briefly, wait again. That is the design rather than an accident of it, so ADR 0003 replaces the gates
with a run that never halts and a human queue drained in one sitting.

**A UI was mandatory.** The Streamlit console was a required step 1.3 deliverable. ADR 0004 makes
files authoritative and a UI permitted only where it reduces required actions.

**The largest unvalidated component came first.** Two drafts of this reset put `rr distill`, reading
an unbounded `knowledge/` folder, between the owner and their first application. ADR 0005 moves it
to stage 5 and keeps a model out of stage 1 entirely.

### Findings applied

- Delivery restaged as six stages: first application (offline), repeatable (offline), source policy
  then first fetch, discovery, model-assisted curation, evidence-gated extras.
- Nine ADRs written, 0002 through 0010. ADR 0001 retains its one surviving point.
- `10-build-plan.md` becomes the document to follow. `11-investigations.md` indexes A-G status.
  `12-feature-inventory.md` maps every requested feature to a stage.
- `00` and `01` deleted; their load-bearing content extracted to `13-discovery-notes.md` first. The
  A-G briefs from `02` were merged into `11-investigations.md` unedited. All three remain in git
  history. An intermediate step in this same review moved them to a `reference/` folder; that folder
  was then deleted, because storing a superseded document elsewhere is not a reason to keep it.
- `docs/agent/coding-standards.md` written: configuration over code, config profiles rather than
  branches, one seam per swappable thing, fakes at every seam, structured logs.
- Eight data items identified as unretrofittable and scheduled for step 1.0: version stamps
  including `output_schema_version`, full posting text, per-posting family assignment history,
  `careers_check` as append-only rows, a source-neutral `employers.yaml`, `schema:` integers,
  resolved application mode, and `content_hash` plus `updated_at` on round-trip files.
- Model pricing re-verified 2026-10-25. An earlier draft used $3/$15 for Sonnet, which is Sonnet
  4.6; Sonnet 5 is $2/$10. Corrected figures: Haiku 4.5 $0.16, Sonnet 5 $0.32, Opus 5 $0.80, Fable 5
  $1.60 per twenty-posting run.

### Reviewed by subagents

`bob` (scope) and `tbro` (feasibility) each reviewed three successive drafts. Their findings changed
the plan rather than confirming it:

- Browser form fill deferred. `bob`: attaching a resume or completing step one persists state the
  employer can see with no submit event to detect, so the boundary is per-portal, not a property of
  the code - and building it means deleting the submission-safety CI assertion on day one. `tbro`:
  3/10 feasible for arbitrary sites, 7/10 for one hand-picked platform, and no prior art exists for
  prefill with a proven no-submit boundary.
- The discovery coverage spike deleted as not applicable, because a hand-pruned employer list
  measures itself. **Nothing replaced the deleted matching spike**, which is recorded as a known gap.
- `tbro` corrected a claim this review had made: stable family IDs do **not** make scores comparable,
  because the profile, prompt and model drift beneath the stable label. Hence the version stamps.
- `tbro` corrected the clustering feedback claim. Distill reads a folder, not usage, so "it improves
  as I use it" is true for matching and curating and false for clustering. The fix is per-posting
  assignment history plus skip reasons, both now scheduled.
- `bob` identified that board APIs are still fetches, so ADR 0006 gates every fetch rather than only
  crawling.
- `tbro` rated the YAML-database sync the highest-risk item relative to its apparent size, and
  supplied the single-owner design in ADR 0009.

### Deliberately not changed

- **Every investigation A through G stays open and unanswered.** An earlier draft of this reset
  closed A as not-applicable and D by self-authored ADR; both were reverted. A is dormant and
  reopens when Overture lands at stage 4. D gates stage 3 and nothing before it, so it costs nothing
  to leave to counsel. F became relevant again when hand-editing returned but blocks nothing. G was
  downgraded from blocking a step to gating stage 2 reporting.
- **The no-submit rule and its CI assertion.** Not negotiable, and the browser-prefill reframing was
  rejected partly because it would have required rewriting the assertion.
- **The careers-page six-outcome enum, block detection, and the 30-employer answer-key discipline.**
  Reviews 1 and 2 got these right; they move to stage 4 unchanged.
- **The restaurant vertical as the starting point.** Still the easiest employer set to enumerate by
  location.
- **Reviews 1 through 4 are kept as written**, including the passages this reset reverses.
- `tbro-stack-log.md` was **not** edited. It belongs to that subagent, which could not write during
  plan mode. Its pending rows are listed in `10-build-plan.md` and need a `tbro` invocation to apply:
  Alembic from step 1.0, Pydantic, `instructor` or `pydantic-ai`, a hosted model API, `count_tokens`,
  Jinja2 autoescape, `ruamel.yaml`, `adjusted_rand_score`, CareerOneStop/NLx, USAJOBS, Adzuna,
  Greenhouse/Lever/Ashby board endpoints, llama.cpp with GBNF, and Streamlit returning to *proposed*.

### Open as of this review

A snapshot, not a live list.

- **Nothing replaced the matching spike.** Stage 4's gate arrives unmeasured with three times the
  surface of the single score it replaces.
- **Walk-in and instructions-only employers have no destination.** Two of six careers-page outcomes
  fall out of the pipeline. Open in the previous plan, deliberately not carried into this one, needs
  a decision by stage 4.
- **Filters beyond distance and compensation are unspecified** - schedule, seniority, remote/hybrid
  were named in planning and not scoped.
- **Every cross-employer posting source is unverified.** CareerOneStop and the National Labor
  Exchange, USAJOBS, and Adzuna are all from recall; no endpoint has been called. Title search across
  employers not individually named may have no permitted source at all.
- **Eligibility is rules evaluated over a model's extraction**, so it inherits that extractor's
  recall. Recorded in ADR 0008 rather than hidden.
- Overture schema and taxonomy state is still unverified and moves on a quarterly cycle.
- No code exists. The next step is step 1.0.

### Addendum, same day - Investigation H added

The owner reopened the Indeed question after this review was written: a third-party service or
open-source tool supplying Indeed-sourced postings is worth considering, noted explicitly as a
**last resort**.

Recorded as **Investigation H** rather than as a rule change, because the question needs a terms and
collection-method review that nobody here can perform. The rule that stands unchanged is **no direct
automated access to Indeed**, and the brief states plainly that running an open-source scraper
locally is direct access with extra steps rather than an exception to it. Only a third party holding
licensed or otherwise lawfully collected data is a genuinely different option.

H's start condition is after stages 3 and 4 demonstrate insufficient yield from permitted sources,
so it blocks nothing and costs nothing to leave open. Six files were brought into agreement:
`10-build-plan.md` non-goals, `11-investigations.md`, `12-feature-inventory.md`, ADR 0006,
`README.md`, and the `rr-refresh` skill. The non-goal bullet had been removed from the build plan and
the README earlier in the day; it is restored in its narrower and accurate form.

### Addendum, same day - user-scoped data roots, and two wish-list features placed

**ADR 0011: data is user-scoped.** The owner had prepared a folder per user, which contradicted the
standing "one applicant, local files" non-goal as written. The two things that non-goal conflated are
now separated: **path layout is nearly free; multi-user operation is not.** A `--user` flag selects a
data root, each user gets their own directory and their own SQLite file, and the non-goal is narrowed
to name what it actually excludes - no authentication, no hosting, no concurrent use by different
people, no rate limiting that reasons across applicants.

One database per user rather than a `user_id` column, because separate files make isolation
structural: no query can forget a filter and nothing can leak through a bug. A discriminator column
would charge every query in the codebase, forever, for cross-user features this project has declared
a non-goal.

The data root became the **ninth** unretrofittable item - it is the only one that is layout rather
than data, and changing it later means moving every file and rewriting every recorded path, including
hashes stored against already-sent applications.

**Two features placed from the wish list.** A **skill-gap report** at stage 5: each `Fit.reasons`
entry already carries a claim and whether it resolved to a fact ID, so an unresolved claim is a
labelled gap and aggregating them is a group-by rather than a model call. Every row traces to a real
posting, which is what keeps it from being generic. A **career coaching plan** at stage 6,
evidence-gated: turning that report into actionable advice needs a model and the output is
unverifiable, so it is built only if the deterministic report proves insufficient and is reported as
suggestion rather than assessment.

### Addendum, same day - plan audit after building step 1.0

The owner asked for a check that everything discussed had actually reached the planning documents,
and set the working agreement explicitly: **a request is placed in the plan before it is built** -
assigned a stage, or deferred with a reason.

The audit found two gaps, one of them caused by this session.

**Personas were built before being planned.** A `personas:` block was added to `profile.yaml` and
persona resolution to `config.py` during step 1.0, and the word appeared in no planning document.
A grep seemed to find it in the feature inventory, but that was a false positive on "personal
tools". Now recorded: a Personas section in the build plan, a feature-inventory row, and a
paragraph in ADR 0011 distinguishing a persona from a user - one person's presentations share a
data root, where different people do not.

**The development workflow never left the scratch plan file.** Written up as
`docs/agent/development-workflow.md`: the plan is the delegation and no project-manager agent is
needed, the role-to-skill mapping, why adding agents increases token use rather than reducing it,
what makes a step land in few iterations, and the request-placement rule above.

**Type checking had been dropped without a decision.** The previous engineering plan specified
strict checking with mypy or pyright; the rewritten coding standards omitted it and `pyproject.toml`
had no checker configured. Noticed only because the editor raised it. Now Pyright in `basic` mode,
recorded in the coding standards with the reason strict was rejected - it demands annotations for
third-party internals this project does not own, and an unread checker is worth nothing.

Everything else discussed in this session was already recorded: the skill-gap report and career
coaching plan, the per-document-type voice manifest, Investigation H, user-scoped data roots, and
config profiles.

---

## Step 1.1 built - 2026-10-26

Not a review. A build record, kept here because the planning documents are the project's memory and
two of these findings change how the next ticket is written.

`rr add` ships: paste a URL and posting text, get a posting row carrying the full text and a content
hash, plus a `posting.md` under `users/<user>/applications/<id>-<slug>/`. 42 tests pass; ruff and the
five safety assertions are green. Nothing new was planned - step 1.1 was already specified - but the
feature inventory gained the row it should have had, since manual intake is a posting source rather
than a special case.

**The safety assertion collided with the ORM, and the assertion won.** SQLModel's query method is
`session.exec(...)`, which `tests/test_safety.py` flags as dynamic execution. That file's own
docstring says to fix the code rather than relax the test, so queries here use SQLAlchemy's
`session.scalars(...)` instead. **That is now the convention for every query in this codebase.** A
compiled regex object was dropped for the same reason, `compile(` being on the same list. No
exemption was argued and no assertion was touched. Recorded because the next person to write a query
will reach for `.exec()` and get a red run with a confusing reason.

**Three defects were found by running the command, not by the tests.** All three are now covered.
The repeat path ignored an explicitly passed `--employer` while the command's own output told the
applicant to pass exactly that to correct a guess. The repeat path also reported "nothing changed"
while changing a field. And `posting.md` was rewritten only when the posting *text* changed, so a
corrected employer left the file disagreeing with its row permanently - and because nothing
downstream reads that file back, the disagreement was silent. `posting.md` is now reconciled against
the row on every add, self-healing rather than conditional.

**Title and employer are flagged guesses rather than required arguments**, per
[ADR 0003](../adr/0003-batch-over-gates.md): the title is the first non-blank line and the employer
comes from the link's host. The employer guess is wrong by construction on hosted boards -
`jobs.lever.co/acme` yields "lever" - which is why the command prints what it guessed and how to
correct it.

**Deliberately not changed.** `rr add` accepts `--profile` and does nothing with it; the uniform
`--user`/`--profile` interface is specified for every command in the build plan, and adding the flag
later would change the command's surface. **Pyright is not run in CI** - the coding standards name it
as the checker "so the editor and CI agree", `.github/workflows/ci.yml` runs ruff, the safety
assertions and pytest only, and the tool is not installed in the project environment. A documented
standard the pipeline does not enforce, recorded rather than fixed in passing.

**Unverified.** "Several pasted postings are on disk and in the database" is demonstrated in the test
suite, not in the owner's own data root, which holds one posting - the one supplied. The dedupe keys
are URL then text hash; cross-source duplicate detection is stage 3 and Investigation B's threshold
does not apply here.
