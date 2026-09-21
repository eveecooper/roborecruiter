---
doc: product-overview
covers: [product intent, goals, limitations, restrictions]
pairs_with: 01-engineering-plan.md
---

# Product

> **What this is, and what it will not do.** Goals, honest limitations, and the restrictions the
> project accepts by design. How it gets built is [the engineering plan](01-engineering-plan.md);
> this document does not cover implementation.

An assisted job application pipeline. It finds front-of-house restaurant openings near a chosen
location, prepares the application materials, and hands the applicant the steps that require a
person.

- **Status:** planning. First build not started.
- **Pilot:** ZIP 94085, 5-mile radius, front-of-house roles (server, host, busser).
- **How it is built:** [engineering plan](01-engineering-plan.md)
- **Decisions:** [`docs/adr/`](../adr/)

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

- The system cannot submit. It prepares the application and stops.
- The first build does not fill forms for you at all. It gives you an application sheet with the
  files and prepared answers ready to copy. Assisted prefill of basic contact fields comes later,
  on specific approved portals, and still hands off before any challenge or submission.
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
- Overture data carries CDLA Permissive 2.0, Apache 2.0, and CC0 1.0 licenses depending on the
  contributing source. These require attribution if the data is redistributed.

### Application conduct

- One application per posting, enforced by the database. A second attempt happens only when the
  applicant presses Resubmit. Because the same opening can appear as two records that were not
  confidently matched, a second warning checks for a recent application to the same employer and
  role, which the applicant can override.
- Attestations, work authorization answers, and voluntary disclosures are answered by the
  applicant at submission.

### Content

- Materials draw only on confirmed facts. Unverifiable statements are flagged, never invented.
- Presentation is deliberately plain: standard sections, a standard font, and a layout applicant
  tracking systems parse reliably. The enforceable rules live in style profiles and are checked in
  code rather than left to habit.

### Privacy

- Knowledge files stay on the applicant's machine. Journals are excluded; an autobiography is
  allowed and is read only by fact extraction.

## Conclusion

The pipeline is deliberately split: automation handles discovery, filtering, and preparation,
where it is reliable and where most of the manual effort sits. The applicant handles judgment,
verification challenges, and submission, where automation is either blocked by design or too
fragile to trust. Every later capability, from writer models to preference learning to email
reading, attaches to that structure without changing it.
