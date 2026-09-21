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

**Scope:** [the engineering plan](01-engineering-plan.md) at draft 2, and
[the open investigations](02-deferred-investigations.md).

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
