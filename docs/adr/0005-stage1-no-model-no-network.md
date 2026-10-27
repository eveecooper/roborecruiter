# ADR 0005: Stage 1 ships no model and no network code

- **Status:** accepted
- **Date:** 2026-10-26
- **Deciders:** EVC

## Context

Two earlier drafts of the reset put a model call in the first stage. One put `rr distill` — a
component reading the entire `knowledge/` folder — in step 1.2, directly between the owner and their
first sent application. A later draft kept it but dropped the clustering, on the theory that
"functional profile generation" was the small version.

Both the `bob` (scope) and `tbro` (feasibility) reviews rejected this, and the second identified why
the smaller version does not help: **clustering was never the unbounded part. The corpus read is.**
Dropping clustering shrinks the output problem and leaves the input problem untouched — one unbounded
call instead of a loop.

The cost of a model in stage 1 is not the API call. It is everything that has to arrive with it: an
API key, a per-run call cap, a cumulative dollar ceiling, a `count_tokens` dry-run for an unbounded
input, a closed output schema, a render-time field allowlist, a deny-set check, version stamps, a
content-addressed response cache, and fifteen to twenty-five hostile fixtures. That is substantially
all of stage 5's safeguard work, bought in exchange for an exit criterion that a hand-written
`profile.yaml` delivers in an afternoon.

The owner separately wants AI-generated candidate knowledge from day one. That is a real requirement
and it is satisfied a different way.

## Decision

**Stage 1 contains no model call and no network access.** Both are asserted mechanically in CI: no
module may expose a submit, click-to-submit or form-post operation, and no module may import
`httpx`, `requests` or `playwright`.

`config/profile.yaml` is drafted **in conversation**: the applicant hands over old resumes and notes,
Claude writes the YAML, the applicant reviews and corrects it. No code, no API key in the project, no
prompt-injection surface, no stage.

`rr distill` arrives in stage 5 as a re-runnable feature, bounded by per-file extraction, a
deterministic merge, three hard caps, a `count_tokens` dry-run that aborts rather than warns, and
output as a proposed diff rather than a direct write.

## Consequences

**Easier.** The first application is produced by a system with two possible failure sources, both of
them files a person can read: the profile data and the template. With a model there would be four,
including prompt and model compliance. The no-network assertion is the cheapest mechanical safety
property available and it holds for free through stages 1 and 2. Prompt injection has no surface at
all until there is a fixture suite to point at it.

**Harder.** The applicant cannot regenerate `profile.yaml` from a changed `knowledge/` folder without
another conversation, until stage 5. Documents in stages 1 and 2 are template fills, not per-posting
prose.

**Foreclosed.** Nothing permanently. The template path is not scaffolding — it becomes the
quick-apply mode behind ADR 0008's null curator and stays in use indefinitely.

**Accepted cost.** Conversation-drafted YAML is not reproducible and not pinned to a prompt version.
It is a one-off artifact the applicant then owns, which is acceptable precisely because they own it.

## Alternatives considered

**Bounded distill in stage 1** — per-file extraction, caps, dry-run, proposed diff. Affordable as
designed, and rejected only because the surrounding safeguard work is not, and because it reverses
the no-model and no-network assertions on day one.

**A throwaway script outside the pipeline** that drafts `profile.yaml`. Rejected as the worst of
both: a model dependency with no CI coverage, and a thing nothing tests that quietly becomes
load-bearing.

**Full distill with clustering, as an earlier draft had it.** Rejected: it put the project's largest
unvalidated component in front of its first deliverable.

## Evidence

- `tbro` review, 2026-10-25: the unbounded corpus read is the cost and injection surface, and
  deferring clustering addresses neither. Bounded distill rated easy once capped; unbounded rated
  difficult.
- `bob` review, 2026-10-25: enumerated the safeguard work that would travel into stage 1, and
  identified the loss of the no-network assertion as the specific cost.
- Verified model pricing, 2026-10-25: drafting twenty postings costs $0.16 to $1.60 depending on
  model, so cost is a bug guard rather than a budget. The unbounded distill read is the real
  exposure.

**What would test it.** If stage 1 reaches a sent application without the missing model having been
an obstacle, the sequencing was right. If drafting from a hand-written profile proves so weak that
the applications are not worth sending, the model was needed earlier than this ADR assumes.
