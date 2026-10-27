# ADR 0003: The run never halts; human work accumulates and is drained in one sitting

- **Status:** accepted
- **Date:** 2026-10-26
- **Deciders:** EVC

## Context

The previous plan routed work to the applicant at three human gates: Gate 1 to select postings,
Gate 2 to approve materials, Gate 3 to verify and submit. The pipeline stopped at each one and
waited.

The owner's objection, in their words, is the rhythm this produces: wait thirty seconds, do
something for ten, wait forty, do something for a minute. The gates are not an accident of the
design, they are the design, so the objection is architectural rather than cosmetic.

What the owner wants instead: the machine runs ahead unattended, accumulates whatever needs a
person, and the person drains that queue in one sitting. Fourteen applications reviewed in one pass
and sent back to back, rather than fourteen interleaved waits.

## Decision

**No stage of the pipeline halts for a human.** Anything the system cannot determine proceeds with a
flagged best guess that is editable afterwards. An unclassifiable title is recorded with low
confidence and an editable field, not a prompt. A fact the curator wants and cannot find is marked
`inferred`, not queued.

Human work reduces to two kinds: **look at a draft, and send it.** There is no approval lifecycle,
no `pending` state the pipeline waits on, and no task table in stage 1.

Batch review arrives in stage 2 as `inbox.yaml`. Batch sending is `rr submit --all`, a terminal
walkthrough that opens each posting in turn, puts the files and copy-ready answers on screen, and
advances on confirmation.

## Consequences

**Easier.** A run is a batch job that can be started and walked away from. Because nothing waits on
a person, no durable job queue, no process supervision and no background worker are needed — the
previous plan's step 2.3 infrastructure is deleted rather than deferred. Correctness becomes
something the applicant opts into per round instead of a toll paid every round.

**Harder.** A flagged guess that nobody reads is a silent error. The flags have to be visible in the
review file or they are decoration. Reviewing fourteen drafts in one stretch is also a worse
attention environment than reviewing one — subtly wrong prose is harder to catch on the fourteenth
than the first.

**Foreclosed.** Any claim that the applicant explicitly approved each document before it was sent.
The record shows what was sent and when; it does not record an approval event, because there is no
longer one.

**Accepted cost.** The batch-review attention problem is real and unmitigated beyond flag
visibility. A sensible early practice is a low per-run cap until the output is trusted.

## Alternatives considered

**Keep the three gates.** Rejected: they are the mechanism producing the rhythm being designed away.

**Background drafting while the applicant works.** Considered and initially chosen, then dropped.
It only existed to keep an interactive review session from stalling, and with files rather than a UI
nothing stalls — the applicant starts a run, leaves, and returns to a complete review file. This
removed concurrency and partial-failure handling from the build entirely.

**Re-run at the end of a session to absorb answers.** Still available and effectively free, since it
is the same command. Not a separate mechanism.

## Evidence

Stated owner preference during the 2026-10-25 planning session, including the explicit rejection of
a background service in favour of one command that can be started and abandoned.

**What would test it.** If flagged guesses routinely reach an employer uncorrected, visibility is
insufficient and some work has to become blocking after all. The honest signal is how often an
application is sent with an `inferred` flag still on it.
