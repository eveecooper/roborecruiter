---
doc: build-plan
covers: [stages, architecture, seams, standards, feature inventory]
status: current
supersedes: 01-engineering-plan.md (deleted 2026-10-26, in git history)
open_items: 11-investigations.md
revision: 2026-10-26
---

# Build Plan

> **The document to follow.** Stages, architecture, and what "done" means for each step.
> Open questions and their briefs: [`11-investigations.md`](11-investigations.md). Specifications
> stages 3 and 4 need, plus the six-outcome enum: [`13-discovery-notes.md`](13-discovery-notes.md).
> Which feature lands when: [`12-feature-inventory.md`](12-feature-inventory.md).
> Why things changed: [`03-review-log.md`](03-review-log.md), then [`../adr/`](../adr/).
> An ADR outranks this document on the single decision it records.

**Stage 1 ships no model and no network code**, both asserted in CI. Paste a posting, a Word
template fills from `config/profile.yaml`, edit the document freely, the terminal walks you through
sending it, and the record stores the hash of the file that went out.

`config/profile.yaml` is AI-generated from day one — in conversation, not in code. The applicant
hands over old resumes and notes, Claude writes the YAML, the applicant corrects it. `rr distill`
becomes a re-runnable feature in stage 5, where a growing knowledge folder justifies the cost
controls and injection defenses it brings.

Everything after stage 1 is ordered by what is cheapest to get right: repeat-run bookkeeping, then
one permitted fetching source, then discovery, then the model work.

## Decisions

Each is recorded as an ADR; this table is the index.

| # | Decision | ADR |
| --- | --- | --- |
| A | Generated documents are hand-editable; the applicant supervises by reading the folders. | [0002](../adr/0002-hand-editing-allowed.md) |
| B | The run never halts for a human. Anything uncertain proceeds with a flagged guess. | [0003](../adr/0003-batch-over-gates.md) |
| C | Files are authoritative. A UI is allowed only where it reduces required actions. | [0004](../adr/0004-files-authoritative-ui-optional.md) |
| D | Stage 1 ships no model and no network code, both mechanically asserted. | [0005](../adr/0005-stage1-no-model-no-network.md) |
| E | Every fetch waits for the source-policy ADR, structured board APIs included. | [0006](../adr/0006-every-fetch-waits-for-source-policy.md) |
| F | Posting sources are capability-tagged against one query object, not a mode/adapter matrix. | [0007](../adr/0007-capability-tagged-posting-sources.md) |
| G | Matching splits into eligibility, fit and preference. The gate is three clauses, not one float. | [0008](../adr/0008-eligibility-fit-preference.md) |
| H | One owner per file. Only `inbox.yaml` and `employers.yaml` round-trip. | [0009](../adr/0009-one-owner-per-file.md) |
| I | Browser form fill stays gated by Investigation C. | [0010](../adr/0010-defer-browser-prefill.md) |
| J | Data is user-scoped: one directory and one database per user. Multi-user *operation* stays a non-goal. | [0011](../adr/0011-user-scoped-data-roots.md) |

ADR 0001 remains accepted on the one point it settles: apply before discover, and manual intake is a
posting source rather than a special case. Its three-phase scheme is replaced by the six stages here.

## Shape

**Everything lives under a user-scoped data root** ([ADR 0011](../adr/0011-user-scoped-data-roots.md)).
One directory and one database per user; `--user <name>` selects it, and a top-level config names the
default so the flag can be omitted.

```
rr.yaml                 top-level: default user, nothing else
users/<name>/
  config/
    run.yaml              shared defaults, limits, caps, area   ← the only place a ZIP appears
    run.{dev,demo,prod}.yaml  profile overlays
    profile.yaml          facts + personas         ← human-owned
    families.yaml         job families + tailoring depth   ← human-owned
    styles/<id>.yaml      template, tone, page limit       ← human-owned
    employers.yaml        source-neutral; hand-written, generated in stage 4 (round-trip)
    models.yaml           per-task model aliases (stage 5)
    voice.yaml            writing samples per document type            ← human-owned
  knowledge/            every raw file, once. The single home for applicant material.
  applications/<id>/    posting.md, tailored.yaml, resume.docx, cover.docx, PDFs
  inbox.yaml            review file (stage 2, round-trip)
  roborecruiter.db      SQLite + Alembic — tool-owned, authoritative
```

