---
doc: discovery-notes
covers: [careers-page outcomes, block detection, discovery accounting, Overture source facts]
status: current
pairs_with: 10-build-plan.md
revision: 2026-10-26
---

# Discovery Notes

> **Specifications that stages 3 and 4 need, and the one enum step 1.0 needs.** Extracted from the
> superseded engineering plan when it was deleted; everything here was verified on 2026-09-20 unless
> marked otherwise, and the Overture facts move. How it gets built:
> [`10-build-plan.md`](10-build-plan.md). What gates it: [`11-investigations.md`](11-investigations.md).

## Careers-page outcomes — the six-outcome enum

**Step 1.0 defines this enum**, though nothing implements it until stage 4. Each employer check
produces exactly one outcome, persisted as an append-only `careers_check` row.

| Outcome | Meaning | Next step |
| --- | --- | --- |
| `PORTAL_FOUND` | Careers page or hiring platform identified | Postings extracted |
| `INSTRUCTIONS_ONLY` | Site says to email or apply in person | No Posting produced — **see the undecided item below** |
| `NONE_FOUND` | Site loaded normally, no hiring signals | Included in periodic spot checks |
| `UNCERTAIN` | Hiring language without a usable link, or page rendered empty | Review list |
| `BLOCKED` | Refused request, challenge page, or `robots.txt` disallow | Review list |
| `UNREACHABLE` | Timeout, server error, or missing domain | Retried twice, then listed |

**Undecided:** `INSTRUCTIONS_ONLY` and employers with no website produce no Posting, so two outcomes
currently fall out of the pipeline. Gate 1 is a posting table, materials fill from a posting, and the
duplicate guard keys on employer plus role. Stage 4 must decide whether a walk-in is a product output
or a report artifact, whether it consumes an application budget slot, and what role the duplicate
guard uses when a site only says it is hiring.

## Detection ladder

Try cheapest first, stop at the first confident result.

1. Read `robots.txt` and the sitemap, which often lists a careers page.
2. Score homepage links by text and address — "careers", "join our team".
3. Probe common paths: `/careers`, `/jobs`.
4. Look for links to known hiring platforms.
5. Crawl up to two levels deep within a fixed page budget.
6. If the site has hiring signals but static fetching cannot expose the target content, escalate to
   **one** bounded browser-render pass before declaring `NONE_FOUND`.

## Block detection

Check every response for: 403 or 429 status; challenge phrases or scripts; redirects to challenge or
login addresses; unexpectedly small pages; missing employer identity. A block disguised as a normal
page cannot be distinguished from a site with no careers page — measured signals catch most blocks,
not all, which is why `BLOCKED` and `UNCERTAIN` route to review rather than being treated as
`NONE_FOUND`.

## Failure-mode taxonomy

Every miss or review item gets one of these recorded, so detection accuracy is diagnosable rather
than just a number: sitemap miss; homepage-link scoring miss; common-path miss; unrecognized external
platform; client-rendered content; redirect or login issue; challenge or block; fetch or parser
failure; other, with notes.

## Discovery accounting labels

Every record returned by a place query gets exactly one: `eligible`; `closed`; `duplicate`;
`wrong-category`; `outside-radius`; `junk/unverifiable`; `eligible-without-website`.

**Missing websites are not noise** — those employers remain valid walk-in targets. This labelling is
what gives Investigation A its denominator.

## Overture Maps facts

**All of this moves. Re-verify before relying on it.** Last checked 2026-09-20.

- Overture collects no data in the field. It merges place listings contributed by member companies,
  matches duplicates with machine learning, and publishes monthly. Record the exact release per run.
- **`confidence` and `operating_status` are different tests and both are needed.** Confidence is the
  likelihood the place exists at all, 0 to 1, and is explicitly independent of whether the business
  is currently open. Neither substitutes for the other.
- **The legacy `categories` property was removed in the 2026-09 release.** Query `taxonomy` and
  `basic_category` instead.
- **Data and taxonomy move on different cycles** — places monthly, taxonomy quarterly in March, June,
  September and December. Pinning the release does not pin the categories; record both.
- Known issues Overture documents itself: duplicate listings, junk records, incomplete properties.
- Roughly four in five place records originate with Meta, sourced largely from public Facebook pages,
  so businesses with no online listing presence are likely underrepresented.

### Licensing — this one is an obligation, not a note

Source data carries CDLA Permissive 2.0, Apache 2.0, or CC0 1.0 depending on the contributing
source. **These require attribution if the data is redistributed.** Local single-applicant use is not
redistribution; any future export, sharing, or hosted deployment is. The obligation travels with the
data.

Contributing sources as of August 2026, largest first: Meta (58.5M, CDLA Permissive 2.0), Microsoft
(6.3M, CDLA), Foursquare (4.6M, Apache 2.0), BrightQuery (2.3M, CDLA), AllThePlaces (1.6M, CC0 1.0),
PinMeTo (164K, CDLA), DAC (149K, CDLA), Krick (17K, CDLA), RenderSEO (3.6K, CDLA).

## Posting identity

Every Posting has an internal canonical ID. A `PostingSourceRef` stores provider, source URL,
immutable snapshot hash, and a platform-native posting ID where one exists — board adapters use the
stable native ID rather than URL text as primary source identity.

**In stage 1 the native ID lives on the posting row as `source_posting_id`**, captured by
`rr add --job-id` or guessed from the link, because it is unretrofittable and one posting has exactly
one source until stage 3. `PostingSourceRef` arrives with the second source, and the column migrates
into it. Scoped per employer: a job ID is unique within one hiring system, not globally.

For sources without a native ID, derive a candidate fingerprint from normalized employer location,
title, job location, canonicalized URL, and source snapshot. **Low-confidence cross-source matches
are flagged as likely duplicates rather than merged automatically** (Investigation B sets the
threshold). This is why the duplicate guard keys on employer plus role independently of posting
identity: one real opening can exist as two canonical postings.

## Library choices for the fetching stages

Named in the superseded plan and not yet re-verified. `tbro` owns
[`../agent/tbro-stack-log.md`](../agent/tbro-stack-log.md); treat that as current and this as
historical intent.

| Concern | Choice |
| --- | --- |
| Employer place data | DuckDB reading Overture GeoParquet files |
| Web requests | httpx |
| Browser automation | Playwright in an isolated worker process |
| Page parsing | extruct, selectolax |
| Structured posting data | `schema.org/JobPosting` via extruct, preferred over parsing |

## Network security boundary

Written in stage 3 alongside the first code that fetches anything, and gated by the same source-policy
ADR.

- Accept only `http`/`https` destinations for automated fetching.
- Reject loopback, private, link-local, multicast, and other non-public targets.
- Revalidate every redirect target and resolved address before connecting.
- Apply request timeout, maximum response size, content-type, redirect-count, and page-budget limits.
- Treat fetched HTML as untrusted data.
- Use isolated Playwright contexts; never inherit the applicant's browser profile.
- Disable arbitrary downloads unless a specific adapter requires and validates them.
