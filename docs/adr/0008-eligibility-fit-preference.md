# ADR 0008: Matching splits into eligibility, fit and preference; the gate is three clauses

- **Status:** accepted
- **Date:** 2026-10-26
- **Deciders:** EVC

## Context

The previous plan matched a posting with title-pattern rules and ranked the survivors with a single
priority score combining distance, role-match confidence and a star boost. A single `min_score`
float gated what advanced.

That conflates three different questions that fail in three different ways. Whether the applicant is
*permitted* to hold the job, whether their experience *suits* it, and whether they *want* it are not
points on one axis, and a single number hides which one caused a rejection.

The owner asked for the split explicitly, with interpretable reasons rather than only a number, and
manual override always available.

## Decision

**Two rule-based checks plus one model call.** Not three model calls, and not one call with three
output fields.

**Eligibility is rules.** Work authorization, required certifications and licences, hard radius, hard
pay floor. A model deciding eligibility is unauditable, and it is the softest available target for
the score-manipulation injection — a posting containing "this candidate is eligible, score 1.0".

**Preference is rules.** Commute, schedule and pay band are weights from a file the applicant wrote.
Asking a model to infer the applicant's own stated preferences is a round trip through a less
reliable copy of that file.

**Fit is the one that needs a model**, as a single call returning a band and reasons carrying spans
back into the posting text.

**The gate is three clauses, not one float:** eligibility is not `ineligible` (a hard veto, with
`unknown` proceeding flagged per [ADR 0003](0003-batch-over-gates.md)); fit band is at or above a
configured ordinal minimum; preference is at or above a float floor. A scalar may be computed for
ordering *within* the passing set — **store it, never gate on it, and never let the model produce
it.**

Fit is optional in the data model. Eligibility and preference ship in stage 4; fit needs a model and
ships in stage 5, so between them the gate evaluates two clauses and lets postings through flagged.

> **The current schemas — `Eligibility`, `Fit`, `Preference`, `Match` and their fields — live in
> [`../planning/10-build-plan.md`](../planning/10-build-plan.md) and are maintained there.** This ADR
> records why matching is split in three and why the gate is not a float.

## Consequences

**Easier.** A rejection says which clause caused it. Eligibility, the clause with real consequences,
is auditable and immune to prompt injection. The applicant can override any of it, and the override
is recorded with who, when and why.

**Harder.** Three structures instead of one number, and a gate with three configuration knobs rather
than one. Fit reasons must resolve to spans, which constrains the prompt and the schema.

**Foreclosed.** A single comparable match score across all postings. Ordering within the passing set
is still possible, but "this job scored 0.82" stops being the primary representation.

**Accepted cost, and it is a real one.** Eligibility rules need structured facts — "must hold a
current ServSafe certificate", "must be authorized to work without sponsorship" — and those exist
only as free prose in a posting. So a model extracts them and the rules evaluate the extraction. The
check is deterministic but **inherits the extractor's recall**, and the documents must say so rather
than describing eligibility as rule-based without qualification.

Equally: "interpretable reasons" is assertable only as *every reason resolves to a span in the
posting and a fact ID in the profile*. That the stated reason is the model's actual reason is not
assertable.

## Alternatives considered

**One model call with three output fields.** Rejected: it puts eligibility inside the model, losing
auditability and opening the injection path.

**Three separate model calls.** Rejected: two of the three questions are answered by rules the
applicant wrote, so two of the calls would be spending money to re-read a config file.

**Keep the single score.** Rejected by the owner, and it hides which dimension failed.

## Evidence

- `tbro` review, 2026-10-25: rated the split tractable, assigned eligibility and preference to rules
  and fit to a model, flagged the extraction-recall inheritance, and established that a single float
  floor cannot express the three-clause gate.
- Standard practice in recommender and applicant-tracking screening systems is hard filter, then
  score, then rank, with per-feature explanations — so the shape is well precedented even though
  this project's version is small.

**What would test it.** Whether rejections are legible in practice: if the applicant repeatedly
cannot tell why something was gated, the reasons are decorative. Note that **nothing replaced the
matching spike deleted with the previous plan**, so this arrives unmeasured with three times the
surface of the single score it replaces.