**One folder, declared roles — no file is ever duplicated.** A cover letter the applicant wrote is
both raw material and a writing sample, so rather than copying it into a second folder,
`config/voice.yaml` names which `knowledge/` files are samples. Paths, not copies: editing the file
updates both uses, and there is no second copy to drift.

The manifest is **keyed by document type first, then by variant name** — `resume.default`,
`cover_letter.default`. Those are different registers (terse verb-first bullets with no first person,
versus first-person prose), so one shared sample set would pull both toward the wrong voice. A style
profile names a single variant and the curator looks it up under whichever document type it is
writing.

The same principle applies to anything else that needs a role: add a manifest in `config/`, never a
parallel directory.

### Personas

**One person, several presentations.** Contact details and headline vary by what the role is - a
front-of-house application and a backend application may use different cities, different contact
addresses, and a headline on one and none on the other. The underlying facts never vary.

Personas live in `config/profile.yaml` under a `personas:` mapping, with `default_persona` naming
the fallback. An application resolves exactly one and **stores the resolved name on its row**, so
history survives a later config change.

A persona is **not** a user. Users are different people with separate data roots and separate
databases ([ADR 0011](../adr/0011-user-scoped-data-roots.md)); personas are one person's
presentations and share everything else. Splitting personas into users would duplicate the whole
knowledge folder and scatter one person's application history across several databases.

A persona carries only: `name`, `email`, `phone`, `location`, `headline`. Anything else that
varies by role belongs to the job family or the style profile, not here.

| Command | Stage | Does |
| --- | --- | --- |
| `rr add <url> [text] [--job-id]` | 1 | paste posting text → `posting.md` + a posting row with full text and the employer's own posting ID. Interactive paste by default, no file needed. No fetching. |
| `rr draft [--all] [--mode] [--persona]` | 1 | fill template from profile → `.docx` → `.pdf` |
| `rr submit [--all]` | 1 | terminal walkthrough: opens the posting, prints paths and copy-ready answers, records channel, elapsed time, file hashes |
| `rr log` / `rr effort` | 1 / 2 | what was sent; where the minutes went |
| `rr inbox [--apply]` | 2 | generate the review file; reimport edits with a conflict check |
| `rr fetch` | 3 | permitted posting sources, within the policy ADR |
| `rr discover` | 4 | Overture place source → `employers.yaml`; careers-page checks |
| `rr distill` | 5 | per-file extraction from `knowledge/` → a proposed diff to `profile.yaml` |

Every command takes `--user <name>`, defaulting to the user named in `rr.yaml`, and
`--profile dev|demo|prod`, defaulting to `prod`.

## Seams

Module boundaries in one process. A service split buys nothing here — no independent scaling,
deploy, or language mix — and costs serialization and cross-wire debugging. The one justified
separate process is the eventual browser worker, because it makes "exposes no submit" a
process-level claim rather than a code-review claim.

| Seam | Interface | Note |
| --- | --- | --- |
| Place source | `iter_places(area) -> Iterable[PlaceRecord]` | Keep `employers.yaml` source-neutral or its shape leaks Overture |
| Posting source | `fetch(q: PostingQuery) -> list[Posting]` | Capability-tagged; see ADR 0007 |
| Careers check | `check(employer) -> Outcome` | Six-outcome enum. Persists as an append-only row, never a column. |
| Curator | `tailor(profile, posting) -> TailoredDraft` | Quick-apply is a null implementation behind this |
| Matcher | `match(posting, profile) -> Match` | Two rule checks plus one model call; see ADR 0008 |
| Renderer | `render(draft, template) -> paths` | The field allowlist lives here |
| Submit walkthrough | — | No interface. One implementation that may never get a second. |

**Excluded as premature:** adapter registries, plugin entry points, DI containers, import-linter.

### Discovery: one query, capability tags

```python
@dataclass(frozen=True)
class PostingQuery:
    titles: tuple[str, ...] = ()
    area: Area | None = None
    employers: tuple[EmployerRef, ...] = ()
    posted_since: date | None = None


class Capability(Enum):
    SEARCH_BY_TITLE
    SEARCH_BY_AREA
    REQUIRES_EMPLOYER_REF
```

A discovery "mode" is a pure function `config -> PostingQuery`, plus a router selecting sources whose
capabilities satisfy the query. No registry, no mode classes. Greenhouse, Lever and Ashby are
`{REQUIRES_EMPLOYER_REF}` and nothing else; an aggregator would be `{SEARCH_BY_TITLE,
SEARCH_BY_AREA}`. Overture populates no cell — it is a place source, not a posting source.

