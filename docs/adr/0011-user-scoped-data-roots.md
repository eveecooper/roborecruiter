# ADR 0011: User-scoped data roots, one database per user

- **Status:** accepted
- **Date:** 2026-10-26
- **Deciders:** EVC

## Context

"One applicant, one machine, local files" has been a standing non-goal since the first plan, stated
in the README, the build plan's non-goals, `CLAUDE.md` and the feature inventory. The reasoning was
that multi-applicant use would need isolation, authentication, hosting and per-employer rate limits
across applicants, all of which are genuinely out of scope for a local tool.

The owner then prepared the repository with a folder per user, loading one user's material for now
and prepping the rest. That contradicts the non-goal as written.

The two things being conflated are worth separating. **Path layout is nearly free. Multi-user
*operation* is not.** The expensive parts were never the directories — they are authentication,
enforced isolation, and rate limiting that has to reason about several applicants hitting the same
employer. None of those are implied by storing one person's files under their own folder.

Path layout is also in the same category as this project's other unretrofittable items: changing it
later means moving every file and rewriting every recorded path, including the file hashes stored
against sent applications.

## Decision

**A `--user` flag selects a data root. Each user gets their own directory and their own SQLite
database.**

```
users/<name>/
  knowledge/      every raw file, once - the single home for applicant material
  config/         profile.yaml, families.yaml, run.yaml, voice.yaml, styles/, employers.yaml
  applications/   one folder per application
  roborecruiter.db
```

A top-level config file names the default user, so the flag can be omitted in normal use.

**A file is stored once and given roles by a manifest, never duplicated into a second folder.** A
cover letter the applicant wrote is both raw material for distillation and a writing sample for voice
matching; `config/voice.yaml` names which `knowledge/` files serve the second role, keyed by document
type so a resume and a cover letter can draw on different registers. Copies drift and symlinks are a
portability problem, so neither is used.

**One database per user, not a `user_id` column.** Separate files give complete isolation at no
cost: no query can forget a filter, and nothing can leak between people even through a bug. A shared
database with a discriminator column would put a correctness obligation on every query in the
codebase, forever, in exchange for nothing this tool needs.

**A persona is not a user.** One person applying under different names, contact details or
headlines is a *presentation*, not a separate applicant. Personas live in a `personas:` mapping
inside that user's `config/profile.yaml`, and an application stores the resolved persona name on
its row so history survives a later config edit. Modelling personas as users would duplicate the
whole knowledge folder per persona and scatter one person's application history across several
databases, making "how many applications have I sent" unanswerable.

**Multi-user operation remains a non-goal**, narrowed to say what it actually excludes: no
authentication, no shared or hosted deployment, no concurrent use by different people, and no
rate limiting that reasons across applicants. The tool serves **one applicant at a time**.

## Consequences

**Easier.** Supporting a second person costs a directory. Isolation is structural rather than
enforced by discipline. Nothing is shared, so nothing can leak. Paths are settled before any file
has been written, which is the only cheap moment to settle them.

**Harder.** Every path in the codebase resolves through the data root rather than being relative to
the repository, so the root has to be threaded from the CLI into anything that touches disk. That is
one parameter, but it has to exist from step 1.0 rather than being introduced later.

**Foreclosed.** Any future feature that compares across users — shared employer rate limiting, a
pooled posting cache, cross-applicant analytics — would need either a shared database or a
cross-root reader. That is deliberate: those features are the non-goal.

**Accepted cost.** Overture data and fetched postings will be duplicated per user rather than shared.
At one-applicant-at-a-time scale this is disk space and nothing else.

## Alternatives considered

**Single user, collapse the folders.** Keeps the non-goal exactly as written and is simplest.
Rejected because the owner has already prepared for several people, and the path layout is the one
part of multi-user that is cheap.

**Shared database with a `user_id` column.** The conventional answer, and wrong here. It buys
cross-user queries this project has declared a non-goal, and charges for them with a filter
obligation on every query plus the permanent possibility of a leak through one missed `WHERE`.

**Full multi-user support** — accounts, enforced isolation, cross-applicant rate limits, eventual
authentication. Rejected: the largest single scope increase available in this project, and it
reverses a non-goal rather than narrowing it.

## Evidence

Owner's stated setup on 2026-10-26: folders already prepared per user, one user's material loaded.
No measurement; this is a layout decision made before any file exists, which is the correct time.

**What would test it.** If a second person is ever actually used, whether anything beyond the
directory needed to change. If shared employer rate limiting turns out to be necessary — because two
applicants crawling the same employers is rude regardless of isolation — then the separate databases
were the wrong call and this ADR is superseded rather than amended.
