# ADR 0009: One owner per file; only two files round-trip, as generate-then-reimport

- **Status:** accepted
- **Date:** 2026-10-26
- **Deciders:** EVC

## Context

The owner's requirement was stated as: SQLite is the authoritative record for postings, statuses,
submissions and history; YAML remains the editable configuration and review interface; synchronise
user edits deliberately; never silently overwrite reviewed information.

The intent is right and the sentence is not a design. Read literally it describes bidirectional
synchronisation between a database and files a human edits, which the `tbro` review rated the
highest-risk item of the five it examined — not because the risk is large in absolute terms, but
because the specific failure is losing a review decision the applicant made by hand, silently.

The load-bearing words missing from the requirement are *which direction* and *which fields*.

## Decision

**One owner per file.** Three categories:

- **Human-owned** — the configuration files. YAML is the truth and **the tool reads them and never
  writes them.** Where the tool has a proposal, it writes a *separate* diff file the applicant
  applies by hand. This removes four of the six configuration files from the problem entirely.
- **Tool-owned** — posting text, hashes, timestamps, measurements, scores, check rows. The database
  is the truth; these appear in YAML only inside a generated read-only block.
- **Round-trip** — only `inbox.yaml` and, from stage 4, `employers.yaml`. Handled as
  **generate-then-reimport**, never as synchronisation.

**Conflict detection is two columns and one comparison**: a `content_hash` on the generated file and
an `updated_at` per contributing row. An unchanged hash means no edits. A changed hash applies only
human-owned fields. **A human edit to a tool-owned field is refused with a message, never silently
ignored** — silent ignoring is the failure that teaches the applicant the file does not work. A
contributing row newer than the file's generation timestamp produces a conflict file and applies
nothing for that row.

Round-trip files use `ruamel.yaml` so the applicant's own comments survive a regenerate.

> **The current field-by-field ownership table and the exact `--apply` rules live in
> [`../planning/10-build-plan.md`](../planning/10-build-plan.md) and are maintained there.** This ADR
> records why sync was rejected, not which fields are currently human-owned.

## Consequences

**Easier.** Four configuration files have exactly one writer, so there is nothing to reconcile. The
two that round-trip have a mechanism with a name and a precedent. A lost decision becomes a visible
conflict file instead of a silent overwrite. Human comments survive, which is what keeps a review
file in use.

**Harder.** The applicant cannot edit a tool-owned field in place even when they are right and the
tool is wrong; they get a refusal and have to change it where it lives. Proposals arrive as a
separate diff file to apply rather than as an edit already made.

**Foreclosed.** Genuine bidirectional database-file synchronisation, which is rare in practice
*because it does not work*.

**Accepted cost.** Two files still carry the round-trip risk, and `ruamel.yaml` is an extra
dependency bought specifically to preserve comments.

The mitigating fact is structural: single user, single machine, no concurrency. There are never two
simultaneous writers, so the failure mode is a lost decision rather than divergence — which is
exactly what the hash comparison catches.

## Alternatives considered

**Bidirectional sync for every config file**, as the requirement read literally. Rejected: it is the
version with the bugs, and the bug loses the applicant's own reviewed judgement.

**YAML as the only truth, database as a pure mirror.** Rejected: posting text, hashes and timestamps
have no business being hand-editable, and a mirror that can be edited is not a mirror.

**Field-level ownership across all files uniformly.** Rejected as more machinery than two
round-trip files need.

## Evidence

- `tbro` review, 2026-10-25: rated this hard and highest-risk relative to apparent size, and
  supplied the single-owner-plus-hash design and the `ruamel.yaml` note.
- Precedent for the safe form is well established: `terraform plan` / `apply`, `kubectl apply`,
  `pip-compile`, and `git add -p` are all generate-edit-reimport with a check. Bidirectional sync
  has no comparable precedent because it does not survive contact with real edits.