## Ten things that are cheap now and unretrofittable later

Nine are data, one is layout. Each is something that cannot be backfilled without rewriting records
that already exist.

1. **Version stamps on every generated row** — `profile_version`, `prompt_version`, `model_alias`,
   `output_schema_version`. Without them a 0.72 in March and a 0.72 in October are different
   measurements wearing one label, and a response cache silently reuses a stale schema shape.
2. **Full posting text persisted**, not a hash and URL. It is stage 5's corpus.
3. **Per-posting family assignment history**, stamped with the frozen `families.yaml` version at the
   moment of assignment. Stable family IDs are necessary and not sufficient: without this there is
   no held-out set to measure clustering against.
4. **`careers_check` as append-only rows** — employer, checked_at, url, outcome, detector_version.
   As a `latest_outcome` column it collapses three facts into one: not checked yet, checked and
   nothing open, checked and unreachable. Rows also make churn visible and give Investigation A its
   denominator.
5. **A source-neutral `employers.yaml`.**
6. **`schema:` integers in every config file**, checked at load, refusing rather than mis-parsing.
   Alembic migrates tables; nothing migrates YAML, and this field is the whole defense.
7. **The resolved application mode on each application row**, or effort reporting can never compare
   quick-apply against deep tailoring.
8. **`content_hash` and per-row `updated_at`** on anything that round-trips through a file.
9. **The user-scoped data root**, threaded from the CLI into anything that touches disk. Changing the
   layout later means moving every file and rewriting every recorded path, including the hashes
   stored against already-sent applications.
10. **The employer's own posting ID** — `source_posting_id`, the number the hiring system uses for
    this opening (IBM's `132846`, Greenhouse's `gh_jid`). It is the only duplicate key that is
    stable when a URL is rewritten and the posting text is edited, and it is what makes
    "have I already applied to this exact requisition at this employer" answerable. Backfilling it
    means revisiting every posting by hand, so it is captured at intake even though nothing enforces
    it until stage 3. Scoped per employer, because a job ID is unique only within one hiring system.
    It lives on the posting row in stage 1 and migrates into `PostingSourceRef`
    ([`13-discovery-notes.md`](13-discovery-notes.md)) when stage 3 gives one posting several sources.

## Matching

Two rule-based checks plus one model call. Not three calls, not one call with three fields.

**Eligibility is rules** — work authorization, required certifications and licences, hard radius,
hard pay floor. A model deciding eligibility is unauditable and is the softest target for
score-manipulation injection. **Preference is also rules** — commute, schedule and pay band are
weights from a file the applicant wrote. **Fit is the one that needs a model**, as one call returning
a band and reasons with spans.

```python
class Blocker(BaseModel):
    rule_id: str
    detail: str
    source_span: Span | None


class Reason(BaseModel):
    claim: str
    posting_span: Span
    fact_id: str | None


class Eligibility(BaseModel):
    status: Literal["eligible", "ineligible", "unknown"]
    blockers: list[Blocker]


class Fit(BaseModel):
    band: Literal["strong", "plausible", "weak"]
    reasons: list[Reason]


class Preference(BaseModel):
    score: float
    contributions: list[tuple[str, float]]


class Match(BaseModel):
    family_id: str
    eligibility: Eligibility
    fit: Fit | None
    preference: Preference
    override: Override | None
    prompt_version: str
    model_alias: str
    output_schema_version: int
```

The gate is three clauses: eligibility not `ineligible` (hard veto; `unknown` proceeds flagged),
fit band at or above a configured ordinal minimum, preference at or above a float floor. A scalar
may be computed for ordering *within* the passing set — store it, never gate on it, and never let the
model produce it.

**The clauses arrive in two stages.** Eligibility and preference are rules and ship in stage 4. Fit
needs a model and ships in stage 5, so between them the gate evaluates two clauses with `fit` absent
and lets a posting through flagged. `Fit` is optional from the start.

**Two honesty notes.** Eligibility rules need structured facts like "must be authorized to work
without sponsorship", and those exist only as free prose — so a model extracts them and the rules
evaluate the extraction. The deterministic check inherits the extractor's recall. And "interpretable
reasons" is assertable only as *every reason resolves to a span in the posting and a fact ID in the
profile*; that the reason is the model's actual reason is not assertable.

