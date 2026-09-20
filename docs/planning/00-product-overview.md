---
doc: product-brief
draft: 1
status: superseded
superseded_by: 01-engineering-plan.md
authoritative_for: [product intent, goals, limitations, restrictions]
---

# Product

> **Draft 1, superseded.** The original product brief, kept for product intent: goals,
> limitations, and the restrictions the project accepts by design. Its engineering specifics are
> stale - [the engineering plan](01-engineering-plan.md) is current, and the known conflicts are
> listed in [Superseded points](#superseded-points) below.

An assisted job application pipeline. It finds front-of-house restaurant openings near a chosen
location, prepares the application materials, and hands the applicant the steps that require a
person.

- **Status:** planning. First build not started.
- **Pilot:** ZIP 94085, 5-mile radius, front-of-house roles (server, host, busser).
- **Design reference:** [kickoff and engineering plan](https://claude.ai/code/artifact/a1c093ef-a47e-43d2-9d29-bb0d2ef5e93d)
- **Decisions:** `docs/adr/`

---

## Goals

### Primary goal

Automate every step of the job search that can be done reliably and within each site's rules, and
route the rest to the applicant at defined points: three review gates, any human-verification
challenge, and the final submit button.

The manual process this replaces is: search a map for restaurants, open each website, hunt for a
careers page, read postings, rewrite a resume, and apply. Searching and reformatting consume most
of that time and are the most automatable parts.

### Product goals

1. **Coverage.** Find openings across an entire area, not just the restaurants a person would
   think to check.
2. **Throughput.** Make volume applying practical, with the number of applications per run set by
   the applicant.
3. **Accuracy.** Produce materials that are factual, standard in format, and free of AI writing
   tells.
4. **Control.** Keep selection, wording, and submission under the applicant's authority.
5. **Extensibility.** Support new job types and new industries through configuration rather than
   new code.

### Success criteria for the first build

| Criterion | Target |
| --- | --- |
| Pilot run | A full scan of ZIP 94085 completes unattended and produces an application sheet |
| Employer coverage | At least 16 of 20 known local restaurants appear in discovery results |
| Careers page outcomes | Every employer ends in a recorded outcome; accuracy measured on a 30-employer hand-checked sample |
| Duplicate applications | Zero applications to the same posting without a deliberate Resubmit |
| Materials quality | Approved documents pass every style rule, and every claim traces to a confirmed fact |
| Applicant effort | Under 5 minutes per application, from opening the sheet to marking it submitted |

### Non-goals for the first build

- Submitting an application without the applicant pressing submit.
- Evading bot detection, solving CAPTCHAs automatically, or ignoring robots.txt.
- Automated access to Indeed or any source whose terms prohibit it.
- Supporting more than one applicant.
- Selecting, calling, or fine-tuning a language model.

---

## Limitations

What the system will not do well, and what it cannot know.

### Data

- Employer data comes from Overture Maps, which lists duplicates, a high junk rate, and low
  property completeness as known issues. Coverage in any given area is unverified until measured.
- Roughly four in five Overture place records originate with Meta, sourced largely from public
  Facebook pages. Businesses with no online listing presence are likely underrepresented.
- Some employers have no website in the data. They can only reach the walk-in list.
- Releases are monthly, so newly opened or closed businesses lag reality.

### Careers page detection

- Detection is heuristic. Websites differ in structure, and some render only in a browser.
- A block disguised as a normal page cannot be distinguished from a site with no careers page.
  Measured signals catch most blocks, not all.
- The miss rate is knowable only through the hand-checked sample, not from the system's own
  confidence.

### Postings

- Postings that exist only on job boards the system does not read will be missed unless the
  applicant adds them through manual intake.
- The same opening often appears in several places, so duplicate detection is a warning rather
  than a guarantee.

### Materials

- The first build has no writer model. Materials come from approved variants with safe fields
  filled per posting, not from per-posting drafting.
- Style rules reduce AI writing tells; they do not remove them. Concrete facts and the applicant's
  own writing samples do most of that work.
- Accuracy depends on the fact bank. Anything the applicant has not confirmed cannot be used.

### Application

- The system cannot submit. It prepares, prefills where allowed, and stops.
- Prefill covers standard contact fields only. Screening questions, attestations, and uploads on
  unfamiliar forms stay manual.
- Response tracking is manual until email reading is added.

### Scale

- One applicant, one machine, local files. Multi-applicant use would require isolation, hosting,
  authentication, and per-employer rate limits that are out of scope.

---

## Restrictions

Rules the system follows by design, not by preference.

### Access and compliance

- The crawler identifies itself honestly, obeys `robots.txt`, honors crawl delays, and rate-limits
  per domain.
- No proxy rotation, disguised browsers, or CAPTCHA-solving services. Challenges are handed to the
  applicant, who completes them in a visible browser session.
- Sources whose terms prohibit automated access receive none. Indeed enters only through manual
  intake, where the applicant pastes a link and description.
- A source policy holds allow and deny lists. Unlisted sources are shown for review and always
  handed off rather than prefilled.
- Overture data carries CDLA Permissive 2.0 and Apache 2.0 licenses, which require attribution if
  data is redistributed.

### Application conduct

- One application per posting, enforced by the database. A second attempt happens only when the
  applicant presses Resubmit.
- A daily cap limits how many applications a run may prepare.
- Attestations, work authorization answers, and voluntary disclosures are answered by the
  applicant at submission.

### Content

- Materials draw only on confirmed facts. Unverifiable statements are flagged, never invented.
- Style rules are enforced in code: no em dashes, en dashes, or ellipsis characters; no banned
  phrases; at most one series of three in prose; single-column layout; word limits.
- Documents use standard sections and a standard font. No tables, text boxes, columns, or icons.

### Privacy and secrets

- Knowledge files stay on the applicant's machine. Journals are excluded; an autobiography is
  allowed and is read only by fact extraction.
- No secrets in the repository. Credentials come from the environment, and any future OAuth scope
  is the narrowest that performs the task.

---

## Tech stack under consideration

Nothing here is locked in. Each choice is replaceable behind a port.

| Concern | Candidate | Notes |
| --- | --- | --- |
| Language | Python 3.12+ | |
| Employer data | DuckDB reading Overture GeoParquet | Query by bounding box straight from cloud storage; no API key |
| Web requests | httpx | Async-capable, with per-domain rate limiting |
| Browser automation | Playwright | Visible sessions for prefill and handoff |
| Page parsing | extruct, selectolax | Structured `JobPosting` data first, HTML parsing second |
| Records | SQLite through SQLModel | Job queue lives in the same database |
| Migrations | Alembic | |
| File store | Local disk, content-hash names | Page snapshots and generated documents |
| Documents | docxtpl | Word templates the applicant designs |
| PDF export | LibreOffice headless | Template font must exist on the conversion machine |
| Command line | Typer | One command per stage |
| Review console | Streamlit | Gates 1 and 2, application sheet, review list |
| Validation | Pydantic | Configuration, external data, and future model output |
| Logging | structlog | Run, job, and employer identifiers on every line |
| Testing | pytest with saved pages | Detection tested against real markup |
| Quality gates | ruff, mypy or pyright, import-linter, pre-commit | Layer boundaries enforced in CI |
| AI providers | Undecided | Tasks bind to model aliases in `config/models.yaml` |

---

## Still being considered

| Topic | Options | Current leaning | What settles it |
| --- | --- | --- | --- |
| Additional posting sources | Adzuna API; National Labor Exchange API; Brave Search API; third-party job data APIs; Google listings through scrapers | Careers pages only at first; trial Adzuna next; no Google scrapers | Unique postings each source adds beyond careers pages |
| Indeed workflow | Manual paste; a browser button that saves the posting being viewed; no Indeed use | Manual paste now | Review of Indeed's terms for applicant-initiated capture |
| Third-party job data APIs | Use for breadth; avoid because collection methods are unclear | Avoid until reviewed | Vendor documentation on how postings are gathered |
| Employer data fallback | Foursquare Open Source Places; Google Places API; OpenStreetMap | Decide after the coverage check | Pilot coverage result |
| Prefill in the first build | Basic contact fields; defer all prefill | Basic fields if the schedule holds | Number of distinct hiring platforms in pilot results |
| Model provider and models | Per task: request parser, fact extractor, resume writer, cover letter writer, reviewer | Decide after the first build ships | Output on fixed sample postings, scored against style rules and claim checks |
| Writer training approach | Examples and rules; fine-tuning | Examples and rules | Output quality on the same sample set |
| Pilot radius and volume | 5 or 10 miles; 20 or 40 applications per run | 5 miles, 20 applications | Posting counts from the pilot |
| Quality score inputs | Distance, role-match confidence, stars, pay, schedule | Distance, role-match confidence, stars | Gate 1 decision data |
| Walk-in list | Include employers without websites; drop them | Include | Applicant preference |
| Email reading | After the first build; never | After enough manual marks exist to measure accuracy | False-positive rate against manual marks |
| Review console | Streamlit; a custom web app | Streamlit | Usability during the posting milestone |

---

## Conclusion

The pipeline is deliberately split: automation handles discovery, filtering, and preparation,
where it is reliable and where most of the manual effort sits. The applicant handles judgment,
verification challenges, and submission, where automation is either blocked by design or too
fragile to trust. Every later capability, from writer models to preference learning to email
reading, attaches to that structure without changing it.

## Future tasks

### Next up

- [ ] Scaffold the repository: configuration schemas, data model, job queue, CLI, CI.
- [ ] Run the Overture query for ZIP 94085 and produce employer records.
- [ ] Compile a list of 20 known restaurants in the pilot area and measure coverage.
- [ ] Decide the pilot radius and the employer data fallback from that result.
- [ ] Build careers page detection with explicit outcome states and block signals.
- [ ] Hand-check 30 pilot employers to create the detection answer key.
- [ ] Build posting extraction, the front-of-house job profile, selection modes, and manual intake.
- [ ] Build the knowledge folder, fact bank, Word templates, PDF export, style linter, and claim check.
- [ ] Build the application sheet, application records, Resubmit, and manual response marking.

### Later feature pushes

1. Assisted sessions for the hiring platforms that appear most often in pilot results.
2. Resume and cover letter writer models, once a model is chosen.
3. Additional job profiles, starting with delivery driver.
4. Optional posting sources approved from the open questions above.
5. Preference learning from logged gate decisions.
6. Email reading that suggests response marks for confirmation.

---

## Superseded points

Draft 2 ([the engineering plan](01-engineering-plan.md)) revisited these specifics. Where this
document and draft 2 disagree, draft 2 is correct. This table is the complete list of *conflicts* -
draft 2 also adds material this brief simply predates (style-profile versioning, fact-bank
versioning, the source-identity split), which the precedence rule covers without listing.

| This brief said | Draft 2 decided | Where in draft 2 |
| --- | --- | --- |
| Prefill in the first build, "basic fields if the schedule holds" | Browser prefill is post-M6 and exposes no submit operation | Decision 22 |
| "Under 5 minutes per application" as a success target | A target that is measured and reported; overruns are recorded, not enforced | Budget semantics |
| "A full scan of ZIP 94085 completes unattended" | Completes without intervention **or** produces an explicit review / dead-letter outcome | Success criteria |
| "A daily cap limits how many applications a run may prepare" | `max_applications` is per-run; no daily cap exists | Selection and run budgets |

The tech stack and "still being considered" tables here are near-duplicates of draft 2's
equivalents and will keep diverging with each revision. They are retained because this is a
historical record. Consult draft 2 for the current answer.
