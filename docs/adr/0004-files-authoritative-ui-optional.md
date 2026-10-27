# ADR 0004: Files are authoritative; a UI is allowed only where it reduces required actions

- **Status:** accepted
- **Date:** 2026-10-26
- **Deciders:** EVC

## Context

The previous plan made a Streamlit review console a required deliverable of step 1.3 and the home of
Gate 2. The owner is a developer who interacts with this tool by editing files, and a console was
neither wanted nor, at one posting at a time, faster than opening a YAML file.

An early draft of the reset over-corrected into a flat prohibition on any user interface. The owner
rejected that too: a UI is fine where it makes the work shorter.

The operative rule is neither "no UI" nor "a console is required". It is **fewest required human
actions**.

## Decision

Files are the authoritative interface. Configuration, candidate facts, job families and styles are
YAML the applicant edits directly; records live in SQLite; generated documents live in folders.

**A user interface is permitted wherever it removes more human work than it costs to build, and
nowhere else.** It is never the system of record — anything a UI captures must be expressible in the
files or the database.

The first place a UI is pre-justified is stage 2's review pass, and only for a specific reason:
capturing a skip reason in one keystroke. Typing reason codes into YAML will not survive the
fortieth packet. That is a measurable action saving, not a preference.

## Consequences

**Easier.** Stages 1 through 4 have no UI to build, no server to start, and no rendering layer to
sanitize untrusted employer content into. Everything is diffable in git and inspectable in an
editor. A fresh agent can read the whole state of the system with file reads.

**Harder.** Any workflow that is genuinely awkward in a text editor stays awkward until someone makes
the case for a screen. Review of many items at once is the obvious candidate.

**Foreclosed.** The previous plan's framing of the review console as load-bearing infrastructure.
Streamlit drops out of the stack for stages 1–4 and returns as *proposed* only.

**Accepted cost.** The judgement "does this reduce required actions" has no mechanical test, so it
will be argued case by case.

## Alternatives considered

**Require a console, as the previous plan did.** Rejected: unwanted, and at low volume slower than a
file.

**Forbid any UI.** Rejected by the owner. It confuses the means with the end — the end is fewer
actions, and sometimes a screen delivers that.

**Terminal UI (Textual) rather than web.** Open. It would keep everything in the terminal and avoid a
server. Worth considering when stage 2's review pass actually needs the keystroke capture.

## Evidence

Owner correction during the 2026-10-25 session: a UI is allowed but not necessary, and the criterion
is least clicking, waiting and required action. No measurement; this is a stated preference and is
recorded as one.