## File ownership and the review round-trip

| Owner | Files / data | Rule |
| --- | --- | --- |
| Human | `run*.yaml`, `profile.yaml`, `families.yaml`, `styles/*.yaml` | YAML is truth. The tool reads and never writes them. Proposals go to a separate diff file the applicant applies. |
| Tool | posting text, file hashes, timestamps, channel, submit seconds, scores, source refs, `careers_check` rows, `model_calls` | The database is truth. Appears in YAML only inside a generated read-only block. |
| Both | `inbox.yaml`, `employers.yaml` | Generate-then-reimport, never sync. |

Conflict detection is two columns and one comparison. When the tool writes a round-trip file it
records the file's `content_hash` and the `updated_at` of every contributing row. On `--apply`:
unchanged hash means skip; changed hash means apply **only human-owned fields** (`status`,
`skip_reason`, `family_id`, `mode_override`, `notes`, hand-entered `careers_url`); a human edit to a
tool-owned field is **refused with a message, never silently ignored**; any contributing row newer
than the file's generation timestamp writes `inbox.conflict.yaml` with both values side by side and
applies nothing for that row.

Use `ruamel.yaml` for round-trip files so the applicant's comments survive a regenerate.

## Safeguards

**Migrations — stage 1, Alembic.** SQLite's `ALTER TABLE` cannot drop or retype a column, so a
hand-rolled version table means writing the 12-step rebuild per change; `batch_alter_table` already
implements it and `--autogenerate` reads the SQLModel definitions. Early for a narrow reason: until
the first real submission the database can be deleted and recreated, but the row holding a sent
file's hash cannot be regenerated — and that lands inside stage 1.

**Cost and caching — stage 5.** Cache key
`sha256(task, model_alias, prompt_version, profile_version, output_schema_version, posting_text_hash)`,
stored in a `model_calls` table. Never invalidated: content-addressed, so any change is a miss by
construction. `--no-cache` flag, prune by age, never cache a failed or retried call.

Cost at 20 postings per run (~60K in, ~20K out), verified 2026-10-25: Haiku 4.5 ~$0.16, Sonnet 5
~$0.32, Opus 5 ~$0.80, Fable 5 ~$1.60. **Drafting is cheap enough that cost limits are a bug guard,
not a budget.** The real exposure is `rr distill`, whose input is unbounded. Limits in order of what
works: a hard per-run call cap, then a cumulative dollar ceiling aborting mid-run, then a
`count_tokens` dry-run for distill only.

**Injection — one assertion in stage 1, the suite in stage 5.** Posting text from a stranger enters
the same prompt as the private profile, and the output becomes a document sent to a stranger.
Defenses by value: a closed output schema plus a render-time field allowlist plus Jinja2 autoescape
(`docxtpl` is Jinja2, making template injection the one attack with a mechanical rather than a
persuasion exploit); provenance as a hard reject for objective fields; a deny-set substring check
against the non-selected private subset; instruction/data separation (free, guarantees nothing).
Asking a model to detect injection is recursive and unmeasurable — skip it.

The suite is 15–25 hostile `posting.md` fixtures asserted against the resulting structured object,
never the `.docx`. It can assert schema validity, no deny-set string, every objective claim
resolving to a fact ID, no surviving Jinja2 delimiters, bands in range. **It cannot assert that the
model ignored the instruction** — that is a compliance rate at a pinned `model_alias`, a tracked
number rather than a red test. The fixtures double as the model-swap regression set.

Stage 1's share is one assertion: posting text is data everywhere, never concatenated as
instruction, never into a path, filename, or shell argument.

**Secrets.** Credentials from the environment, never the repository. `knowledge/`,
`config/profile.yaml`, `applications/`, `inbox.yaml` and the database are all gitignored. From stage
5, `rr draft --explain` prints exactly what text goes to which model.

## Two application modes

Deep tailoring subsumes quick-apply. Quick-apply is the deep path with cover-letter fields empty and
the curator call replaced by a copy of the profile's standard fields — a **null curator behind the
`tailor()` seam**, not a second pipeline. Schema unchanged, provided cover-letter fields are
`Optional`. Renderer unchanged, provided the template comes from `style_id`.

Decided as a per-family default in `families.yaml`, overridable per posting at `rr add`, with
`--mode` on `rr draft` for a batch. The **resolved** mode persists on the application row.

Stage 1 is quick-apply, because it has no model — so the template path never becomes dead code.

