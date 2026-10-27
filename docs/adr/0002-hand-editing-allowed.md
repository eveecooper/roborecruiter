# ADR 0002: Generated documents are hand-editable

- **Status:** accepted
- **Date:** 2026-10-26
- **Deciders:** EVC

## Context

Decision 34 of the previous engineering plan forbade hand-editing a generated application document.
The applicant was to change a fact or a template and regenerate.

The stated reason was claim provenance. The actual reason is recorded in the investigation brief
that the rule was protecting: draft 2 of the plan required every objective factual claim in every
document, *including applicant-edited ones*, to trace to a confirmed fact. Verifying that in free
prose means extracting claims from English, which needs a language model that Phase 1 explicitly
refused to use. The criterion was therefore untestable as written.

Investigation F's brief says so plainly: the failure the brief existed to prevent was "prevented by
removing the criterion's subject rather than by answering the question"
(`../planning/11-investigations.md`, Investigation F).

Separately, the rule made the tool worse at its only job. A wording change the templates did not
anticipate required a template change.

## Decision

Generated documents are hand-editable at any point. Provenance is **advisory**, not enforced:
generated fields carry a source, content the model inferred rather than found is flagged at review
time, and nothing locks or invalidates.

The renderer records each file's content hash. If the applicant has edited a file, a re-render
writes `resume.v2.docx` rather than overwriting it. The application record stores the hash of the
file actually sent.

## Consequences

**Easier.** The applicant can fix wording without changing a template. Generated material becomes a
draft rather than a final artifact, which is what it always was in practice. The approval-versioning
machinery — approvals bound to document hashes, style-profile versions, posting snapshots and
fact-bank versions, invalidating on any upstream change — is no longer needed, and it was
substantial.

**Harder.** Nothing structurally guarantees that an edited document contains only confirmed claims.
The applicant supervises by reading, which is a weaker guarantee than the one withdrawn.

**Foreclosed.** The claim that every objective assertion in every shipped document traces to a
confirmed fact. That claim is withdrawn rather than reinterpreted. The narrower claim that survives:
every claim in *generated* text is structurally bound to a source, and the record identifies exactly
which file was sent.

**Accepted cost.** A fabricated claim introduced by hand can reach an employer. The mitigation is
that the applicant wrote it and can see it, which is how every manually written application already
works.

## Alternatives considered

**Keep regenerate-only.** Preserves structural provenance absolutely. Rejected: it exists to protect
an untestable criterion, and the rigidity is a real cost paid every time a template does not
anticipate a sentence.

**Whole-document attestation.** Diff an edited render against the approved one and require the
applicant to attest to the whole document. Rejected as ceremony — the applicant edited it, so the
attestation adds a click and no information.

**Span-level claim detection.** A detector flags high-risk tokens (dates, durations, numbers,
employer names, titles, certifications) that do not match a confirmed fact. Deferred, not rejected:
it is worth building only if Investigation F measures its coverage as worth having, because a
detector that catches some claims and misses others invites more trust than it earns.

## Evidence

- Investigation F's own note, which records that the criterion could not be met or tested and that
  the previous draft resolved it by deleting its subject.
- The previous plan's step 1.3 exit criteria, which bound a Gate 2 approval to four separate
  versioned inputs — machinery that existed to serve the withdrawn criterion.

**What would test this.** If hand-edited documents in real use turn out to contain claims the
applicant did not intend, the advisory model is insufficient and whole-document attestation becomes
the fallback. Investigation F remains open and is the prerequisite for anything stronger.