Worth stating plainly: quick-apply makes *drafting* cheap, and drafting was never the bottleneck.
`submit_seconds` is.

## Stages

### Stage 1 — First real application

**No model. No network.** Both asserted in CI.

| Step | Deliverable | Exit criteria |
| --- | --- | --- |
| 1.0 | Repo, ruff, pytest, SQLModel + Alembic initial revision, the nine unretrofittable items, persona resolution, six-outcome enum, `schema:` loader check, config profiles, gitignore | CI green. Three assertions pass: no submit-capable path; no `httpx`/`requests`/`playwright` import; posting text never used as instruction, path, filename or shell argument. `alembic upgrade head` applies to an empty database. |
| 1.1 | `rr add`: paste URL + posting text → `posting.md` and a posting row with full text and the employer's posting ID. Batchable. **One command and one paste** — no intermediate file, and the job ID, title and employer are read out of the pasted text by rules where the posting labels them. | Several pasted postings are on disk and in the database. Re-pasting the same posting does not create a second one, caught by employer-plus-job-ID first, then URL, then text hash — so it holds even when the URL is rewritten and the text is edited. Adding a posting costs one command, one paste and one end-of-input keystroke, with no `--job-id` or `--title` typed when the posting labels them. |
| 1.2 | `rr draft [--all]`: template fill from `config/profile.yaml` via docxtpl, pinned LibreOffice → PDF, render-time field allowlist, Jinja2 autoescape | A posting renders to `.docx` and `.pdf`. A field not declared by the template is refused. An edited file is never overwritten — `.v2` is written instead. |
| 1.3 | `rr submit [--all]`: terminal walkthrough; records channel, elapsed time, and the hash of each file sent. `rr log`. | **One real application sent end to end, with `rr log` naming the hash of the file that went out.** |

Effort *statistics* wait for Investigation G; stage 1 records the raw numbers without reporting
distributions.

### Stage 2 — Repeatable, still offline

`inbox.yaml` with statuses, in-place corrections, and skip reasons as an enum — without a reason a
skip is uninterpretable, since postings get skipped for commute, pay, schedule and
already-applied, and only "the score was wrong" is a scoring label. Several hand-written families
with tailoring depth. Duplicate prevention. Closed and stale handling, and a new-since-last-run
view. The file-ownership rules and conflict check above. Family assignment history accumulating.

**Exit criteria.** Repeated runs lose no tracking state and never re-present prior decisions. A hand
edit to a tool-owned field is refused with a message. A stale contributing row produces
`inbox.conflict.yaml` and applies nothing for that row. Comments survive a regenerate.

A new-since-last-run view is not optional polish: without it, run two re-presents run one and the
tool's value falls off after the first use.

### Stage 3 — Source policy, then the first fetch

| Step | Deliverable | Exit criteria |
| --- | --- | --- |
| 3.0 | **Source-policy ADR, from Investigation D answered** — crawler identity, robots-versus-terms precedence, whether third-party page snapshots may be retained | The ADR exists. **Nothing in 3.1 may run before it does.** |
| 3.1 | `PostingSource` + `PostingQuery` + capability router. One or two sources chosen from the Investigation E census, within policy. Cross-source dedupe. | New postings arrive without hand-pasting, and every fetch traces to a clause in the ADR. Rate caps and robots.txt obedience asserted against a local test server. |

**Decide deliberately.** ATS endpoints are per-board and need an employer reference — they are not
search engines, so title search over them is a fan-out across an employer list already maintained.
Candidate cross-employer sources, **all unverified and all subject to 3.0**: CareerOneStop and the
National Labor Exchange (US Department of Labor, free token, aggregates state workforce agencies,
likely the broadest permitted index); USAJOBS (federal only); Adzuna (free tier, attribution terms).
Google for Jobs has no public search API. Indeed is denied for direct access; a third-party route is [Investigation H](11-investigations.md), open and a last resort. Expect title-based discovery
to work better for software roles than for local hourly work — this stage may make the reach-goal
vertical viable before the restaurant one.

### Stage 4 — Discovery

Overture behind `iter_places` → a source-neutral `employers.yaml` the applicant prunes.
Careers checks persisted as append-only rows against the six-outcome enum. Distance and
compensation filters. The match gate, so filtering precedes generation.

**The gate is partial here.** Eligibility and preference are rules and work; fit needs a model and
does not arrive until stage 5, so the gate runs two clauses and lets postings through flagged.
Family assignment is by hand or by title rules until stage 5.

**Exit criteria.** The tool regularly surfaces openings the applicant did not find. A second check
of the same employer appends a row rather than updating one. **Investigation A reopens here.**

**Scope risk.** Careers-page extraction across arbitrary small-business sites has no bounded effort
estimate. If it drags, cut detection and let `employers.yaml` carry hand-pasted careers URLs.

### Stage 5 — Model-assisted curation

One typed `call(task, output_model, inputs)` site via `instructor` or `pydantic-ai`, with per-task
aliases in `models.yaml` — the clusterer reads an unbounded corpus while the scorer and curator see
one profile and one posting, so a single global alias is wrong.

**`rr distill`, bounded.** Per-file extraction (one call per file, `list[Fact]` with path and
byte-span provenance, a per-file byte cap, oversize files chunked deterministically or refused —
never silently truncated). Deterministic merge, deduping by normalized text with no model. Three hard
caps in `run.yaml`: max files, max bytes per file, max calls per run. A `count_tokens` dry-run that
aborts rather than warns. Output is a **proposed diff** against `profile.yaml`, never a direct write.

**Posting field extraction by model.** Stage 1 reads a posting's title and job ID from the labels
the posting prints, by rule. That is cheap and it misses an unlabelled posting. Here a model
extracts the structured fields — title, requisition ID, location, pay band, schedule, required
certifications — into a closed schema with spans back into the text. It is the same extraction
[ADR 0008](../adr/0008-eligibility-fit-preference.md) already depends on for eligibility, which is
why it belongs in this stage rather than earlier: it arrives with the output schema, the field
allowlist, the response cache and the hostile fixtures that make a model's output safe to act on.
The rule-based reader stays as the fallback and as the comparison that says whether the model is
worth its cost.

Then fit scoring, family clustering as a proposed diff with stable IDs, response caching, call cap
and dollar ceiling, the full injection suite, style profiles, parallel drafting, and a profile prune
step — edits add claims and nothing removes them, so the call designed to stay small grows
monotonically without one.

**Voice matching.** `config/voice.yaml` names which `knowledge/` files are writing samples, keyed by
document type then variant (`resume.default`, `cover_letter.default`). The curator receives the
matching files as **few-shot examples** — examples placed in the prompt for the model to imitate.
**Resume and cover letter get separate sets** because they are different registers; sharing one
pulls both wrong. Editing the manifest changes the voice: no training run, no stored weights, nothing
duplicated, and it survives a model upgrade untouched. **Fine-tuning stays out of the plan**: it needs
far more material than one applicant produces, costs money per run, goes stale when the base model is
replaced, and cannot be reverted cheaply.

**Exit criteria.** Review and editing effort per application falls without document quality slipping.
The hostile-fixture suite passes its deterministic assertions, with the compliance rate *reported*
at a pinned `model_alias` rather than asserted. A cached call with a changed `output_schema_version`
misses rather than returning a stale shape. `rr distill` aborts on a `count_tokens` estimate over the
configured cap, before the first paid call.

**How clustering gets measured, honestly.** The family diff is free and descriptive — families
proposed, merged, split, unchanged. Adjusted Rand Index over *posting* partitions, hand-assigned
versus clustered, answers "how different", never "which is right". The one real measurement is a
blind comparison: both family sets produce profiles, both draft the same held-out postings, and the
applicant picks the better output with the family-set ID hashed out of the filenames. Report it as a
preference rate with a wide interval — at n=20, roughly ±20 points.

**Scoring feedback is calibration against the applicant's own judgement, not accuracy.** Only
postings past the gate get judged, so the label set never contains false negatives, and employer
replies are too sparse and silent to supply ground truth.

**Skill-gap report.** Each `Fit.reasons` entry already carries a claim, a span into the posting, and
whether that claim resolved to a fact ID in the profile — so **an unresolved claim is a labelled
gap.** Aggregating them across accumulated postings is a group-by, not a model call: "14 of 20
`backend` postings wanted Kubernetes; the profile has no Kubernetes claim." Every row traces to a
real posting, which is what makes it worth reading rather than generic.

Break it down by family, and by whether the posting was applied to or skipped — a gap appearing only
in postings already skipped for other reasons is not worth acting on.

### Stage 6 — Evidence-gated

Email-response tracking, follow-up reminders, an optional web interface, a local API. Browser
prefill **only** if Investigation C clears it — its hostile-form suite and its ruling on
employer-visible partial applications are the gate — and only if `channel` data shows one portal
carrying real volume. Multi-applicant support stays a standing non-goal, not a late feature.

**Career coaching plan.** Turning stage 5's gap report into "here is what to go do about it" needs a
model, and that output is **unverifiable**: career advice is generic by default and is the feature
most likely to feel valuable while saying nothing. Build it only if the deterministic report proves
insufficient on its own, and report it as suggestion rather than assessment.

Build only what measured volume and recorded minutes justify.

## Non-goals

**This section is the single home for why something is excluded.**
[`12-feature-inventory.md`](12-feature-inventory.md) records *that* a feature is out and points
here for the reason.

These hold in every stage.

- **No code path that can submit an application.** CI asserts no adapter exposes a submit,
  click-to-submit, or form-post operation. It is the only mechanical guarantee behind the project's
  hardest rule; everything else would be discipline.
- **No bot-detection evasion, CAPTCHA solving, or proxy rotation.** Challenges go to the applicant,
  who completes them in a visible browser session.
- **No direct automated access to Indeed**, or to any source whose terms forbid it. Indeed enters by
  pasting a link and description, which already works. Running an open-source scraper locally is
  direct access with extra steps and is covered by this rule, not an exception to it.
  **Whether a third party can supply Indeed-sourced postings lawfully is
  [Investigation H](11-investigations.md)** — open, and a last resort by the owner's explicit
  framing: it is considered only after stages 3 and 4 show the permitted sources yield too little.
- **No claim in generated materials that does not trace to a confirmed fact.** Unverifiable
  statements are flagged, never invented.
- **No fine-tuning of a model on the applicant's writing.** It needs far more material than one
  applicant produces, costs money per run, goes stale when the base model is replaced, and cannot be
  reverted cheaply. Templates, style profiles and few-shot examples selected by `config/voice.yaml` instead — cheaper,
  reversible, and they survive a model upgrade.
- **No services architecture.** Separate processes buy nothing here — no independent scaling, deploy,
  or language mix — and cost serialization and cross-wire debugging. Modules in one process. The
  stage 6 browser worker is the one exception, justified because it makes "exposes no submit" a
  process-level claim rather than a code-review claim.
- **No approval gate that halts the pipeline.** Replaced by flagged guesses
  ([ADR 0003](../adr/0003-batch-over-gates.md)); halting is the rhythm being designed away.
- **No multi-user *operation*.** Data is user-scoped and a second person costs a directory
  ([ADR 0011](../adr/0011-user-scoped-data-roots.md)), but there is no authentication, no shared or
  hosted deployment, no concurrent use by different people, and no rate limiting that reasons across
  applicants. The tool serves one applicant at a time.
- **No scheduler or background service.** Rejecting it kept a durable job queue and process
  supervision out of the build. Once stage 3 exists, an operating-system scheduled task calling
  `rr fetch` is a configuration step, not code.
- **No fourth environment.** Three config profiles, not four: the fourth would be UAT, where someone
  other than the developer validates a release, and on a single-applicant tool the owner is both
  people. An unexercised config path is a liability rather than a safety net.

## Feature inventory

See [`12-feature-inventory.md`](12-feature-inventory.md) for every requested feature and the stage
it arrives in.

## Engineering standards

See [`../agent/coding-standards.md`](../agent/coding-standards.md). Summary: configuration over
code; one module per concern and one seam per swappable thing; config profiles rather than branches;
tests at the seam with a fake per seam; structured logs carrying run, posting and application
identifiers; readable over clever.

## Open and unverified

**Open investigations** and what each gates: [`11-investigations.md`](11-investigations.md).

**Two scoped decisions still outstanding**, neither blocking stage 1. Walk-in and instructions-only
employers produce no Posting, so two of the six careers-page outcomes currently have no destination —
this was an open question in the previous plan and was deliberately not carried into this one. And
of the filters named during planning, only distance and compensation are scoped; schedule, seniority
and remote/hybrid are unspecified.

**Unverified facts this plan depends on.** Nothing replaced the matching spike deleted with the old
plan, so stage 4's gate arrives unmeasured with three times the surface of the old single score.
Every cross-employer job source named in stage 3 is unverified until an endpoint is actually called.
The Overture schema and taxonomy move on separate cycles and have not been re-checked. Model prices
were verified 2026-10-25 and move.
